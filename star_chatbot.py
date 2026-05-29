import streamlit as st
from openai import OpenAI

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
# 🎨 Streamlit UI
# =============================================
st.title("🌟 별자리 RAG 챗봇")
st.caption("한국에서 관측 가능한 별자리에 대해 물어보세요!")

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 입력창
if prompt := st.chat_input("질문을 입력하세요..."):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            answer = ask(prompt)
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
