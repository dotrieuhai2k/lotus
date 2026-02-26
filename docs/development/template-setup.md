# Hướng dẫn thiết lập môi trường (Dev Setup)

## 1. Yêu cầu (Prerequisites)
* Docker & Docker Compose
* Python 3.10+
* Node.js 18+

## 2. Cài đặt (Installation)

Clone repository và cài đặt thư viện:

```bash
git clone https://github.com/your-org/lotus.git
cd lotus
pip install -r requirements.txt
```

## 3. Chạy ứng dụng (Running)

Khởi động server ở chế độ development:

```bash
docker-compose up -d
python manage.py runserver
```

Truy cập Web tại: `http://localhost:8000`