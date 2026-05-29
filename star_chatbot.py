import streamlit as st
from openai import OpenAI
from datetime import datetime
import pytz
import random

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

# =============================================
# 🔮 타로카드 데이터
# =============================================
# 실제 라이더-웨이트(Rider-Waite-Smith, 1909, 퍼블릭 도메인) 메이저 아르카나 22장
# 카드 이미지는 위키미디어 공용(Wikimedia Commons)에서 제공
_W = "https://upload.wikimedia.org/wikipedia/commons/thumb/{}/RWS_Tarot_{}.jpg/330px-RWS_Tarot_{}.jpg"
TAROT_CARDS = [
    {"name": "🌟 바보 (The Fool)", "upright": "새로운 시작, 자유로운 정신, 모험", "reverse": "무모함, 경솔함, 위험", "img": _W.format("9/90", "00_Fool", "00_Fool")},
    {"name": "🪄 마법사 (The Magician)", "upright": "의지력, 창조력, 집중", "reverse": "속임수, 재능 낭비", "img": _W.format("d/de", "01_Magician", "01_Magician")},
    {"name": "🌙 여사제 (The High Priestess)", "upright": "직관, 신비, 내면의 지식", "reverse": "비밀, 억압된 감정", "img": _W.format("8/88", "02_High_Priestess", "02_High_Priestess")},
    {"name": "🌸 여황제 (The Empress)", "upright": "풍요, 모성, 창조성", "reverse": "의존성, 창의력 부족", "img": _W.format("d/d2", "03_Empress", "03_Empress")},
    {"name": "👑 황제 (The Emperor)", "upright": "권위, 안정, 리더십", "reverse": "지배욕, 경직성", "img": _W.format("c/c3", "04_Emperor", "04_Emperor")},
    {"name": "🙏 교황 (The Hierophant)", "upright": "전통, 신앙, 조언", "reverse": "고집, 규칙에 얽매임", "img": _W.format("8/8d", "05_Hierophant", "05_Hierophant")},
    {"name": "💑 연인 (The Lovers)", "upright": "사랑, 선택, 조화", "reverse": "불균형, 잘못된 선택", "img": _W.format("d/db", "06_Lovers", "06_Lovers")},
    {"name": "🏆 전차 (The Chariot)", "upright": "승리, 의지력, 극복", "reverse": "방향 상실, 통제력 부족", "img": _W.format("9/9b", "07_Chariot", "07_Chariot")},
    {"name": "💪 힘 (Strength)", "upright": "용기, 인내, 내면의 힘", "reverse": "나약함, 자기 의심", "img": _W.format("f/f5", "08_Strength", "08_Strength")},
    {"name": "🏮 은둔자 (The Hermit)", "upright": "내면 탐구, 지혜, 고독", "reverse": "고립, 외로움", "img": _W.format("4/4d", "09_Hermit", "09_Hermit")},
    {"name": "☸️ 운명의 수레바퀴 (Wheel of Fortune)", "upright": "행운, 변화, 전환점", "reverse": "불운, 저항", "img": _W.format("3/3c", "10_Wheel_of_Fortune", "10_Wheel_of_Fortune")},
    {"name": "⚖️ 정의 (Justice)", "upright": "공정함, 진실, 균형", "reverse": "불공평, 편견", "img": _W.format("e/e0", "11_Justice", "11_Justice")},
    {"name": "🙃 매달린 사람 (The Hanged Man)", "upright": "희생, 새로운 관점, 기다림", "reverse": "순교, 지연", "img": _W.format("2/2b", "12_Hanged_Man", "12_Hanged_Man")},
    {"name": "💀 죽음 (Death)", "upright": "변화, 끝과 시작, 전환", "reverse": "저항, 변화 거부", "img": _W.format("d/d7", "13_Death", "13_Death")},
    {"name": "⚗️ 절제 (Temperance)", "upright": "균형, 인내, 조화", "reverse": "불균형, 과잉", "img": _W.format("f/f8", "14_Temperance", "14_Temperance")},
    {"name": "😈 악마 (The Devil)", "upright": "속박, 집착, 욕망", "reverse": "해방, 속박에서 벗어남", "img": _W.format("5/55", "15_Devil", "15_Devil")},
    {"name": "🗼 탑 (The Tower)", "upright": "급격한 변화, 혼란, 계시", "reverse": "재난 회피, 두려움", "img": _W.format("5/53", "16_Tower", "16_Tower")},
    {"name": "⭐ 별 (The Star)", "upright": "희망, 영감, 평화", "reverse": "절망, 믿음 부족", "img": _W.format("d/db", "17_Star", "17_Star")},
    {"name": "🌕 달 (The Moon)", "upright": "환상, 두려움, 무의식", "reverse": "혼란, 오해", "img": _W.format("7/7f", "18_Moon", "18_Moon")},
    {"name": "☀️ 태양 (The Sun)", "upright": "기쁨, 성공, 활력", "reverse": "슬픔, 비현실", "img": _W.format("1/17", "19_Sun", "19_Sun")},
    {"name": "🎺 심판 (Judgement)", "upright": "부활, 반성, 내면의 부름", "reverse": "자기 의심, 후회", "img": _W.format("d/dd", "20_Judgement", "20_Judgement")},
    {"name": "🌍 세계 (The World)", "upright": "완성, 통합, 성취", "reverse": "미완성, 지연", "img": _W.format("f/ff", "21_World", "21_World")},
]

def get_tarot_reading(card, concern):
    """타로카드 AI 해석"""
    is_reversed = random.choice([True, False])
    meaning = card["reverse"] if is_reversed else card["upright"]
    direction = "역방향 🔄" if is_reversed else "정방향 ✨"

    prompt = f"""
    타로카드 '{card["name"]}'이 {direction}으로 나왔습니다.
    카드 의미: {meaning}
    사용자 고민: {concern}

    이 카드를 바탕으로 따뜻하고 신비로운 분위기로 3-4문장 해석해주세요.
    한국어로 답변해주세요.
    """
    response = client.chat.completions.create(
        model=deploymentname,
        messages=[
            {"role": "system", "content": "당신은 신비로운 타로카드 점술사입니다. 따뜻하고 신비로운 분위기로 해석해주세요."},
            {"role": "user", "content": prompt}
        ]
    )
    return card["name"], direction, meaning, response.choices[0].message.content

# =============================================
# 🔮 타로카드 버튼/카드 스타일
# =============================================
st.markdown("""
<style>
    /* 사이드바 완전히 숨기기 */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* 타로카드 뒷면 버튼 스타일 */
    [data-testid="stExpander"] .stButton > button {
        height: 90px !important;
        border-radius: 12px !important;
        border: none !important;
        background: linear-gradient(160deg, #3a1d6e 0%, #6633cc 45%, #1a0b3d 100%) !important;
        box-shadow: 0 0 10px rgba(150,90,255,0.5), inset 0 0 12px rgba(200,150,255,0.25) !important;
        font-size: 1.7rem !important;
        color: #e8d0ff !important;
        transition: transform 0.15s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stExpander"] .stButton > button:hover {
        transform: translateY(-6px) scale(1.04) !important;
        box-shadow: 0 0 20px rgba(200,150,255,0.9), 0 8px 20px rgba(100,50,200,0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# 타로카드 뽑기 트리거 버튼 (가운데 정렬)
tcol1, tcol2, tcol3 = st.columns([1, 1.4, 1])
with tcol2:
    if st.button("🔮 타로카드 점 보기", use_container_width=True):
        st.session_state.show_tarot = not st.session_state.get("show_tarot", False)

# 타로카드 팝업
if st.session_state.get("show_tarot", False):
    with st.expander("🔮 타로카드 점술 - 카드를 선택하세요", expanded=True):
        concern = st.text_input("✨ 오늘의 고민을 입력하세요", placeholder="예: 오늘 하루 운세가 궁금해요...")

        st.markdown("<p style='color:#cc99ff; text-align:center; font-size:0.95rem; margin-top:10px;'>🃏 마음이 끌리는 카드를 클릭하세요</p>", unsafe_allow_html=True)

        # 카드 펼치기 (2줄 x 6장 = 12장)
        card_faces = ["🌜", "✦", "☾", "✶", "🔮", "⭐", "☽", "✷", "🌟", "✵", "☄", "✺"]
        for row in range(2):
            cols = st.columns(6)
            for j, col in enumerate(cols):
                idx = row * 6 + j
                with col:
                    if st.button(card_faces[idx], key=f"card_{idx}", use_container_width=True):
                        st.session_state.selected_tarot = random.choice(TAROT_CARDS)
                        st.session_state.tarot_concern = concern

        # 선택된 카드 결과 표시
        if st.session_state.get("selected_tarot") and st.session_state.get("tarot_concern"):
            card = st.session_state.selected_tarot
            concern_text = st.session_state.tarot_concern
            with st.spinner("🔮 카드를 해석하는 중..."):
                card_name, direction, meaning, reading = get_tarot_reading(card, concern_text)

            is_rev = "역방향" in direction
            rotate = "transform:rotate(180deg);" if is_rev else ""

            st.markdown(f"""
            <div style='background:linear-gradient(160deg, rgba(60,20,110,0.9), rgba(20,8,50,0.9));
            border:1px solid rgba(180,100,255,0.5); border-radius:18px; padding:24px; margin-top:16px;
            box-shadow:0 0 25px rgba(150,90,255,0.4); text-align:center;'>
                <h3 style='color:#dd99ff; text-shadow:0 0 12px rgba(200,120,255,0.7);'>{card_name}</h3>
                <img src='{card["img"]}' style='width:180px; border-radius:10px; margin:10px auto;
                box-shadow:0 0 20px rgba(180,120,255,0.6); {rotate}'>
                <p style='color:#bb77ff;'>{direction} | {meaning}</p>
                <hr style='border-color:rgba(180,100,255,0.3);'>
                <p style='color:#e8d8ff; line-height:1.8; text-align:left;'>{reading}</p>
            </div>
            """, unsafe_allow_html=True)

        if st.button("✖ 닫기", key="close_tarot"):
            st.session_state.show_tarot = False
            st.session_state.selected_tarot = None
            st.session_state.tarot_concern = None
            st.rerun()

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
