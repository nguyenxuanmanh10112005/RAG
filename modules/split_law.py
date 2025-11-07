import fitz, re, os, json

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

def split_articles(text):
    lines = text.split('\n')
    articles = []
    current_title = ""
    current_content = []
    in_article = False

    # Pattern để nhận diện điều luật
    article_pattern = re.compile(r"^Điều\s+\d+[a-zA-Z]?\.\s*[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯ]")

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if article_pattern.match(line):
            if in_article and current_title:
                articles.append({
                    "title": current_title,
                    "content": "\n".join(current_content).strip()
                })
            current_title = re.sub(r"\s+", " ", line).strip()
            if not current_title.endswith("."):
                current_title += "."
            current_content = []
            in_article = True
        else:
            if in_article:
                current_content.append(line)

    if in_article and current_title:
        articles.append({
            "title": current_title,
            "content": "\n".join(current_content).strip()
        })

    return articles

def save_articles(articles):
    os.makedirs("storage/articles", exist_ok=True)
    metadata = []

    for art in articles:
        match = re.search(r"Điều\s+(\d+)", art['title'])
        num = match.group(1) if match else "000"
        safe_id = f"dieu_{int(num):03d}"
        filename = f"storage/articles/{safe_id}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(art['content'])

        metadata.append({
            "id": safe_id,
            "title": art['title'],
            "file": filename
        })

    with open("storage/law_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    print(f"Đã tách thành công {len(articles)} điều luật!")

if __name__ == "__main__":
    pdf_path = "data/luat_lao_dong.pdf"
    if not os.path.exists(pdf_path):
        print("Không tìm thấy PDF. Đặt file vào data/luat_lao_dong.pdf")
    else:
        print("Đang đọc PDF...")
        text = extract_text(pdf_path)
        print("Đang tách các điều luật...")
        articles = split_articles(text)
        save_articles(articles)
        print("Hoàn tất!")