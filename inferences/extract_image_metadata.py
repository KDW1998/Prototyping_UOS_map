#!/usr/bin/env python3
"""
Extract GPS and timestamp information from images
이미지로부터 GPS 좌표와 시간 정보를 추출하는 스크립트
"""

import os
import json
import argparse
from glob import glob
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pandas as pd


def get_exif_data(image_path):
    """이미지에서 EXIF 데이터 추출"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if exif_data is None:
            return None
        
        exif = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            exif[tag] = value
        
        return exif
    except Exception as e:
        print(f"Error reading EXIF from {image_path}: {e}")
        return None


def get_gps_info(exif_data):
    """EXIF 데이터에서 GPS 정보 추출"""
    if exif_data is None:
        return None
    
    gps_info = {}
    
    if 'GPSInfo' in exif_data:
        for key in exif_data['GPSInfo'].keys():
            decode = GPSTAGS.get(key, key)
            gps_info[decode] = exif_data['GPSInfo'][key]
    
    return gps_info if gps_info else None


def convert_to_degrees(value):
    """GPS 좌표를 도(degree) 단위로 변환"""
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)


def get_lat_lon(gps_info):
    """GPS 정보에서 위도, 경도 추출"""
    if not gps_info:
        return None, None
    
    try:
        lat = None
        lon = None
        
        if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
            lat = convert_to_degrees(gps_info['GPSLatitude'])
            if gps_info['GPSLatitudeRef'] == 'S':
                lat = -lat
        
        if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
            lon = convert_to_degrees(gps_info['GPSLongitude'])
            if gps_info['GPSLongitudeRef'] == 'W':
                lon = -lon
        
        return lat, lon
    except Exception as e:
        print(f"Error converting GPS coordinates: {e}")
        return None, None


def get_timestamp(exif_data):
    """EXIF 데이터에서 시간 정보 추출"""
    if exif_data is None:
        return None
    
    time_fields = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
    
    for field in time_fields:
        if field in exif_data:
            try:
                timestamp_str = exif_data[field]
                timestamp = datetime.strptime(timestamp_str, "%Y:%m:%d %H:%M:%S")
                return timestamp
            except Exception as e:
                continue
    
    return None


def extract_metadata_from_images(image_dir, output_excel=None, output_json=None):
    """
    이미지 디렉토리에서 모든 이미지의 메타데이터 추출
    """
    image_files = glob(os.path.join(image_dir, "*.jpg")) + \
                  glob(os.path.join(image_dir, "*.JPG")) + \
                  glob(os.path.join(image_dir, "*.png")) + \
                  glob(os.path.join(image_dir, "*.PNG"))
    
    print(f"Found {len(image_files)} images in {image_dir}")
    
    metadata_list = []
    images_with_gps = 0
    images_with_time = 0
    
    for img_path in sorted(image_files):
        img_name = os.path.basename(img_path)
        print(f"\nProcessing: {img_name}")
        
        exif_data = get_exif_data(img_path)
        gps_info = get_gps_info(exif_data)
        lat, lon = get_lat_lon(gps_info)
        timestamp = get_timestamp(exif_data)
        
        if lat and lon:
            print(f"  GPS: {lat:.6f}, {lon:.6f}")
            images_with_gps += 1
        else:
            print(f"  GPS: Not found")
        
        if timestamp:
            print(f"  Time: {timestamp}")
            images_with_time += 1
        else:
            print(f"  Time: Not found")
        
        metadata = {
            'image_name': img_name,
            'image_path': img_path,
            'latitude': lat,
            'longitude': lon,
            'timestamp': timestamp.isoformat() if timestamp else None,
            'timestamp_object': timestamp,
            'has_gps': lat is not None and lon is not None,
            'has_timestamp': timestamp is not None
        }
        
        metadata_list.append(metadata)
    
    metadata_list_sorted = sorted(
        metadata_list, 
        key=lambda x: x['timestamp_object'] if x['timestamp_object'] else datetime.max
    )
    
    print(f"\n" + "="*60)
    print(f"Summary:")
    print(f"  Total images: {len(image_files)}")
    print(f"  Images with GPS: {images_with_gps}")
    print(f"  Images with timestamp: {images_with_time}")
    print(f"="*60)
    
    if output_excel:
        df_data = []
        for idx, metadata in enumerate(metadata_list_sorted):
            df_data.append({
                'sequence': idx + 1,
                'image_name': metadata['image_name'],
                'latitude': metadata['latitude'],
                'longitude': metadata['longitude'],
                'timestamp': metadata['timestamp'],
                'has_gps': metadata['has_gps'],
                'has_timestamp': metadata['has_timestamp']
            })
        
        df = pd.DataFrame(df_data)
        df.to_excel(output_excel, index=False, engine='openpyxl')
        print(f"\nExcel file saved to: {output_excel}")
    
    if output_json:
        json_data = []
        for idx, metadata in enumerate(metadata_list_sorted):
            json_data.append({
                'sequence': idx + 1,
                'image_name': metadata['image_name'],
                'latitude': metadata['latitude'],
                'longitude': metadata['longitude'],
                'timestamp': metadata['timestamp'],
                'has_gps': metadata['has_gps'],
                'has_timestamp': metadata['has_timestamp']
            })
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"JSON file saved to: {output_json}")
    
    return metadata_list_sorted


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Extract GPS metadata from images')
    parser.add_argument('--input_dir', required=True, help='Input image directory')
    parser.add_argument('--output_json', required=True, help='Output JSON file path')
    parser.add_argument('--output_excel', required=True, help='Output Excel file path')
    
    args = parser.parse_args()
    
    metadata = extract_metadata_from_images(args.input_dir, args.output_excel, args.output_json)
    
    print(f"\nMetadata extraction complete.")
    print(f"Total entries: {len(metadata)}")


if __name__ == "__main__":
    main()

