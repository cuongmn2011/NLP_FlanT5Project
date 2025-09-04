import os
import torch
import whisper
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import logging
from text_processor import segment_text

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# --- Tải các mô hình AI khi ứng dụng khởi động ---
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Sử dụng thiết bị: {device}")

# Tải mô hình Whisper
try:
    logger.info("Đang tải mô hình Whisper...")
    whisper_model = whisper.load_model("base", device=device)
    logger.info("Tải mô hình Whisper thành công!")
except Exception as e:
    logger.error(f"Lỗi khi tải mô hình Whisper: {e}")
    whisper_model = None

# Tải mô hình Flan-T5 đã fine-tune
MODEL_PATH = "/app/model"
try:
    logger.info(f"Đang tải mô hình T5 từ '{MODEL_PATH}'...")
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Thư mục model không tồn tại.")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    grammar_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(device)
    logger.info("Tải mô hình T5 thành công!")
except Exception as e:
    logger.error(f"Lỗi khi tải mô hình T5: {e}")
    tokenizer = None
    grammar_model = None

# --- Định nghĩa các API endpoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    API này chỉ nhận audio và trả về một khối văn bản duy nhất.
    """
    if not whisper_model:
        return JSONResponse(status_code=500, content={"error": "Mô hình Whisper chưa được tải."})
    
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        logger.info(f"Bắt đầu chuyển đổi file: {file.filename}")
        result = whisper_model.transcribe(temp_path)
        os.remove(temp_path)
        logger.info("Chuyển đổi audio thành công!")
        
        return JSONResponse(content={"text": result.get("text", "")})
    except Exception as e:
        logger.error(f"Lỗi trong quá trình chuyển đổi audio: {e}")
        return JSONResponse(status_code=500, content={"error": "Có lỗi xảy ra khi xử lý file audio."})

@app.post("/analyze")
async def analyze_text(text: str = Form(...)):
    """
    API này nhận một khối văn bản, tách câu, phân tích từng câu và trả về kết quả.
    """
    if not grammar_model or not tokenizer:
        return JSONResponse(status_code=500, content={"error": "Mô hình ngữ pháp chưa được tải."})

    try:
        if not text.strip():
            return JSONResponse(status_code=400, content={"error": "Không có văn bản để phân tích."})
        
        logger.info(f"Bắt đầu phân tích văn bản: '{text[:100]}...'")
        
        # BƯỚC 1: Tách văn bản thành list các câu
        sentences = segment_text(text)
        logger.info(f"Đã tách thành {len(sentences)} câu.")
        
        analysis_results = []
        
        # BƯỚC 2: Lặp qua từng câu và sửa lỗi
        for sentence in sentences:
            if not sentence.strip():
                continue

            inputs = tokenizer(sentence, return_tensors="pt", max_length=128, truncation=True).to(device)
            output_ids = grammar_model.generate(
                **inputs, 
                max_length=128, 
                num_beams=5, 
                early_stopping=True
            )
            corrected_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            
            is_correct = sentence.strip().lower() == corrected_text.strip().lower()

            analysis_results.append({
                "original": sentence,
                "corrected": corrected_text,
                "is_correct": is_correct
            })
            
        logger.info("Phân tích hoàn tất.")
        return JSONResponse(content={"results": analysis_results})
        
    except Exception as e:
        logger.error(f"Lỗi trong quá trình phân tích: {e}")
        return JSONResponse(status_code=500, content={"error": "Có lỗi xảy ra khi phân tích ngữ pháp."})

