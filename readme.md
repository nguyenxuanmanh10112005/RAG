# Hệ thống Hỏi Đáp Luật Lao Động (RAG)

## Giới thiệu

Hệ thống RAG (Retrieval-Augmented Generation) để hỏi đáp về Bộ luật Lao động Việt Nam. Sử dụng FAISS để tìm kiếm vector và Ollama (llama3.2:1b) để tạo câu trả lời. Hoạt động hoàn toàn offline sau khi cài đặt.

## Công nghệ sử dụng

- **Python 3.8+**
- **FAISS** - Vector database để tìm kiếm ngữ nghĩa
- **SentenceTransformers** - Tạo embedding (bkai-foundation-models/vietnamese-bi-encoder)
- **Ollama** - Chạy LLM offline (llama3.2:1b)
- **Streamlit** - Giao diện web đơn giản

## Cấu trúc project

```
RAG/
├── data/
│   └── luat_lao_dong.pdf          # File PDF gốc
├── modules/
│   ├── split_law.py               # Tách PDF thành từng điều
│   ├── embed_law.py               # Tạo vector database
│   ├── retriever.py               # Class tìm kiếm
│   └── web_app.py                 # App chính (Streamlit)
├── storage/
│   ├── articles/                  # 69 file điều luật đã tách
│   ├── law_index.faiss           # FAISS index
│   └── law_metadata.json          # Metadata
└── requirements.txt
```

## Cài đặt

### 1. Cài đặt Python packages

```bash
pip install -r requirements.txt
```

### 2. Cài đặt Ollama

1. Tải Ollama: https://ollama.com/download
2. Cài đặt xong, mở terminal chạy:

```bash
ollama pull llama3.2:1b
```

### 3. Xây dựng database

```bash
# Bước 1: Tách PDF thành các điều luật
python modules/split_law.py

# Bước 2: Tạo vector embeddings và FAISS index
python modules/embed_law.py
```

**Lưu ý:** Cần có file `data/luat_lao_dong.pdf` trước khi chạy.

## Chạy ứng dụng

```bash
# Chạy từ thư mục gốc của project
streamlit run modules/web_app.py
```

Trình duyệt sẽ tự động mở tại `http://localhost:8501`

## Cách hoạt động

1. **Nhập câu hỏi** → Ví dụ: "Điều 1 nói về gì?"
2. **Tìm kiếm vector** → FAISS tìm 3 điều luật liên quan nhất
3. **Tạo câu trả lời** → Ollama LLM dựa trên context tìm được
4. **Hiển thị kết quả** → Câu trả lời + nguồn tham khảo

## Ví dụ sử dụng

- "Điều 1 nói về gì?"
- "Quyền của người lao động"
- "Nghỉ phép năm như thế nào?"
- "Thời hạn thử việc là bao lâu?"
- "Mức lương tối thiểu"

## Yêu cầu hệ thống

- **Python 3.8+**
- **RAM:** 16GB+ (llama3.2:1b),
- **Ollama** đã cài đặt
- **Dung lượng:** ~3-5GB (bao gồm models và data)

### Các model khuyến nghị

| Model | Kích thước | RAM cần | Đặc điểm |
|-------|------------|---------|----------|
| `qwen2:0.5b` | 352MB | 1GB | Siêu nhẹ, phù hợp máy yếu |
| `qwen2:1.5b` | 934MB | 2GB | Nhẹ, cân bằng tốt |
| `llama3.2:1b` | 1.3GB | 2GB | **Khuyến nghị** - Ổn định nhất |
| `gemma2:2b` | 1.6GB | 4GB | Chất lượng tốt |
| `llama3.2:3b` | 2.0GB | 6GB | Chất lượng cao |
| `phi3:latest` | 2.2GB | 8GB | Mạnh nhất |

## Troubleshooting

### Không tìm thấy file PDF
```bash
# Đặt file PDF vào đúng vị trí
mkdir -p data
# Copy file luat_lao_dong.pdf vào thư mục data/
```

### Không tìm thấy FAISS index
```bash
# Tạo lại vector database
python modules/embed_law.py
```

### Ollama không hoạt động
```bash
# Kiểm tra Ollama
ollama --version
ollama serve  # Khởi động Ollama server

# Kiểm tra models
ollama list
```

### Model không tồn tại
```bash
# Tải model khuyến nghị
ollama pull llama3.2:1b

# Hoặc model nhẹ hơn
ollama pull qwen2:0.5b
```

### Lỗi import modules
- Đảm bảo chạy từ thư mục gốc (không phải từ trong `modules/`)
- Kiểm tra Python path và dependencies

### Model trả lời chậm/sai
- Thử model lớn hơn: `llama3.2:3b` hoặc `phi3:latest`
- Tăng số lượng context trong code
- Kiểm tra RAM còn đủ không

## Cải thiện chất lượng

### 1. Nâng cấp model LLM
```bash
# Model chất lượng cao hơn
ollama pull llama3.2:3b
ollama pull phi3:latest
```

Sửa trong `modules/web_app.py`:
```python
LLM_MODEL = "llama3.2:3b"  # Thay vì "llama3.2:1b"
```

### 2. Tăng số lượng context
Sửa trong `modules/web_app.py`:
```python
context = retriever.search(prompt, k=5)  # Tăng từ 3 lên 5
```

### 3. Tinh chỉnh embedding model
Nếu muốn thử model embedding khác, sửa trong `modules/embed_law.py` và `modules/retriever.py`:
```python
MODEL_NAME = "keepitreal/vietnamese-sbert"  # Model khác
```
**Lưu ý:** Phải chạy lại `embed_law.py` sau khi đổi model embedding.

## Tính năng

- Tìm kiếm ngữ nghĩa chính xác với Vietnamese BERT
- Auto-fallback models - Tự động chọn model khả dụng
- Hiển thị nguồn tham khảo với độ liên quan
- Error handling thông minh với gợi ý sửa lỗi
- Giao diện đơn giản, dễ sử dụng
- Hoạt động offline hoàn toàn

## Performance

### Thời gian phản hồi trung bình
- **Tìm kiếm:** ~0.1-0.3s (FAISS)
- **Tạo câu trả lời:** ~2-10s (tùy model)
- **Tổng cộng:** ~3-15s

### Tips tối ưu
- Dùng SSD thay vì HDD để tăng tốc I/O
- Đóng các app khác khi chạy model lớn
- Restart Ollama nếu phản hồi chậm

## Roadmap

- [ ] Thêm support cho nhiều bộ luật khác
- [ ] Cải thiện prompt engineering
- [ ] Thêm tính năng export câu trả lời
- [ ] Tích hợp voice input/output
- [ ] API endpoint cho integration

## Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

## License

MIT License - Tự do sử dụng và chỉnh sửa.

---

**Chúc bạn sử dụng vui vẻ!**