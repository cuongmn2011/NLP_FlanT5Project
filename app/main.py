import os
import torch
import whisper
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import tempfile

# --- 1. KHỞI TẠO CÁC BIẾN TOÀN CỤC VÀ TẢI MODEL ---

# Xác định thiết bị (GPU nếu có, không thì CPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

# Đường dẫn tới model đã fine-tune (bên trong container)
MODEL_PATH = "/app/model"

# Khởi tạo FastAPI app và templates
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Tải model và tokenizer một lần duy nhất khi ứng dụng khởi động
try:
    print("Loading Whisper model...")
    # Chọn model 'base' để cân bằng giữa tốc độ và độ chính xác
    whisper_model = whisper.load_model("base", device=DEVICE)
    print("Whisper model loaded.")

    print(f"Loading fine-tuned grammar model from {MODEL_PATH}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    grammar_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(DEVICE)
    print("Fine-tuned grammar model loaded.")

except Exception as e:
    print(f"Error loading models: {e}")
    whisper_model = None
    tokenizer = None
    grammar_model = None

# --- 2. ĐỊNH NGHĨA CÁC API ENDPOINTS ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render trang chủ."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """Nhận file audio, chuyển thành text bằng Whisper."""
    if not whisper_model:
        return JSONResponse(content={"error": "Whisper model is not loaded."}, status_code=500)

    try:
        # Whisper cần đường dẫn file, không phải bytes, nên ta tạo file tạm
        with tempfile.NamedTemporaryFile(delete=True, suffix=".tmp") as tmp:
            tmp.write(await audio_file.read())
            tmp.flush()
            
            # Thực hiện transcribe
            result = whisper_model.transcribe(tmp.name, fp16=torch.cuda.is_available())
            return JSONResponse(content={"transcription": result['text']})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/correct_grammar")
async def correct_grammar_endpoint(request: Request):
    """Nhận text, sửa lỗi ngữ pháp bằng model đã fine-tune."""
    if not tokenizer or not grammar_model:
        return JSONResponse(content={"error": "Grammar model is not loaded."}, status_code=500)

    try:
        data = await request.json()
        text_to_correct = data.get("text", "")

        if not text_to_correct:
            return JSONResponse(content={"corrected_text": ""})

        # Tokenize và đưa qua model
        inputs = tokenizer(text_to_correct, return_tensors="pt").to(DEVICE)
        outputs = grammar_model.generate(
            **inputs, 
            max_length=256, 
            num_beams=5, # Sử dụng beam search để kết quả tốt hơn
            early_stopping=True
        )
        
        # Decode kết quả
        corrected_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return JSONResponse(content={"corrected_text": corrected_text})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

