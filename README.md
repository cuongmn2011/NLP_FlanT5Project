# **Ứng dụng Phân tích Ngữ pháp Tiếng Anh bằng Giọng nói**

Dự án web app này sử dụng AI để chuyển đổi giọng nói tiếng Anh thành văn bản, cho phép người dùng chỉnh sửa, sau đó phân tích và sửa các lỗi ngữ pháp theo từng câu.

Toàn bộ hệ thống được đóng gói bằng Docker, bao gồm một backend FastAPI, frontend HTML/JavaScript, và Nginx làm reverse proxy để hỗ trợ HTTPS.

## **✨ Tính năng chính**

* **Chuyển đổi Giọng nói:** Sử dụng mô hình base của OpenAI Whisper.  
* **Nguồn Audio:** Hỗ trợ tải file audio hoặc ghi âm trực tiếp.  
* **Chỉnh sửa & Phân tích:** Giao diện cho phép chỉnh sửa văn bản trước khi gửi đi phân tích bằng mô hình Flan-T5 đã được fine-tune.  
* **Kết quả Chi tiết:** Hiển thị kết quả phân tích cho từng câu, làm nổi bật các câu sai và đề xuất sửa lỗi.  
* **Bảo mật:** Hỗ trợ kết nối HTTPS.  
* **Dễ dàng triển khai:** Được đóng gói hoàn toàn bằng Docker và Docker Compose.

## **⚙️ Luồng xử lý & Công nghệ**

Dự án hoạt động theo một luồng xử lý gồm 3 giai đoạn chính, kết hợp các mô hình AI khác nhau:

#### **1\. Giai đoạn 1: Chuyển đổi Audio thành Text**

* **Chức năng:** Nhận file âm thanh (ghi âm hoặc tải lên) từ người dùng và chuyển đổi thành một khối văn bản thô.  
* **Model sử dụng:** **OpenAI Whisper (phiên bản base)**.  
* **Logic xử lý:**  
  1. Giao diện người dùng (index.html) gửi file audio đến endpoint /transcribe của backend.  
  2. Backend (main.py) nhận file, lưu tạm thời.  
  3. Mô hình whisper.transcribe() được gọi để xử lý file audio.  
  4. Kết quả là một khối văn bản duy nhất được trả về cho giao diện và hiển thị trong ô textarea.

#### **2\. Giai đoạn 2: Phân tích Văn bản**

* **Chức năng:** Lấy văn bản (đã được người dùng chỉnh sửa nếu có), tách thành các câu riêng biệt, sau đó phân tích ngữ pháp cho từng câu.  
* **Model sử dụng:**  
  * **Tách câu:** **spaCy (model en\_core\_web\_sm)**.  
  * **Sửa lỗi ngữ pháp:** **Flan-T5 (phiên bản small đã được fine-tune)**.  
* **Logic xử lý:**  
  1. Người dùng nhấn nút "Phân tích Văn bản". Giao diện gửi nội dung từ textarea đến endpoint /analyze.  
  2. Backend (main.py) nhận khối văn bản.  
  3. Hàm segment\_text() trong text\_processor.py được gọi. Hàm này sử dụng spaCy để phân tích và áp dụng các quy tắc (dấu câu, liên từ,...) để tách văn bản thành một danh sách (list) các câu.  
  4. Backend lặp qua danh sách câu này. Với **mỗi câu**, nó sử dụng mô hình Flan-T5 đã fine-tune để tạo ra một phiên bản đã sửa lỗi.  
  5. Nó so sánh câu gốc và câu đã sửa để xác định xem câu đó có đúng ngữ pháp hay không (is\_correct).

#### **3\. Giai đoạn 3: Hiển thị Kết quả & Xuất file**

* **Chức năng:** Trình bày kết quả phân tích một cách trực quan và cho phép người dùng xuất ra file.  
* **Logic xử lý:**  
  1. Backend trả về một danh sách các kết quả, mỗi phần tử chứa: original (câu gốc), corrected (câu đã sửa), và is\_correct (đúng/sai).  
  2. Giao diện (index.html) dùng JavaScript để lặp qua danh sách này và tự động tạo ra các dòng kết quả, đánh dấu màu xanh cho câu đúng và màu cam/đỏ cho câu sai kèm đề xuất.  
  3. Khi người dùng nhấn "Xuất file", JavaScript sẽ tập hợp tất cả các câu **đã được sửa** lại, ghép chúng thành một đoạn văn hoàn chỉnh và cho phép tải về dưới dạng file .txt.

## **📂 Cấu trúc Dự án (Sau khi cài đặt)**

.  
├── model/              \# (Sẽ được tạo) Chứa model T5 đã tải về  
├── app/  
│   ├── main.py  
│   ├── text\_processor.py  
│   └── templates/  
│       └── index.html  
├── nginx/  
│   ├── nginx.conf  
│   └── Dockerfile  
├── certs/              \# (Sẽ được tạo) Chứa chứng chỉ SSL  
├── .gitignore  
├── Dockerfile  
├── docker-compose.yml  
├── requirements.txt  
└── README.md

## **🚀 Hướng dẫn Cài đặt & Chạy từ GitHub**

Đây là các bước để thiết lập dự án từ đầu trên một máy mới (local hoặc VM trên cloud).

### **Yêu cầu**

* [Git](https://git-scm.com/downloads)  
* [Docker](https://www.docker.com/products/docker-desktop/)  
* [Docker Compose](https://docs.docker.com/compose/install/) (Thường đi kèm với Docker Desktop)

### **Bước 1: Lấy mã nguồn**

Mở terminal của bạn và clone repository từ GitHub:

git clone https://github.com/cuongmn2011/NLP_FlanT5Project.git
cd \<tên\_thư\_mục\_dự\_án\>

### **Bước 2: Tải Model đã Fine-tune**

Mô hình AI không được lưu trữ trên GitHub. Bạn cần tải nó về từ Google Drive và đặt vào đúng vị trí.

1. **Tạo thư mục model:**  
   mkdir model

2. **Tải model:**  
   * Truy cập vào link Google Drive sau để tải file chứa model: https://drive.google.com/drive/folders/1SORTpqFCoslXttbho3Pb5zQKA4QTrmaL?usp=sharing
   * Giải nén file zip đó và **copy toàn bộ nội dung** (bao gồm các file như config.json, model.safetensors, tokenizer.json,...) vào thư mục model bạn vừa tạo.

### **Bước 3: Tạo Chứng chỉ SSL (Cho HTTPS)**

Lệnh này sẽ tạo ra hai file cert.pem và key.pem trong một thư mục mới tên là certs.

* **Trên Linux/macOS hoặc Git Bash trên Windows:**  
  \# Tạo thư mục  
  mkdir certs

  \# Chạy lệnh tạo cert (dùng // ở đầu cho Git Bash)  
  openssl req \-x509 \-newkey rsa:4096 \-keyout certs/key.pem \-out certs/cert.pem \\  
    \-days 365 \-nodes \-subj "//C=VN/ST=HCMC/L=HCMC/O=MyProject/OU=Dev/CN=localhost"

### **Bước 4: Xây dựng và Chạy Ứng dụng**

Bây giờ, bạn chỉ cần chạy một lệnh duy nhất. Docker sẽ lo phần còn lại.

docker-compose up \--build

* \--build: Bắt buộc ở lần chạy đầu tiên để xây dựng các Docker image.  
* Quá trình này sẽ mất một lúc để tải các image nền và cài đặt thư viện.

### **Bước 5: Truy cập Ứng dụng**

Sau khi các container đã khởi động xong, mở trình duyệt và truy cập:

[**https://localhost**](https://www.google.com/search?q=https://localhost)

Trình duyệt sẽ hiển thị cảnh báo bảo mật. Bạn chỉ cần chọn **"Advanced" (Nâng cao)** → **"Proceed to localhost" (Tiếp tục truy cập)** để vào trang web.

## **🛠️ Lệnh Docker hữu ích**

* **Chạy ở chế độ nền (detached):**  
  docker-compose up \--build \-d

* **Xem log theo thời gian thực:**  
  docker-compose logs \-f

* **Dừng ứng dụng:**  
  docker-compose down  
