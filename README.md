# 균열 탐지 시스템 (Crack Detection System)

초해상화(Super Resolution)와 균열 탐지(Crack Detection)를 결합한 AI 기반 파이프라인입니다.

## 시스템 요구사항

- **OS**: Linux (Windows WSL2 지원)
- **GPU**: NVIDIA CUDA 지원 GPU (CUDA 11.8 이상)
- **Python**: 3.9
- **Conda**: Anaconda 또는 Miniconda

## 환경 설정

### 방법 1: Conda Environment 파일 사용 (권장)

```bash
# 1. repository 클론 또는 다운로드
cd /path/to/Prototyping_UOS

# 2. conda 환경 생성
conda env create -f environment.yml

# 3. 환경 활성화
conda activate Prototyping_UOS
```

### 방법 2: requirements.txt 사용

```bash
# 1. conda 환경 생성 (Python 3.9)
conda create -n Prototyping_UOS python=3.9

# 2. 환경 활성화
conda activate Prototyping_UOS

# 3. PyTorch 설치 (CUDA 11.8)
conda install pytorch==2.0.1 torchvision pytorch-cuda=11.8 -c pytorch -c nvidia

# 4. 나머지 패키지 설치
pip install -r requirements.txt
```

## 프로젝트 구조

```
Prototyping_UOS/
├── 균열탐지.sh                    # 메인 실행 스크립트
├── environment.yml               # Conda 환경 설정 파일
├── requirements.txt             # Python 패키지 의존성 파일
├── README.md                    # 프로젝트 설명서 (현재 파일)
├── 사용방법.txt                  # 간단한 사용 설명서
├── 모델/                         # 모델 파일 디렉토리
│   ├── 초해상화/
│   │   ├── 초해상화_config.py
│   │   └── 초해상화_weight.pth
│   └── 균열탐지/
│       ├── 균열탐지_config.py
│       └── 균열탐지_weight.pth
├── inferences/                  # 유틸리티 함수
│   ├── extract_image_metadata.py
│   ├── generate_maps.py
│   ├── prototyping_crack_detection.py
│   ├── super_resolution.py
│   ├── quantify_seg_results.py
│   ├── utils.py
│   └── config.py
├── 촬영이미지/                   # 입력 이미지 폴더
└── 균열탐지_결과/                # 결과 저장 폴더
    ├── 균열이미지/               # 균열이 표시된 이미지들
    ├── 균열목록.xlsx            # 균열 위치 목록 (Excel)
    ├── 이미지정보.json          # GPS 메타데이터
    └── 개별위치_지도.html       # 개별 위치 지도
```

## 사용법

### 기본 사용법

```bash
# 환경 활성화
conda activate Prototyping_UOS

# 실행
bash 균열탐지.sh
```

### 실행 과정

스크립트는 다음 4단계를 자동으로 수행합니다:

1. **STEP 0: GPS 정보 추출**
   - 촬영이미지 폴더의 이미지에서 GPS 좌표와 시간 정보 추출

2. **STEP 1: 이미지 화질 향상**
   - 초해상화 기술로 이미지 해상도를 4배 향상

3. **STEP 2: AI 균열 탐지**
   - 고해상도 이미지에서 균열 자동 탐지 및 정량화

4. **STEP 3: 지도 생성**
   - GPS 좌표와 균열 정보를 결합하여 인터랙티브 지도 생성

## 입력 요구사항

- 입력 이미지는 `촬영이미지` 폴더에 배치
- 이미지는 GPS EXIF 데이터 포함 필요 (스마트폰 위치 서비스 활성화)
- 지원 형식: JPG, JPEG, PNG

## 출력 파일

### 균열탐지_지도_결과.html (최상위 폴더)
- 모든 균열 위치가 표시된 인터랙티브 지도
- 빨간색 선: 이동 경로 (시간 순서)
- 화살표: 이동 방향
- 파란색 점: 모든 촬영 위치
- 빨간색 마커: 균열 발견 위치 (클릭 시 이미지 표시)

### 균열탐지_결과 폴더
- `균열목록.xlsx`: 균열 위치 목록 (위도, 경도, 이미지 경로)
- `균열이미지/`: 균열이 빨간색으로 표시된 이미지들
- `이미지정보.json`: 모든 이미지의 GPS 메타데이터
- `개별위치_지도.html`: 첫 번째 균열 위치의 상세 지도

## 주요 의존성

- **PyTorch 2.0.1** (CUDA 11.8)
- **MMagic 1.0.1**: 초해상화 모델
- **MMSegmentation 1.0.0**: 균열 탐지 모델
- **MMCV 2.0.1**: 컴퓨터 비전 유틸리티
- **OpenCV**: 이미지 처리
- **Folium**: 지도 시각화
- **Pandas**: 데이터 처리

## 파이프라인 설명

### 1. GPS 메타데이터 추출
- 원본 이미지에서 EXIF 데이터 읽기
- GPS 좌표(위도/경도)와 촬영 시간 추출
- 시간 순서로 정렬하여 이동 경로 추적

### 2. 초해상화 (Super Resolution)
- EDSR (Enhanced Deep Super-Resolution) 모델 사용
- 이미지 해상도를 4배 향상 (예: 1024x1024 → 4096x4096)
- 더 정확한 균열 탐지를 위한 전처리

### 3. 균열 탐지 (Crack Detection)
- ConvNeXt-Tiny FPN 기반 Semantic Segmentation
- Sliding window 방식으로 대용량 이미지 처리
- 균열 폭과 길이 자동 정량화
- GPS 좌표와 매칭

### 4. 지도 생성
- Folium 라이브러리로 인터랙티브 지도 생성
- 위성 이미지 베이스맵 사용
- 경로 추적 및 균열 위치 시각화

## 설정 변경

### 탐지 민감도 조절

`inferences/config.py` 파일을 열어서 다음 값을 조절:

```python
# 슬라이딩 윈도우 크기
WINDOW_SIZE = 1024

# 윈도우 겹침 비율 (0.0 ~ 1.0)
OVERLAP_RATIO = 0.1

# 신뢰도 임계값 (0.0 ~ 1.0)
# 높을수록 확실한 균열만 탐지
SCORE_THRESHOLD = 0.8

# 최소 균열 크기 필터링 (픽셀 단위)
# 작은 균열도 탐지하려면 0으로 설정
MIN_CRACK_AREA = 100
MIN_CRACK_WIDTH = 0
MIN_CRACK_LENGTH = 0

# 시각화 설정
VISUALIZATION_ALPHA = 0.6  # 균열 오버레이 투명도
CRACK_COLOR = [0, 0, 255]  # BGR 형식 (빨간색)
```

## 문제 해결

### CUDA Out of Memory 오류
```bash
# inferences/config.py에서 WINDOW_SIZE를 축소
WINDOW_SIZE = 512  # 기본값 1024에서 512로 감소
```

### ImportError: No module named 'mmagic'
```bash
# 환경이 제대로 활성화되었는지 확인
conda activate Prototyping_UOS

# 패키지 재설치
pip install mmagic==1.0.1
```

### GPS 정보 없음 오류
- 이미지에 GPS 정보가 포함되어 있는지 확인
- 스마트폰으로 촬영할 때 위치 서비스를 활성화해야 함
- 확인 명령: `exiftool 이미지.jpg | grep GPS`

### 모델 파일을 찾을 수 없음
- `모델/초해상화/` 폴더에 config와 weight 파일이 있는지 확인
- `모델/균열탐지/` 폴더에 config와 weight 파일이 있는지 확인
- 파일 권한 확인: `ls -lh 모델/*/`

## 성능 최적화 팁

1. **GPU 메모리 관리**
   - 배치 처리 후 자동으로 `torch.cuda.empty_cache()` 호출 (이미 구현됨)
   
2. **처리 속도 개선**
   - Sliding window 크기 조정 (기본값: 1024x1024)
   - Overlap ratio 조정 (기본값: 0.1)
   - 더 작은 이미지로 테스트 후 전체 실행

3. **대용량 이미지 처리**
   - 이미지 크기 제한 자동 해제 (이미 구현됨)
   - 필요시 이미지를 분할하여 처리

## 기술 상세

### 초해상화 모델
- **모델**: EDSR (Enhanced Deep Residual Networks)
- **업스케일**: 4배 (x4)
- **입력**: RGB 이미지
- **출력**: 고해상도 RGB 이미지

### 균열 탐지 모델
- **백본**: ConvNeXt-Tiny
- **헤드**: FPN (Feature Pyramid Network)
- **학습 데이터**: Hard Negative Samples 포함
- **출력**: Binary mask (0: 배경, 1: 균열)

### 정량화 알고리즘
- **폭 계산**: Medial axis를 이용한 거리 맵 생성
- **길이 계산**: Skeleton 픽셀 개수
- **균열 연결**: 인접한 균열 자동 병합

## 라이선스 및 참고

.

### 사용 프레임워크
- MMagic (OpenMMLab)
- MMSegmentation (OpenMMLab)
- MMCV (OpenMMLab)

## 지원

- 간단한 사용법: `사용방법.txt` 참조
- 빠른 시작: `QUICKSTART.md` 참조
- 기술 문의: 이 문서의 "문제 해결" 섹션 참조
