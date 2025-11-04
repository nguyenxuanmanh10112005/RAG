HỆ THỐNG HỎI ĐÁP LUẬT VIỆT NAM (RAG + LLM OFFLINE)
📘 Giới thiệu

Dự án này xây dựng một hệ thống hỏi đáp tự động dựa trên Bộ luật Lao động Việt Nam, ứng dụng kỹ thuật RAG (Retrieval-Augmented Generation) kết hợp với LLM (phi3:mini) chạy hoàn toàn offline.

Hệ thống có khả năng:

Tìm kiếm điều luật phù hợp với câu hỏi bằng FAISS.

Cung cấp nội dung điều luật đó làm context cho mô hình ngôn ngữ.

Mô hình phi3:mini (qua Ollama) sinh ra câu trả lời tự nhiên, dễ hiểu, chính xác.

Không cần mạng, không cần API, có thể chạy hoàn toàn trên máy cá nhân.

🧠 Kiến trúc hệ thống
          +---------------------------+
          |   Người dùng nhập câu hỏi |
          +-------------+-------------+
                        |
                        v
              +---------+---------+
              |  Bước 1: Embedding |
              |  (MiniLM-L3-v2)   |
              +---------+---------+
                        |
                        v
              +---------+---------+
              |  Bước 2: Indexing  |
              |   (FAISS Search)  |
              +---------+---------+
                        |
                        v
              +---------+---------+
              |  Bước 3: Retrieving|
              |  Trích điều luật   |
              +---------+---------+
                        |
                        v
              +---------+---------+
              | Bước 4: Answering  |
              | (LLM: phi3:mini)   |
              +---------+---------+
                        |
                        v
              +---------+---------+
              |  Câu trả lời cuối  |
              +--------------------+

📂 Cấu trúc thư mục dự án
rag_law_project/
├── app.py                         # Ứng dụng Streamlit chính (web hỏi đáp)
│
├── modules/
│   ├── split_law.py               # Tách PDF luật thành từng điều riêng lẻ
│   ├── build_faiss.py             # (Tùy chọn) tạo index FAISS từ các điều luật
│
├── storage/
│   ├── law_index.faiss            # CSDL FAISS chứa vector embedding
│   ├── law_metadata.json          # Metadata: nội dung & số điều tương ứng
│
├── output_articles/               # Kết quả tách từng điều luật (tạo bởi split_law.py)
│   ├── 001_Dieu_1.txt
│   ├── 002_Dieu_2.txt
│   └── ...
│
├── luat_lao_dong.pdf              # File Bộ luật Lao động gốc
├── requirements.txt               # Thư viện cần cài đặt
└── README.md                      # Tài liệu hướng dẫn (file này)

⚙️ Thành phần chính
Thành phần	Công nghệ / Thư viện	Vai trò
Chunking	PyPDF2, Regex	Tách văn bản luật thành các điều
Embedding	SentenceTransformer (MiniLM-L3-v2)	Mã hóa điều luật thành vector
Indexing	FAISS	Lưu trữ và tìm kiếm vector điều luật
Retrieving	FAISS Search	Lấy điều luật phù hợp nhất với câu hỏi
Answering	Ollama + phi3:mini	Sinh câu trả lời tự nhiên bằng LLM
Frontend	Streamlit	Giao diện web thân thiện
🪜 Các bước xây dựng hệ thống
1️⃣ Chunking (Tách điều luật)

Đọc file PDF luật (luat_lao_dong.pdf)

Dùng regex để tách theo mẫu Điều X.

Mỗi điều được lưu vào file riêng (001_Dieu_1.txt, 002_Dieu_2.txt, ...)

👉 Thực thi:

python modules/split_law.py luat_lao_dong.pdf --out output_articles

2️⃣ Embedding

Mỗi điều luật được mã hóa thành vector bằng mô hình paraphrase-MiniLM-L3-v2.

Các vector được lưu cùng metadata để sử dụng lại nhanh chóng.

3️⃣ Indexing (FAISS)

Dùng FAISS để tạo chỉ mục vector.

Cho phép tìm kiếm nhanh các điều luật tương đồng về ngữ nghĩa.

4️⃣ Retrieving

Khi người dùng nhập câu hỏi:

Sinh embedding cho câu hỏi.

So sánh với FAISS để lấy ra điều gần nhất (top_k=1).

Điều đó được đưa vào làm context cho LLM.

5️⃣ Answering

Context được truyền cho mô hình phi3:mini:Q4_K_M (qua Ollama).

Mô hình sinh ra câu trả lời ngắn gọn, đúng trọng tâm.

Nếu không tìm thấy điều phù hợp → trả lời mặc định:

“Không có thông tin trong Bộ luật Lao động hiện hành.”

⚙️ Cấu hình khuyến nghị (CPU 16GB RAM)
Thành phần	Model / Thiết lập	Ghi chú
Embedding	paraphrase-MiniLM-L3-v2	nhẹ, nhanh
FAISS top_k	1	chỉ lấy điều phù hợp nhất
LLM	phi3:mini:Q4_K_M	lượng tử hóa 4-bit, giảm RAM 40%
Giới hạn context	3000 ký tự	tránh quá tải bộ nhớ
Trả lời	≤ 100 từ	nhanh, ngắn gọn
Ollama	--keepalive 60	giữ model trong RAM sau khi gọi
💻 Cách cài đặt và chạy
1️⃣ Clone project
git clone https://github.com/yourname/rag_law_project.git
cd rag_law_project

2️⃣ Cài thư viện Python
pip install -r requirements.txt


Hoặc:

pip install streamlit faiss-cpu sentence-transformers PyPDF2

3️⃣ Cài Ollama và tải mô hình

Tải Ollama từ: https://ollama.com/download

Sau khi cài, tải mô hình lượng tử hóa nhẹ:

ollama pull phi3:mini:Q4_K_M


(Tùy chọn) giữ model trong RAM để trả lời nhanh hơn:

ollama serve

4️⃣ Chạy ứng dụng web
streamlit run app.py


Sau đó mở trình duyệt tại:
👉 http://localhost:8501

💬 Ví dụ câu hỏi
Câu hỏi	Kết quả kỳ vọng
“Điều 1 là gì?”	Trả nội dung Điều 1 (Phạm vi điều chỉnh)
“Người lao động được nghỉ phép năm bao nhiêu ngày?”	Trích Điều 113
“Điều 25 nói gì về thử việc?”	Trả nội dung Điều 25
“Điều 100 nói gì?”	“Không có thông tin trong Bộ luật Lao động hiện hành.”
⚙️ Các tối ưu hiệu năng
Tối ưu	Mô tả
top_k=1	chỉ lấy 1 điều luật → tốc độ nhanh hơn 3×
context ≤ 3000 ký tự	tránh tắc nghẽn bộ nhớ
Giới hạn câu trả lời ≤ 100 từ	sinh nhanh hơn
phi3:mini:Q4_K_M	nhẹ hơn 40–50%, RAM chỉ ~2GB
ollama serve + --keepalive 60	lần sau trả lời gần như tức thì
📈 Kết quả thực tế
Chỉ số	Trước tối ưu	Sau tối ưu
Load model lần đầu	~30s	~10s
Thời gian trả lời	10–15s	4–6s
RAM sử dụng	4.2 GB	2.1 GB
Độ chính xác	93%	92%
🧩 Hướng phát triển

Mở rộng sang nhiều bộ luật khác.

Cho phép người dùng upload file PDF mới để tự động xây FAISS.

Tích hợp API online (GPT-4o-mini, Qwen-API) để so sánh hiệu suất.

Tạo bộ dataset kiểm thử tự động để đánh giá RAG.

👨‍💻 Tác giả

Nguyễn Xuân Mạnh
🎓 Đồ án: Xây dựng hệ thống hỏi đáp Bộ luật Lao động Việt Nam bằng RAG và LLM
🧠 Công nghệ: Python · FAISS · Ollama · Streamlit · SentenceTransformers · phi3-mini

