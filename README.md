# ptud-gk-de-02

## Thông tin cá nhân
- **Họ tên:** Phan Lâm Hùng
- **Mã sinh viên:** 22661791

## Mô tả dự án
Đây là một ứng dụng web đơn giản được xây dựng bằng Flask, cung cấp các chức năng chính như sau:

- **Quản lý tài khoản người dùng:**
  - Bắt buộc đăng kí tài khoản khi vào web click vào Task chuyển đến đăng nhập.
  - Cho phép người dùng đăng ký, đăng nhập và upload avatar.
  
- **Quản lý công việc (Task):**  
  - Người dùng có thể tạo công việc với các thông tin: tiêu đề, nội dung, trạng thái, thời gian tạo, ngày hoàn thành dự kiến, thời gian hoàn thành thực tế và mức độ ưu tiên.  
  - Cho phép đánh dấu công việc là "hoàn thành" bằng nút "Đánh dấu hoàn thành".  
  - Hỗ trợ xóa công việc đơn lẻ hoặc xóa hàng loạt theo yêu cầu.

- **Quản lý phân loại công việc (Category):**  
  - Người dùng có thể thêm, sửa và xoá danh mục phân loại công việc để dễ dàng sắp xếp và theo dõi các công việc.
  
- **Chức năng quản trị (Admin):**  
  - Admin có thể quản lý người dùng (khóa tài khoản, reset mật khẩu) và quản lý các công việc từ giao diện riêng, xem các task của User.

## Hướng dẫn cài đặt và chạy
1. **Clone repository:**
   ```bash
   git clone https://github.com/ben2xx4/ptud-gk-de-2.git
   cd fask-tiny-app
   ```

2. **Tạo và kích hoạt virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Trên Linux/MacOS
   # hoặc trên Windows:
   venv\Scripts\activate
   ```

3. **Cài đặt các thư viện cần thiết:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Khởi tạo cơ sở dữ liệu và chạy migrations (nếu sử dụng Flask-Migrate),(trong source đã có sẳn database, có thể bỏ qua bước này):**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Chạy ứng dụng:**
   ```bash
   python app.py
   ```

6. **Truy cập ứng dụng:**
   Mở trình duyệt và truy cập địa chỉ: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Ghi chú
- Yêu cầu: Python 3.6+  
- Thư mục **static/avatars** dùng để lưu trữ ảnh đại diện người dùng.  
- Ứng dụng đã được triển khai các chức năng quản lý công việc, phân loại công việc và các chức năng quản trị người dùng.

---
