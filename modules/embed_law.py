import os
import json
import numpy as np
import faiss
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

def load_articles(folder="storage/articles"):
    """Đọc tất cả file điều luật và trả về danh sách nội dung."""
    files = sorted([f for f in os.listdir(folder) if f.endswith(".txt")])
    texts = []
    for f in tqdm(files, desc="📖 Đang đọc các điều luật"):
        with open(os.path.join(folder, f), "r", encoding="utf-8") as file:
            texts.append(file.read())
    return files, texts

def create_embeddings(texts, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """Sinh embedding vector cho từng điều luật."""
    print(f"🧠 Đang tải mô hình embedding: {model_name}")
    model = SentenceTransformer(model_name)
    print("🔍 Đang sinh vector embedding cho các điều luật...")
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return embeddings

def build_faiss_index(embeddings, index_path="storage/law_index.faiss"):
    """Tạo và lưu FAISS index."""
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, index_path)
    print(f"✅ Đã lưu FAISS index tại: {index_path}")

def save_metadata(files, texts, metadata_path="storage/law_metadata.json"):
    """Lưu thông tin (tên file + nội dung) vào JSON."""
    data = [{"file": f, "content": t} for f, t in zip(files, texts)]
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Đã lưu metadata tại: {metadata_path}")

if __name__ == "__main__":
    # 1️⃣ Đọc các file điều luật
    files, texts = load_articles("storage/articles")

    # 2️⃣ Sinh embedding vector
    embeddings = create_embeddings(texts)

    # 3️⃣ Lưu FAISS index
    build_faiss_index(embeddings, "storage/law_index.faiss")

    # 4️⃣ Lưu metadata JSON
    save_metadata(files, texts, "storage/law_metadata.json")

    print("\n🎯 Hoàn tất xây dựng cơ sở dữ liệu vector cho hệ thống RAG!")
