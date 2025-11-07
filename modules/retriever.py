# modules/retriever.py
from sentence_transformers import SentenceTransformer
import faiss, json, os

class LawRetriever:
    def __init__(self):
        try:
            self.model = SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder')
        except Exception as e:
            raise Exception(f"Không thể tải model embedding: {e}")
        
        if not os.path.exists("storage/law_index.faiss"):
            raise FileNotFoundError("Không tìm thấy FAISS index. Chạy embed_law.py trước!")
        
        if not os.path.exists("storage/law_metadata.json"):
            raise FileNotFoundError("Không tìm thấy metadata. Chạy split_law.py trước!")
        
        try:
            self.index = faiss.read_index("storage/law_index.faiss")
            with open("storage/law_metadata.json", 'r', encoding='utf-8') as f:
                self.meta = json.load(f)
        except Exception as e:
            raise Exception(f"Lỗi khi tải dữ liệu: {e}")

    def search(self, q, k=5):
        try:
            vec = self.model.encode([q], normalize_embeddings=True).astype('float32')
            scores, idxs = self.index.search(vec, k)
            res = []
            for i, s in zip(idxs[0], scores[0]):
                if i >= len(self.meta):
                    continue
                m = self.meta[i]
                if os.path.exists(m['file']):
                    try:
                        with open(m['file'], 'r', encoding='utf-8') as f:
                            text = f.read().strip()
                        res.append({
                            "ref": m['title'],
                            "text": text,
                            "score": round(float(s), 3)
                        })
                    except Exception as e:
                        print(f"Lỗi đọc file {m['file']}: {e}")
                        continue
            return res
        except Exception as e:
            print(f"Lỗi tìm kiếm: {e}")
            return []