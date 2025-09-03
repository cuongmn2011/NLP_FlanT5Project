# Sử dụng base image Python 3.10 phiên bản slim để tối ưu dung lượng
FROM python:3.10-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Cập nhật danh sách package và cài đặt ffmpeg mà không cần hỏi
RUN apt-get update && apt-get install -y ffmpeg

# Sao chép file requirements.txt vào trước
# Docker sẽ cache bước này, giúp build nhanh hơn nếu requirements không thay đổi
COPY requirements.txt .

# Cài đặt các thư viện Python cần thiết
# --no-cache-dir để không lưu cache, giúp giảm kích thước image
RUN pip install --no-cache-dir -r requirements.txt

# Tải model ngôn ngữ nhỏ gọn của spaCy cho tiếng Anh
RUN python -m spacy download en_core_web_sm

# Sao chép toàn bộ thư mục 'app' (chứa main.py và templates) vào container
COPY ./app /app

# Mở cổng 8000 để ứng dụng có thể nhận request
EXPOSE 8000

# Lệnh để chạy ứng dụng khi container khởi động
# Uvicorn sẽ chạy server FastAPI, lắng nghe trên tất cả các địa chỉ IP (host 0.0.0.0) ở port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

