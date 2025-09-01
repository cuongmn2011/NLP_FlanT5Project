# **Ứng dụng Sửa lỗi Ngữ pháp Tiếng Anh bằng Giọng nói**

Đây là một dự án web app cho phép người dùng chuyển đổi giọng nói tiếng Anh (qua file audio hoặc ghi âm trực tiếp) thành văn bản, sau đó sử dụng một mô hình AI đã được fine-tune (Flan-T5) để phân tích và sửa các lỗi ngữ pháp trong văn bản đó.

Toàn bộ ứng dụng được đóng gói bằng Docker và hỗ trợ HTTPS thông qua Nginx reverse proxy.

## **✨ Tính năng chính**

* **Chuyển đổi Giọng nói thành Văn bản:** Sử dụng mô hình Whisper của OpenAI để có độ chính xác cao.  
* **Nhiều nguồn Audio:** Hỗ trợ tải lên file audio (.mp3, .wav, .m4a, v.v.) hoặc ghi âm trực tiếp từ trình duyệt.  
* **Chỉnh sửa Linh hoạt:** Cho phép người dùng chỉnh sửa văn bản đã được chuyển đổi trước khi phân tích.  
* **Phân tích Ngữ pháp:** Sử dụng mô hình Flan-T5 đã được fine-tune để sửa lỗi ngữ pháp một cách hiệu quả.  
* **Xuất kết quả:** Cho phép tải kết quả văn bản đã sửa về dưới dạng file .txt.  
* **Bảo mật:** Hỗ trợ kết nối HTTPS để đảm bảo an toàn.  
* **Dễ dàng triển khai:** Toàn bộ ứng dụng được đóng gói trong Docker, có thể chạy chỉ bằng một lệnh.

## **📂 Cấu trúc Dự án**

.  
├── model/              \# CHỨA MODEL T5 ĐÃ FINE-TUNE CỦA BẠN  
│   ├── config.json  
│   ├── model.safetensors  
│   └── tokenizer.json  
│  
├── app/  
│   ├── main.py         \# Backend API (FastAPI)  
│   └── templates/  
│       └── index.html  \# Giao diện người dùng  
│  
├── nginx/  
│   ├── nginx.conf      \# Cấu hình Nginx  
│   └── Dockerfile      \# Dockerfile cho Nginx  
│  
├── certs/              \# CHỨA CHỨNG CHỈ SSL  
│   ├── cert.pem  
│   └── key.pem  
│  
├── .gitignore          \# File bỏ qua các file không cần thiết  
├── Dockerfile          \# Dockerfile cho ứng dụng FastAPI  
├── docker-compose.yml  \# File để điều phối các container  
├── requirements.txt    \# Các thư viện Python cần thiết  
└── README.md           \# File hướng dẫn này

## **🚀 Hướng dẫn Cài đặt và Chạy**

### **Yêu cầu**

* [Docker](https://www.docker.com/products/docker-desktop/)  
* [Docker Compose](https://docs.docker.com/compose/install/) (Thường đi kèm với Docker Desktop)

### **Các bước cài đặt**

**Bước 1: Sao chép (Clone) Dự án**

git clone \<your-repository-url\>  
cd \<your-project-directory\>

**Bước 2: Đặt Model đã Fine-tune vào thư mục model**

Đây là bước quan trọng nhất. Hãy copy toàn bộ các file của mô hình Flan-T5 mà bạn đã huấn luyện trên Colab vào thư mục ./model. Thư mục này phải chứa ít nhất các file sau:

* config.json  
* model.safetensors (hoặc pytorch\_model.bin)  
* tokenizer.json  
* tokenizer\_config.json  
* special\_tokens\_map.json

**Bước 3: Tạo Chứng chỉ SSL cho HTTPS (Để chạy ở local)**

Mở terminal và chạy lệnh sau để tạo một chứng chỉ tự ký (self-signed certificate). Lệnh này sẽ tạo ra hai file cert.pem và key.pem trong thư mục ./certs.

\# Tạo thư mục certs nếu chưa có  
mkdir \-p certs

\# Lệnh tạo chứng chỉ  
openssl req \-x509 \-newkey rsa:4096 \-keyout certs/key.pem \-out certs/cert.pem \\  
  \-sha256 \-days 365 \-nodes \-subj "/C=XX/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"

**Bước 4: Xây dựng (Build) và Chạy Ứng dụng**

Mở terminal ở thư mục gốc của dự án và chạy lệnh sau:

docker-compose up --build

* \--build: Docker sẽ xây dựng lại các images dựa trên Dockerfile nếu có thay đổi.  
* Lần đầu tiên chạy sẽ mất một lúc để tải base images và cài đặt các thư viện.

**Bước 5: Truy cập Ứng dụng**

Sau khi các container đã khởi động xong, hãy mở trình duyệt và truy cập:

[**https://localhost**](https://www.google.com/search?q=https://localhost)

Vì chúng ta dùng chứng chỉ tự ký, trình duyệt sẽ hiển thị cảnh báo bảo mật. Bạn chỉ cần chọn "Advanced" (Nâng cao) \-\> "Proceed to localhost" (Tiếp tục truy cập) để vào trang web.

## **🛠️ Công nghệ sử dụng**

* **Backend:** FastAPI, Uvicorn  
* **Frontend:** HTML, Tailwind CSS, JavaScript  
* **AI Models:** OpenAI Whisper, Fine-tuned Flan-T5  
* **Deployment:** Docker, Docker Compose, Nginx

### **Lệnh tạo cert**
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "//C=XX/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"