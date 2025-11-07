import os, json, numpy as np
from sentence_transformers import SentenceTransformer
import faiss

MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"

print(f"Đang tải model: {MODEL_NAME}...")
try:
    model = SentenceTransformer(MODEL_NAME)
    EMBEDDING_DIM = model.get_sentence_embedding_dimension()
    print(f"Model đã tải thành công! Embedding dim: {EMBEDDING_DIM}")
except Exception as e:
    print(f"Lỗi khi tải model: {e}")
    print("Hãy kiểm tra kết nối internet hoặc thử model khác.")
    exit(1)

def load_articles():
    if not os.path.exists("storage/law_metadata.json"):
        print("Không tìm thấy metadata. Chạy split_law.py trước!")
        exit(1)
    
    try:
        with open("storage/law_metadata.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"Lỗi đọc metadata: {e}")
        exit(1)
    
    texts = []
    missing_files = 0
    for item in metadata:
        if os.path.exists(item['file']):
            with open(item['file'], 'r', encoding='utf-8') as f:
                texts.append(f.read().strip())
        else:
            texts.append("")
            missing_files += 1
    
    if missing_files > 0:
        print(f"Cảnh báo: {missing_files} file bị thiếu")
    
    return metadata, texts

metadata, texts = load_articles()
print(f"Đang tạo embedding cho {len(texts)} điều luật...")
embeddings = model.encode(texts, batch_size=8, show_progress_bar=True, normalize_embeddings=True)
embeddings = np.array(embeddings).astype('float32')

print("Đang tạo FAISS index...")
index = faiss.IndexFlatIP(EMBEDDING_DIM)
index.add(embeddings)
faiss.write_index(index, "storage/law_index.faiss")
print(f"Hoàn tất! Đã tạo FAISS index với {embeddings.shape[0]} vectors, {embeddings.shape[1]} dimensions")