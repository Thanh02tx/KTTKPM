
import os
import time
import uuid
import logging
import base64
import mimetypes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import PaymentMethod,Bill
from .serializers import PaymentMethodSerializer,BillSerializer
import requests
import cloudinary.uploader
URL_USER_SV ="http://localhost:8001"
URL_APPT_SV ="http://localhost:8002"
URL_LAB_SV ="http://localhost:8003"
IMAGE_BILL=r"D:\final-microservice\image\bill"
@api_view(['GET'])
def get_active_payment_methods(request):
    methods = PaymentMethod.objects.filter(is_active=True)
    serializer = PaymentMethodSerializer(methods, many=True)
    
    return Response({
        "errCode": 0,
        "message": "Lấy phương thức thanh toán thành công",
        "data": serializer.data
    }, status=status.HTTP_200_OK)
    
# @api_view(['POST'])
# def create_bill(request):
#     token = request.headers.get('Authorization')

#     if not token:
#         return Response({
#             "errCode": 1,
#             "message": "Không tìm thấy token trong header",
#             "data": []
#         }, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         # Gọi sang User Service để kiểm tra vai trò cashier
#         response = requests.get(
#             f"{URL_USER_SV}/api/u/check-role-cashier",
#             headers={'Authorization': token}
#         )
#     except requests.exceptions.RequestException as e:
#         return Response({
#             "errCode": 1,
#             "message": f"Lỗi khi gọi User Service: {str(e)}",
#             "data": []
#         }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

#     if response.status_code != 200:
#         return Response({
#             "errCode": 1,
#             "message": "Không xác thực được vai trò cashier (User Service lỗi)",
#             "data": []
#         }, status=status.HTTP_403_FORBIDDEN)

#     response_data = response.json()

#     if response_data.get('errCode') != 0:
#         return Response({
#             "errCode": 1,
#             "message": "Bạn không có quyền truy cập với vai trò cashier",
#             "data": []
#         }, status=status.HTTP_403_FORBIDDEN)

#     cashier_id = response_data.get('user_id')

#     # Dữ liệu hóa đơn
#     data = request.data
#     medical_id = data.get('medical_id')  # <-- YÊU CẦU phải có medical_id

#     if not medical_id:
#         return Response({
#             "errCode": 1,
#             "message": "Thiếu mã hồ sơ khám (medical_id)",
#             "data": []
#         }, status=status.HTTP_400_BAD_REQUEST)

#     data['cashier_id'] = cashier_id

#     # Kiểm tra và lưu ảnh nếu có
#     image_base64 = data.get("image")
#     if not image_base64 or image_base64.strip() == "":
#         return Response({
#             "errCode": 10,
#             "message": "Ảnh không hợp lệ hoặc không có ảnh"
#         }, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         if "base64," in image_base64:
#             format_info, imgstr = image_base64.split(";base64,")
#             mime_type = format_info.split(":")[-1].lower()  # ví dụ: image/png
#             ext = mimetypes.guess_extension(mime_type) or '.jpg'
#             ext = ext.lstrip('.')  # bỏ dấu chấm
#         else:
#             imgstr = image_base64
#             ext = "jpg"  # fallback

#         if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
#             return Response({
#                 "errCode": 11,
#                 "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
#             }, status=status.HTTP_400_BAD_REQUEST)

#         timestamp = int(time.time())
#         unique_id = uuid.uuid4().hex[:8]
#         file_name = f"{timestamp}-{unique_id}.{ext}"

#         os.makedirs(IMAGE_BILL, exist_ok=True)
#         image_path = os.path.join(IMAGE_BILL, file_name)
#         with open(image_path, "wb") as f:
#             f.write(base64.b64decode(imgstr))

#         data["image"] = file_name  # Lưu tên file ảnh vào dữ liệu để lưu vào hóa đơn

#     except Exception as e:
#         return Response({
#             "errCode": 12,
#             "message": f"Lỗi khi xử lý ảnh: {str(e)}"
#         }, status=status.HTTP_400_BAD_REQUEST)

#     # Tiến hành lưu hóa đơn
#     serializer = BillSerializer(data=data)
#     if serializer.is_valid():
#         bill = serializer.save()

#         # Gọi LAB_SV để cập nhật trạng thái các test request
#         lab_res = requests.put(
#             f"{URL_LAB_SV}/api/l/mark-test-requests-paid",
#             json={'id': medical_id}
#         )

#         # Gọi APPOINTMENT_SV để cập nhật trạng thái thanh toán của cuộc hẹn
#         appt_res = requests.put(
#             f"{URL_APPT_SV}/api/a/mark-appointment-paid",
#             json={'id': medical_id}
#         )

#         return Response({
#             "errCode": 0,
#             "message": "Tạo hóa đơn thành công và đã cập nhật trạng thái liên quan",
#         }, status=status.HTTP_201_CREATED)
#     else:
#         return Response({
#             "errCode": 1,
#             "message": "Dữ liệu không hợp lệ",
#         }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@transaction.atomic
def create_bill(request):
    token = request.headers.get('Authorization')

    if not token:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy token trong header",
            "data": []
        }, status=status.HTTP_400_BAD_REQUEST)

    # Gọi User Service kiểm tra vai trò
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-cashier",
            headers={'Authorization': token}
        )
    except requests.exceptions.RequestException as e:
        return Response({
            "errCode": 1,
            "message": f"Lỗi khi gọi User Service: {str(e)}",
            "data": []
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if response.status_code != 200:
        return Response({
            "errCode": 1,
            "message": "Không xác thực được vai trò cashier (User Service lỗi)",
            "data": []
        }, status=status.HTTP_403_FORBIDDEN)

    response_data = response.json()
    if response_data.get('errCode') != 0:
        return Response({
            "errCode": 1,
            "message": "Bạn không có quyền truy cập với vai trò cashier",
            "data": []
        }, status=status.HTTP_403_FORBIDDEN)

    cashier_id = response_data.get('user_id')

    # Lấy dữ liệu hóa đơn
    data = request.data
    medical_id = data.get('medical_id')

    if not medical_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu mã hồ sơ khám (medical_id)",
            "data": []
        }, status=status.HTTP_400_BAD_REQUEST)

    data['cashier_id'] = cashier_id

    # Xử lý ảnh base64
    image_base64 = data.get("image")
    if not image_base64 or image_base64.strip() == "":
        return Response({
            "errCode": 10,
            "message": "Ảnh không hợp lệ hoặc không có ảnh"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        upload_response = cloudinary.uploader.upload(
            image_base64,
            folder="bills",  # tên folder trong Cloudinary
            public_id=f"{int(time.time())}-{uuid.uuid4().hex[:8]}",
            resource_type="image"
        )
        data["image"] = upload_response.get("secure_url")

    except Exception as e:
        return Response({
            "errCode": 12,
            "message": f"Lỗi khi upload ảnh lên Cloudinary: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Lưu hóa đơn vào DB
    serializer = BillSerializer(data=data)
    if serializer.is_valid():
        bill = serializer.save()

        # Gọi sang LAB Service để cập nhật trạng thái
        try:
            requests.put(
                f"{URL_LAB_SV}/api/l/mark-test-requests-paid",
                json={'id': medical_id}
            )
        except Exception:
            pass  # Có thể log lại nếu muốn

        # Gọi Appointment Service để cập nhật trạng thái thanh toán
        try:
            requests.put(
                f"{URL_APPT_SV}/api/a/mark-appointment-paid",
                json={'id': medical_id}
            )
        except Exception:
            pass

        return Response({
            "errCode": 0,
            "message": "Tạo hóa đơn thành công và đã cập nhật trạng thái liên quan"
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            "errCode": 1,
            "message": "Dữ liệu không hợp lệ",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
