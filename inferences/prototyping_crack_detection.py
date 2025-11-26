#!/usr/bin/env python3
"""
Crack Detection for Prototyping Examples
Prototyping_examples 이미지에 대한 균열 탐지 및 GPS 메타데이터 통합

python inferences/prototyping_crack_detection.py --crack_config 
"""

import os
import sys
import json
import argparse
import pandas as pd
import numpy as np
import mmcv
import cv2
from glob import glob
from mmseg.apis import init_model
from torch.cuda import empty_cache
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# 기존 모듈 import
sys.path.append(os.path.dirname(__file__))
from quantify_seg_results import quantify_crack_width_length
from utils import inference_segmentor_sliding_window
from config import CONFIG


def calculate_pixel_to_mm(shooting_distance_mm, config):
    """
    Pin-hole 모델을 이용하여 픽셀을 실제 크기(mm)로 변환하는 비율 계산
    
    공식: GSD (Ground Sampling Distance) = (센서크기 × 촬영거리) / (이미지픽셀 × 초점거리)
    
    Args:
        shooting_distance_mm (float): 촬영거리 (mm)
        config (dict): 카메라 설정 정보
    
    Returns:
        float: 1픽셀당 실제 크기 (mm/pixel)
    """
    sensor_width_mm = config['SENSOR_WIDTH_MM']
    focal_length_mm = config['FOCAL_LENGTH_MM']
    image_width_px = config['IMAGE_WIDTH_PX']
    sr_scale = config['SUPER_RESOLUTION_SCALE']
    
    # Pin-hole 모델: 1픽셀당 실제 크기
    # 초해상화로 픽셀이 증가했으므로 SR scale로 나눠야 함
    pixel_to_mm = (sensor_width_mm * shooting_distance_mm) / (focal_length_mm * image_width_px * sr_scale)
    
    return pixel_to_mm


def convert_crack_to_real_size(crack_quantification_results, pixel_to_mm):
    """
    픽셀 단위 균열 정보를 실제 크기(mm)로 변환
    
    Args:
        crack_quantification_results (list): [(coordinates, "avg_width x max_width x length", class_id), ...]
        pixel_to_mm (float): 픽셀→mm 변환 비율
    
    Returns:
        list: [(coordinates, avg_width_mm, max_width_mm, length_mm, measurement_str, class_id), ...]
    """
    converted_results = []
    
    for result in crack_quantification_results:
        coordinates = result[0]
        measurements = result[1]
        class_id = result[2]
        
        try:
            # "avg_width x max_width x length" 형식 파싱
            parts = measurements.split('x')
            avg_width_px = float(parts[0])
            max_width_px = float(parts[1])
            length_px = float(parts[2])
            
            # 실제 크기로 변환 (width는 반지름이므로 2배)
            avg_width_mm = avg_width_px * pixel_to_mm * 2
            max_width_mm = max_width_px * pixel_to_mm * 2
            length_mm = length_px * pixel_to_mm
            
            measurement_str = f"평균:{avg_width_mm:.2f}mm, 최대:{max_width_mm:.2f}mm, 길이:{length_mm:.2f}mm"
            
            converted_results.append([
                coordinates,
                avg_width_mm,
                max_width_mm,
                length_mm,
                measurement_str,
                class_id
            ])
        except Exception as e:
            print(f"Warning: Failed to convert crack measurement: {e}")
            continue
    
    return converted_results


def load_metadata_json(json_path):
    """Load GPS metadata from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Create a dictionary for quick lookup by image name
    metadata_dict = {item['image_name']: item for item in metadata}
    return metadata_dict


def get_exif_gps_from_image(image_path):
    """
    Extract GPS coordinates from image EXIF data.
    Returns (latitude, longitude) or (None, None) if not found.
    """
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if exif_data is None:
            return None, None
        
        # Get GPS info
        gps_info = {}
        for key, value in exif_data.items():
            tag = TAGS.get(key, key)
            if tag == 'GPSInfo':
                for gps_key in value:
                    gps_tag = GPSTAGS.get(gps_key, gps_key)
                    gps_info[gps_tag] = value[gps_key]
        
        if not gps_info:
            return None, None
        
        # Convert to decimal degrees
        def convert_to_degrees(value):
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)
        
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
        print(f"Error extracting GPS from {image_path}: {e}")
        return None, None


def filter_crack_by_size(crack_quantification_results, min_area=None, min_width=None, min_length=None):
    """크기 기준으로 크랙 필터링 (값이 0이면 필터링 비활성화)"""
    if not crack_quantification_results:
        return []
    
    filtered_results = []
    
    for result in crack_quantification_results:
        coordinates = result[0]
        measurements = result[1]
        
        try:
            # "avg_width x max_width x length" 형식 파싱
            parts = measurements.split('x')
            avg_width = float(parts[0])
            max_width = float(parts[1])
            length = float(parts[2])
        except:
            continue
        
        # 면적 계산
        coord_parts = coordinates.replace('(', '').replace(')', '').split('-')
        if len(coord_parts) == 2:
            try:
                min_coords = tuple(map(int, coord_parts[0].split(',')))
                max_coords = tuple(map(int, coord_parts[1].split(',')))
                area = (max_coords[0] - min_coords[0]) * (max_coords[1] - min_coords[1])
            except:
                area = avg_width * length
        else:
            area = avg_width * length
        
        # 크기 필터링 (0이면 필터링 안함)
        if min_area is not None and min_area > 0 and area < min_area:
            continue
        if min_width is not None and min_width > 0 and avg_width < min_width:
            continue
        if min_length is not None and min_length > 0 and length < min_length:
            continue
        
        filtered_results.append(result)
    
    return filtered_results


def visualize_crack_detection(seg_result, crack_mask, color=None, alpha=None):
    """크랙 탐지 결과를 빨간색 오버레이로 시각화"""
    if color is None:
        color = CONFIG['CRACK_COLOR']
    if alpha is None:
        alpha = CONFIG['VISUALIZATION_ALPHA']
    
    mask_bool = crack_mask == 1
    color_array = np.array(color, dtype=np.uint8)
    
    seg_result[mask_bool, :] = seg_result[mask_bool, :] * (1 - alpha) + color_array * alpha
    
    return seg_result


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Crack Detection for Prototyping Examples')
    parser.add_argument('--crack_config', required=True, help='크랙 탐지 모델 설정 파일 경로')
    parser.add_argument('--crack_checkpoint', required=True, help='크랙 탐지 모델 체크포인트 파일 경로')
    parser.add_argument('--input_dir', default='/home/user/PT/Prototyping_examples', help='입력 이미지 디렉토리')
    parser.add_argument('--output_dir', default='/home/user/PT/PyDracula/init/data/Images', help='결과 이미지 저장 디렉토리')
    parser.add_argument('--metadata_json', default='/home/user/PT/PyDracula/init/data/all_images_metadata.json', help='GPS 메타데이터 JSON 파일')
    parser.add_argument('--excel_output', default='/home/user/PT/PyDracula/init/data/data.xlsx', help='Excel 출력 파일 경로')
    parser.add_argument('--shooting_distance_mm', type=float, required=True, help='촬영거리 (mm 단위)')
    
    args = parser.parse_args()
    
    # 픽셀→mm 변환 비율 계산
    pixel_to_mm = calculate_pixel_to_mm(args.shooting_distance_mm, CONFIG)
    print(f"\nPixel to mm conversion rate: {pixel_to_mm:.6f} mm/pixel")
    print(f"Shooting distance: {args.shooting_distance_mm/1000:.2f}m ({args.shooting_distance_mm}mm)")
    print(f"Super-resolution scale: {CONFIG['SUPER_RESOLUTION_SCALE']}x")
    
    # 출력 디렉토리 생성
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("="*60)
    print("Crack Detection for Prototyping Examples")
    print("="*60)
    
    # GPS 메타데이터 로드
    print(f"\nLoading GPS metadata from: {args.metadata_json}")
    if os.path.exists(args.metadata_json):
        metadata_dict = load_metadata_json(args.metadata_json)
        print(f"Loaded metadata for {len(metadata_dict)} images")
    else:
        print(f"Warning: Metadata file not found. Will extract GPS from EXIF.")
        metadata_dict = {}
    
    # 모델 초기화
    print(f"\nInitializing crack detection model...")
    crack_model = init_model(args.crack_config, args.crack_checkpoint, device='cuda:0')
    print("Model initialized successfully")
    
    # 입력 이미지 리스트
    img_list = glob(os.path.join(args.input_dir, '*.jpg')) + \
               glob(os.path.join(args.input_dir, '*.JPG')) + \
               glob(os.path.join(args.input_dir, '*.png'))
    
    print(f"\nFound {len(img_list)} images to process")
    
    # 탐지 결과 저장용 리스트
    detection_results = []
    
    # 각 이미지에 대해 처리
    for idx, img_path in enumerate(sorted(img_list)):
        img_name = os.path.basename(img_path)
        print(f"\n[{idx+1}/{len(img_list)}] Processing: {img_name}")
        
        try:
            # 크랙 탐지 수행
            _, crack_mask = inference_segmentor_sliding_window(
                crack_model, img_path,
                color_mask=None,
                score_thr=CONFIG['SCORE_THRESHOLD'],
                window_size=CONFIG['WINDOW_SIZE'],
                overlap_ratio=CONFIG['OVERLAP_RATIO']
            )
            
            # 원본 이미지 로드
            seg_result = mmcv.imread(img_path)
            
            # 크랙 정량화 (픽셀 단위)
            seg_result_with_annotation, crack_quantification_results = quantify_crack_width_length(
                seg_result.copy(), crack_mask, CONFIG['CRACK_COLOR']
            )
            
            print(f"Detected: {len(crack_quantification_results)} cracks (pixel units)")
            
            # 실제 크기로 변환 (mm 단위)
            crack_real_size_results = convert_crack_to_real_size(
                crack_quantification_results, 
                pixel_to_mm
            )
            
            print(f"Converted to real size: {len(crack_real_size_results)} cracks")
            
            # 크기 필터링 (실제 크기 기준)
            # crack_real_size_results 구조: [coordinates, avg_width_mm, max_width_mm, length_mm, measurement_str, class_id]
            filtered_cracks = [
                crack for crack in crack_real_size_results
                if crack[1] >= CONFIG['MIN_CRACK_WIDTH'] and crack[3] >= CONFIG['MIN_CRACK_LENGTH']
            ]
            
            print(f"After filtering: {len(filtered_cracks)} cracks")
            
            # 균열이 탐지되면 저장
            has_cracks = len(crack_real_size_results) > 0
            
            if has_cracks:
                # GPS 정보 및 촬영 시간 가져오기
                timestamp = None
                if img_name in metadata_dict:
                    latitude = metadata_dict[img_name]['latitude']
                    longitude = metadata_dict[img_name]['longitude']
                    timestamp = metadata_dict[img_name].get('timestamp', None)
                    print(f"GPS from metadata: {latitude:.6f}, {longitude:.6f}")
                    if timestamp:
                        print(f"Timestamp: {timestamp}")
                else:
                    # EXIF에서 GPS 추출 시도
                    latitude, longitude = get_exif_gps_from_image(img_path)
                    if latitude and longitude:
                        print(f"GPS from EXIF: {latitude:.6f}, {longitude:.6f}")
                    else:
                        print(f"Warning: No GPS data found, skipping...")
                        continue
                
                # 결과 이미지 저장
                output_name = img_name.replace('.png', '.jpg').replace('.PNG', '.jpg')
                output_path = os.path.join(args.output_dir, output_name)
                
                # 시각화
                visualized_image = visualize_crack_detection(
                    seg_result.copy(), crack_mask,
                    color=CONFIG['CRACK_COLOR'],
                    alpha=CONFIG['VISUALIZATION_ALPHA']
                )
                
                # JPG로 저장 (400x400 리사이즈)
                resized = cv2.resize(visualized_image, (400, 400), interpolation=cv2.INTER_AREA)
                cv2.imwrite(output_path, resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                print(f"Saved to: {output_path}")
                
                # 균열 정보 수집
                # crack_real_size_results 구조: [coordinates, avg_width_mm, max_width_mm, length_mm, measurement_str, class_id]
                if crack_real_size_results:
                    crack_count = len(crack_real_size_results)
                    
                    # 평균 균열 폭 (모든 균열의 평균 폭의 평균)
                    avg_width_mm = np.mean([c[1] for c in crack_real_size_results])
                    
                    # 최대 균열 폭 (모든 균열의 최대 폭 중 최댓값)
                    max_width_mm = np.max([c[2] for c in crack_real_size_results])
                    
                    # 총 길이 (모든 균열 길이의 합)
                    total_length_mm = np.sum([c[3] for c in crack_real_size_results])
                else:
                    avg_width_mm = 0
                    max_width_mm = 0
                    total_length_mm = 0
                    crack_count = 0
                
                # 탐지 결과 추가
                detection_results.append({
                    '위도': latitude,
                    '경도': longitude,
                    '이미지 경로': output_name,
                    '촬영시간': timestamp if timestamp else '',
                    '균열 개수': crack_count,
                    '평균 균열 폭(mm)': round(avg_width_mm, 2),
                    '최대 균열 폭(mm)': round(max_width_mm, 2),
                    '총 균열 길이(mm)': round(total_length_mm, 2),
                })
            else:
                print(f"No significant cracks detected")
            
            # GPU 메모리 정리
            empty_cache()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Excel 파일로 저장
    if detection_results:
        df = pd.DataFrame(detection_results)
        df.to_excel(args.excel_output, index=False, engine='openpyxl')
        print(f"\nDetection results saved to Excel: {args.excel_output}")
        print(f"Total images with cracks: {len(detection_results)}")
    else:
        print(f"\nWarning: No cracks detected in any images")
    
    print("\n" + "="*60)
    print("Crack Detection Complete!")
    print("="*60)


if __name__ == '__main__':
    main()

