#!/usr/bin/env python3
"""
Generate damage maps with path tracking
균열 탐지 결과를 지도에 시각화
"""

import os
import json
import argparse
import pandas as pd
import folium
import base64
from branca.element import MacroElement, Template


class PolyLineDecorator(MacroElement):
    """Custom PolyLineDecorator using Leaflet.PolylineDecorator plugin."""
    
    _template = Template("""
        {% macro script(this, kwargs) %}
            var script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/leaflet-polylinedecorator@1.6.0/dist/leaflet.polylineDecorator.min.js';
            document.head.appendChild(script);
            
            script.onload = function() {
                var pathCoordinates = {{ this.path_coordinates }};
                
                var polyline = L.polyline(pathCoordinates, {
                    color: 'red',
                    weight: 3,
                    opacity: 0.7
                }).addTo({{ this._parent.get_name() }});
                
                var decorator = L.polylineDecorator(polyline, {
                    patterns: [
                        {
                            offset: '5%',
                            repeat: '100px',
                            symbol: L.Symbol.arrowHead({
                                pixelSize: 12,
                                polygon: false,
                                pathOptions: {
                                    stroke: true,
                                    weight: 2,
                                    color: 'red',
                                    fillOpacity: 1,
                                    fillColor: 'red'
                                }
                            })
                        }
                    ]
                }).addTo({{ this._parent.get_name() }});
            };
        {% endmacro %}
    """)
    
    def __init__(self, path_coordinates):
        super(PolyLineDecorator, self).__init__()
        self._name = 'PolyLineDecorator'
        self.path_coordinates = path_coordinates


def read_excel(excel_path):
    """Read Excel file and return DataFrame."""
    df = pd.read_excel(excel_path)
    return df


def read_metadata_json(json_path):
    """Read all images metadata JSON file for path tracking."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return metadata
    except FileNotFoundError:
        print(f"Warning: Metadata file not found: {json_path}")
        return []
    except Exception as e:
        print(f"Warning: Error reading metadata: {e}")
        return []


def make_damage_list(df):
    """Convert DataFrame to list of damage data dictionaries."""
    if df is None or df.empty:
        print("Invalid DataFrame")
        return []
    
    ITEMS_DATA = []
    
    for index, row in df.iterrows():
        # 균열 정보 추출
        crack_count = row.get('균열 개수', 0)
        avg_width = row.get('평균 균열 폭(mm)', 0)
        max_width = row.get('최대 균열 폭(mm)', 0)
        total_length = row.get('총 균열 길이(mm)', 0)
        timestamp = row.get('촬영시간', '')
        
        # 촬영시간 포맷팅 (ISO 형식 → 읽기 쉬운 형식)
        formatted_time = timestamp
        if timestamp and 'T' in str(timestamp):
            try:
                # ISO 형식 (2023-10-15T14:30:00) → 2023-10-15 14:30:00
                formatted_time = str(timestamp).replace('T', ' ')
            except:
                formatted_time = str(timestamp)
        
        item_dict = {
            "name": formatted_time if formatted_time else f"이미지 {index + 1}",
            "image_path": row['이미지 경로'], 
            "latitude": row['위도'],
            "longitude": row['경도'],
            "timestamp": formatted_time,
            "crack_count": crack_count,
            "avg_width_mm": avg_width,
            "max_width_mm": max_width,
            "total_length_mm": total_length,
        }
        ITEMS_DATA.append(item_dict)
    
    return ITEMS_DATA


def make_popup_html(item, encoded_image=None):
    """Create HTML content for popup with crack information."""
    if item is None:
        return ""
    
    # 균열 정보 추출
    crack_count = item.get('crack_count', 0)
    avg_width = item.get('avg_width_mm', 0)
    max_width = item.get('max_width_mm', 0)
    total_length = item.get('total_length_mm', 0)
    timestamp = item.get('timestamp', '')
    
    # 헤더 정보 (촬영 시간)
    header_html = f"""
    <div style="margin-bottom: 10px; padding: 5px; background-color: #e3f2fd; border-radius: 3px;">
        <b style="font-size: 14px;">📸 {timestamp if timestamp else '촬영 정보'}</b>
    </div>
    """
    
    # 위치 정보
    location_html = f"""
    <div style="margin: 5px 0; font-size: 11px; color: #666;">
        📍 위도: {item['latitude']:.6f}<br>
        📍 경도: {item['longitude']:.6f}
    </div>
    """
    
    # 균열 정보 HTML 생성
    crack_info = f"""
    <div style="margin: 5px 0; padding: 5px; background-color: #f0f0f0; border-radius: 3px;">
        <b>🔍 균열 정보</b><br>
        • 균열 개수: {crack_count}개<br>
        • 평균 폭: {avg_width:.2f}mm<br>
        • 최대 폭: {max_width:.2f}mm<br>
        • 총 길이: {total_length:.2f}mm
    </div>
    """
    
    if encoded_image is None:
        html_template = f"""
        {header_html}
        {location_html}
        {crack_info}
        (이미지 없음)
        """
    else:
        html_template = f"""
        <div style="width: 250px;">
            {header_html}
            {location_html}
            {crack_info}
            <img src="data:image/jpeg;base64,{encoded_image}" width="200" style="margin-top: 5px; border-radius: 3px;">
        </div>
        """
    return html_template


def make_total_damage_map(damage_data, html_path_total, image_dir, metadata=None):
    """
    Generate total damage map with path tracking and crack markers.
    """
    if damage_data is None or len(damage_data) == 0:
        print("Invalid Damage Data")
        return
    
    avg_lat = sum(item['latitude'] for item in damage_data) / len(damage_data)
    avg_lon = sum(item['longitude'] for item in damage_data) / len(damage_data)
    map_center = [avg_lat, avg_lon]

    damage_map = folium.Map(location=map_center, zoom_start=11, tiles='Esri.WorldImagery', attr='Esri')

    # Add Path Tracking
    if metadata and len(metadata) > 0:
        path_coordinates = []
        for item in metadata:
            if item.get('has_gps', False):
                path_coordinates.append([item['latitude'], item['longitude']])
        
        if len(path_coordinates) > 1:
            decorator = PolyLineDecorator(path_coordinates)
            damage_map.add_child(decorator)
            
            for item in metadata:
                if item.get('has_gps', False):
                    folium.CircleMarker(
                        location=[item['latitude'], item['longitude']],
                        radius=3,
                        color='cyan',
                        fill=True,
                        fillColor='cyan',
                        fillOpacity=0.6,
                        tooltip=f"{item['image_name']}\n{item.get('timestamp', 'N/A')}"
                    ).add_to(damage_map)
            
            print(f"Path tracking added: {len(path_coordinates)} locations")
    
    # Add Crack Detection Markers
    for item in damage_data:
        image_path = os.path.join(image_dir, item.get("image_path"))
        
        if os.path.exists(image_path):
            encoded_image = base64.b64encode(open(image_path, 'rb').read()).decode()
        else:
            encoded_image = None
            print(f"Warning: Image not found: {item.get('image_path')}")
        
        popup_html = make_popup_html(item, encoded_image)

        # Tooltip 정보 생성 (촬영시간 + 균열 요약)
        timestamp = item.get('timestamp', '')
        tooltip_text = f"📸 {timestamp}\n🔍 균열 {item.get('crack_count', 0)}개 (최대폭: {item.get('max_width_mm', 0):.1f}mm)"

        if encoded_image is None:
            popup = folium.Popup(popup_html, max_width=300)
        else:
            iframe = folium.IFrame(popup_html, width=280, height=450)
            popup = folium.Popup(iframe)
        
        folium.Marker(
            location=[item['latitude'], item['longitude']],
            popup=popup,
            tooltip=tooltip_text,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(damage_map)

    damage_map.save(html_path_total)
    print(f"Total damage map saved to: {html_path_total}")


def make_each_damage_map(map_data, html_path_each, image_dir):
    """Generate individual damage map for a single location."""
    if map_data is None:
        print("Invalid Damage Data")
        return
    
    map_center = [map_data['latitude'], map_data['longitude']]
    damage_map = folium.Map(location=map_center, zoom_start=15, tiles='Esri.WorldImagery', attr='Esri')

    image_path = os.path.join(image_dir, map_data.get("image_path"))
    
    if os.path.exists(image_path):
        encoded_image = base64.b64encode(open(image_path, 'rb').read()).decode()
    else:
        encoded_image = None

    popup_html = make_popup_html(map_data, encoded_image)

    # Tooltip 정보 생성 (촬영시간 + 균열 요약)
    timestamp = map_data.get('timestamp', '')
    tooltip_text = f"📸 {timestamp}\n🔍 균열 {map_data.get('crack_count', 0)}개 (최대폭: {map_data.get('max_width_mm', 0):.1f}mm)"

    if encoded_image is None:
        popup = folium.Popup(popup_html, max_width=300)
    else:
        iframe = folium.IFrame(popup_html, width=280, height=450)
        popup = folium.Popup(iframe)

    folium.Marker(
        location=[map_data['latitude'], map_data['longitude']],
        popup=popup,
        tooltip=tooltip_text
        ).add_to(damage_map)

    damage_map.save(html_path_each)
    print(f"Individual damage map saved to: {html_path_each}")


def main():
    """Main function to generate maps."""
    parser = argparse.ArgumentParser(description='Generate damage maps')
    parser.add_argument('--excel_input', required=True, help='Input Excel file with crack data')
    parser.add_argument('--metadata_json', required=True, help='Metadata JSON file for path tracking')
    parser.add_argument('--image_dir', required=True, help='Directory containing crack images')
    parser.add_argument('--output_html', required=True, help='Output HTML file for total map')
    parser.add_argument('--individual_html', required=True, help='Output HTML file for individual map')
    
    args = parser.parse_args()
    
    print("="*60)
    print("Damage Map Generation with Path Tracking")
    print("="*60)
    
    if not os.path.exists(args.excel_input):
        print(f"Error: Excel file not found at {args.excel_input}")
        return
    
    print(f"\nReading crack detection data from: {args.excel_input}")
    
    df = read_excel(args.excel_input)
    damage_data = make_damage_list(df)
    
    if not damage_data or len(damage_data) == 0:
        print("Error: No damage data found in Excel file")
        return
    
    print(f"Found {len(damage_data)} crack detection locations")
    
    print(f"\nReading path tracking data from: {args.metadata_json}")
    metadata = read_metadata_json(args.metadata_json)
    
    if metadata and len(metadata) > 0:
        print(f"Found {len(metadata)} total images for path tracking")
    else:
        print("Warning: No metadata found. Map will be generated without path tracking.")
    
    print("\nGenerating total damage map...")
    make_total_damage_map(damage_data, args.output_html, args.image_dir, metadata)
    
    print("\nGenerating individual damage map (first location)...")
    make_each_damage_map(damage_data[0], args.individual_html, args.image_dir)
    
    print("\n" + "="*60)
    print("All maps generated successfully")
    print("="*60)
    print(f"Total map (with path): {args.output_html}")
    print(f"Individual map: {args.individual_html}")
    print("\nData Sources:")
    print("  - Path tracking: metadata JSON (all images)")
    print("  - Crack markers: Excel file (detected only)")
    print("\nMap Legend:")
    print("  - Red Line: Movement path (time sequence)")
    print("  - Arrows: Direction of movement")
    print("  - Cyan Dots: All image capture locations")
    print("  - Red Markers: Crack detection locations (click for image)")
    print("="*60)


if __name__ == "__main__":
    main()

