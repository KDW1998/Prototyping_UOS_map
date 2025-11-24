#!/bin/bash

##############################################################################
# Crack Detection and Map Generation Workflow
# 균열 탐지 및 지도 생성 자동화 시스템
#
# 사용법:
#   bash 균열탐지.sh
##############################################################################

set -e

# Path configuration (경로 설정)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

##############################################################################
# STEP -1: 촬영거리 입력받기
##############################################################################
echo "============================================================"
echo "균열 탐지 및 지도 생성 시스템"
echo "============================================================"
echo ""
echo "실제 균열 크기를 계산하기 위해 촬영거리 정보가 필요합니다."
echo ""
echo "촬영거리 입력 (단위: 미터, 예: 1.5):"
read -p "> " SHOOTING_DISTANCE

# 입력값 검증
if ! [[ "$SHOOTING_DISTANCE" =~ ^[0-9]*\.?[0-9]+$ ]]; then
    echo "오류: 올바른 숫자를 입력해주세요. (예: 1.5)"
    exit 1
fi

# 미터를 밀리미터로 변환
SHOOTING_DISTANCE_MM=$(echo "$SHOOTING_DISTANCE * 1000" | bc)

echo ""
echo "입력된 촬영거리: ${SHOOTING_DISTANCE}m (${SHOOTING_DISTANCE_MM}mm)"
echo ""

# Model configuration (모델 설정)
SR_CONFIG="$SCRIPT_DIR/모델/초해상화/초해상화_config.py"
SR_CHECKPOINT="$SCRIPT_DIR/모델/초해상화/초해상화_weight.pth"
CRACK_CONFIG="$SCRIPT_DIR/모델/균열탐지/균열탐지_config.py"
CRACK_CHECKPOINT="$SCRIPT_DIR/모델/균열탐지/균열탐지_weight.pth"

# Directory paths (디렉토리 경로)
INPUT_DIR="$SCRIPT_DIR/촬영이미지"
SR_OUTPUT_DIR="$SCRIPT_DIR/초해상화_이미지"
OUTPUT_DIR="$SCRIPT_DIR/균열탐지_결과/균열이미지"
METADATA_JSON="$SCRIPT_DIR/균열탐지_결과/이미지정보.json"
EXCEL_OUTPUT="$SCRIPT_DIR/균열탐지_결과/균열목록.xlsx"
MAP_OUTPUT="$SCRIPT_DIR/균열탐지_지도_결과.html"
INDIVIDUAL_MAP_OUTPUT="$SCRIPT_DIR/균열탐지_결과/개별위치_지도.html"

# Create directories
mkdir -p "$SR_OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
mkdir -p "$(dirname "$METADATA_JSON")"

echo "입력 폴더: $INPUT_DIR"
echo "결과 폴더: $SCRIPT_DIR/균열탐지_결과"
echo ""

##############################################################################
# STEP 0: GPS 정보 추출
##############################################################################
echo "============================================================"
echo "STEP 0/4: 이미지에서 GPS 정보 추출 중"
echo "============================================================"

cd "$SCRIPT_DIR/inferences"
python3 extract_image_metadata.py \
    --input_dir "$INPUT_DIR" \
    --output_json "$METADATA_JSON" \
    --output_excel "$SCRIPT_DIR/균열탐지_결과/이미지정보.xlsx"

if [ $? -eq 0 ]; then
    echo "GPS 정보 추출 완료"
else
    echo "오류: GPS 정보 추출 실패"
    exit 1
fi
echo ""

##############################################################################
# STEP 1: 초해상화 처리
##############################################################################
echo "============================================================"
echo "STEP 1/4: 이미지 화질 향상 중 (초해상화 처리)"
echo "============================================================"

cd "$SCRIPT_DIR"

python3 inferences/super_resolution.py \
    --model-name edsr \
    --model-config "$SR_CONFIG" \
    --model-ckpt "$SR_CHECKPOINT" \
    --img-dir "$INPUT_DIR" \
    --result-out-dir "$SR_OUTPUT_DIR" \
    --device cuda

if [ $? -eq 0 ]; then
    echo "이미지 화질 향상 완료"
else
    echo "오류: 이미지 화질 향상 실패"
    exit 1
fi
echo ""

##############################################################################
# STEP 2: 균열 탐지
##############################################################################
echo "============================================================"
echo "STEP 2/4: AI 균열 탐지 수행 중"
echo "============================================================"

cd "$SCRIPT_DIR"

python3 inferences/prototyping_crack_detection.py \
    --crack_config "$CRACK_CONFIG" \
    --crack_checkpoint "$CRACK_CHECKPOINT" \
    --input_dir "$SR_OUTPUT_DIR" \
    --output_dir "$OUTPUT_DIR" \
    --metadata_json "$METADATA_JSON" \
    --excel_output "$EXCEL_OUTPUT" \
    --shooting_distance_mm "$SHOOTING_DISTANCE_MM"

if [ $? -eq 0 ]; then
    echo "균열 탐지 완료"
else
    echo "오류: 균열 탐지 실패"
    exit 1
fi
echo ""

##############################################################################
# STEP 3: 지도 생성
##############################################################################
echo "============================================================"
echo "STEP 3/4: 지도 생성 중"
echo "============================================================"

cd "$SCRIPT_DIR/inferences"

python3 generate_maps.py \
    --excel_input "$EXCEL_OUTPUT" \
    --metadata_json "$METADATA_JSON" \
    --image_dir "$OUTPUT_DIR" \
    --output_html "$MAP_OUTPUT" \
    --individual_html "$INDIVIDUAL_MAP_OUTPUT"

if [ $? -eq 0 ]; then
    echo "지도 생성 완료"
else
    echo "오류: 지도 생성 실패"
    exit 1
fi
echo ""

##############################################################################
# 완료
##############################################################################
echo "============================================================"
echo "STEP 4/4: 모든 작업 완료"
echo "============================================================"
echo ""
echo "생성된 파일:"
echo "  - 균열 지도: $MAP_OUTPUT"
echo "  - 균열 목록: $EXCEL_OUTPUT"
echo "  - 균열 이미지: $OUTPUT_DIR"
echo ""
echo "지도를 열려면:"
echo "  xdg-open $MAP_OUTPUT"
echo ""
echo "============================================================"

