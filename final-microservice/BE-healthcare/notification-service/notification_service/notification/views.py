import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import re

# Config SMTP
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465  # SSL
SMTP_USERNAME = 'dotienthanh28062002@gmail.com'
SMTP_PASSWORD = 'nopodxdrhmwlahcm'

@api_view(['POST'])
def send_email(request):
    """
    API nhận dữ liệu và gửi email bằng smtplib (HTML body)
    """
    if request.method == 'POST':
        subject = 'Thông báo đặt lịch thành công'
        doctor_name = request.data.get('doctor_name')
        date = request.data.get('date')
        room = request.data.get('room_name')
        time = request.data.get('time')
        patient_name = request.data.get('patient_name')
        recipient_email = request.data.get('recipient_email')

        # Check thiếu dữ liệu
        if not all([doctor_name, date, room, time, patient_name, recipient_email]):
            return Response({
                "error": "Dữ liệu không hợp lệ hoặc thiếu thông tin",
                "errCode": 1
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, recipient_email):
            return Response({
                "error": "Email không hợp lệ",
                "errCode": 2
            }, status=status.HTTP_400_BAD_REQUEST)

        # Tạo body HTML
        body_html = f"""
        <html>
        <body>
            <div>
                <h1>Thông báo đặt lịch khám thành công!</h1>
                <p><strong>Xin chào {patient_name}!</strong></p>
                <p>Thông tin lịch hẹn:</p>
                <p><strong>Bác sĩ:</strong> {doctor_name}</p>
                <p><strong>Thời gian:</strong> {date} - {time}</p>
                <p><strong>Phòng:</strong> {room}</p>
                <p>Vui lòng đến đúng giờ.</p>
            </div>
        </body>
        </html>
        """

        # Tạo email MIME
        message = MIMEMultipart("alternative")
        message["Subject"] = f"{subject} - {patient_name}"
        message["From"] = SMTP_USERNAME
        message["To"] = recipient_email

        mime_text = MIMEText(body_html, "html")
        message.attach(mime_text)

        try:
            # Gửi email
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_USERNAME, recipient_email, message.as_string())

            return Response({
                "message": "Email đã được gửi thành công!",
                "errCode": 0
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Lỗi khi gửi email: {e}")
            return Response({
                "error": "Có lỗi khi gửi email. Vui lòng thử lại sau.",
                "errCode": 3
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
