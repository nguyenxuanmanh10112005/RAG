import streamlit as st
import faiss
import json
import numpy as np
import subprocess
import re
import unicodedata
from sentence_transformers import SentenceTransformer

# ==========================
# ⚙️ 1. Cấu hình Ollama
# ==========================
OLLAMA_PATH = r"C:\Users\ADMIN\AppData\Local\Programs\Ollama\ollama.exe"
MODEL_NAME = "qwen2:0.5b"

# ==========================
# ⚙️ 2. Load mô hình embedding & dữ liệu FAISS
# ==========================
@st.cache_resource
def load_model():
    return SentenceTransformer("intfloat/multilingual-e5-small")

@st.cache_resource
def load_data():
    index = faiss.read_index("storage/law_index.faiss")
    with open("storage/law_metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    # Lưu danh sách số điều để kiểm tra
    existing_articles = [int(re.findall(r"\d+", m['content'])[0]) for m in metadata]
    return index, metadata, existing_articles

model = load_model()
index, metadata, existing_articles = load_data()

# ==========================
# 🧹 3. Chuẩn hóa văn bản
# ==========================
def normalize_text(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ==========================
# 🔍 4. FAISS retrieval
# ==========================
def retrieve_context(query, top_k=1, threshold=0.25):
    query_norm = normalize_text(query)
    q_emb = model.encode([query_norm], convert_to_numpy=True)
    D, I = index.search(q_emb, top_k)

    sims = [1 / (1 + d) for d in D[0]]
    contexts = []
    for idx, sim in zip(I[0], sims):
        if idx < len(metadata) and sim >= threshold:
            contexts.append(f"[Độ tương đồng: {sim:.2f}]\n{metadata[idx]['content']}")

    # Fallback nếu không tìm thấy kết quả
    if not contexts and top_k < 6:
        return retrieve_context(query, top_k=6, threshold=0.15)

    return "\n---\n".join(contexts), len(contexts)

# ==========================
# ⚖️ 5. Kiểm tra câu hỏi về số điều
# ==========================
def check_article_exists(query):
    """Nếu người dùng hỏi Điều X, kiểm tra X có tồn tại không"""
    match = re.search(r"điều\s*(\d+)", query.lower())
    if match:
        number = int(match.group(1))
        if number not in existing_articles:
            return False
    return True

# ==========================
# 🤖 6. Gọi Ollama qwen2:0.5b
# ==========================
def generate_answer(context, query):
    prompt = f"""
Bạn là trợ lý pháp lý am hiểu Bộ luật Lao động Việt Nam.

Các điều luật liên quan:
{context}

Câu hỏi: {query}

Yêu cầu:
- Trả lời ngắn gọn (≤120 từ), dễ hiểu, bằng tiếng Việt.
- Chỉ dựa trên nội dung điều luật, không bịa đặt.
- Nếu không có thông tin, trả lời:
  "Không có thông tin trong Bộ luật Lao động hiện hành."
"""
    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", MODEL_NAME],
            input=prompt,
            text=True,
            encoding="utf-8",
            errors="ignore",
            capture_output=True,
            timeout=180
        )
        if result.returncode != 0:
            return f"⚠️ Lỗi Ollama: {result.stderr.strip() or result.stdout.strip()}"
        return result.stdout.strip() or "⚠️ Không nhận được phản hồi từ mô hình."
    except Exception as e:
        return f"⚠️ Lỗi khi gọi Ollama: {e}"

# ==========================
# 🌐 7. Giao diện Streamlit
# ==========================
st.set_page_config(page_title="Hỏi đáp Luật Việt Nam (RAG)", page_icon="⚖️")
st.title("⚖️ HỆ THỐNG HỎI ĐÁP LUẬT VIỆT NAM (RAG)")
st.caption("Dựa trên FAISS + mô hình LLM qwen2:0.5b chạy offline qua Ollama.")

query = st.text_input("🔎 Nhập câu hỏi:", placeholder="Ví dụ: Điều 1 nói về vấn đề gì?")

if query:
    with st.spinner("⏳ Đang truy xuất và xử lý..."):
        # Kiểm tra nếu người dùng hỏi Điều X không tồn tại
        if not check_article_exists(query):
            st.warning("⚖️ Không có thông tin trong Bộ luật Lao động hiện hành.")
        else:
            context, found = retrieve_context(query)

            if found == 0:
                st.warning("⚖️ Không tìm thấy điều luật liên quan. Hãy thử diễn đạt lại câu hỏi.")
            else:
                st.info(f"🔍 Đã tìm thấy {found} điều luật liên quan.")
                if len(context) > 4000:
                    context = context[:4000]

                answer = generate_answer(context, query)
                st.subheader("🧠 Câu trả lời:")
                st.success(answer)

                with st.expander("📜 Xem các điều luật được sử dụng"):
                    st.text(context)
