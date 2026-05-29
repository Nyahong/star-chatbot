import streamlit as st
from openai import OpenAI
from datetime import datetime
import pytz
import io
from audio_recorder_streamlit import audio_recorder

# =============================================
# 🎨 페이지 설정
# =============================================
st.set_page_config(
    page_title="별자리 RAG 챗봇",
    page_icon="🌟",
    layout="centered"
)

# =============================================
# 🎨 CSS 스타일 (우주 분위기 - 확실하게 동작하는 버전)
# =============================================
st.markdown("""
<style>
    /* 전체 배경 */
    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"] {
        background-color: #020817 !important;
        background-image: radial-gradient(ellipse at 50% 100%, #0d1b4b 0%, #020817 60%) !important;
    }

    /* 메인 컨테이너 */
    [data-testid="stMain"], .main, section.main {
        background-color: transparent !important;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #050d24 !important;
    }

    /* 헤더 영역 */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* 타이틀 */
    h1 {
        color: #c8d8ff !important;
        text-align: center !important;
        text-shadow: 0 0 15px #4466ff, 0 0 30px #2233aa !important;
        letter-spacing: 2px !important;
    }

    /* 일반 텍스트 */
    p, span, label, div {
        color: #c8d8ff !important;
    }

    /* caption */
    [data-testid="stCaptionContainer"] p {
        color: #7788bb !important;
        text-align: center !important;
    }

    /* 채팅 메시지 */
    [data-testid="stChatMessage"] {
        background: rgba(15, 25, 80, 0.6) !important;
        border: 1px solid rgba(80, 120, 255, 0.3) !important;
        border-radius: 15px !important;
        margin-bottom: 10px !important;
    }

    /* 입력창 배경 */
    [data-testid="stChatInputContainer"] {
        background: rgba(10, 20, 60, 0.8) !important;
        border: 1.5px solid rgba(80, 140, 255, 0.8) !important;
        border-radius: 25px !important;
        box-shadow: 0 0 10px rgba(60, 120, 255, 0.5),
                    0 0 20px rgba(60, 120, 255, 0.3),
                    0 0 40px rgba(60, 120, 255, 0.15) !important;
        animation: glowPulse 2.5s ease-in-out infinite !important;
    }

    /* 입력창 글로우 애니메이션 */
    @keyframes glowPulse {
        0%   { box-shadow: 0 0 8px rgba(60,120,255,0.4), 0 0 20px rgba(60,120,255,0.2); }
        50%  { box-shadow: 0 0 16px rgba(80,160,255,0.8), 0 0 35px rgba(80,160,255,0.4), 0 0 60px rgba(80,160,255,0.2); }
        100% { box-shadow: 0 0 8px rgba(60,120,255,0.4), 0 0 20px rgba(60,120,255,0.2); }
    }

    /* 입력창 텍스트 */
    [data-testid="stChatInputContainer"] textarea {
        color: #ffffff !important;
        background: transparent !important;
    }

    /* 버튼 */
    [data-testid="stChatInputSubmitButton"] {
        background: rgba(50, 80, 200, 0.8) !important;
        border-radius: 50% !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# 🕐 현재 시간/날짜 함수 (한국 시간 기준)
# =============================================
def get_current_time():
    korea = pytz.timezone("Asia/Seoul")
    now = datetime.now(korea)
    date_str = now.strftime("%Y년 %m월 %d일 (%a)")
    time_str = now.strftime("%H:%M:%S")
    return date_str, time_str

# =============================================
# 🔑 키값 설정 (secrets.toml에서 불러오기)
# =============================================
searchendpoint = st.secrets["SEARCH_ENDPOINT"]
searchkey      = st.secrets["SEARCH_KEY"]
index          = st.secrets["SEARCH_INDEX"]
sematic        = st.secrets["SEARCH_SEMATIC"]

apikey         = st.secrets["OPENAI_API_KEY"]
endpoint       = st.secrets["OPENAI_ENDPOINT"]
deploymentname = st.secrets["OPENAI_DEPLOY"]

# =============================================
# 📦 클라이언트 초기화
# =============================================
client = OpenAI(
    base_url=endpoint,
    api_key=apikey
)

# =============================================
# 💬 RAG 질문 함수
# =============================================
def ask(question):
    response = client.chat.completions.create(
        model=deploymentname,
        messages=[
            {
                "role": "system",
                "content": "당신은 별자리 전문가입니다. 주어진 데이터를 기반으로 친절하게 답변하세요."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        extra_body={
            "data_sources": [{
                "type": "azure_search",
                "parameters": {
                    "endpoint": searchendpoint,
                    "index_name": index,
                    "semantic_configuration": sematic,
                    "query_type": "semantic",
                    "fields_mapping": {},
                    "in_scope": True,
                    "strictness": 3,
                    "top_n_documents": 5,
                    "authentication": {
                        "type": "api_key",
                        "key": searchkey
                    }
                }
            }]
        }
    )
    return response.choices[0].message.content

# =============================================
# 🎨 UI
# =============================================
st.title("✨ 별자리 RAG 챗봇 ✨")
st.caption("🔭 한국에서 관측 가능한 별자리에 대해 물어보세요!")

# 현재 날짜 / 시간 표시
date_str, time_str = get_current_time()
st.markdown(f"""
<div style='text-align:center; padding:8px 0 16px 0;'>
    <span style='
        background:rgba(10,20,80,0.8);
        border:1px solid rgba(100,150,255,0.5);
        border-radius:20px;
        padding:6px 16px;
        margin:4px;
        font-size:0.9rem;
        color:#aabbff;
        display:inline-block;'>
        📅 {date_str}
    </span>
    <span style='
        background:rgba(10,20,80,0.8);
        border:1px solid rgba(100,150,255,0.5);
        border-radius:20px;
        padding:6px 16px;
        margin:4px;
        font-size:0.9rem;
        color:#aabbff;
        display:inline-block;'>
        🕐 {time_str} (KST)
    </span>
</div>
""", unsafe_allow_html=True)

# 예시 질문 태그
st.markdown("""
<div style='text-align:center; padding:0 0 20px 0;'>
    <span style='
        background:rgba(30,50,130,0.7);
        border:1px solid rgba(100,150,255,0.4);
        border-radius:20px;
        padding:6px 14px;
        margin:3px;
        font-size:0.82rem;
        color:#aac4ff;
        display:inline-block;'>
        💫 겨울에 볼 수 있는 별자리?
    </span>
    <span style='
        background:rgba(30,50,130,0.7);
        border:1px solid rgba(100,150,255,0.4);
        border-radius:20px;
        padding:6px 14px;
        margin:3px;
        font-size:0.82rem;
        color:#aac4ff;
        display:inline-block;'>
        🌙 오리온자리는 언제 봐?
    </span>
    <span style='
        background:rgba(30,50,130,0.7);
        border:1px solid rgba(100,150,255,0.4);
        border-radius:20px;
        padding:6px 14px;
        margin:3px;
        font-size:0.82rem;
        color:#aac4ff;
        display:inline-block;'>
        ⭐ 가장 넓은 별자리는?
    </span>
</div>
""", unsafe_allow_html=True)

# 대화 기록 초기화 + 첫 인사말
if "messages" not in st.session_state:
    date_str2, time_str2 = get_current_time()
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"안녕하세요! 🌟 저는 별자리 전문 챗봇이에요.\n\n오늘은 **{date_str2}** 이고, 현재 시각은 **{time_str2} (KST)** 입니다.\n\n오늘 밤 어떤 별자리가 궁금하신가요? 위치를 알려주시면 더 정확하게 알려드릴게요! 🔭"
        }
    ]

# 이전 대화 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# =============================================
# 🎤 음성 입력
# =============================================
st.markdown("<div style='text-align:center; padding: 10px 0 5px 0; color:#7788bb;'>🎤 마이크로 질문하기</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    audio_bytes = audio_recorder(
        text="",
        recording_color="#4466ff",
        neutral_color="#334488",
        icon_size="2x"
    )

if audio_bytes:
    # Whisper로 음성 → 텍스트 변환
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.wav"
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="ko"
    )
    voice_prompt = transcript.text
    if voice_prompt:
        with st.chat_message("user"):
            st.write(f"🎤 {voice_prompt}")
        st.session_state.messages.append({"role": "user", "content": voice_prompt})

        with st.chat_message("assistant"):
            with st.spinner("🔭 별자리를 탐색하는 중..."):
                answer = ask(voice_prompt)
            st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

# 텍스트 입력창
if prompt := st.chat_input("🌟 별자리에 대해 무엇이든 물어보세요..."):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("🔭 별자리를 탐색하는 중..."):
            answer = ask(prompt)
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
