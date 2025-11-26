"""
Enhanced Crack Detection Configuration
개선된 크랙 탐지 시스템 설정 파일

이 파일에서 모든 설정값을 수정할 수 있습니다.
"""

import os

# =============================================================================
# 기본 경로 설정
# =============================================================================
BASE_DIR = "/home/user/Prototyping_UOS"

# Excel 파일 저장 경로 (수정 가능)
EXCEL_OUTPUT_PATH = os.path.join(BASE_DIR, "PyDracula/init/data/crack_detection_results.xlsx")

# 탐지 결과 이미지 저장 경로 (수정 가능)
IMAGE_OUTPUT_PATH = os.path.join(BASE_DIR, "crack_detection_images")

# =============================================================================
# Pin-Hole 모델 설정 (픽셀 → 실제 크기 변환)
# =============================================================================
# 카메라 센서 크기 (mm) - 일반적인 스마트폰 카메라 기준
SENSOR_WIDTH_MM = 8.16   # S22 일반 모델 센서 가로
SENSOR_HEIGHT_MM = 6.14  # S22 일반 모델 센서 세로

# 카메라 초점거리 (mm) - 카메라 스펙에 맞게 수정 필요
FOCAL_LENGTH_MM = 5.4  # 일반적인 스마트폰 카메라

# 이미지 해상도 (픽셀) - 실제 촬영 이미지 해상도에 맞게 수정
IMAGE_WIDTH_PX = 4032
IMAGE_HEIGHT_PX = 3024

# 초해상화 스케일 (SR scale factor)
# 예: 2.0 = 2배 확대, 4.0 = 4배 확대
SUPER_RESOLUTION_SCALE = 4.0  # EDSR 모델의 스케일에 맞게 설정

# =============================================================================
# 크기 필터링 설정 (픽셀 단위)
# =============================================================================
# 최소 크랙 면적 (픽셀 단위) - 얇고 긴 균열 탐지
MIN_CRACK_AREA = 100  # 면적 필터링 비활성화

# 최소 크랙 폭 (픽셀 단위) - 매우 얇은 균열까지 탐지
MIN_CRACK_WIDTH = 0  # 폭 필터링 비활성화

# 최소 크랙 길이 (픽셀 단위) - 모든 길이의 균열 탐지
MIN_CRACK_LENGTH = 0  # 길이 필터링 비활성화 (원본 균열탐지.py와 동일)

# =============================================================================
# 시각화 설정
# =============================================================================
# 빨간색 오버레이 투명도 (0.0-1.0)
VISUALIZATION_ALPHA = 0.6  # 원본 균열탐지.py와 동일한 alpha 값

# 크랙 표시 색상 (BGR 형식)
CRACK_COLOR = [0, 0, 255]  # 빨간색

# =============================================================================
# 모델 추론 설정
# =============================================================================
# 슬라이딩 윈도우 크기 (multi_scale_inference와 동일하게 2048로 변경)
WINDOW_SIZE = 1024

# 윈도우 겹침 비율
OVERLAP_RATIO = 0.1

# 신뢰도 임계값
SCORE_THRESHOLD = 0.1  # multi_scale_inference와 동일하게 0.1로 설정

# =============================================================================
# 기본 좌표 설정 (이미지에서 좌표를 추출할 수 없는 경우 사용)
# =============================================================================
DEFAULT_LATITUDE = 37.5665   # 서울시청 위도
DEFAULT_LONGITUDE = 126.9780  # 서울시청 경도

# =============================================================================
# 파일 확장자 설정
# =============================================================================
DEFAULT_INPUT_SUFFIX = '.png'
DEFAULT_OUTPUT_SUFFIX = '.png'
DEFAULT_MASK_SUFFIX = '.png'

# =============================================================================
# 설정 사전 정의 (코드에서 사용)
# =============================================================================
CONFIG = {
    'EXCEL_OUTPUT_PATH': EXCEL_OUTPUT_PATH,
    'IMAGE_OUTPUT_PATH': IMAGE_OUTPUT_PATH,
    'MIN_CRACK_AREA': MIN_CRACK_AREA,
    'MIN_CRACK_WIDTH': MIN_CRACK_WIDTH,
    'MIN_CRACK_LENGTH': MIN_CRACK_LENGTH,
    'VISUALIZATION_ALPHA': VISUALIZATION_ALPHA,
    'CRACK_COLOR': CRACK_COLOR,
    'WINDOW_SIZE': WINDOW_SIZE,
    'OVERLAP_RATIO': OVERLAP_RATIO,
    'SCORE_THRESHOLD': SCORE_THRESHOLD,
    'DEFAULT_LATITUDE': DEFAULT_LATITUDE,
    'DEFAULT_LONGITUDE': DEFAULT_LONGITUDE,
    'DEFAULT_INPUT_SUFFIX': DEFAULT_INPUT_SUFFIX,
    'DEFAULT_OUTPUT_SUFFIX': DEFAULT_OUTPUT_SUFFIX,
    'DEFAULT_MASK_SUFFIX': DEFAULT_MASK_SUFFIX,
    # Pin-hole model settings
    'SENSOR_WIDTH_MM': SENSOR_WIDTH_MM,
    'SENSOR_HEIGHT_MM': SENSOR_HEIGHT_MM,
    'FOCAL_LENGTH_MM': FOCAL_LENGTH_MM,
    'IMAGE_WIDTH_PX': IMAGE_WIDTH_PX,
    'IMAGE_HEIGHT_PX': IMAGE_HEIGHT_PX,
    'SUPER_RESOLUTION_SCALE': SUPER_RESOLUTION_SCALE,
}
