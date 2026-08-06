# 필요한 라이브러리 임포트
import streamlit as st
from groq import Groq
from datetime import datetime

# ============================================================================
# 에이전틱 워크플로우 기반 언어 학습 코치 시스템
# 3명의 특화된 언어 학습 코치가 팀을 이루어 사용자를 지원
# ============================================================================

def call_openai(client, prompt):
    """OpenAI ChatGPT API 호출 및 에러 처리"""
    try:
        response = client.chat.completions.create(
            model="llama-3-groq-8b-tool-user",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        text = response.choices[0].message.content
        if not text:
            raise ValueError("AI 모델이 빈 응답을 반환했습니다.")
        return text
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "authentication" in error_msg.lower():
            raise ValueError("API 키가 유효하지 않습니다. OpenAI에서 발급받은 키를 확인해주세요.") from e
        if "429" in error_msg or "quota" in error_msg.lower():
            raise ValueError("API 사용 한도를 초과했습니다. 잠시 후 다시 시도해주세요.") from e
        raise ValueError(f"AI 응답 생성 중 오류가 발생했습니다: {error_msg}") from e


def validate_input(language, input_data):
    """학습자 입력 데이터 검증"""
    errors = []
    if not language or not language.strip():
        errors.append("학습 언어를 선택하거나 입력해주세요.")
    if not input_data.get("learning_goals", "").strip():
        errors.append("학습 목표를 입력해주세요.")
    return errors


class LanguageLearningTeam:
    """AI 기반 언어 학습 코치 팀 관리 클래스"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        # API 키가 있으면 사용, 없으면 환경변수에서 자동으로 가져옴
        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = Groq()  # OPENAI_API_KEY 환경변수 사용
        
        # 3명의 특화된 언어 학습 코치 초기화
        self.assessment_coach = AssessmentCoach(self.client)  # 학습자 평가 및 계획 전문가
        self.language_coach = LanguageCoach(self.client)     # 언어 지식 및 이론 전문가
        self.practice_coach = PracticeCoach(self.client)  # 실전 연습 및 활용 전문가
        
        # 워크플로우 로그 초기화
        self.workflow_logs = []
    
    def get_learning_advice(self, language, input_data):
        """사용자 요청에 따라 3명의 코치가 순차적으로 협업하여 조언 제공"""
        # 워크플로우 기록 시작
        workflow_log = {
            "language": language,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "coaches_involved": ["AssessmentCoach", "LanguageCoach", "PracticeCoach"],
            "steps": []
        }
        
        # 1단계: 학습자 평가 코치의 초기 분석 및 계획
        st.markdown("### 1단계: 학습자 평가 및 학습 계획 수립 중...")
        with st.spinner("학습자 평가 코치가 분석 중입니다..."):
            initial_assessment = self.assessment_coach.analyze(language, input_data)
            workflow_log["steps"].append({"coach": "AssessmentCoach", "action": "initial_assessment"})
        
        # 2단계: 언어 코치의 언어 지식 및 학습 자료 추가
        st.markdown("### 2단계: 언어 지식 및 학습 자료 분석 중...")
        with st.spinner("언어 코치가 언어 지식을 분석 중입니다..."):
            language_knowledge = self.language_coach.enhance(initial_assessment, language, input_data)
            workflow_log["steps"].append({"coach": "LanguageCoach", "action": "language_enhancement"})
        
        # 3단계: 실전 연습 코치의 활용 전략 최적화
        st.markdown("### 3단계: 실전 연습 및 활용 전략 최적화 중...")
        with st.spinner("실전 연습 코치가 최종 조언을 준비 중입니다..."):
            final_advice = self.practice_coach.finalize(language_knowledge, language, input_data)
            workflow_log["steps"].append({"coach": "PracticeCoach", "action": "finalization"})
        
        # 워크플로우 로그 저장
        self.workflow_logs.append(workflow_log)
        
        # 각 코치별 결과를 모두 반환
        return {
            "assessment": initial_assessment,
            "language": language_knowledge,
            "practice": final_advice
        }


class AssessmentCoach:
    """학습자 평가 및 계획 전문 코치"""
    
    def __init__(self, client):
        self.client = client
        self.coach_name = "김준서 평가 코치"
        self.coach_intro = """
        안녕하세요, 김준서 평가 코치입니다. 저는 학습자의 현재 수준을 평가하고 맞춤형 학습 계획을 수립하는 전문가입니다.
        15년간의 언어 교육 및 학습자 평가 경험을 바탕으로 여러분의 언어 학습 여정을 설계해 드리겠습니다.
        """
    
    def analyze(self, language, input_data):
        """사용자 요청에 대한 학습자 평가 및 계획 수립"""
        prompt = f"""
        당신은 '{self.coach_name}'이라는 언어 학습자 평가 전문 코치입니다.
        {self.coach_intro}
        
        다음 정보를 바탕으로 {language} 학습자를 평가하고 학습 계획을 수립해주세요:
        
        현재 수준: {input_data.get('current_level', '')}
        학습 목표: {input_data.get('learning_goals', '')}
        학습 시간: {input_data.get('study_time', '')}
        사전 경험: {input_data.get('prior_experience', '')}
        학습 스타일: {input_data.get('learning_style', '')}
        어려움/도전: {input_data.get('challenges', '')}
        
        다음 항목을 포함하는 학습자 평가 및 계획을 제공해주세요:
        1. 현재 언어 수준 (CEFR 기준 평가 및 설명)
        2. 학습자 강점 및 약점 분석
        3. 학습 목표의 구체화 및 현실적 타임라인
        4. 단계별 학습 계획 및 우선순위
        5. 학습 스타일에 맞는 접근법 제안
        6. 예상 도전 요소 및 극복 전략
        
        분석 결과에 현재 수준 평가, 학습 목표 설정, 맞춤형 학습 계획을 반드시 포함해 주세요.
        전문적이면서도 이해하기 쉬운 언어로 설명해 주세요.
        """
        
        return call_openai(self.client, prompt)


class LanguageCoach:
    """언어 지식 및 이론 전문 코치"""
    
    def __init__(self, client):
        self.client = client
        self.coach_name = "이민지 언어 코치"
        self.coach_intro = """
        안녕하세요, 이민지 언어 코치입니다. 저는 언어 구조, 문법, 어휘, 발음 등 언어 지식과 학습 자료를 전문으로 합니다.
        12년간의 언어학 및 외국어 교육 경험을 통해 여러분께 효과적인 언어 지식과 자료를 제공하겠습니다.
        """
    
    def enhance(self, previous_assessment, language, input_data):
        """평가 코치의 분석을 바탕으로 언어 지식 및 학습 자료 제공"""
        prompt = f"""
        당신은 '{self.coach_name}'이라는 언어 지식 전문 코치입니다.
        {self.coach_intro}
        
        학습자 평가 코치가 제공한 다음 분석을 검토하고, 언어 지식 관점에서 보완해주세요:
        
        === 학습자 평가 코치의 분석 ===
        {previous_assessment}
        === 분석 끝 ===
        
        {language} 학습을 위한 언어 지식과 학습 자료를 제공해주세요:
        
        1. 핵심 언어 구조
           - {language}의 기본 구조적 특징
           - 모국어와의 주요 차이점
           - 학습자 수준에 맞는 문법 체계 설명
        
        2. 필수 어휘 및 표현
           - 학습 단계별 우선 습득 어휘 영역
           - 일상 회화에 필수적인 표현
           - 어휘 학습 전략 및 방법론
        
        3. 발음 및 억양 가이드
           - 핵심 발음 규칙 및 패턴
           - 어려운 발음 요소 및 연습법
           - 자연스러운 억양 개발 방법
        
        4. 맞춤형 학습 자료 추천
           - 학습 수준에 적합한 교재/온라인 자료
           - 언어 능력별 추천 미디어 (영화, 음악, 팟캐스트 등)
           - 자기주도 학습을 위한 디지털 리소스
           
        현재 수준: {input_data.get('current_level', '')}
        학습 목표: {input_data.get('learning_goals', '')}
        학습 스타일: {input_data.get('learning_style', '')}
        관심사: {input_data.get('interests', '')}
        
        언어 구조 설명, 핵심 문법 개념, 필수 어휘 영역, 발음 가이드, 추천 학습 자료를 반드시 포함해 주세요.
        """
        
        return call_openai(self.client, prompt)


class PracticeCoach:
    """실전 연습 및 활용 전문 코치"""
    
    def __init__(self, client):
        self.client = client
        self.coach_name = "박도윤 실전 코치"
        self.coach_intro = """
        안녕하세요, 박도윤 실전 코치입니다. 저는 언어의 실제 활용 방법, 효과적인 연습 전략, 문화적 맥락을 전문으로 합니다.
        10년간의 언어 코칭 및 문화 간 소통 경험을 통해 여러분의 언어 능력이 실생활에서 빛날 수 있도록 지원하겠습니다.
        """
    
    def finalize(self, previous_language, language, input_data):
        """평가 코치와 언어 코치의 분석을 바탕으로 최종 실전 연습 전략 제공"""
        prompt = f"""
        당신은 '{self.coach_name}'이라는 실전 연습 전문 코치입니다.
        {self.coach_intro}
        
        학습자 평가 코치와 언어 코치가 제공한, 다음 분석을 검토하고 최종적으로 완성해주세요:
        
        === 이전 코치들의 분석 ===
        {previous_language}
        === 분석 끝 ===
        
        {language} 학습을 위한 실전 연습 및 활용 전략을 제안해주세요:
        
        1. 일상 활용 연습법
           - 혼자서 할 수 있는 연습 활동
           - 현지인과의 대화 기회 찾기/활용법
           - 일상 루틴에 언어 학습 통합하기
        
        2. 효과적인 능력별 연습 전략
           - 듣기 능력 향상을 위한 연습
           - 말하기 유창성 개발 방법
           - 읽기/쓰기 실력 강화 활동
        
        3. 문화적 맥락과 실용적 표현
           - 언어와 문화의 연결 이해하기
           - 실생활 상황별 유용한 표현
           - 문화적 뉘앙스와 적절한 언어 사용
        
        4. 지속적 향상 및 동기 유지 전략
           - 장기적 학습 동기 유지 방법
           - 진척도 측정 및 자가 평가 도구
           - 언어 학습 공동체 참여 방안
           
        현재 수준: {input_data.get('current_level', '')}
        학습 목표: {input_data.get('learning_goals', '')}
        관심사: {input_data.get('interests', '')}
        학습 환경: {input_data.get('learning_environment', '')}
        실생활 활용 상황: {input_data.get('usage_scenarios', '')}
        
        최종 조언에는 다음 세 코치의 관점이 균형있게 통합되어야 합니다:
        1. 학습자 평가 코치 (수준 평가 및 학습 계획)
        2. 언어 코치 (언어 지식 및 학습 자료)
        3. 실전 연습 코치 (실제 활용 및 연습 전략)
        
        실용적이고 효과적인 연습 전략, 문화적 맥락, 지속적 향상 방법을 포함한 종합적인 가이드를 제공해주세요.
        """
        
        return call_openai(self.client, prompt)


# ============================================================================
# Streamlit 웹 애플리케이션 구현
# ============================================================================

def main():
    """Streamlit 웹 애플리케이션의 메인 로직"""
    # 페이지 기본 설정
    st.set_page_config(
        page_title="AI 언어 학습 코치 팀",
        page_icon="🗣️🌏📚",
        layout="wide"
    )
    
    # 페이지 제목 및 설명
    st.title("🗣️🌏📚 AI 언어 학습 코치 팀")
    st.markdown("""
    ### 3명의 전문 코치가 협업하여 맞춤형 언어 학습 가이드를 제공합니다
    
    * **김준서 평가 코치**: 학습자 수준 평가와 맞춤형 학습 계획 수립
    * **이민지 언어 코치**: 언어 지식과 효과적인 학습 자료 제공
    * **박도윤 실전 코치**: 실제 활용 방법과 효과적인 연습 전략 제안
    """)
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("🔑 API 설정")
        # API 키 입력 필드 (선택사항)
        api_key = st.text_input("OpenAI API 키 (선택사항)", type="password",
                                help="입력하지 않으면 환경변수 OPENAI_API_KEY를 사용합니다.")
        
        if not api_key:
            st.info("API 키를 입력하지 않으면 환경변수 OPENAI_API_KEY를 자동으로 사용합니다.")
            
        st.markdown("---")
        
        # 코치 소개
        st.markdown("### 🧠 코치 소개")
        
        coach_tab = st.selectbox("코치 정보 보기", 
                                ["김준서 평가 코치", "이민지 언어 코치", "박도윤 실전 코치"])
        
        if coach_tab == "김준서 평가 코치":
            st.markdown("""
            **김준서 평가 코치**
            
            학습자 평가 전문가로 15년간 언어 교육 및 학습자 평가 분야에서 활동했습니다.
            과학적인 평가 방법과 개인 맞춤형 학습 계획으로 여러분의 언어 학습 여정을 설계합니다.
            
            * 전문 분야: 언어 능력 평가, 학습 계획 설계, 목표 설정, 학습 흐름 최적화
            * 경력: 어학원 평가 책임자, 대학 언어 교육 센터, 온라인 학습 플랫폼 교육 디렉터
            """)
        
        elif coach_tab == "이민지 언어 코치":
            st.markdown("""
            **이민지 언어 코치**
            
            언어 지식 전문가로 12년간 언어학 및 외국어 교육 분야에서 활동했습니다.
            체계적인 언어 지식과 최적화된 학습 자료로 효율적인 언어 습득을 지원합니다.
            
            * 전문 분야: 언어 구조, 문법 체계, 어휘 확장, 발음 교정, 학습 자료 큐레이션
            * 경력: 언어학 교수, 교재 개발자, 다국어 구사자, 언어 교육 컨설턴트
            """)
        
        elif coach_tab == "박도윤 실전 코치":
            st.markdown("""
            **박도윤 실전 코치**
            
            실전 연습 전문가로 10년간 언어 코칭 및 문화 간 소통 분야에서 활동했습니다.
            실용적인 활용 전략과 문화적 맥락을 통해 언어를 생활 속에서 자연스럽게 구사할 수 있도록 돕습니다.
            
            * 전문 분야: 대화 기술, 실전 활용 전략, 문화적 감각, 의사소통 효율성, 지속적 동기 부여
            * 경력: 언어 교환 프로그램 운영자, 해외 주재원 코치, 문화 간 소통 전문가, 다국어 가이드
            """)
    
    # 언어 선택 드롭다운
    language = st.selectbox(
        "학습하고자 하는 언어를 선택하세요",
        ["영어", "일본어", "중국어", "스페인어", "프랑스어", "독일어", "이탈리아어", "러시아어", "한국어", "아랍어", "포르투갈어", "기타"]
    )
    
    # 기타 언어 선택 시 직접 입력
    if language == "기타":
        language = st.text_input("학습하고자 하는 언어를 입력하세요")
    
    # 카드 스타일 CSS 수정
    st.markdown("""
    <style>
    /* 기본 Streamlit 테마 유지를 위한 설정 */
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }

    /* 답변 카드 스타일 */
    .coach-card {
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        color: #000000;  /* 카드 내부 글자색을 검정색으로 설정 */
        background-color: #FFFFFF;  /* 카드 배경색을 흰색으로 설정 */
    }

    .assessment-coach {
        border-left: 5px solid #0077B6;
    }

    .language-coach {
        border-left: 5px solid #2D6A4F;
    }

    .practice-coach {
        border-left: 5px solid #D4A017;
    }

    /* 답변 카드 내부 텍스트 스타일 */
    .coach-card p, .coach-card li, .coach-card div {
        color: #000000 !important;
    }

    /* 나머지 UI 요소들은 기본 다크 테마 유지 */
    .stMarkdown:not(.coach-card), .stText:not(.coach-card) {
        color: #FAFAFA !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 워크플로우 설명
    with st.expander("에이전틱 워크플로우 프로세스 보기"):
        st.markdown("""
        ### 에이전틱 워크플로우 프로세스
        
        1. **요청 분석**: 사용자의 언어 학습 요청을 분석하여 필요한 전문성 식별
        2. **팀 구성**: 각 요청에 최적화된 AI 언어 코치 팀 구성
        3. **학습자 평가**: 학습자 평가 코치가 현재 수준과 학습 계획을 종합적으로 분석
        4. **언어 지식**: 언어 코치가 맞춤형 언어 지식과 학습 자료 제시
        5. **실전 전략**: 실전 연습 코치가 효과적인 활용 방법과 연습 전략 제안
        6. **통합 가이드**: 세 코치의 관점을 통합한 최종 맞춤형 언어 학습 가이드 제공
        """)
    
    # 학습자 정보 입력 필드
    st.subheader(f"🌟 {language} 학습 정보 입력")
    
    # 두 개의 컬럼으로 분할
    col1, col2 = st.columns(2)
    
    with col1:
        current_level = st.selectbox(
            "현재 언어 수준",
            ["완전 초보 (아는 단어 없음)", "입문 (몇 가지 기본 표현)", "초급 (간단한 대화 가능)", 
             "중급 (일상 대화 가능)", "중상급 (유창하지만 제한적)", "고급 (거의 유창함)"]
        )
        
        learning_goals = st.text_area(
            "학습 목표 (구체적으로 적어주세요)",
            placeholder="예: 여행시 기본 대화 가능, 비즈니스 미팅 진행, 원어민과 유창한 대화, 영화 자막 없이 이해하기 등"
        )
        
        learning_style = st.multiselect(
            "선호하는 학습 스타일 (여러 개 선택 가능)",
            ["읽기/쓰기 중심", "듣기/말하기 중심", "문법 체계적 학습", "대화 중심 실용적 학습", 
             "앱/게임 활용 학습", "미디어(영화/음악) 활용", "몰입형 학습", "정기적 반복 학습"]
        )
    
    with col2:
        study_time = st.selectbox(
            "주당 학습 가능 시간",
            ["1-3시간", "4-6시간", "7-10시간", "11-15시간", "16시간 이상"]
        )
        
        prior_experience = st.text_area(
            "이전 언어 학습 경험",
            placeholder="예: 고등학교 2년 동안 배움, 독학 6개월, 온라인 강의 수강, 비슷한 언어 구사 경험 등"
        )
        
        interests = st.text_area(
            "관심사 (언어 학습에 활용할 주제)",
            placeholder="예: 여행, 요리, 영화, 비즈니스, 문학, 음악, 스포츠 등"
        )
    
    learning_environment = st.selectbox(
        "주요 학습 환경",
        ["혼자서 독학", "온라인 강의/앱 활용", "학원/과외 수업", "언어 교환/대화 파트너", "현지 국가 거주", "혼합형"]
    )
    
    usage_scenarios = st.text_area(
        "주요 활용 상황",
        placeholder="예: 여행, 직장/비즈니스, 학업, 취미, 이민/장기 거주, 국제 연애/결혼 등"
    )
    
    challenges = st.text_area(
        "겪고 있는 어려움 또는 도전 (선택사항)",
        placeholder="예: 발음이 어려움, 문법 이해가 안됨, 말하기가 두려움, 어휘 암기가 안됨, 학습 지속이 어려움 등"
    )
    
    # 학습 계획 생성 버튼
    if st.button("학습 계획 생성"):
        input_data = {
            "current_level": current_level,
            "learning_goals": learning_goals,
            "study_time": study_time,
            "prior_experience": prior_experience,
            "learning_style": ", ".join(learning_style) if learning_style else "",
            "challenges": challenges,
            "interests": interests,
            "learning_environment": learning_environment,
            "usage_scenarios": usage_scenarios
        }

        validation_errors = validate_input(language, input_data)
        if validation_errors:
            for error in validation_errors:
                st.warning(error)
        else:
            try:
                learning_team = LanguageLearningTeam(api_key if api_key else None)
                result = learning_team.get_learning_advice(language, input_data)

                st.session_state["last_result"] = result
                st.session_state["workflow_logs"] = learning_team.workflow_logs
            except ValueError as e:
                st.error(str(e))

    # 결과 표시 (세션 상태에 저장된 경우)
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        st.markdown("### 📊 언어 학습 코치 팀 분석 결과")
        st.markdown(f"""<div class="coach-card assessment-coach"><b>김준서 평가 코치</b><br><br>{result['assessment']}</div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="coach-card language-coach"><b>이민지 언어 코치</b><br><br>{result['language']}</div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="coach-card practice-coach"><b>박도윤 실전 코치 (최종 통합 조언)</b><br><br>{result['practice']}</div>""", unsafe_allow_html=True)

    # 워크플로우 로그 표시
    if "workflow_logs" in st.session_state and st.session_state["workflow_logs"]:
        with st.expander("📋 워크플로우 로그 보기"):
            for log in st.session_state["workflow_logs"]:
                st.markdown(f"**{log['timestamp']}** | 언어: {log['language']}")
                for step in log["steps"]:
                    st.markdown(f"- {step['coach']}: {step['action']}")
                st.markdown("---")

# 스크립트가 직접 실행될 때만 main() 함수 실행
if __name__ == "__main__":
    main()
