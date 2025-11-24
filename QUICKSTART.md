# 빠른 시작 가이드

## 3분 안에 시작하기

### 0. 환경 설정 (최초 1회만)

```bash
# 프로젝트 폴더로 이동
cd /path/to/Prototyping_UOS

# conda 환경 생성 (5~10분 소요)
conda env create -f environment.yml

# 환경 활성화
conda activate Prototyping_UOS
```

✅ 환경 설정은 처음 한 번만 하면 됩니다!

### 1. 이미지 준비
촬영한 이미지를 `촬영이미지` 폴더에 넣으세요.

### 2. 실행
```bash
conda activate Prototyping_UOS
bash 균열탐지.sh
```

**촬영거리 입력:**
- 실행하면 촬영거리를 입력하라는 프롬프트가 나타납니다
- 예: `1.5` (1.5미터에서 촬영한 경우)
- 이 정보로 픽셀 크기를 실제 크기(mm)로 변환합니다

### 3. 결과 확인
`균열탐지_지도_결과.html` 파일을 열어보세요!
- 균열의 실제 폭과 길이가 mm 단위로 표시됩니다

---

## 상세 사용 방법

### 필수 준비사항

1. **Conda 설치 확인**
   ```bash
   conda --version
   ```
   Conda가 설치되어 있지 않다면:
   - [Miniconda 다운로드](https://docs.conda.io/en/latest/miniconda.html)
   - 또는 [Anaconda 다운로드](https://www.anaconda.com/download)

2. **GPU 확인 (선택사항, 하지만 권장)**
   ```bash
   nvidia-smi
   ```
   GPU가 있으면 10배 이상 빠릅니다!

### 환경 설정 (최초 1회)

#### 방법 1: environment.yml 사용 (권장)

```bash
cd /path/to/Prototyping_UOS
conda env create -f environment.yml
conda activate Prototyping_UOS
```

#### 방법 2: 수동 설치

```bash
# 1. conda 환경 생성
conda create -n Prototyping_UOS python=3.9

# 2. 환경 활성화
conda activate Prototyping_UOS

# 3. PyTorch 설치
conda install pytorch==2.0.1 torchvision pytorch-cuda=11.8 -c pytorch -c nvidia

# 4. 나머지 패키지 설치
pip install -r requirements.txt
```

### 프로그램 실행

```bash
# 1. 환경 활성화 (매번 필요)
conda activate Prototyping_UOS

# 2. 프로그램 실행
bash 균열탐지.sh

# 3. 촬영거리 입력 (프롬프트에서 요청)
# 예: 1.5 (미터 단위로 입력)
```

실행하면 다음 과정이 자동으로 진행됩니다:
- **STEP -1**: 촬영거리 입력 (실제 크기 계산용)
- **STEP 0**: GPS 정보 추출
- **STEP 1**: 이미지 화질 향상 (초해상화)
- **STEP 2**: AI 균열 탐지 + 실제 크기 계산
- **STEP 3**: 지도 생성 (균열 크기 정보 포함)

### 결과 확인하기

#### 1. 지도로 보기
`균열탐지_지도_결과.html` 파일을 더블클릭하세요.

- **빨간색 마커**: 균열 발견 위치
  - 마우스를 올리면 촬영시간, 균열 개수, 최대 폭 표시
  - 클릭하면 상세 정보 팝업 표시
- **빨간색 선**: 이동 경로 (시간 순서)
- **파란색 점**: 모든 촬영 위치

**팝업 정보:**
- 📸 촬영시간 (YYYY-MM-DD HH:MM:SS)
- 📍 위치 (위도, 경도)
- 🔍 균열 통계:
  - 균열 개수
  - 최대 균열 폭/길이 (mm)
  - 평균 균열 폭/길이 (mm)
- 균열 이미지

#### 2. Excel로 보기
`균열탐지_결과/균열목록.xlsx` 파일을 열어보세요.

Excel에 다음 정보가 포함되어 있습니다:
- 위도, 경도
- 이미지 경로
- 📸 촬영시간 (YYYY-MM-DD HH:MM:SS)
- 균열 개수
- 최대 균열 폭(mm), 최대 균열 길이(mm)
- 평균 균열 폭(mm), 평균 균열 길이(mm)

#### 3. 이미지로 보기
`균열탐지_결과/균열이미지/` 폴더에서 균열이 표시된 이미지를 확인하세요.

---

## 모델 파일 정보

모델 파일은 프로젝트에 이미 포함되어 있습니다:

```
모델/
├── 초해상화/
│   ├── 초해상화_config.py      (14 KB)
│   └── 초해상화_weight.pth     (23 MB)
└── 균열탐지/
    ├── 균열탐지_config.py      (113 KB)
    └── 균열탐지_weight.pth     (69 MB)
```

별도로 모델을 다운로드하거나 설정할 필요가 없습니다!

---

## 자주 묻는 질문

### Q: 환경 설정은 언제 해야 하나요?
**A:** 최초 1회만 하면 됩니다. 이후에는 `conda activate Prototyping_UOS`만 실행하면 됩니다.

### Q: 실행이 너무 오래 걸려요
**A:** 
- 이미지 개수와 크기에 따라 시간이 달라집니다
- GPU를 사용하면 훨씬 빠릅니다 (CPU 대비 10배 이상)
- 처음 테스트할 때는 이미지 몇 장으로 시작하세요

### Q: "conda: command not found" 오류가 나요
**A:** Conda가 설치되어 있지 않습니다. [Miniconda](https://docs.conda.io/en/latest/miniconda.html)를 설치하세요.

### Q: "GPS 정보 없음" 오류가 나요
**A:** 이미지에 GPS 정보가 포함되어야 합니다. 스마트폰으로 촬영할 때 위치 서비스를 켜세요.

### Q: "CUDA out of memory" 오류가 나요
**A:** GPU 메모리가 부족합니다. `inferences/config.py` 파일에서 `WINDOW_SIZE`를 512로 줄이세요.

### Q: GPU가 없어도 되나요?
**A:** 네, CPU로도 실행 가능합니다. 다만 처리 시간이 훨씬 오래 걸립니다.

### Q: 촬영거리를 정확히 모르는데 어떻게 하나요?
**A:** 
- 가능한 한 정확히 측정하는 것이 좋습니다 (줄자 사용)
- 대략적인 거리라도 입력하면 상대적 비교는 가능합니다
- 이후 실제 균열을 측정하여 보정 계수를 적용할 수 있습니다

### Q: 균열 크기가 정확한가요?
**A:** 정확도는 다음에 영향을 받습니다:
- 촬영거리 측정 정확도
- 카메라 스펙 입력 정확도
- 촬영 각도 (수직으로 촬영할수록 정확)
- 일반적으로 ±10% 이내 오차

### Q: 카메라 정보를 어디서 찾나요?
**A:** 
- 스마트폰: 제조사 웹사이트 → 스펙 → 카메라
- 예: "iPhone 13 camera specs", "Galaxy S21 sensor size"
- EXIF 데이터: `exiftool 이미지.jpg | grep -i "focal\|sensor"`

---

## 설정 변경

### 카메라 설정 (중요!)

정확한 균열 크기 계산을 위해 카메라 정보를 입력하세요:

`inferences/config.py` 파일을 열어서 다음 값을 수정:

```python
# 카메라 센서 크기 (mm) - 카메라 스펙에 맞게 수정
SENSOR_WIDTH_MM = 6.17    # 스마트폰 카메라 기본값
SENSOR_HEIGHT_MM = 4.56

# 카메라 초점거리 (mm)
FOCAL_LENGTH_MM = 4.25

# 이미지 해상도 (픽셀) - 실제 촬영 이미지 해상도
IMAGE_WIDTH_PX = 4032
IMAGE_HEIGHT_PX = 3024

# 초해상화 스케일
SUPER_RESOLUTION_SCALE = 2.0  # 2배 확대
```

**카메라 정보 확인 방법:**
- 스마트폰: 제조사 웹사이트에서 카메라 스펙 확인
- EXIF에서 확인: `exiftool 이미지.jpg | grep "Focal Length"`

### 탐지 민감도 조절

```python
# 신뢰도 임계값 (0.0 ~ 1.0)
# 낮을수록 더 많은 균열 탐지
SCORE_THRESHOLD = 0.1

# 최소 균열 크기 (픽셀)
MIN_CRACK_AREA = 100
MIN_CRACK_WIDTH = 0
MIN_CRACK_LENGTH = 0

# 슬라이딩 윈도우 크기
# GPU 메모리가 부족하면 1024로 줄이세요
WINDOW_SIZE = 2048
```

---

## 프로젝트 구조

```
Prototyping_UOS/
├── 균열탐지.sh ⭐                # 실행 파일
├── environment.yml              # Conda 환경 설정
├── 모델/                        # AI 모델 (포함됨)
│   ├── 초해상화/
│   └── 균열탐지/
├── 촬영이미지/                  # 입력 이미지 폴더
├── 균열탐지_결과/               # 결과 저장 폴더
└── 균열탐지_지도_결과.html ⭐   # 최종 결과 지도
```

---

## 문제 해결

### 환경 생성 실패

```bash
# 기존 환경 삭제 후 재생성
conda env remove -n Prototyping_UOS
conda env create -f environment.yml
```

### 패키지 설치 오류

```bash
# pip 업그레이드
pip install --upgrade pip

# 개별 패키지 재설치
pip install mmagic==1.0.1
pip install mmsegmentation==1.0.0
```

### 모델 로딩 실패

모델 파일이 제대로 있는지 확인:
```bash
ls -lh 모델/초해상화/
ls -lh 모델/균열탐지/
```

---

## 팁

- **처음 실행**: 이미지 5~10장으로 테스트해보세요
- **지도 파일**: 웹브라우저에서 열립니다 (Chrome, Firefox, Edge 등)
- **결과 백업**: 중요한 결과는 다른 곳에 복사해두세요
- **환경 비활성화**: 작업 완료 후 `conda deactivate` 실행

---

## 다음 단계

1. ✅ 환경 설정 완료
2. ✅ 테스트 이미지로 실행
3. ✅ 결과 확인
4. 📸 실제 촬영 이미지로 대량 처리
5. 📊 결과 분석 및 리포트 작성

더 자세한 내용은 `README.md` 파일을 참조하세요!
