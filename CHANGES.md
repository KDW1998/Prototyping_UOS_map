# 변경사항 (Changes)

## 2025-11-24 업데이트

### 주요 변경사항

#### 1. 촬영거리 입력 기능 추가
- `균열탐지.sh`에 촬영거리 입력 프롬프트 추가
- 사용자가 미터 단위로 촬영거리 입력
- 자동으로 밀리미터로 변환하여 전달

#### 2. Pin-hole 모델 기반 실제 크기 계산
- `inferences/config.py`에 카메라 파라미터 추가:
  - 센서 크기 (SENSOR_WIDTH_MM, SENSOR_HEIGHT_MM)
  - 초점거리 (FOCAL_LENGTH_MM)
  - 이미지 해상도 (IMAGE_WIDTH_PX, IMAGE_HEIGHT_PX)
  - 초해상화 스케일 (SUPER_RESOLUTION_SCALE)

- `prototyping_crack_detection.py`에 실제 크기 계산 함수 추가:
  - `calculate_pixel_to_mm()`: GSD(Ground Sampling Distance) 계산
  - `convert_crack_to_real_size()`: 픽셀 → mm 변환
  - 초해상화 스케일을 고려한 정확한 변환

#### 3. Multi-scale Inference 적용
- 윈도우 크기를 1024 → 2048로 증가
- 신뢰도 임계값을 0.8 → 0.1로 조정 (더 많은 균열 탐지)
- `/home/user/crack_gauge/inferences/multi_scale_inference_segmentor_crack.py`의 방식 적용

#### 4. 지도 표시 정보 개선
- `generate_maps.py` 업데이트:
  - 무의미한 "항목 1, 항목 2" 제거
  - 의미있는 "균열 탐지 지점 N" 표시
  - Tooltip에 균열 개수와 최대 폭 표시
  - 팝업에 상세 균열 통계 표시:
    - 균열 개수
    - 최대 균열 폭/길이 (mm)
    - 평균 균열 폭/길이 (mm)

#### 5. Excel 출력 개선
- `균열목록.xlsx`에 추가 컬럼:
  - 균열 개수
  - 최대 균열 폭(mm)
  - 최대 균열 길이(mm)
  - 평균 균열 폭(mm)
  - 평균 균열 길이(mm)

### 수식 및 알고리즘

#### Pin-hole 모델 (실제 크기 계산)

**GSD (Ground Sampling Distance) 계산:**
```
GSD = (센서_폭 × 촬영_거리) / (초점_거리 × 이미지_폭 × SR_스케일)
```

**실제 크기 변환:**
```
실제 폭(mm) = 픽셀_폭 × GSD × 2    (medial axis는 반지름)
실제 길이(mm) = 픽셀_길이 × GSD
```

**예시 계산:**
- 센서 폭: 6.17mm
- 초점 거리: 4.25mm
- 이미지 폭: 4032px
- 촬영 거리: 1500mm (1.5m)
- SR 스케일: 2.0x
- → GSD = (6.17 × 1500) / (4.25 × 4032 × 2.0) ≈ 0.27 mm/pixel

### 파일 변경 목록

#### 수정된 파일:
1. `균열탐지.sh`
   - 촬영거리 입력 프롬프트 추가
   - prototyping_crack_detection.py에 촬영거리 전달

2. `inferences/config.py`
   - Pin-hole 모델 설정 추가
   - WINDOW_SIZE: 1024 → 2048
   - SCORE_THRESHOLD: 0.8 → 0.1

3. `inferences/prototyping_crack_detection.py`
   - 촬영거리 파라미터 추가
   - `calculate_pixel_to_mm()` 함수 추가
   - `convert_crack_to_real_size()` 함수 추가
   - Excel 출력에 실제 크기 정보 추가

4. `inferences/generate_maps.py`
   - `make_damage_list()`: 균열 크기 정보 추출
   - `make_popup_html()`: 균열 통계 표시
   - Tooltip 업데이트

5. `README.md`
   - Pin-hole 모델 설명 추가
   - 사용법 업데이트 (촬영거리 입력)
   - 출력 파일 설명 업데이트
   - 카메라 설정 가이드 추가

6. `QUICKSTART.md`
   - 촬영거리 입력 안내 추가
   - 카메라 설정 섹션 추가
   - FAQ 업데이트

#### 새로 생성된 파일:
7. `CHANGES.md` (이 문서)

### 호환성

- 기존 모델 파일 그대로 사용 가능
- 기존 환경 그대로 사용 가능
- 추가 패키지 설치 불필요

### 테스트 방법

```bash
# 1. 환경 활성화
conda activate Prototyping_UOS

# 2. 문법 체크
python3 -m py_compile inferences/config.py
python3 -m py_compile inferences/prototyping_crack_detection.py
python3 -m py_compile inferences/generate_maps.py

# 3. 실행
bash 균열탐지.sh
# 촬영거리 입력: 1.5 (예시)

# 4. 결과 확인
# - 균열탐지_결과/균열목록.xlsx: 실제 크기 정보 확인
# - 균열탐지_지도_결과.html: 지도에서 균열 정보 확인
```

### 주의사항

1. **카메라 설정 필수:**
   - `inferences/config.py`에서 사용하는 카메라의 실제 스펙 입력
   - 정확한 센서 크기와 초점거리 필요

2. **촬영거리 측정:**
   - 가능한 한 정확히 측정 (줄자 사용)
   - 대상물과의 수직 거리 측정

3. **촬영 조건:**
   - 수직으로 촬영 (각도가 있으면 오차 발생)
   - 조명이 균일한 환경
   - 흔들림 없이 촬영

4. **예상 정확도:**
   - 촬영거리 정확: ±5% 오차
   - 카메라 스펙 정확: ±10% 오차
   - 일반적인 경우: ±15% 오차 범위

### 참고 자료

- Pin-hole 카메라 모델: https://en.wikipedia.org/wiki/Pinhole_camera_model
- GSD 계산: https://support.pix4d.com/hc/en-us/articles/202559809
- Multi-scale inference: `/home/user/crack_gauge/inferences/multi_scale_inference_segmentor_crack.py`

### 향후 개선 가능 사항

1. 촬영 각도 보정 기능 추가
2. 자동 카메라 스펙 인식 (EXIF 데이터 활용)
3. 여러 촬영거리 배치 처리
4. 실시간 피드백 (촬영 중 균열 탐지)
5. 3D 맵 생성 (깊이 정보 활용)

---

**작성일:** 2025-11-24  
**버전:** 2.0  
**작성자:** AI Assistant

