import requests
import json
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
import mimetypes

load_dotenv()

class APIService:
    def __init__(self):
        self.springboot_base_url = os.getenv("SPRINGBOOT_API_URL", "http://localhost:8080")
        self.fastapi_base_url = os.getenv("FASTAPI_API_URL", "http://localhost:8000")

    def upload_image(self, image_file: bytes, body_part: str) -> Dict[str, Any]:
        """이미지 업로드 API 호출"""
        url = f"{self.springboot_base_url}/api/v1/diagnosis/image-upload"
        
        # 파일 확장자에 따른 Content-Type 설정
        content_type = mimetypes.guess_type('image.jpg')[0]  # 기본값으로 image/jpeg 설정
        if isinstance(image_file, bytes):
            if image_file.startswith(b'\xff\xd8'):  # JPEG 시그니처
                content_type = 'image/jpeg'
            elif image_file.startswith(b'\x89PNG'):  # PNG 시그니처
                content_type = 'image/png'
        
        files = {
            'image': ('image.jpg', image_file, content_type)
        }
        data = {"bodyPart": body_part}
        
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()

    def validate_image(self, diagnosis_id: str) -> Dict[str, Any]:
        """이미지 검증 API 호출"""
        url = f"{self.fastapi_base_url}/api/v1/diagnosis/validate"
        data = {"diagnosis_id": diagnosis_id}
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def classify_image(self, diagnosis_id: str) -> Dict[str, Any]:
        """이미지 분류 API 호출"""
        url = f"{self.springboot_base_url}/api/v1/diagnosis/classify"
        data = {"diagnosisId": diagnosis_id}
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_image_description(self, diagnosis_id: str) -> Dict[str, Any]:
        """이미지 상태 설명 API 호출"""
        url = f"{self.fastapi_base_url}/api/v1/diagnosis/image-description"
        data = {"diagnosis_id": diagnosis_id}
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def submit_symptoms(self, diagnosis_id: str, symptoms: list) -> Dict[str, Any]:
        """추가 증상 입력 API 호출"""
        url = f"{self.springboot_base_url}/api/v1/diagnosis/symptom"
        data = {
            "diagnosisId": diagnosis_id,
            "symptoms": symptoms
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        # 빈 응답이 오는 경우 성공으로 처리
        return {"status": "success", "message": "증상이 성공적으로 저장되었습니다."}

    def submit_other_symptoms(self, diagnosis_id: str, other_symptoms: str) -> Dict[str, Any]:
        """기타 증상 입력 API 호출"""
        url = f"{self.fastapi_base_url}/api/v1/diagnosis/other-symptom"
        data = {
            "diagnosis_id": diagnosis_id,
            "other_symptom_text": other_symptoms
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_final_diagnosis(self, diagnosis_id: str) -> Dict[str, Any]:
        """최종 진단 API 호출"""
        url = f"{self.fastapi_base_url}/api/v1/diagnosis/rag"
        data = {"diagnosis_id": diagnosis_id}
        
        # SSE 응답을 처리하기 위한 요청
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()
        
        # SSE 응답 처리
        full_diagnosis = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # 'data: ' 이후의 JSON 파싱
                        if 'chunk' in data:
                            full_diagnosis += data['chunk']
                        elif 'error' in data:
                            raise Exception(data['error'])
                    except json.JSONDecodeError:
                        continue
        
        return {"diagnosis": full_diagnosis} 