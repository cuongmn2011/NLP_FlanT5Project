import os
import torch
import whisper
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import logging

# --- Cấu hình logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- SỬA LỖI Ở ĐÂY ---
# Đường dẫn tìm kiếm template bây giờ là "templates", tương đối so với thư mục làm việc /app
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
        raise FileNotFoundError("Thư mục model không tồn tại. Vui lòng đặt model đã huấn luyện vào đúng vị trí.")
    
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
    """
    API để hiển thị trang chủ.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    API nhận file audio, chuyển đổi thành văn bản bằng Whisper.
    """
    if not whisper_model:
        return JSONResponse(status_code=500, content={"error": "Mô hình Whisper chưa được tải."})
    
    try:
        # Lưu file audio tạm thời
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        logger.info(f"Bắt đầu chuyển đổi file: {file.filename}")
        result = whisper_model.transcribe(temp_path)
        logger.info("Chuyển đổi thành công!")
        
        # Xóa file tạm
        os.remove(temp_path)
        
        return JSONResponse(content={"text": result["text"]})
    except Exception as e:
        logger.error(f"Lỗi trong quá trình chuyển đổi audio: {e}")
        return JSONResponse(status_code=500, content={"error": "Có lỗi xảy ra khi xử lý file audio."})

@app.post("/correct-grammar")
async def correct_grammar(request: Request):
    """
    API nhận văn bản, sửa lỗi ngữ pháp bằng model đã fine-tune.
    """
    if not grammar_model or not tokenizer:
        return JSONResponse(status_code=500, content={"error": "Mô hình sửa lỗi ngữ pháp chưa được tải."})

    try:
        data = await request.json()
        text = data.get("text", "")
        if not text:
            return JSONResponse(status_code=400, content={"error": "Không có văn bản nào để phân tích."})

        logger.info(f"Bắt đầu sửa lỗi cho văn bản: '{text[:50]}...'")
        
        inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True).to(device)
        output_ids = grammar_model.generate(
            **inputs, 
            max_length=128, 
            num_beams=5, 
            early_stopping=True
        )
        corrected_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        logger.info(f"Sửa lỗi thành công. Kết quả: '{corrected_text[:50]}...'")
        
        return JSONResponse(content={"corrected_text": corrected_text})
    except Exception as e:
        logger.error(f"Lỗi trong quá trình sửa ngữ pháp: {e}")
        return JSONResponse(status_code=500, content={"error": "Có lỗi xảy ra khi phân tích ngữ pháp."})

