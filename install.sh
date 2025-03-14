#!/bin/bash
# Sử dụng:
#   chmod +x install.sh
#   ./install.sh
# Kiểm tra xem python3 đã được cài đặt chưa
if ! command -v python3 &> /dev/null; then
    echo "Python3 không được cài đặt. Vui lòng cài đặt Python3."
    exit 1
fi

# Tạo virtual environment nếu chưa tồn tại
if [ ! -d "venv" ]; then
    echo "Tạo virtual environment..."
    python3 -m venv venv
fi

# Kích hoạt virtual environment
echo "Kích hoạt virtual environment..."
source venv/bin/activate

# Nâng cấp pip và cài đặt các gói cần thiết
echo "Cài đặt các gói cần thiết từ requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Khởi tạo cơ sở dữ liệu
echo "Khởi tạo cơ sở dữ liệu..."
python -c "from app import db, app; app.app_context().push(); db.create_all()"

echo "Cài đặt hoàn tất. Đang chạy server..."
# Chạy server
python app.py

#kiem tra database co chua
ls -lh app.db
#chua co thi tao

python -c "from app import db, app; app.app_context().push(); db.create_all()"

#check database tren bash
sqlite3 app.db
.tables   -- Xem danh sách bảng
.schema users;   -- Xem cấu trúc bảng "users"
SELECT * FROM User;   -- Xem dữ liệu trong bảng "users"
SELECT * FROM Post;
