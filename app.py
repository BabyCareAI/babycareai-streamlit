import streamlit as st
import os
from PIL import Image
import io
from services.api_service import APIService
import time
import mimetypes

# 페이지 설정
st.set_page_config(
    page_title="아기 피부 진단",
    page_icon="👶",
    layout="wide"
)

# API 서비스 초기화
api_service = APIService()

# 세션 상태 초기화
if 'diagnosis_id' not in st.session_state:
    st.session_state.diagnosis_id = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'diagnosis_complete' not in st.session_state:
    st.session_state.diagnosis_complete = False
if 'selected_body_part' not in st.session_state:
    st.session_state.selected_body_part = None
if 'symptoms_submitted' not in st.session_state:
    st.session_state.symptoms_submitted = False

def reset_session():
    """세션 상태 초기화"""
    st.session_state.diagnosis_id = None
    st.session_state.current_step = 1
    st.session_state.diagnosis_complete = False
    st.session_state.selected_body_part = None
    st.session_state.symptoms_submitted = False

def process_image_upload():
    """이미지 업로드 및 처리"""
    try:
        uploaded_file = st.file_uploader("피부 사진을 업로드해주세요", type=['jpg', 'jpeg', 'png'])
        
        # 부위 카테고리별 그룹화
        body_part_categories = {
            "얼굴 부위": [
                ("얼굴", "FACE"),
                ("뺨", "CHEEKS"),
                ("이마", "FOREHEAD"),
                ("턱", "CHIN"),
                ("눈", "EYES"),
                ("눈꺼풀", "EYELIDS"),
                ("코", "NOSE"),
                ("입", "MOUTH"),
                ("입술", "LIPS"),
                ("귀", "EAR"),
                ("헤어라인", "HAIRLINE"),
                ("입안", "INSIDE_THE_MOUTH"),
                ("입천장", "ROOF_OF_THE_MOUTH"),
                ("잇몸", "GUMS"),
                ("혀", "TONGUE")
            ],
            "상체 부위": [
                ("목", "NECK"),
                ("목구멍", "THROAT"),
                ("가슴", "CHEST"),
                ("배", "TUMMY"),
                ("몸통", "TORSO"),
                ("등", "BACK"),
                ("겨드랑이", "ARMPITS"),
                ("팔", "ARMS"),
                ("팔꿈치", "ELBOWS"),
                ("손", "HANDS"),
                ("손바닥", "PALMS"),
                ("손목", "WRISTS")
            ],
            "하체 부위": [
                ("다리", "LEGS"),
                ("무릎", "KNEES"),
                ("무릎뼈", "KNEECAPS"),
                ("오금", "BACKS_OF_KNEES"),
                ("허벅지", "THIGHS"),
                ("허벅지 안쪽", "INNER_THIGHS"),
                ("발", "FEET"),
                ("발바닥", "SOLES"),
                ("발가락", "TOES"),
                ("발가락 사이", "BETWEEN_TOES")
            ],
            "기타 부위": [
                ("두피", "SCALP"),
                ("머리", "HEAD"),
                ("엉덩이", "BOTTOM"),
                ("기저귀 부위", "NAPPY_AREA"),
                ("생식기", "GENITALS"),
                ("피부 주름", "SKIN_FOLDS"),
                ("물린 부위 주변 피부", "SKIN_AROUND_THE_BITE"),
                ("전신", "WHOLE_BODY")
            ]
        }

        # 부위 선택 UI
        st.subheader("피부 부위 선택")
        
        # 탭 생성
        tabs = st.tabs(list(body_part_categories.keys()))
        
        # 각 탭에 해당하는 부위 표시
        for tab, (category, parts) in zip(tabs, body_part_categories.items()):
            with tab:
                cols = st.columns(4)  # 4열로 구성
                for i, (name, enum) in enumerate(parts):
                    with cols[i % 4]:
                        if st.button(name, key=f"body_part_{enum}"):
                            st.session_state.selected_body_part = enum
                            st.experimental_rerun()
        
        # 선택된 부위 표시
        if st.session_state.selected_body_part:
            st.success(f"선택된 부위: {next((name for name, enum in sum(body_part_categories.values(), []) if enum == st.session_state.selected_body_part), '')}")

        if uploaded_file and st.session_state.selected_body_part:
            if st.button("진단 시작"):
                # 이미지 파일 확장자 확인
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                if file_extension not in ['.jpg', '.jpeg', '.png']:
                    st.error("지원하지 않는 파일 형식입니다. JPG 또는 PNG 파일만 업로드 가능합니다.")
                    return
                
                # 이미지 업로드
                with st.spinner("피부 사진 업로드 중..."):
                    image_bytes = uploaded_file.getvalue()
                    response = api_service.upload_image(image_bytes, st.session_state.selected_body_part)
                    st.session_state.diagnosis_id = response.get('diagnosisId')
                
                # 이미지 검증
                with st.spinner("피부 사진 검증 중..."):
                    validation = api_service.validate_image(st.session_state.diagnosis_id)
                    if not validation.get('is_skin_related'):
                        st.error("피부 관련 이미지가 아닙니다. 다른 이미지를 업로드해주세요.")
                        return
                
                # 이미지 분류 및 상태 설명
                with st.spinner("피부 상태 확인 중..."):
                    classification = api_service.classify_image(st.session_state.diagnosis_id)
                    description = api_service.get_image_description(st.session_state.diagnosis_id)
                
                st.session_state.current_step = 2
                st.experimental_rerun()
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")

def process_symptoms():
    """증상 입력 처리"""
    try:
        if not st.session_state.symptoms_submitted:
            st.subheader("추가 증상 입력")
            
            # 증상 카테고리별 그룹화
            symptom_categories = {
                "피부 관련": [
                    ("발진", "RASH"),
                    ("붉은 발진", "RED_RASH"),
                    ("가려운 발진", "ITCHY_RASH"),
                    ("여드름성 발진", "PIMPLY_RASH"),
                    ("고리 모양 발진", "RING_SHAPED_RASH"),
                    ("번지는 발진", "SPREADING_RASH"),
                    ("얼룩덜룩한 발진", "BLOTCHY_RASH"),
                    ("붉은 반점", "RED_SPOTS"),
                    ("붉은 덩어리", "RED_BUMPS"),
                    ("가려운 덩어리", "ITCHY_BUMPS"),
                    ("솟아오른 덩어리", "RAISED_BUMPS"),
                    ("작은 솟아오른 반점", "TINY_RAISED_SPOTS"),
                    ("붉은 피부", "RED_SKIN"),
                    ("붉어짐", "REDNESS"),
                    ("가려운 피부", "ITCHY_SKIN"),
                    ("건조한 피부", "DRY_SKIN"),
                    ("비늘 모양 피부", "SCALY_SKIN"),
                    ("껍질이 벗겨지는 피부", "FLAKY_SKIN"),
                    ("피부 벗겨짐", "PEELING_SKIN"),
                    ("갈라진 피부", "CRACKED_SKIN"),
                    ("물집", "BLISTERS"),
                    ("수포", "FLUID_FILLED_BLISTERS"),
                    ("통증성 물집", "PAINFUL_BLISTERS"),
                    ("고름 찬 반점", "PUS_FILLED_SPOTS"),
                    ("작은 물집 같은 염증", "SMALL_BLISTER_LIKE_SORES"),
                    ("작은 황백색 농포", "SMALL_YELLOW_WHITE_PUSTULES"),
                    ("여드름", "PIMPLES"),
                    ("좁쌀 여드름", "WHITEHEADS"),
                    ("하얀 반점", "WHITE_PATCHES"),
                    ("비늘 모양 반점", "SCALY_PATCHES"),
                    ("솟아오른 반점", "RAISED_PATCHES"),
                    ("염증", "SORES"),
                    ("굴 같은 자국", "BURROWS"),
                    ("통증 없는 혹", "PAINLESS_BUMP"),
                    ("악화 (습진)", "FLARE_UPS_ECZEMA"),
                    ("만졌을 때 따뜻함", "WARM_TO_TOUCH"),
                    ("부기", "SWELLING"),
                    ("출혈", "BLEEDING")
                ],
                "눈 관련": [
                    ("눈 분비물", "DISCHARGE_FROM_EYES"),
                    ("눈 건조", "DRYNESS_EYES"),
                    ("눈 자극", "EYE_IRRITATION"),
                    ("눈의 이물감", "GRITTINESS_EYES"),
                    ("가려운 눈", "ITCHY_EYES"),
                    ("부은 눈", "PUFFY_EYES"),
                    ("눈의 통증", "SORE_EYES"),
                    ("붉은 눈", "RED_EYES"),
                    ("눈물", "WATERY_EYES"),
                    ("결막염", "PINK_EYE"),
                    ("딱딱한 속눈썹", "CRUSTY_EYELASHES"),
                    ("끈적거리는 눈꺼풀", "STICKY_EYELIDS")
                ],
                "일반 증상": [
                    ("열", "FEVER"),
                    ("갑작스러운 발열", "SUDDEN_FEVER"),
                    ("기침", "COUGH"),
                    ("콧물", "RUNNY_NOSE"),
                    ("재채기", "SNEEZING"),
                    ("목의 통증", "SORE_THROAT"),
                    ("귀앓이", "EARACHE"),
                    ("귀 잡아당김", "TUGGING_AT_EAR"),
                    ("입의 통증", "SORE_MOUTH"),
                    ("구취", "BAD_BREATH"),
                    ("혀의 백태", "WHITE_COATING_ON_TONGUE"),
                    ("부은 잇몸", "SWOLLEN_GUMS"),
                    ("부은 샘", "SWOLLEN_GLANDS"),
                    ("부은 림프샘", "SWOLLEN_LYMPH_GLANDS"),
                    ("부은 목 샘", "SWOLLEN_NECK_GLANDS"),
                    ("식욕 부진", "LOSS_OF_APPETITE"),
                    ("수유 거부", "RELUCTANCE_TO_FEED"),
                    ("설사", "DIARRHOEA"),
                    ("경미한 설사", "MILD_DIARRHOEA"),
                    ("메스꺼움", "NAUSEA"),
                    ("두통", "HEADACHE"),
                    ("근육통", "MUSCLE_ACHES"),
                    ("쑤시고 아픔", "ACHES_AND_PAINS"),
                    ("통증", "PAIN"),
                    ("쓰림", "SORENESS"),
                    ("불쾌감", "DISCOMFORT"),
                    ("피로", "TIREDNESS"),
                    ("평소와 다른 피로", "UNUSUAL_TIREDNESS"),
                    ("무기력함", "LETHARGIC"),
                    ("과민성", "IRRITABILITY"),
                    ("짜증", "ANNOYANCE"),
                    ("칭얼거림", "GRIZZLY"),
                    ("침 흘림", "DROOLING"),
                    ("청각 곤란", "DIFFICULTY_HEARING"),
                    ("삼킴 곤란", "DIFFICULTY_SWALLOWING"),
                    ("독감 유사 증상", "FLU_LIKE_SYMPTOMS"),
                    ("황달", "JAUNDICE"),
                    ("알레르기 반응", "ALLERGIC_REACTIONS"),
                    ("탈모 (두피)", "HAIR_LOSS_SCALP"),
                    ("기저귀 갈 때 울음", "CRYING_DURING_NAPPY_CHANGES")
                ]
            }
            
            # 탭 생성
            symptom_tabs = st.tabs(list(symptom_categories.keys()))
            
            selected_symptoms = []
            
            # 각 탭에 해당하는 증상 표시
            for tab, (category, symptoms) in zip(symptom_tabs, symptom_categories.items()):
                with tab:
                    cols = st.columns(4)  # 4열로 구성
                    for i, (symptom_name, symptom_enum) in enumerate(symptoms):
                        with cols[i % 4]:
                            if st.checkbox(symptom_name, key=f"symptom_{symptom_enum}"):
                                selected_symptoms.append(symptom_enum)

            other_symptoms = st.text_area("기타 특이사항이 있다면 입력해주세요")

            # 증상 제출 버튼을 위한 컨테이너 생성
            submit_button_container = st.empty()
            
            # 증상 제출 버튼 표시
            if submit_button_container.button("증상 제출"):
                if not selected_symptoms:
                    st.error("최소 1개 이상의 증상을 선택해주세요.")
                    return


                # 증상 제출 처리
                try:                   
                    # 로딩 메시지를 위한 컨테이너 생성
                    loading_container = st.empty()
                    # 버튼 컨테이너를 비워서 버튼 제거
                    submit_button_container.empty()
                    # 증상 처리 중 메시지 표시
                    with loading_container:
                        with st.spinner("증상을 처리하고 있습니다..."):
                            # 추가 증상 제출
                            api_service.submit_symptoms(st.session_state.diagnosis_id, selected_symptoms)
                            
                            # 기타 증상 제출
                            if other_symptoms:
                                api_service.submit_other_symptoms(st.session_state.diagnosis_id, other_symptoms)
                            
                            # 증상 제출이 완료된 후에 상태 업데이트
                            st.session_state.symptoms_submitted = True
                            st.session_state.current_step = 3
                            
                            st.experimental_rerun()
                except Exception as e:
                    st.error(f"증상 제출 중 오류가 발생했습니다: {str(e)}")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")

def show_diagnosis():
    """최종 진단 결과 표시"""
    try:
        # 이전 UI를 완전히 지우기
        for _ in range(10):  # 여러 번 empty()를 호출하여 모든 이전 UI 요소를 지움
            st.empty()
        
        st.subheader("진단 결과")
        
        # 스트리밍 응답을 표시할 빈 컨테이너 생성
        result_container = st.empty()
        full_diagnosis = ""
        
        # 로딩 애니메이션을 위한 컨테이너
        loading_container = st.empty()
        
        # 스트리밍 응답 처리
        with loading_container:
            with st.spinner("최종 진단 중입니다... 🤔"):
                for chunk in api_service.get_final_diagnosis(st.session_state.diagnosis_id):
                    if 'chunk' in chunk:
                        # 첫 번째 청크가 나오면 로딩 애니메이션 제거
                        loading_container.empty()
                        full_diagnosis += chunk['chunk']
                        result_container.write(full_diagnosis)
        
        if st.button("새로운 진단 시작하기"):
            reset_session()
            st.experimental_rerun()
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")

def main():
    st.title("👶 아기 피부 진단")
    
    # 진행 상태 표시
    steps = ["이미지 업로드", "증상 입력", "진단 결과"]
    st.progress((st.session_state.current_step - 1) / (len(steps) - 1))
    st.write(f"현재 단계: {steps[st.session_state.current_step - 1]}")
    
    # 현재 단계에 따른 처리
    if st.session_state.current_step == 1:
        process_image_upload()
    elif st.session_state.current_step == 2:
        process_symptoms()
    elif st.session_state.current_step == 3:
        show_diagnosis()

if __name__ == "__main__":
    main()
