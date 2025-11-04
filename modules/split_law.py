import re
import os
import textwrap
from PyPDF2 import PdfReader

def extract_text(pdf_path: str) -> str:
    """Đọc toàn bộ nội dung PDF và chuẩn hóa văn bản."""
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    # Gộp dòng, xóa khoảng trắng thừa, sửa lỗi OCR phổ biến
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('Đi ều', 'Điều')
    text = text.replace('Ðiều', 'Điều')  # OCR lỗi thường gặp
    return text.strip()

def split_articles(text: str):
    """
    Tách văn bản luật thành từng điều:
    - Dựa vào 'Điều X.' ở đầu dòng hoặc sau xuống dòng.
    - Giữ nguyên phần tiêu đề của điều.
    """
    # Thêm xuống dòng trước mỗi "Điều X."
    text = re.sub(r'(?<!\n)(Điều\s+\d+\.)', r'\n\1', text)

    # Regex nhận tiêu đề mỗi điều ở đầu dòng
    header_re = re.compile(r'(?m)^\s*(Điều\s+\d+\.[^\n]*)')
    matches = list(header_re.finditer(text))

    articles = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        header = m.group(1).strip()
        body_raw = text[m.end():end].strip()

        # Làm sạch nội dung
        body_single_line = " ".join(body_raw.split())
        body_wrapped = "\n".join(textwrap.wrap(body_single_line, width=100))

        # Lấy số điều
        num_match = re.search(r'Điều\s+(\d+)', header)
        number = num_match.group(1) if num_match else "NA"

        articles.append({
            "number": number,
            "header": header,
            "body": body_wrapped
        })

    print(f"✅ Phát hiện {len(articles)} điều luật trong văn bản.")
    return articles

def save_articles(articles, out_dir: str):
    """Lưu từng điều ra file riêng."""
    os.makedirs(out_dir, exist_ok=True)
    for a in articles:
        fname = f"{int(a['number']):03d}_Dieu_{a['number']}.txt"
        path = os.path.join(out_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(a['header'] + "\n\n")
            f.write(a['body'] + "\n")
    print(f"🎯 Đã lưu {len(articles)} điều vào thư mục {out_dir}")

if __name__ == "__main__":
    pdf_path = "data/luat_lao_dong.pdf"
    output_dir = "storage/articles"

    print("📖 Đang đọc file PDF...")
    text = extract_text(pdf_path)
    articles = split_articles(text)
    save_articles(articles, output_dir)
