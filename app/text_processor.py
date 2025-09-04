import spacy

# Tải model ngôn ngữ tiếng Anh của spaCy.
# Lệnh download sẽ được thực hiện trong Dockerfile.
nlp = spacy.load("en_core_web_sm")

# FANBOYS conjunctions
COORDINATING_CONJUNCTIONS = {"for", "and", "nor", "but", "or", "yet", "so"}

def segment_text(text: str) -> list[str]:
    """
    Tách một đoạn văn bản dài thành các câu ngắn hơn dựa trên bộ quy tắc.
    """
    # Xử lý văn bản bằng spaCy để có được các thông tin ngữ pháp
    doc = nlp(text)
    
    segments = []
    current_segment = []

    for token in doc:
        # Nối token hiện tại vào câu đang xử lý
        current_segment.append(token.text_with_ws)

        # --- Áp dụng các quy tắc tách câu ---

        # Quy tắc 1 & 2: Tách câu dựa trên dấu câu và liên từ FANBOYS
        # Tách nếu là dấu chấm câu cuối cùng, hoặc là dấu phẩy theo sau bởi một liên từ
        # và từ tiếp theo là chủ ngữ của một mệnh đề mới.
        is_punct_split = token.text in [".", ";", ":", "?"]
        is_fanboy_split = (
            token.text == "," and
            token.i + 1 < len(doc) and
            doc[token.i + 1].lower_ in COORDINATING_CONJUNCTIONS and
            token.i + 2 < len(doc) and
            doc[token.i + 2].dep_ in ("nsubj", "nsubjpass") # nsubj: nominal subject
        )

        if is_punct_split or is_fanboy_split:
            segments.append("".join(current_segment).strip())
            current_segment = []
        
        # Quy tắc 4: Tách nếu câu quá dài (ví dụ: > 20 từ)
        # và token hiện tại là một dấu phẩy hoặc một liên từ phụ thuộc (subordinating conjunction)
        elif len("".join(current_segment).split()) > 20 and (token.text == "," or token.dep_ == "mark"):
            segments.append("".join(current_segment).strip())
            current_segment = []

    # Thêm phần câu còn lại nếu có
    if current_segment:
        segments.append("".join(current_segment).strip())

    # Lọc ra các câu rỗng có thể được tạo ra do dấu câu liên tiếp
    final_sentences = [s for s in segments if s]
    
    return final_sentences

