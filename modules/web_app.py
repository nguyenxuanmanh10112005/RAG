import streamlit as st
import requests
import os
import sys

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2:1b"
FALLBACK_MODELS = ["qwen2:0.5b", "qwen2:1.5b", "gemma2:2b", "llama3.2:3b", "phi3:mini", "phi3:latest"]

def check_ollama():
    try:
        return requests.get("http://localhost:11434", timeout=5).status_code == 200
    except:
        return False

def get_available_models():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=10)
        if r.status_code == 200:
            return [m["name"] for m in r.json().get("models", [])]
        return []
    except:
        return []

def check_model_exists(model_name):
    available = get_available_models()
    return (model_name in available or 
            f"{model_name}:latest" in available or
            any(name.startswith(model_name + ":") for name in available))

def generate_answer(prompt, model_name):
    if not check_ollama():
        return "Lỗi: Ollama chưa chạy. Chạy 'ollama serve' trước."
    
    if not check_model_exists(model_name):
        return f"Lỗi: Model '{model_name}' chưa có. Chạy 'ollama pull {model_name}'"
    
    try:
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0, "num_ctx": 4096}
        }
        r = requests.post(OLLAMA_URL, json=payload, timeout=180)
        
        if r.status_code == 500:
            return f"Lỗi server. Thử: ollama pull {model_name} hoặc khởi động lại Ollama"
        
        r.raise_for_status()
        return r.json()["response"]
    except requests.exceptions.Timeout:
        return "Timeout: Model phản hồi quá chậm. Thử model nhẹ hơn."
    except Exception as e:
        return f"Lỗi: {e}"

# Kiểm tra files cần thiết
if not os.path.exists("storage/law_metadata.json"):
    st.error("Chưa chạy: python modules/split_law.py")
    st.stop()
if not os.path.exists("storage/law_index.faiss"):
    st.error("Chưa chạy: python modules/embed_law.py")
    st.stop()

@st.cache_resource
def load_retriever():
    try:
        from modules.retriever import LawRetriever
        return LawRetriever()
    except Exception as e:
        st.error(f"Lỗi khởi tạo: {e}")
        st.stop()

retriever = load_retriever()

# Kiểm tra Ollama và tìm model khả dụng
if not check_ollama():
    st.error("Ollama chưa chạy. Chạy: ollama serve")
    st.stop()

current_model = LLM_MODEL
if not check_model_exists(LLM_MODEL):
    st.warning(f"Model {LLM_MODEL} chưa có, tìm model khác...")
    for fallback in FALLBACK_MODELS:
        if check_model_exists(fallback):
            current_model = fallback
            st.info(f"Sử dụng model: {current_model}")
            break
    else:
        st.error("Không tìm thấy model nào. Chạy: ollama pull llama3.2:1b")
        st.stop()

LLM_MODEL = current_model

st.set_page_config(page_title="Luật Lao Động AI", layout="centered")
st.title("Hỏi Đáp Bộ luật Lao động 2019")
st.caption("Dựa trên PDF chính thức")
st.success(f"Sẵn sàng với model: {LLM_MODEL}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Hỏi về luật lao động..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm..."):
            context = retriever.search(prompt, k=3)
            if not context:
                answer = "Không tìm thấy quy định phù hợp. Thử câu hỏi khác."
            else:
                ctx_str = "\n\n".join([f"{r['ref']}:\n{r['text']}" for r in context])
                full_prompt = f"""Dựa trên Bộ luật Lao động 2019, trả lời câu hỏi sau:

Câu hỏi: {prompt}

Thông tin liên quan:
{ctx_str}

Trả lời ngắn gọn và trích dẫn điều luật:"""
                answer = generate_answer(full_prompt, LLM_MODEL)

            st.markdown(answer)
            if context:
                with st.expander("Nguồn tham khảo"):
                    for r in context:
                        st.caption(f"{r['ref']} (Độ liên quan: {r['score']:.2f})")
                        st.write(r['text'][:500] + ("..." if len(r['text']) > 500 else ""))

    st.session_state.messages.append({"role": "assistant", "content": answer})