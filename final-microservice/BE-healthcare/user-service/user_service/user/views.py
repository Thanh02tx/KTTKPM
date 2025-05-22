# 🔹 Python Standard Library
import os
import time
import uuid
import logging
import base64
import mimetypes
import re
import  cloudinary.uploader
from urllib.parse import urlparse
# 🔹 Third-party Libraries
import jwt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated
# 🔹 Django Imports
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.http import JsonResponse
from django.forms.models import model_to_dict
# 🔹 Local App Imports
from .models import User, Doctor, BaseProfile,Nurse,Technician,Pharmacist,Cashier,Patient
from .serializers import DoctorSerializer,NurseSerializer,TechnicianSerializer,PharmacistSerializer,CashierSerializer,PatientSerializer
logger = logging.getLogger(__name__)
IMAGE_DOCTOR = r"D:\final-microservice\image\doctor"
IMAGE_NURSE = r"D:\final-microservice\image\nurse"
IMAGE_TECH = r"D:\final-microservice\image\technician"
IMAGE_PHARMA = r"D:\final-microservice\image\pharmacist"
IMAGE_CASHIER = r"D:\final-microservice\image\cashier"
IMAGE_PATIENT = r"D:\final-microservice\image\patient"
@api_view(['GET'])
@permission_classes([AllowAny])
def get_gender_choices(request):
    try:
        gender_choices = [{'value': key, 'label': label} for key, label in BaseProfile.GENDER_CHOICES]
        # Trả về dữ liệu với errCode = 0 (thành công)
        return Response({
            'errCode': 0,
            'errMessage': 'Success',
            'data': gender_choices
        })
    except Exception as e:
        # Trả về lỗi với errCode = 1 và thông báo lỗi
        return Response({
            'errCode': 1,
            'errMessage': str(e),
            'data': []
        })



# Đăng ký tài khoản mới

@api_view(['POST'])
@permission_classes([AllowAny])
def register_patient(request):
    # Kiểm tra nếu request body có chứa 'email' và 'password'
    email = request.data.get('email')
    password = request.data.get('password')

    # Kiểm tra xem email đã tồn tại trong cơ sở dữ liệu hay chưa
    if get_user_model().objects.filter(email=email).exists():
        return Response({'errCode': 1, 'message': 'Email đã tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

    # Nếu email chưa tồn tại, tạo tài khoản mới với role mặc định là 'patient'
    user = get_user_model().objects.create_user(email=email, password=password, role='patient')

    # Trả về thông tin người dùng đã đăng ký thành công
    return Response({
        'errCode': 0,
        'message': 'Đăng ký thành công',
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_email_from_token(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'errCode': 1, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    try:
        # Giải mã token
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get('user_id')

        if not user_id:
            return Response({'errCode': 2, 'message': 'Token không chứa user_id'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        user = User.objects.filter(id=user_id).first()

        if not user:
            return Response({'errCode': 3, 'message': 'Người dùng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

        email = user.email
        return Response({'errCode': 0, 'message': 'Lấy email thành công', 'data': {'email': email}}, status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return Response({'errCode': 4, 'message': 'Token đã hết hạn'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({'errCode': 5, 'message': 'Token không hợp lệ'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'errCode': 6, 'message': 'Lỗi hệ thống', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, email=email, password=password)
    if user is not None:
        token = AccessToken.for_user(user)
        # ✅ Thêm email vào payload
        token['email'] = user.email

        return Response({
            "errCode": 0,
            "message": "Đăng nhập thành công.",
            "data": {
                "token": str(token),
                "email": user.email,
                "role":user.role
            }
        }, status=status.HTTP_200_OK)

    return Response({
        "errCode": 2,
        "message": "Thông tin đăng nhập không chính xác.",
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def check_admin_role(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'errCode': 1, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    try:
        # Giải mã token
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decoded.get('user_id')  # Lấy id từ payload token

        if not user_id:
            return Response({'errCode': 1, 'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=user_id).first()

        if not user:
            return Response({'errCode': 1, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.role == 'admin':
            return Response({'errCode': 0, 'message': 'User is admin'}, status=status.HTTP_200_OK)
        else:
            return Response({'errCode': 1, 'message': 'User is not admin'}, status=status.HTTP_403_FORBIDDEN)

    except jwt.ExpiredSignatureError:
        return Response({'errCode': 1, 'message': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({'errCode': 1, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def check_nurse_role(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'errCode': 1, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    try:
        # Giải mã token
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decoded.get('user_id')  # Lấy user_id từ payload token

        if not user_id:
            return Response({'errCode': 1, 'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=user_id).first()

        if not user:
            return Response({'errCode': 1, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.role == 'nurse':
            return Response({
                'errCode': 0,
                'message': 'User is nurse',
                'user_id': user_id  # Trả về user_id sau khi giải mã
            }, status=status.HTTP_200_OK)
        else:
            return Response({'errCode': 1, 'message': 'User is not nurse'}, status=status.HTTP_403_FORBIDDEN)

    except jwt.ExpiredSignatureError:
        return Response({'errCode': 1, 'message': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({'errCode': 1, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_cashier_role(request):
    try:
        user = request.user  # Người dùng đã xác thực từ request

        if user.role != 'cashier':  # Kiểm tra vai trò người dùng
            return JsonResponse({
                'errCode': 1,
                'message': 'User is not cashier'
            }, status=status.HTTP_403_FORBIDDEN)

        # Nếu người dùng có vai trò là cashier
        return JsonResponse({
            'errCode': 0,
            'message': 'User is cashier',
            'user_id': user.id  # Trả về user_id
        })

    except Exception as e:
        return JsonResponse({
            'errCode': 2,
            'message': 'Lỗi hệ thống',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_technician_role(request):
    try:
        user = request.user  # Người dùng đã xác thực từ request

        if user.role != 'technician':  # Kiểm tra vai trò người dùng
            return JsonResponse({
                'errCode': 1,
                'message': 'User is not cashier'
            }, status=status.HTTP_403_FORBIDDEN)

        # Nếu người dùng có vai trò là technician
        return JsonResponse({
            'errCode': 0,
            'message': 'User is technician',
            'user_id': user.id  # Trả về user_id
        })

    except Exception as e:
        return JsonResponse({
            'errCode': 2,
            'message': 'Lỗi hệ thống',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_pharmacist_role(request):
    try:
        user = request.user  # Người dùng đã xác thực từ request

        if user.role != 'pharmacist':  # Kiểm tra vai trò người dùng
            return JsonResponse({
                'errCode': 1,
                'message': 'User is not pharmacist'
            }, status=status.HTTP_403_FORBIDDEN)

        # Nếu người dùng có vai trò là pharmacist
        return JsonResponse({
            'errCode': 0,
            'message': 'User is pharmacist',
            'user_id': user.id  # Trả về user_id
        })

    except Exception as e:
        return JsonResponse({
            'errCode': 2,
            'message': 'Lỗi hệ thống',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

@api_view(['GET'])
def check_doctor_role(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({'errCode': 1, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    try:
        # Giải mã token
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = decoded.get('user_id')  # Lấy user_id từ payload token

        if not user_id:
            return Response({'errCode': 1, 'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=user_id).first()

        if not user:
            return Response({'errCode': 1, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.role == 'doctor':
            return Response({
                'errCode': 0,
                'message': 'User is doctor',
                'user_id': user_id  # Trả về user_id sau khi giải mã
            }, status=status.HTTP_200_OK)
        else:
            return Response({'errCode': 1, 'message': 'User is not nurse'}, status=status.HTTP_403_FORBIDDEN)

    except jwt.ExpiredSignatureError:
        return Response({'errCode': 1, 'message': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({'errCode': 1, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_doctor(request):
    try:
        user = request.user
        if user.role != 'admin':
            return Response({
                "errCode": 4,
                "message": "Bạn không có quyền tạo bác sĩ"
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        User = get_user_model()

        # 📌 Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=data.get("email")).exists():
            return Response({
                "errCode": 9,
                "message": "Email đã được sử dụng"
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Xử lý ảnh base64 upload lên Cloudinary
        image_base64 = data.get("image")
        if not image_base64 or image_base64.strip() == "":
            return Response({
                "errCode": 10,
                "message": "Ảnh không hợp lệ hoặc không có ảnh"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if "base64," in image_base64:
                format_info, imgstr = image_base64.split(";base64,")
                mime_type = format_info.split(":")[-1].lower()
                ext = mimetypes.guess_extension(mime_type) or '.jpg'
                ext = ext.lstrip('.')
            else:
                imgstr = image_base64
                ext = "jpg"

            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                return Response({
                    "errCode": 11,
                    "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                }, status=status.HTTP_400_BAD_REQUEST)

            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:16]
            cloud_name = f"doctor_{timestamp}_{unique_id}"

            upload_result = cloudinary.uploader.upload(
                base64.b64decode(imgstr),
                public_id=cloud_name,
                folder="doctors"
            )

            image_url = upload_result.get("secure_url")
            if image_url:
                data["image"] = image_url
            else:
                return Response({
                    "errCode": 13,
                    "message": "Không lấy được URL ảnh từ Cloudinary"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Tạo user mới cho bác sĩ
        new_user = User.objects.create_user(
            email=data.get("email"),
            password=data.get("password"),
            role="doctor"
        )
        data["user"] = new_user.id

        # ✅ Tạo bác sĩ
        serializer = DoctorSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Tạo bác sĩ thành công",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        # ⚠️ Nếu lỗi thì rollback user đã tạo
        new_user.delete()
        return Response({
            "errCode": 1,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_doctor_with_user_status(request):
    try:
        doctors = Doctor.objects.select_related('user').all()
        
        doctor_list = []
        for doc in doctors:
            doctor_list.append({
                "id": doc.id,
                "name": doc.name,
                "date_of_birth": doc.date_of_birth,
                "user_id": doc.user.id,
                "degree": doc.degree,
                "user": {
                    "is_active": doc.user.is_active
                }
            })

        return Response({
            "errCode": 0,
            "message": "Lấy danh sách bác sĩ thành công",
            "method": request.method,
            "data": doctor_list
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": []
        }, status=500)



@api_view(['PUT'])
@transaction.atomic
def change_active_user(request):
    try:
        # 📌 Lấy token từ header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"errCode": 3, "message": "Thiếu hoặc sai định dạng token"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]

        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded.get('user_id')
            if not user_id:
                return Response({"errCode": 7, "message": "Token không chứa user_id"}, status=status.HTTP_401_UNAUTHORIZED)

            User = get_user_model()
            admin_user = User.objects.get(id=user_id)

            if admin_user.role != 'admin':
                return Response({"errCode": 4, "message": "Bạn không có quyền thay đổi trạng thái người dùng"}, status=status.HTTP_403_FORBIDDEN)

        except jwt.ExpiredSignatureError:
            return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"errCode": 8, "message": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        # 📌 Xử lý thay đổi trạng thái người dùng
        target_id = request.data.get('id')
        if not target_id:
            return Response({"errCode": 9, "message": "Thiếu ID người dùng cần thay đổi"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_user = User.objects.get(id=target_id)
            target_user.is_active = not target_user.is_active
            target_user.save()

            return Response({
                "errCode": 0,
                "message": f"Trạng thái hoạt động đã được cập nhật thành {'hoạt động' if target_user.is_active else 'không hoạt động'}"
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"errCode": 10, "message": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Lỗi sửa trạng thái: {e}")
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_doctor(request):
#     try:
#         doctor_id = request.GET.get('id')
#         if not doctor_id:
#             return Response({
#                 "errCode": 3,
#                 "message": "Thiếu ID bác sĩ"
#             }, status=400)

#         doctor = Doctor.objects.get(id=doctor_id)

#         data = model_to_dict(doctor)

#         # Đọc ảnh và chuyển sang base64 định dạng chuẩn
#         data['image_name']=doctor.image
#         image_base64 = ""
#         if doctor.image:
#             image_path = os.path.join(IMAGE_DOCTOR, doctor.image)
#             if os.path.exists(image_path):
#                 mime_type, _ = mimetypes.guess_type(image_path)
#                 if mime_type:
#                     with open(image_path, 'rb') as img_file:
#                         encoded = base64.b64encode(img_file.read()).decode('utf-8')
#                         image_base64 = f"data:{mime_type};base64,{encoded}"

#         data['image'] = image_base64

#         return Response({
#             "errCode": 0,
#             "message": "Lấy bác sĩ thành công",
#             "method": request.method,
#             "data": data
#         }, status=200)

#     except Doctor.DoesNotExist:
#         return Response({
#             "errCode": 1,
#             "message": "Không tìm thấy bác sĩ",
#             "data": {}
#         }, status=404)

#     except Exception as e:
#         return Response({
#             "errCode": 2,
#             "message": "Lỗi hệ thống",
#             "method": request.method,
#             "error": str(e),
#             "data": {}
#         }, status=500)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_doctor(request):
    try:
        doctor_id = request.GET.get('id')
        if not doctor_id:
            return Response({
                "errCode": 3,
                "message": "Thiếu ID bác sĩ"
            }, status=400)

        doctor = Doctor.objects.get(id=doctor_id)

        data = model_to_dict(doctor)

        # Lấy tên ảnh (đã tự động lưu trên Cloudinary)
        data['image_name'] = doctor.image

        # Trường `doctor.image` đã lưu URL của ảnh, không cần thêm `.url`
        if doctor.image:
            data['image'] = doctor.image
        else:
            data['image'] = None

        return Response({
            "errCode": 0,
            "message": "Lấy bác sĩ thành công",
            "method": request.method,
            "data": data
        }, status=200)

    except Doctor.DoesNotExist:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy bác sĩ",
            "data": {}
        }, status=404)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": {}
        }, status=500)
        
# @api_view(['PUT'])
# @transaction.atomic
# def update_doctor(request):
#     try:
#         auth_header = request.headers.get('Authorization')
#         if not auth_header or not auth_header.startswith("Bearer "):
#             return Response({"errCode": 3, "message": "Thiếu hoặc sai định dạng token"}, status=status.HTTP_401_UNAUTHORIZED)

#         token = auth_header.split(" ")[1]
#         decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#         user_id = decoded.get('user_id')

#         User = get_user_model()
#         user = User.objects.get(id=user_id)

#         if user.role != 'admin':
#             return Response({"errCode": 4, "message": "Bạn không có quyền cập nhật bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

#         data = request.data.copy()
#         doctor_id = data.get("id")
#         if not doctor_id:
#             return Response({"errCode": 5, "message": "Thiếu id bác sĩ"}, status=status.HTTP_400_BAD_REQUEST)

#         doctor = Doctor.objects.filter(id=doctor_id).first()
#         if not doctor:
#             return Response({"errCode": 6, "message": "Không tìm thấy bác sĩ"}, status=status.HTTP_404_NOT_FOUND)

#         # ✅ Xoá ảnh cũ
#         old_image_name = data.get("image_name")
#         if old_image_name:
#             old_path = os.path.join(IMAGE_DOCTOR, old_image_name)
#             if os.path.exists(old_path):
#                 os.remove(old_path)

#         # ✅ Xử lý ảnh mới
#         image_base64 = data.get("image")
#         if image_base64 and image_base64.strip() != "":
#             try:
#                 if "base64," in image_base64:
#                     format_info, imgstr = image_base64.split(";base64,")
#                     mime_type = format_info.split(":")[-1].lower()
#                     ext = mimetypes.guess_extension(mime_type) or '.jpg'
#                     ext = ext.lstrip('.')
#                 else:
#                     imgstr = image_base64
#                     ext = "jpg"

#                 if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
#                     return Response({
#                         "errCode": 11,
#                         "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 timestamp = int(time.time())
#                 unique_id = uuid.uuid4().hex[:8]
#                 file_name = f"{timestamp}-{unique_id}.{ext}"

#                 os.makedirs(IMAGE_DOCTOR, exist_ok=True)
#                 image_path = os.path.join(IMAGE_DOCTOR, file_name)
#                 with open(image_path, "wb") as f:
#                     f.write(base64.b64decode(imgstr))

#                 data["image"] = file_name  # cập nhật ảnh mới vào DB
#             except Exception as e:
#                 return Response({
#                     "errCode": 12,
#                     "message": "Lỗi xử lý ảnh base64",
#                     "error": str(e)
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         # ✅ Cập nhật bác sĩ
#         serializer = DoctorSerializer(doctor, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "errCode": 0,
#                 "message": "Cập nhật bác sĩ thành công",
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)

#         return Response({
#             "errCode": 2,
#             "message": "Lỗi dữ liệu đầu vào",
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

#     except jwt.ExpiredSignatureError:
#         return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
#     except jwt.InvalidTokenError:
#         return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
#     except Exception as e:
#         return Response({
#             "errCode": 99,
#             "message": "Lỗi không xác định",
#             "error": str(e)
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_doctor(request):
    try:
        user = request.user
        if user.role != 'admin':
            return Response({"errCode": 4, "message": "Bạn không có quyền cập nhật bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        doctor_id = data.get("id")

        if not doctor_id:
            return Response({"errCode": 5, "message": "Thiếu id bác sĩ"}, status=status.HTTP_400_BAD_REQUEST)

        doctor = Doctor.objects.filter(id=doctor_id).first()
        if not doctor:
            return Response({"errCode": 6, "message": "Không tìm thấy bác sĩ"}, status=status.HTTP_404_NOT_FOUND)

        image_base64 = data.get("image")
        if image_base64 and image_base64.strip() != "":
            try:
                # ❌ Xoá ảnh cũ trên Cloudinary nếu có
                old_image_url = doctor.image
                match = re.search(r'/upload/(?:v\d+/)?(?P<public_id>.+?)\.(?:jpg|jpeg|png|gif|webp)', old_image_url)
                if match:
                    public_id = match.group('public_id')  # ví dụ: 'doctors/doctor_...'
                    cloudinary.uploader.destroy(public_id)

                # ✅ Xử lý ảnh base64 mới
                if "base64," in image_base64:
                    format_info, imgstr = image_base64.split(";base64,")
                    mime_type = format_info.split(":")[-1].lower()
                    ext = mimetypes.guess_extension(mime_type) or '.jpg'
                    ext = ext.lstrip('.')
                else:
                    imgstr = image_base64
                    ext = "jpg"

                if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:16]
                cloud_name = f"doctor_{timestamp}_{unique_id}"

                upload_result = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=cloud_name,
                    folder="doctors"
                )

                image_url = upload_result.get("secure_url")
                if image_url:
                    data["image"] = image_url
                else:
                    return Response({
                        "errCode": 13,
                        "message": "Không lấy được URL ảnh từ Cloudinary"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Cập nhật thông tin bác sĩ
        serializer = DoctorSerializer(doctor, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật bác sĩ thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 2,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_nurse(request):
    try:
        user = request.user

        if user.role != 'admin':
            return Response({
                "errCode": 4,
                "message": "Bạn không có quyền tạo y tá"
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        User = get_user_model()

        # 📌 Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=data.get("email")).exists():
            return Response({
                "errCode": 9,
                "message": "Email đã được sử dụng"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Xử lý ảnh base64 và upload lên Cloudinary
        image_base64 = data.get("image")
        if not image_base64 or image_base64.strip() == "":
            return Response({
                "errCode": 10,
                "message": "Ảnh không hợp lệ hoặc không có ảnh"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if "base64," in image_base64:
                format_info, imgstr = image_base64.split(";base64,")
                mime_type = format_info.split(":")[-1].lower()
                ext = mimetypes.guess_extension(mime_type) or '.jpg'
                ext = ext.lstrip('.')
            else:
                imgstr = image_base64
                ext = "jpg"

            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                return Response({
                    "errCode": 11,
                    "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                }, status=status.HTTP_400_BAD_REQUEST)

            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:16]
            cloud_name = f"nurse_{timestamp}_{unique_id}"

            upload_result = cloudinary.uploader.upload(
                base64.b64decode(imgstr),
                public_id=cloud_name,
                folder="nurses"
            )

            image_url = upload_result.get("secure_url")
            if not image_url:
                raise Exception("Không lấy được URL từ Cloudinary")

            data["image"] = image_url

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh hoặc upload ảnh lên Cloud",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Tạo user mới cho y tá
        new_user = User.objects.create_user(
            email=data.get("email"),
            password=data.get("password"),
            role="nurse"
        )
        data["user"] = new_user.id

        # 📌 Tạo nurse record
        serializer = NurseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Tạo y tá thành công",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        # ⚠️ Nếu lỗi thì rollback user đã tạo
        new_user.delete()
        return Response({
            "errCode": 1,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_nurse_by_token(request):
    try:
        user = request.user  # Lấy từ token

        # Cố gắng truy ra y tá
        try:
            nurse = Nurse.objects.get(user_id=user.id)
            data = model_to_dict(nurse)
        except Nurse.DoesNotExist:
            data = {}  # Không có y tá, trả về rỗng

        return Response({
            "errCode": 0,
            "message": "Lấy thông tin y tá thành công",
            "data": data
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e),
            "data": {}
        }, status=500)


        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pharmacist_by_token(request):
    try:
        user = request.user  # Lấy từ token

        # Cố gắng truy ra y tá
        try:
            pharmacist = Pharmacist.objects.get(user_id=user.id)
            data = model_to_dict(pharmacist)
        except pharmacist.DoesNotExist:
            data = {}  # Không có y tá, trả về rỗng

        return Response({
            "errCode": 0,
            "message": "Lấy thông tin y tá thành công",
            "data": data
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e),
            "data": {}
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_nurse_with_user_status(request):
    try:
        nurses = Nurse.objects.select_related('user').all()
        
        nurse_list = []
        for nur in nurses:
            nurse_list.append({
                "id": nur.id,
                "name": nur.name,
                "date_of_birth": nur.date_of_birth,
                "user_id": nur.user.id,
                "phone":nur.phone,
                "user": {
                    "is_active": nur.user.is_active
                }
            })

        return Response({
            "errCode": 0,
            "message": "Lấy danh sách bác sĩ thành công",
            "method": request.method,
            "data": nurse_list
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": []
        }, status=500)
        
        
@api_view(['GET'])
@permission_classes([AllowAny])
def get_nurse(request):
    try:
        nurse_id = request.GET.get('id')
        if not nurse_id:
            return Response({
                "errCode": 3,
                "message": "Thiếu ID y tá"
            }, status=400)

        nurse = Nurse.objects.get(id=nurse_id)
        data = model_to_dict(nurse)  # image đã nằm trong data nếu dùng ImageField

        return Response({
            "errCode": 0,
            "message": "Lấy y tá thành công",
            "method": request.method,
            "data": data
        }, status=200)

    except Nurse.DoesNotExist:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy y tá",
            "data": {}
        }, status=404)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": {}
        }, status=500)

       
@api_view(['GET'])
@permission_classes([AllowAny])
def get_nurse_by_user(request):
    try:
        nurse_id = request.GET.get('id')
        if not nurse_id:
            return Response({
                "errCode": 3,
                "message": "Thiếu ID y tá"
            }, status=400)

        nurse = Nurse.objects.get(user_id=nurse_id)
        data = model_to_dict(nurse)  # image đã nằm trong data nếu dùng ImageField

        return Response({
            "errCode": 0,
            "message": "Lấy y tá thành công",
            "method": request.method,
            "data": {
                "name":data.get("name")
            }
        }, status=200)

    except Nurse.DoesNotExist:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy y tá",
            "data": {}
        }, status=404)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": {}
        }, status=500)

     
@api_view(['GET'])
@permission_classes([AllowAny])
def get_doctor_by_user(request):
    try:
        doctor_id = request.GET.get('id')
        if not doctor_id:
            return Response({
                "errCode": 3,
                "message": "Thiếu ID y tá"
            }, status=400)

        doctor = Doctor.objects.get(user_id=doctor_id)
        data = model_to_dict(doctor)  # image đã nằm trong data nếu dùng ImageField

        return Response({
            "errCode": 0,
            "message": "Lấy y tá thành công",
            "method": request.method,
            "data": {
                "name":data.get("name")
            }
        }, status=200)

    except Nurse.DoesNotExist:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy bác sĩ",
            "data": {}
        }, status=404)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": {}
        }, status=500)
        
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_nurse(request):
    try:
        user = request.user
        if user.role != 'admin':
            return Response({
                "errCode": 4,
                "message": "Bạn không có quyền cập nhật y tá"
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        nurse_id = data.get("id")
        if not nurse_id:
            return Response({
                "errCode": 5,
                "message": "Thiếu id y tá"
            }, status=status.HTTP_400_BAD_REQUEST)

        nurse = Nurse.objects.filter(id=nurse_id).first()
        if not nurse:
            return Response({
                "errCode": 6,
                "message": "Không tìm thấy y tá"
            }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Nếu có ảnh mới thì xử lý upload
        image_base64 = data.get("image")
        if image_base64 and image_base64.strip() != "":
            try:
                if "base64," in image_base64:
                    format_info, imgstr = image_base64.split(";base64,")
                    mime_type = format_info.split(":")[-1].lower()
                    ext = mimetypes.guess_extension(mime_type) or '.jpg'
                    ext = ext.lstrip('.')
                else:
                    imgstr = image_base64
                    ext = "jpg"

                if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:16]
                cloud_name = f"nurse_update_{timestamp}_{unique_id}"

                upload_result = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=cloud_name,
                    folder="nurses"
                )

                image_url = upload_result.get("secure_url")
                if not image_url:
                    raise Exception("Không lấy được URL ảnh từ Cloudinary")

                data["image"] = image_url

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh hoặc upload ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Cập nhật thông tin y tá
        serializer = NurseSerializer(nurse, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật y tá thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 2,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_nurse_token(request):
    try:
        user = request.user
        nurse = Nurse.objects.filter(user_id=user.id).first()
        if not nurse:
            return Response({
                "errCode": 6,
                "message": "Không tìm thấy y tá tương ứng với tài khoản"
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        image_base64 = data.get("image")
        
        if image_base64 and image_base64.strip() != "":
            # Có ảnh mới => xử lý xóa ảnh cũ + upload ảnh mới
            try:
                # Xoá ảnh cũ nếu có
                if nurse.image:
                    parsed_url = urlparse(nurse.image)
                    path_parts = parsed_url.path.split('/')  # ['', 'image', 'upload', 'v12345', 'nurses', 'filename.jpg']
                    if 'upload' in path_parts:
                        index = path_parts.index('upload')
                        public_id_parts = path_parts[index + 2:]  # ['nurses', 'filename.jpg']
                        public_id_with_ext = "/".join(public_id_parts)       # nurses/filename.jpg
                        public_id = os.path.splitext(public_id_with_ext)[0]  # nurses/filename
                        cloudinary.uploader.destroy(public_id)

                # Xử lý upload ảnh mới
                if "base64," in image_base64:
                    format_info, imgstr = image_base64.split(";base64,")
                    mime_type = format_info.split(":")[-1].lower()
                    ext = mimetypes.guess_extension(mime_type) or '.jpg'
                    ext = ext.lstrip('.')
                else:
                    imgstr = image_base64
                    ext = "jpg"

                if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:16]
                cloud_name = f"nurse_{timestamp}_{unique_id}"

                upload_result = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=cloud_name,
                    folder="nurses"
                )

                image_url = upload_result.get("secure_url")
                if not image_url:
                    raise Exception("Không lấy được URL ảnh từ Cloudinary")

                data["image"] = image_url

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh hoặc upload ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Nếu không có ảnh mới thì không truyền key "image" vào data để tránh ghi đè ảnh cũ thành rỗng
            if "image" in data:
                data.pop("image")

        # Cập nhật thông tin y tá (cả các trường khác)
        serializer = NurseSerializer(nurse, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật y tá thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 2,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_pharmacist_token(request):
    try:
        user = request.user
        pharmacist = Pharmacist.objects.filter(user_id=user.id).first()
        if not pharmacist:
            return Response({
                "errCode": 6,
                "message": "Không tìm thấy y tá tương ứng với tài khoản"
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        image_base64 = data.get("image")
        
        if image_base64 and image_base64.strip() != "":
            # Có ảnh mới => xử lý xóa ảnh cũ + upload ảnh mới
            try:
                # Xoá ảnh cũ nếu có
                if pharmacist.image:
                    parsed_url = urlparse(pharmacist.image)
                    path_parts = parsed_url.path.split('/')  # ['', 'image', 'upload', 'v12345', 'nurses', 'filename.jpg']
                    if 'upload' in path_parts:
                        index = path_parts.index('upload')
                        public_id_parts = path_parts[index + 2:]  # ['nurses', 'filename.jpg']
                        public_id_with_ext = "/".join(public_id_parts)       # nurses/filename.jpg
                        public_id = os.path.splitext(public_id_with_ext)[0]  # nurses/filename
                        cloudinary.uploader.destroy(public_id)

                # Xử lý upload ảnh mới
                if "base64," in image_base64:
                    format_info, imgstr = image_base64.split(";base64,")
                    mime_type = format_info.split(":")[-1].lower()
                    ext = mimetypes.guess_extension(mime_type) or '.jpg'
                    ext = ext.lstrip('.')
                else:
                    imgstr = image_base64
                    ext = "jpg"

                if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:16]
                cloud_name = f"pharmacist_{timestamp}_{unique_id}"

                upload_result = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=cloud_name,
                    folder="pharmacists"
                )

                image_url = upload_result.get("secure_url")
                if not image_url:
                    raise Exception("Không lấy được URL ảnh từ Cloudinary")

                data["image"] = image_url

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh hoặc upload ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Nếu không có ảnh mới thì không truyền key "image" vào data để tránh ghi đè ảnh cũ thành rỗng
            if "image" in data:
                data.pop("image")

        # Cập nhật thông tin pharmacist (cả các trường khác)
        serializer = PharmacistSerializer(pharmacist, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật ktv thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 2,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    


 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_cashier_token(request):
    try:
        user = request.user
        cashier = Cashier.objects.filter(user_id=user.id).first()
        if not cashier:
            return Response({
                "errCode": 6,
                "message": "Không tìm thấy y tá tương ứng với tài khoản"
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        image_base64 = data.get("image")
        
        if image_base64 and image_base64.strip() != "":
            # Có ảnh mới => xử lý xóa ảnh cũ + upload ảnh mới
            try:
                # Xoá ảnh cũ nếu có
                if cashier.image:
                    parsed_url = urlparse(cashier.image)
                    path_parts = parsed_url.path.split('/')  # ['', 'image', 'upload', 'v12345', 'nurses', 'filename.jpg']
                    if 'upload' in path_parts:
                        index = path_parts.index('upload')
                        public_id_parts = path_parts[index + 2:]  # ['nurses', 'filename.jpg']
                        public_id_with_ext = "/".join(public_id_parts)       # nurses/filename.jpg
                        public_id = os.path.splitext(public_id_with_ext)[0]  # nurses/filename
                        cloudinary.uploader.destroy(public_id)

                # Xử lý upload ảnh mới
                if "base64," in image_base64:
                    format_info, imgstr = image_base64.split(";base64,")
                    mime_type = format_info.split(":")[-1].lower()
                    ext = mimetypes.guess_extension(mime_type) or '.jpg'
                    ext = ext.lstrip('.')
                else:
                    imgstr = image_base64
                    ext = "jpg"

                if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:16]
                cloud_name = f"cashier_{timestamp}_{unique_id}"

                upload_result = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=cloud_name,
                    folder="cashiers"
                )

                image_url = upload_result.get("secure_url")
                if not image_url:
                    raise Exception("Không lấy được URL ảnh từ Cloudinary")

                data["image"] = image_url

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh hoặc upload ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Nếu không có ảnh mới thì không truyền key "image" vào data để tránh ghi đè ảnh cũ thành rỗng
            if "image" in data:
                data.pop("image")

        # Cập nhật thông tin pharmacist (cả các trường khác)
        serializer = CashierSerializer(cashier, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật ktv thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 2,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        

 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_doctor_token(request):
    try:
        user = request.user
        doctor = Doctor.objects.filter(user_id=user.id).first()
        if not doctor:
            return Response({
                "errCode": 6,
                "message": "Không tìm thấy y tá tương ứng với tài khoản"
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        image_base64 = data.get("image")
        
        if image_base64 and image_base64.strip() != "":
            # Có ảnh mới => xử lý xóa ảnh cũ + upload ảnh mới
            try:
                # Xoá ảnh cũ nếu có
                if doctor.image:
                    parsed_url = urlparse(doctor.image)
                    path_parts = parsed_url.path.split('/')  # ['', 'image', 'upload', 'v12345', 'nurses', 'filename.jpg']
                    if 'upload' in path_parts:
                        index = path_parts.index('upload')
                        public_id_parts = path_parts[index + 2:]  # ['nurses', 'filename.jpg']
                        public_id_with_ext = "/".join(public_id_parts)       # nurses/filename.jpg
                        public_id = os.path.splitext(public_id_with_ext)[0]  # nurses/filename
                        cloudinary.uploader.destroy(public_id)

                # Xử lý upload ảnh mới
                if "base64," in image_base64:
                    format_info, imgstr = image_base64.split(";base64,")
                    mime_type = format_info.split(":")[-1].lower()
                    ext = mimetypes.guess_extension(mime_type) or '.jpg'
                    ext = ext.lstrip('.')
                else:
                    imgstr = image_base64
                    ext = "jpg"

                if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:16]
                cloud_name = f"doctor_{timestamp}_{unique_id}"

                upload_result = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=cloud_name,
                    folder="doctors"
                )

                image_url = upload_result.get("secure_url")
                if not image_url:
                    raise Exception("Không lấy được URL ảnh từ Cloudinary")

                data["image"] = image_url

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh hoặc upload ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Nếu không có ảnh mới thì không truyền key "image" vào data để tránh ghi đè ảnh cũ thành rỗng
            if "image" in data:
                data.pop("image")

        # Cập nhật thông tin pharmacist (cả các trường khác)
        serializer = DoctorSerializer(doctor, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật ktv thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 2,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

      
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_technician_token(request):
    try:
        user = request.user
        technician = Technician.objects.filter(user_id=user.id).first()
        if not technician:
            return Response({
                "errCode": 6,
                "message": "Không tìm thấy y tá tương ứng với tài khoản"
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        image_base64 = data.get("image")
        
        if image_base64 and image_base64.strip() != "":
            # Có ảnh mới => xử lý xóa ảnh cũ + upload ảnh mới
            try:
                # Xoá ảnh cũ nếu có
                if technician.image:
                    parsed_url = urlparse(technician.image)
                    path_parts = parsed_url.path.split('/')  # ['', 'image', 'upload', 'v12345', 'nurses', 'filename.jpg']
                    if 'upload' in path_parts:
                        index = path_parts.index('upload')
                        public_id_parts = path_parts[index + 2:]  # ['nurses', 'filename.jpg']
                        public_id_with_ext = "/".join(public_id_parts)       # nurses/filename.jpg
                        public_id = os.path.splitext(public_id_with_ext)[0]  # nurses/filename
                        cloudinary.uploader.destroy(public_id)

                # Xử lý upload ảnh mới
                if "base64," in image_base64:
                    format_info, imgstr = image_base64.split(";base64,")
                    mime_type = format_info.split(":")[-1].lower()
                    ext = mimetypes.guess_extension(mime_type) or '.jpg'
                    ext = ext.lstrip('.')
                else:
                    imgstr = image_base64
                    ext = "jpg"

                if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:16]
                cloud_name = f"technician_{timestamp}_{unique_id}"

                upload_result = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=cloud_name,
                    folder="technicians"
                )

                image_url = upload_result.get("secure_url")
                if not image_url:
                    raise Exception("Không lấy được URL ảnh từ Cloudinary")

                data["image"] = image_url

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh hoặc upload ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Nếu không có ảnh mới thì không truyền key "image" vào data để tránh ghi đè ảnh cũ thành rỗng
            if "image" in data:
                data.pop("image")

        # Cập nhật thông tin pharmacist (cả các trường khác)
        serializer = TechnicianSerializer(technician, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật ktv thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 2,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_technician(request):
    try:
        user = request.user
        if user.role != 'admin':
            return Response({
                "errCode": 4,
                "message": "Bạn không có quyền tạo kỹ thuật viên"
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        User = get_user_model()

        # 📌 Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=data.get("email")).exists():
            return Response({
                "errCode": 9,
                "message": "Email đã được sử dụng"
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Xử lý ảnh base64 upload lên Cloudinary
        image_base64 = data.get("image")
        if not image_base64 or image_base64.strip() == "":
            return Response({
                "errCode": 10,
                "message": "Ảnh không hợp lệ hoặc không có ảnh"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if "base64," in image_base64:
                format_info, imgstr = image_base64.split(";base64,")
                mime_type = format_info.split(":")[-1].lower()
                ext = mimetypes.guess_extension(mime_type) or '.jpg'
                ext = ext.lstrip('.')
            else:
                imgstr = image_base64
                ext = "jpg"

            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                return Response({
                    "errCode": 11,
                    "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                }, status=status.HTTP_400_BAD_REQUEST)

            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:16]
            cloud_name = f"technician_{timestamp}_{unique_id}"

            upload_result = cloudinary.uploader.upload(
                base64.b64decode(imgstr),
                public_id=cloud_name,
                folder="technicians"
            )

            image_url = upload_result.get("secure_url")
            if image_url:
                data["image"] = image_url
            else:
                return Response({
                    "errCode": 13,
                    "message": "Không lấy được URL ảnh từ Cloudinary"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Tạo user mới cho kỹ thuật viên
        new_user = User.objects.create_user(
            email=data.get("email"),
            password=data.get("password"),
            role="technician"
        )
        data["user"] = new_user.id

        # ✅ Tạo bản ghi kỹ thuật viên
        serializer = TechnicianSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Tạo kỹ thuật viên thành công",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        # ⚠️ Nếu lỗi thì rollback user đã tạo
        new_user.delete()
        return Response({
            "errCode": 1,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_technician_with_user_status(request):
    try:
        technicians = Technician.objects.select_related('user').all()
        
        technician_list = []
        for tec in technicians:
            technician_list.append({
                "id": tec.id,
                "name": tec.name,
                "date_of_birth": tec.date_of_birth,
                "user_id": tec.user.id,
                "phone":tec.phone,
                "user": {
                    "is_active": tec.user.is_active
                }
            })

        return Response({
            "errCode": 0,
            "message": "Lấy danh sách kĩ thuật viên thành công",
            "method": request.method,
            "data": technician_list
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": []
        }, status=500)
        
        
      
@api_view(['GET'])
@permission_classes([AllowAny])
def get_technician(request):
    try:
        technician_id = request.GET.get('id')
        if not technician_id:
            return Response({
                "errCode": 3,
                "message": "Thiếu ID y tá"
            }, status=400)

        technician = Technician.objects.get(id=technician_id)

        data = model_to_dict(technician)
        return Response({
            "errCode": 0,
            "message": "Lấy y tá thành công",
            "method": request.method,
            "data": data
        }, status=200)

    except Technician.DoesNotExist:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy kĩ thuật viên",
            "data": {}
        }, status=404)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": {}
        }, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_technician(request):
    try:
        # Kiểm tra quyền của người dùng
        user = request.user
        if user.role != 'admin':
            return Response({
                "errCode": 4,
                "message": "Bạn không có quyền cập nhật kỹ thuật viên"
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        technician_id = data.get("id")
        if not technician_id:
            return Response({
                "errCode": 5,
                "message": "Thiếu id kỹ thuật viên"
            }, status=status.HTTP_400_BAD_REQUEST)

        technician = Technician.objects.filter(id=technician_id).first()
        if not technician:
            return Response({
                "errCode": 6,
                "message": "Không tìm thấy kỹ thuật viên"
            }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Xử lý ảnh base64 và upload lên Cloudinary
        image_base64 = data.get("image")
        if image_base64 and image_base64.strip() != "":
            try:
                # ❌ Xoá ảnh cũ nếu có
                old_image_url = technician.image
                match = re.search(r'/upload/(?:v\d+/)?(?P<public_id>.+?)\.(?:jpg|jpeg|png|gif|webp)', old_image_url or "")
                if match:
                    public_id = match.group('public_id')  # ví dụ: 'technicians/technician_...'
                    cloudinary.uploader.destroy(public_id)

                # ✅ Tách định dạng ảnh và decode base64
                if "base64," in image_base64:
                    format_info, imgstr = image_base64.split(";base64,")
                    mime_type = format_info.split(":")[-1].lower()
                    ext = mimetypes.guess_extension(mime_type) or '.jpg'
                    ext = ext.lstrip('.')
                else:
                    imgstr = image_base64
                    ext = "jpg"

                if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Tạo tên ảnh duy nhất để upload lên Cloudinary
                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:8]
                cloud_name = f"technician_{timestamp}_{unique_id}"

                # Upload ảnh lên Cloudinary
                upload_result = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=cloud_name,
                    folder="technicians"
                )

                image_url = upload_result.get("secure_url")
                if not image_url:
                    raise Exception("Không lấy được URL ảnh từ Cloudinary")

                data["image"] = image_url  # Cập nhật ảnh mới vào DB

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh base64 hoặc upload ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Cập nhật thông tin kỹ thuật viên
        serializer = TechnicianSerializer(technician, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật kỹ thuật viên thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 2,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_pharmacist(request):
    try:
        # Kiểm tra quyền của người dùng
        user = request.user
        if user.role != 'admin':
            return Response({
                "errCode": 4,
                "message": "Bạn không có quyền tạo kĩ thuật viên"
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        # Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=data.get("email")).exists():
            return Response({"errCode": 9, "message": "Email đã được sử dụng"}, status=status.HTTP_400_BAD_REQUEST)

        # Xử lý ảnh base64 và upload lên Cloudinary
        image_base64 = data.get("image")
        if not image_base64 or image_base64.strip() == "":
            return Response({
                "errCode": 10,
                "message": "Ảnh không hợp lệ hoặc không có ảnh"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Kiểm tra và lấy thông tin định dạng của ảnh
            if "base64," in image_base64:
                format_info, imgstr = image_base64.split(";base64,")
                mime_type = format_info.split(":")[-1].lower()
                ext = mimetypes.guess_extension(mime_type) or '.jpg'
                ext = ext.lstrip('.')
            else:
                imgstr = image_base64
                ext = "jpg"  # fallback

            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                return Response({
                    "errCode": 11,
                    "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Tạo tên ảnh duy nhất để upload lên Cloudinary
            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:8]
            cloud_name = f"pharmacist_{timestamp}_{unique_id}"

            # Upload ảnh lên Cloudinary
            upload_result = cloudinary.uploader.upload(
                base64.b64decode(imgstr),
                public_id=cloud_name,
                folder="pharmacists"
            )

            image_url = upload_result.get("secure_url")
            if not image_url:
                raise Exception("Không lấy được URL ảnh từ Cloudinary")

            data["image"] = image_url  # Cập nhật URL ảnh mới vào DB

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64 hoặc upload ảnh",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # Tạo user mới cho kĩ thuật viên
        new_user = User.objects.create_user(
            email=data.get("email"),
            password=data.get("password"),
            role="pharmacist"
        )
        data["user"] = new_user.id

        # Tạo kĩ thuật viên
        serializer = PharmacistSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Tạo Kĩ thuật viên thành công",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        # Nếu lỗi thì rollback user đã tạo
        new_user.delete()
        return Response({
            "errCode": 1,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Lỗi tạo kĩ thuật viên: {e}")
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_pharmacist_with_user_status(request):
    try:
        phars = Pharmacist.objects.select_related('user').all()
        
        phar_list = []
        for ph in phars:
            phar_list.append({
                "id": ph.id,
                "name": ph.name,
                "date_of_birth": ph.date_of_birth,
                "user_id": ph.user.id,
                "phone":ph.phone,
                "user": {
                    "is_active": ph.user.is_active
                }
            })

        return Response({
            "errCode": 0,
            "message": "Lấy danh sách kĩ thuật viên thành công",
            "method": request.method,
            "data": phar_list
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": []
        }, status=500)
        
        
      
@api_view(['GET'])
@permission_classes([AllowAny])
def get_pharmacist(request):
    try:
        pharmacist_id = request.GET.get('id')
        if not pharmacist_id:
            return Response({
                "errCode": 3,
                "message": "Thiếu ID y tá"
            }, status=400)

        pharmacist = Pharmacist.objects.get(id=pharmacist_id)

        data = model_to_dict(pharmacist)
        return Response({
            "errCode": 0,
            "message": "Lấy y tá thành công",
            "method": request.method,
            "data": data
        }, status=200)

    except Pharmacist.DoesNotExist:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy kĩ thuật viên",
            "data": {}
        }, status=404)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": {}
        }, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_pharmacist(request):
    try:
        user = request.user
        if user.role != 'admin':
            return Response({
                "errCode": 4,
                "message": "Bạn không có quyền cập nhật y tá"
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        pharmacist_id = data.get("id")

        if not pharmacist_id:
            return Response({
                "errCode": 5,
                "message": "Thiếu ID y tá"
            }, status=status.HTTP_400_BAD_REQUEST)

        pharmacist = Pharmacist.objects.filter(id=pharmacist_id).first()
        if not pharmacist:
            return Response({
                "errCode": 6,
                "message": "Không tìm thấy y tá"
            }, status=status.HTTP_404_NOT_FOUND)

        image_base64 = data.get("image")
        if image_base64 and image_base64.strip() != "":
            try:
                # ❌ Xoá ảnh cũ trên Cloudinary nếu có
                old_image_url = pharmacist.image
                match = re.search(r'/upload/(?:v\d+/)?(?P<public_id>.+?)\.(?:jpg|jpeg|png|gif|webp)', old_image_url)
                if match:
                    public_id = match.group('public_id')  # ví dụ: 'pharmacists/pharmacist_...'
                    cloudinary.uploader.destroy(public_id)

                # ✅ Xử lý ảnh base64 mới
                if "base64," in image_base64:
                    format_info, imgstr = image_base64.split(";base64,")
                    mime_type = format_info.split(":")[-1].lower()
                    ext = mimetypes.guess_extension(mime_type) or '.jpg'
                    ext = ext.lstrip('.')
                else:
                    imgstr = image_base64
                    ext = "jpg"

                if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:16]
                cloud_name = f"pharmacist_{timestamp}_{unique_id}"

                upload_result = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=cloud_name,
                    folder="pharmacists"
                )

                image_url = upload_result.get("secure_url")
                if image_url:
                    data["image"] = image_url
                else:
                    return Response({
                        "errCode": 13,
                        "message": "Không lấy được URL ảnh từ Cloudinary"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Cập nhật thông tin y tá
        serializer = PharmacistSerializer(pharmacist, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật y tá thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 2,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_cashier(request):
    try:
        user = request.user
        if user.role != 'admin':
            return Response({
                "errCode": 4,
                "message": "Bạn không có quyền tạo thu ngân"
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        # 📌 Kiểm tra email trùng
        User = get_user_model()
        email = data.get("email")
        if User.objects.filter(email=email).exists():
            return Response({
                "errCode": 9,
                "message": "Email đã được sử dụng"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Xử lý ảnh base64 & upload Cloudinary
        image_base64 = data.get("image")
        if not image_base64 or image_base64.strip() == "":
            return Response({
                "errCode": 10,
                "message": "Ảnh không hợp lệ hoặc không có ảnh"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # — Tách định dạng & base64
            if "base64," in image_base64:
                header, imgstr = image_base64.split(";base64,")
                mime_type = header.split(":")[1].lower()
            else:
                imgstr = image_base64
                mime_type = "image/jpeg"

            # — Kiểm tra định dạng hợp lệ
            allowed_mime_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif']
            if mime_type not in allowed_mime_types:
                return Response({
                    "errCode": 11,
                    "message": f"Định dạng ảnh không được hỗ trợ: {mime_type}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # — Tạo public_id duy nhất
            ts = int(time.time())
            uid = uuid.uuid4().hex[:8]
            public_id = f"cashier_{ts}_{uid}"

            # — Upload ảnh
            upload = cloudinary.uploader.upload(
                base64.b64decode(imgstr),
                public_id=public_id,
                folder="cashiers",
                resource_type="image"
            )

            secure_url = upload.get("secure_url")
            if not secure_url:
                raise Exception("Không lấy được URL từ Cloudinary")

            data["image"] = secure_url

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64 hoặc upload ảnh",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Tạo user mới
        new_user = User.objects.create_user(
            email=data.get("email"),
            password=data.get("password"),
            role="cashier"
        )
        data["user"] = new_user.id

        # 📌 Tạo cashier
        serializer = CashierSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Tạo thu ngân thành công",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        # ❌ Nếu lỗi => rollback user đã tạo
        new_user.delete()
        return Response({
            "errCode": 1,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_cashier_with_user_status(request):
    try:
        cashiers = Cashier.objects.select_related('user').all()
        
        cashier_list = []
        for cashier in cashiers:
            cashier_list.append({
                "id": cashier.id,
                "name": cashier.name,
                "date_of_birth": cashier.date_of_birth,
                "user_id": cashier.user.id,
                "phone":cashier.phone,
                "user": {
                    "is_active": cashier.user.is_active
                }
            })

        return Response({
            "errCode": 0,
            "message": "Lấy danh sách kĩ thuật viên thành công",
            "method": request.method,
            "data": cashier_list
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": []
        }, status=500)
        
        
      
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cashier(request):
    try:
        cashier_id = request.GET.get('id')
        if not cashier_id:
            return Response({
                "errCode": 3,
                "message": "Thiếu ID thu ngân"
            }, status=400)

        cashier = Cashier.objects.get(id=cashier_id)

        data = model_to_dict(cashier)
        return Response({
            "errCode": 0,
            "message": "Lấy y tá thành công",
            "method": request.method,
            "data": data
        }, status=200)

    except Cashier.DoesNotExist:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy kĩ thuật viên",
            "data": {}
        }, status=404)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": {}
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cashier_by_token(request):
    try:
        user = request.user  # Lấy từ token

        # Cố gắng truy ra y tá
        try:
            cashier = Cashier.objects.get(user_id=user.id)
            data = model_to_dict(cashier)
        except cashier.DoesNotExist:
            data = {}  # Không có y tá, trả về rỗng

        return Response({
            "errCode": 0,
            "message": "Lấy thông tin y tá thành công",
            "data": data
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e),
            "data": {}
        }, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_by_token(request):
    try:
        user = request.user  # <-- Đã có user ở đây
        try:
            doctor = Doctor.objects.filter(user=user).first()
            data = model_to_dict(doctor)
        except doctor.DoesNotExist:
            data = {}  

        return Response({
            "errCode": 0,
            "message": "Truy vấn thành công",
            "method": request.method,
            "data": data
        })

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": {}
        }, status=500) 
       
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_technician_by_token(request):
    try:
        user = request.user  # Lấy từ token

        # Cố gắng truy ra y tá
        try:
            tech = Technician.objects.get(user_id=user.id)
            data = model_to_dict(tech)
        except tech.DoesNotExist:
            data = {}  # Không có y tá, trả về rỗng

        return Response({
            "errCode": 0,
            "message": "Lấy thông tin y tá thành công",
            "data": data
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e),
            "data": {}
        }, status=500)
        
          
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cashier_by_user(request):
    try:
        user_id = request.GET.get('id')
        if not user_id:
            return Response({
                "errCode": 3,
                "message": "Thiếu ID người dùng"
            }, status=400)

        # Tìm thu ngân theo user_id
        cashier = Cashier.objects.filter(user_id=user_id).first()

        if cashier:
            data = {
                "name": cashier.name
            }
        else:
            data = {}  # Không có thu ngân nhưng vẫn errCode = 0

        return Response({
            "errCode": 0,
            "message": "Truy vấn thành công",
            "method": request.method,
            "data": data
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": {}
        }, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_cashier(request):
    try:
        # 1️⃣ Kiểm tra quyền người dùng
        user = request.user
        if user.role != 'admin':
            return Response({
                "errCode": 4,
                "message": "Bạn không có quyền cập nhật thu ngân"
            }, status=status.HTTP_403_FORBIDDEN)

        # 2️⃣ Lấy dữ liệu và tìm cashier
        data = request.data.copy()
        cashier_id = data.get("id")
        if not cashier_id:
            return Response({
                "errCode": 5,
                "message": "Thiếu id thu ngân"
            }, status=status.HTTP_400_BAD_REQUEST)

        cashier = Cashier.objects.filter(id=cashier_id).first()
        if not cashier:
            return Response({
                "errCode": 6,
                "message": "Không tìm thấy thu ngân"
            }, status=status.HTTP_404_NOT_FOUND)

        # 3️⃣ Xử lý ảnh base64 & Cloudinary
        image_base64 = data.get("image")
        if image_base64 and image_base64.strip() != "":
            try:
                # — Xoá ảnh cũ nếu có
                old_url = cashier.image or ""
                match = re.search(
                    r'/upload/(?:v\d+/)?(?P<public_id>.+?)\.(?:jpg|jpeg|png|gif|webp)',
                    old_url
                )
                if match:
                    cloudinary.uploader.destroy(match.group('public_id'))

                # — Tách định dạng và base64
                if "base64," in image_base64:
                    header, imgstr = image_base64.split(";base64,")
                    mime_type = header.split(":")[1].lower()
                else:
                    imgstr = image_base64
                    mime_type = "image/jpeg"

                # — Kiểm tra MIME hợp lệ
                allowed_mime_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif']
                if mime_type not in allowed_mime_types:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không hỗ trợ: {mime_type}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # — Tạo public_id duy nhất
                ts = int(time.time())
                uid = uuid.uuid4().hex[:8]
                public_id = f"cashier_{ts}_{uid}"

                # — Upload ảnh
                upload = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=public_id,
                    folder="cashiers",
                    resource_type="image"
                )

                secure_url = upload.get("secure_url")
                if not secure_url:
                    raise Exception("Không lấy được URL từ Cloudinary")

                data["image"] = secure_url  # cập nhật ảnh mới

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh base64 hoặc upload ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # 4️⃣ Cập nhật thông tin thu ngân
        serializer = CashierSerializer(cashier, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật thu ngân thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 2,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
@permission_classes([AllowAny])
def get_select_all_doctor(request):
    try:
        # CHỈ LẤY CASHIER có user đang hoạt động (is_active=True)
        doctors = Doctor.objects.select_related('user').filter(user__is_active=True)
        
        doctor_list = []
        for dt in doctors:
            doctor_list.append({
                "value": dt.user_id,
                "label": dt.name,
            })

        return Response({
            "errCode": 0,
            "message": "Lấy danh sách doctor thành công",
            "method": request.method,
            "data": doctor_list
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": []
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_select_all_nurse(request):
    try:
        # CHỈ LẤY CASHIER có user đang hoạt động (is_active=True)
        nurses = Nurse.objects.select_related('user').filter(user__is_active=True)
        
        nurse_list = []
        for dt in nurses:
            nurse_list.append({
                "value": dt.user_id,
                "label": dt.name,
            })

        return Response({
            "errCode": 0,
            "message": "Lấy danh sách doctor thành công",
            "method": request.method,
            "data": nurse_list
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": []
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_doctor_home(request):
    try:
        doctors = Doctor.objects.select_related('user').filter(user__is_active=True)
        doctor_list = []

        for doc in doctors:
            image_url = None

            if doc.image:
                # Giả sử bạn lưu ảnh trên Cloud và đường dẫn ảnh là URL từ cloud
                image_url = doc.image  # Đây là URL ảnh từ cloud

            doctor_list.append({
                "id": doc.id,
                "name": doc.name,
                "user_id": doc.user_id,
                "degree": doc.degree,
                "image": image_url,
            })

        return Response({
            "errCode": 0,
            "message": "Lấy danh sách bác sĩ thành công",
            "method": request.method,
            "data": doctor_list
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": []
        }, status=500)

        
        
@api_view(['GET'])
@permission_classes([AllowAny])
def get_doctor_by_user_id(request):
    try:
        userId = request.GET.get('id')
        if not userId:
            return Response({
                "errCode": 3,
                "message": "Thiếu ID bác sĩ"
            }, status=400)

        doctor = Doctor.objects.get(user_id=userId)

        data = model_to_dict(doctor)

        return Response({
            "errCode": 0,
            "message": "Lấy bác sĩ thành công",
            "method": request.method,
            "data": data
        }, status=200)

    except Doctor.DoesNotExist:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy bác sĩ",
            "data": {}
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
            "error": str(e),
            "data": {}
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_patient_record(request):
    try:
        user = request.user

        data = request.data.copy()
        data["user"] = user.id

        # 📌 Xử lý ảnh base64
        image_base64 = data.get("image")
        if not image_base64 or image_base64.strip() == "":
            return Response({
                "errCode": 10,
                "message": "Ảnh không hợp lệ hoặc không có ảnh"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # — Tách định dạng & nội dung base64
            if "base64," in image_base64:
                header, imgstr = image_base64.split(";base64,")
                mime_type = header.split(":")[1].lower()
            else:
                imgstr = image_base64
                mime_type = "image/jpeg"

            # — Kiểm tra định dạng hợp lệ
            allowed_mime_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif']
            if mime_type not in allowed_mime_types:
                return Response({
                    "errCode": 11,
                    "message": f"Định dạng ảnh không được hỗ trợ: {mime_type}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # — Tạo tên ảnh duy nhất
            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:8]
            public_id = f"patient_{timestamp}_{unique_id}"

            # — Upload lên Cloudinary
            upload_result = cloudinary.uploader.upload(
                base64.b64decode(imgstr),
                public_id=public_id,
                folder="patients",
                resource_type="image"
            )

            secure_url = upload_result.get("secure_url")
            if not secure_url:
                raise Exception("Không lấy được URL từ Cloudinary")

            data["image"] = secure_url

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64 hoặc upload ảnh",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Tạo hồ sơ bệnh nhân
        serializer = PatientSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Tạo hồ sơ bệnh nhân thành công",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "errCode": 1,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def get_all_patient_records_by_user(request):
    try:
        user = request.user
        user_id = user.id

        patients = Patient.objects.filter(user_id=user_id).values("id", "name", "date_of_birth", "image")

        return Response({
            "errCode": 0,
            "message": "Lấy danh sách hồ sơ bệnh nhân thành công",
            "data": patients
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Lỗi khi lấy hồ sơ bệnh nhân: {e}")
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_record_by_id(request):
    try:
        user = request.user

        # Lấy id bệnh nhân từ query string
        patient_id = request.GET.get('id')
        if not patient_id:
            return Response({
                "errCode": 1,
                "message": "Thiếu tham số id trong query string"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Lọc bệnh nhân theo id và user
        patient = Patient.objects.filter(user_id=user.id, id=patient_id).first()
        if not patient:
            return Response({
                "errCode": 9,
                "message": "Bệnh nhân không tồn tại"
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize dữ liệu
        serializer = PatientSerializer(patient)

        return Response({
            "errCode": 0,
            "message": "Lấy hồ sơ bệnh nhân thành công",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def update_patient_record(request):
    try:
        user = request.user
        data = request.data.copy()
        patient_id = data.get("id")

        if not patient_id:
            return Response({"errCode": 1, "message": "Thiếu ID bệnh nhân"}, status=status.HTTP_400_BAD_REQUEST)

        patient = Patient.objects.filter(id=patient_id, user_id=user.id).first()
        if not patient:
            return Response({"errCode": 9, "message": "Hồ sơ bệnh nhân không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        # 📌 Xử lý ảnh mới nếu có
        image_base64 = data.get("image")
        if image_base64 and image_base64.strip() != "":
            try:
                # Tách định dạng & nội dung base64
                if "base64," in image_base64:
                    header, imgstr = image_base64.split(";base64,")
                    mime_type = header.split(":")[1].lower()
                else:
                    imgstr = image_base64
                    mime_type = "image/jpeg"

                # Kiểm tra định dạng hợp lệ
                allowed_mime_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif']
                if mime_type not in allowed_mime_types:
                    return Response({
                        "errCode": 11,
                        "message": f"Định dạng ảnh không được hỗ trợ: {mime_type}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Xoá ảnh cũ nếu tồn tại (URL Cloudinary)
                if patient.image and "cloudinary.com" in patient.image:
                    public_id = patient.image.split("/")[-1].split(".")[0]
                    cloudinary.uploader.destroy(f"patients/{public_id}")

                # Upload ảnh mới lên Cloudinary
                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:8]
                public_id = f"patient_{timestamp}_{unique_id}"

                upload_result = cloudinary.uploader.upload(
                    base64.b64decode(imgstr),
                    public_id=public_id,
                    folder="patients",
                    resource_type="image"
                )

                secure_url = upload_result.get("secure_url")
                if not secure_url:
                    raise Exception("Không lấy được URL từ Cloudinary")

                data["image"] = secure_url

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý hoặc upload ảnh",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["image"] = patient.image  # Không có ảnh mới thì giữ nguyên ảnh cũ

        # 📌 Cập nhật dữ liệu bệnh nhân
        serializer = PatientSerializer(patient, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Cập nhật hồ sơ bệnh nhân thành công",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "errCode": 1,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
