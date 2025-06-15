# 아기 피부 진단 애플리케이션

이 프로젝트는 아기의 피부 상태를 진단하는 Streamlit 기반의 웹 애플리케이션입니다.

## 설치 방법

1. Python 3.8 이상이 설치되어 있어야 합니다.
2. 가상환경을 생성하고 활성화합니다:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 또는
   .\venv\Scripts\activate  # Windows
   ```
3. 필요한 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

## 환경 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가합니다:

```
SPRINGBOOT_API_URL=http://localhost:8080
FASTAPI_API_URL=http://localhost:8000
```

## 실행 방법

1. SpringBoot 백엔드 서버가 실행 중인지 확인합니다.
2. FastAPI 백엔드 서버가 실행 중인지 확인합니다.
3. Streamlit 애플리케이션을 실행합니다:
   ```bash
   streamlit run app.py
   ```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:8501`로 접속합니다.
2. 피부 사진을 업로드하고 피부 부위를 선택합니다.
3. 추가 증상을 입력합니다.
4. 진단 결과를 확인합니다.

## 프로젝트 구조

```
babycareai-streamlit/
├── app.py                # 메인 Streamlit 애플리케이션
├── services/            # API 서비스 모듈
│   └── api_service.py   # API 통신 서비스
├── requirements.txt     # Python 패키지 의존성
└── README.md           # 프로젝트 문서
``` 