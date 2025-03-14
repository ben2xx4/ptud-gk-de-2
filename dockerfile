# Sử dụng Python 3.9 (hoặc 3.x)
FROM python:3.9-slim

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép file requirements
COPY requirements.txt /app

# Cài đặt các thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn
COPY . /app

# Mở cổng 5000
EXPOSE 5000

# Khởi chạy ứng dụng
CMD ["python", "app.py"]

#để database được đồng bộ từ docker: run bash : docker run -p 5000:5000 -v $(pwd)/data:/app my-flask-app

