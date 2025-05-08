# 🔹 Python Standard Library
import os
import time
import uuid
import logging
import base64
import mimetypes
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
@transaction.atomic
def create_doctor(request):
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
            user = User.objects.get(id=user_id)

            if user.role != 'admin':
                return Response({"errCode": 4, "message": "Bạn không có quyền tạo bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

        except jwt.ExpiredSignatureError:
            return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"errCode": 8, "message": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        # 📌 Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=data.get("email")).exists():
            return Response({"errCode": 9, "message": "Email đã được sử dụng"}, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Xử lý ảnh base64
        image_base64 = data.get("image")
        if not image_base64 or image_base64.strip() == "":
            return Response({
                "errCode": 10,
                "message": "Ảnh không hợp lệ hoặc không có ảnh"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if "base64," in image_base64:
                format_info, imgstr = image_base64.split(";base64,")
                mime_type = format_info.split(":")[-1].lower()  # ví dụ: image/png
                ext = mimetypes.guess_extension(mime_type) or '.jpg'
                ext = ext.lstrip('.')  # bỏ dấu chấm
            else:
                imgstr = image_base64
                ext = "jpg"  # fallback

            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                return Response({
                    "errCode": 11,
                    "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                }, status=status.HTTP_400_BAD_REQUEST)

            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:8]
            file_name = f"{timestamp}-{unique_id}.{ext}"

            os.makedirs(IMAGE_DOCTOR, exist_ok=True)
            image_path = os.path.join(IMAGE_DOCTOR, file_name)
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(imgstr))

            data["image"] = file_name  # lưu tên file vào DB

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Tạo user mới cho bác sĩ
        new_user = User.objects.create_user(
            email=data.get("email"),
            password=data.get("password"),
            role="doctor"
        )
        data["user"] = new_user.id

        # 📌 Tạo bác sĩ
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

    except Exception as e:
        logger.error(f"Lỗi tạo bác sĩ: {e}")
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

        # Đọc ảnh và chuyển sang base64 định dạng chuẩn
        data['image_name']=doctor.image
        image_base64 = ""
        if doctor.image:
            image_path = os.path.join(IMAGE_DOCTOR, doctor.image)
            if os.path.exists(image_path):
                mime_type, _ = mimetypes.guess_type(image_path)
                if mime_type:
                    with open(image_path, 'rb') as img_file:
                        encoded = base64.b64encode(img_file.read()).decode('utf-8')
                        image_base64 = f"data:{mime_type};base64,{encoded}"

        data['image'] = image_base64

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
        
@api_view(['PUT'])
@transaction.atomic
def update_doctor(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"errCode": 3, "message": "Thiếu hoặc sai định dạng token"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get('user_id')

        User = get_user_model()
        user = User.objects.get(id=user_id)

        if user.role != 'admin':
            return Response({"errCode": 4, "message": "Bạn không có quyền cập nhật bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        doctor_id = data.get("id")
        if not doctor_id:
            return Response({"errCode": 5, "message": "Thiếu id bác sĩ"}, status=status.HTTP_400_BAD_REQUEST)

        doctor = Doctor.objects.filter(id=doctor_id).first()
        if not doctor:
            return Response({"errCode": 6, "message": "Không tìm thấy bác sĩ"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Xoá ảnh cũ
        old_image_name = data.get("image_name")
        if old_image_name:
            old_path = os.path.join(IMAGE_DOCTOR, old_image_name)
            if os.path.exists(old_path):
                os.remove(old_path)

        # ✅ Xử lý ảnh mới
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
                        "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:8]
                file_name = f"{timestamp}-{unique_id}.{ext}"

                os.makedirs(IMAGE_DOCTOR, exist_ok=True)
                image_path = os.path.join(IMAGE_DOCTOR, file_name)
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(imgstr))

                data["image"] = file_name  # cập nhật ảnh mới vào DB
            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh base64",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Cập nhật bác sĩ
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

    except jwt.ExpiredSignatureError:
        return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@api_view(['POST'])
@transaction.atomic
def create_nurse(request):
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
            user = User.objects.get(id=user_id)

            if user.role != 'admin':
                return Response({"errCode": 4, "message": "Bạn không có quyền tạo bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

        except jwt.ExpiredSignatureError:
            return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"errCode": 8, "message": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        # 📌 Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=data.get("email")).exists():
            return Response({"errCode": 9, "message": "Email đã được sử dụng"}, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Xử lý ảnh base64
        image_base64 = data.get("image")
        if not image_base64 or image_base64.strip() == "":
            return Response({
                "errCode": 10,
                "message": "Ảnh không hợp lệ hoặc không có ảnh"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if "base64," in image_base64:
                format_info, imgstr = image_base64.split(";base64,")
                mime_type = format_info.split(":")[-1].lower()  # ví dụ: image/png
                ext = mimetypes.guess_extension(mime_type) or '.jpg'
                ext = ext.lstrip('.')  # bỏ dấu chấm
            else:
                imgstr = image_base64
                ext = "jpg"  # fallback

            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                return Response({
                    "errCode": 11,
                    "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                }, status=status.HTTP_400_BAD_REQUEST)

            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:8]
            file_name = f"{timestamp}-{unique_id}.{ext}"

            os.makedirs(IMAGE_NURSE, exist_ok=True)
            image_path = os.path.join(IMAGE_NURSE, file_name)
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(imgstr))

            data["image"] = file_name  # lưu tên file vào DB

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Tạo user mới cho y tá
        new_user = User.objects.create_user(
            email=data.get("email"),
            password=data.get("password"),
            role="nurse"
        )
        data["user"] = new_user.id

        # 📌 Tạo bác sĩ
        serializer = NurseSerializer(data=data)
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

    except Exception as e:
        logger.error(f"Lỗi tạo y tá: {e}")
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

        data = model_to_dict(nurse)

        # Đọc ảnh và chuyển sang base64 định dạng chuẩn
        data['image_name']=nurse.image
        image_base64 = ""
        if nurse.image:
            image_path = os.path.join(IMAGE_NURSE, nurse.image)
            if os.path.exists(image_path):
                mime_type, _ = mimetypes.guess_type(image_path)
                if mime_type:
                    with open(image_path, 'rb') as img_file:
                        encoded = base64.b64encode(img_file.read()).decode('utf-8')
                        image_base64 = f"data:{mime_type};base64,{encoded}"

        data['image'] = image_base64

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
        
       
@api_view(['PUT'])
@transaction.atomic
def update_nurse(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"errCode": 3, "message": "Thiếu hoặc sai định dạng token"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get('user_id')

        User = get_user_model()
        user = User.objects.get(id=user_id)

        if user.role != 'admin':
            return Response({"errCode": 4, "message": "Bạn không có quyền cập nhật bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        nurse_id = data.get("id")
        if not nurse_id:
            return Response({"errCode": 5, "message": "Thiếu id bác sĩ"}, status=status.HTTP_400_BAD_REQUEST)

        nurse = Nurse.objects.filter(id=nurse_id).first()
        if not nurse:
            return Response({"errCode": 6, "message": "Không tìm thấy bác sĩ"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Xoá ảnh cũ
        old_image_name = data.get("image_name")
        if old_image_name:
            old_path = os.path.join(IMAGE_NURSE, old_image_name)
            if os.path.exists(old_path):
                os.remove(old_path)

        # ✅ Xử lý ảnh mới
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
                        "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:8]
                file_name = f"{timestamp}-{unique_id}.{ext}"

                os.makedirs(IMAGE_NURSE, exist_ok=True)
                image_path = os.path.join(IMAGE_NURSE, file_name)
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(imgstr))

                data["image"] = file_name  # cập nhật ảnh mới vào DB
            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh base64",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Cập nhật bác sĩ
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

    except jwt.ExpiredSignatureError:
        return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
      

@api_view(['POST'])
@transaction.atomic
def create_technician(request):
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
            user = User.objects.get(id=user_id)

            if user.role != 'admin':
                return Response({"errCode": 4, "message": "Bạn không có quyền tạo bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

        except jwt.ExpiredSignatureError:
            return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"errCode": 8, "message": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        # 📌 Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=data.get("email")).exists():
            return Response({"errCode": 9, "message": "Email đã được sử dụng"}, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Xử lý ảnh base64
        image_base64 = data.get("image")
        if not image_base64 or image_base64.strip() == "":
            return Response({
                "errCode": 10,
                "message": "Ảnh không hợp lệ hoặc không có ảnh"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if "base64," in image_base64:
                format_info, imgstr = image_base64.split(";base64,")
                mime_type = format_info.split(":")[-1].lower()  # ví dụ: image/png
                ext = mimetypes.guess_extension(mime_type) or '.jpg'
                ext = ext.lstrip('.')  # bỏ dấu chấm
            else:
                imgstr = image_base64
                ext = "jpg"  # fallback

            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                return Response({
                    "errCode": 11,
                    "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                }, status=status.HTTP_400_BAD_REQUEST)

            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:8]
            file_name = f"{timestamp}-{unique_id}.{ext}"

            os.makedirs(IMAGE_TECH, exist_ok=True)
            image_path = os.path.join(IMAGE_TECH, file_name)
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(imgstr))

            data["image"] = file_name  # lưu tên file vào DB

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Tạo user mới cho y tá
        new_user = User.objects.create_user(
            email=data.get("email"),
            password=data.get("password"),
            role="technician"
        )
        data["user"] = new_user.id

        # 📌 Tạo bác sĩ
        serializer = TechnicianSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Tạo Kĩ thuật viên thành công",
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

    except Exception as e:
        logger.error(f"Lỗi tạo kĩ thuật viên: {e}")
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

        # Đọc ảnh và chuyển sang base64 định dạng chuẩn
        data['image_name']=technician.image
        image_base64 = ""
        if technician.image:
            image_path = os.path.join(IMAGE_TECH, technician.image)
            if os.path.exists(image_path):
                mime_type, _ = mimetypes.guess_type(image_path)
                if mime_type:
                    with open(image_path, 'rb') as img_file:
                        encoded = base64.b64encode(img_file.read()).decode('utf-8')
                        image_base64 = f"data:{mime_type};base64,{encoded}"

        data['image'] = image_base64

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
@transaction.atomic
def update_technician(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"errCode": 3, "message": "Thiếu hoặc sai định dạng token"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get('user_id')

        User = get_user_model()
        user = User.objects.get(id=user_id)

        if user.role != 'admin':
            return Response({"errCode": 4, "message": "Bạn không có quyền cập nhật bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        technician_id = data.get("id")
        if not technician_id:
            return Response({"errCode": 5, "message": "Thiếu id bác sĩ"}, status=status.HTTP_400_BAD_REQUEST)

        technician = Technician.objects.filter(id=technician_id).first()
        if not technician:
            return Response({"errCode": 6, "message": "Không tìm thấy bác sĩ"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Xoá ảnh cũ
        old_image_name = data.get("image_name")
        if old_image_name:
            old_path = os.path.join(IMAGE_TECH, old_image_name)
            if os.path.exists(old_path):
                os.remove(old_path)

        # ✅ Xử lý ảnh mới
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
                        "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:8]
                file_name = f"{timestamp}-{unique_id}.{ext}"

                os.makedirs(IMAGE_TECH, exist_ok=True)
                image_path = os.path.join(IMAGE_TECH, file_name)
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(imgstr))

                data["image"] = file_name  # cập nhật ảnh mới vào DB
            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh base64",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Cập nhật bác sĩ
        serializer = TechnicianSerializer(technician, data=data, partial=True)
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

    except jwt.ExpiredSignatureError:
        return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi không xác định",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

@api_view(['POST'])
@transaction.atomic
def create_pharmacist(request):
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
            user = User.objects.get(id=user_id)

            if user.role != 'admin':
                return Response({"errCode": 4, "message": "Bạn không có quyền tạo bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

        except jwt.ExpiredSignatureError:
            return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"errCode": 8, "message": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        # 📌 Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=data.get("email")).exists():
            return Response({"errCode": 9, "message": "Email đã được sử dụng"}, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Xử lý ảnh base64
        image_base64 = data.get("image")
        if not image_base64 or image_base64.strip() == "":
            return Response({
                "errCode": 10,
                "message": "Ảnh không hợp lệ hoặc không có ảnh"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if "base64," in image_base64:
                format_info, imgstr = image_base64.split(";base64,")
                mime_type = format_info.split(":")[-1].lower()  # ví dụ: image/png
                ext = mimetypes.guess_extension(mime_type) or '.jpg'
                ext = ext.lstrip('.')  # bỏ dấu chấm
            else:
                imgstr = image_base64
                ext = "jpg"  # fallback

            if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
                return Response({
                    "errCode": 11,
                    "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                }, status=status.HTTP_400_BAD_REQUEST)

            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:8]
            file_name = f"{timestamp}-{unique_id}.{ext}"

            os.makedirs(IMAGE_PHARMA, exist_ok=True)
            image_path = os.path.join(IMAGE_PHARMA, file_name)
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(imgstr))

            data["image"] = file_name  # lưu tên file vào DB

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Tạo user mới cho y tá
        new_user = User.objects.create_user(
            email=data.get("email"),
            password=data.get("password"),
            role="pharmacist"
        )
        data["user"] = new_user.id

        # 📌 Tạo bác sĩ
        serializer = PharmacistSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Tạo Kĩ thuật viên thành công",
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

        # Đọc ảnh và chuyển sang base64 định dạng chuẩn
        data['image_name']=pharmacist.image
        image_base64 = ""
        if pharmacist.image:
            image_path = os.path.join(IMAGE_PHARMA, pharmacist.image)
            if os.path.exists(image_path):
                mime_type, _ = mimetypes.guess_type(image_path)
                if mime_type:
                    with open(image_path, 'rb') as img_file:
                        encoded = base64.b64encode(img_file.read()).decode('utf-8')
                        image_base64 = f"data:{mime_type};base64,{encoded}"

        data['image'] = image_base64

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
@transaction.atomic
def update_pharmacist(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"errCode": 3, "message": "Thiếu hoặc sai định dạng token"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get('user_id')

        User = get_user_model()
        user = User.objects.get(id=user_id)

        if user.role != 'admin':
            return Response({"errCode": 4, "message": "Bạn không có quyền cập nhật bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        pharmacist_id = data.get("id")
        if not pharmacist_id:
            return Response({"errCode": 5, "message": "Thiếu id bác sĩ"}, status=status.HTTP_400_BAD_REQUEST)

        pharmacist = Pharmacist.objects.filter(id=pharmacist_id).first()
        if not pharmacist:
            return Response({"errCode": 6, "message": "Không tìm thấy bác sĩ"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Xoá ảnh cũ
        old_image_name = data.get("image_name")
        if old_image_name:
            old_path = os.path.join(IMAGE_PHARMA, old_image_name)
            if os.path.exists(old_path):
                os.remove(old_path)

        # ✅ Xử lý ảnh mới
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
                        "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:8]
                file_name = f"{timestamp}-{unique_id}.{ext}"

                os.makedirs(IMAGE_PHARMA, exist_ok=True)
                image_path = os.path.join(IMAGE_PHARMA, file_name)
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(imgstr))

                data["image"] = file_name  # cập nhật ảnh mới vào DB
            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh base64",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Cập nhật bác sĩ
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

    except jwt.ExpiredSignatureError:
        return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
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
        if not user.is_authenticated:
            return Response({"errCode": 3, "message": "Chưa xác thực"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.role != 'admin':
            return Response({"errCode": 4, "message": "Bạn không có quyền tạo thu ngân"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        # 📌 Kiểm tra email đã tồn tại chưa
        User = get_user_model()
        if User.objects.filter(email=data.get("email")).exists():
            return Response({"errCode": 9, "message": "Email đã được sử dụng"}, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Xử lý ảnh base64
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
                    "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                }, status=status.HTTP_400_BAD_REQUEST)

            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:8]
            file_name = f"{timestamp}-{unique_id}.{ext}"

            os.makedirs(IMAGE_CASHIER, exist_ok=True)
            image_path = os.path.join(IMAGE_CASHIER, file_name)
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(imgstr))

            data["image"] = file_name

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Tạo user mới cho thu ngân
        new_user = User.objects.create_user(
            email=data.get("email"),
            password=data.get("password"),
            role="cashier"
        )
        data["user"] = new_user.id

        serializer = CashierSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "errCode": 0,
                "message": "Tạo thu ngân thành công",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        new_user.delete()
        return Response({
            "errCode": 1,
            "message": "Lỗi dữ liệu đầu vào",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Lỗi tạo thu ngân: {e}")
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

        # Đọc ảnh và chuyển sang base64 định dạng chuẩn
        data['image_name']=cashier.image
        image_base64 = ""
        if cashier.image:
            image_path = os.path.join(IMAGE_CASHIER, cashier.image)
            if os.path.exists(image_path):
                mime_type, _ = mimetypes.guess_type(image_path)
                if mime_type:
                    with open(image_path, 'rb') as img_file:
                        encoded = base64.b64encode(img_file.read()).decode('utf-8')
                        image_base64 = f"data:{mime_type};base64,{encoded}"

        data['image'] = image_base64

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
        user = request.user  # <-- Đã có user ở đây
        cashier = Cashier.objects.filter(user=user).first()

        if cashier:
            data = {
                "name": cashier.name
            }
        else:
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
def get_doctor_by_token(request):
    try:
        user = request.user  # <-- Đã có user ở đây
        doctor = Doctor.objects.filter(user=user).first()

        if doctor:
            data = {
                "name": doctor.name
            }
        else:
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
        user = request.user  # <-- Đã có user ở đây
        tech = Technician.objects.filter(user=user).first()

        if tech:
            data = {
                "name": tech.name
            }
        else:
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
def get_pharmacist_by_token(request):
    try:
        user = request.user  # <-- Đã có user ở đây
        phar = Pharmacist.objects.filter(user=user).first()

        if phar:
            data = {
                "name": phar.name
            }
        else:
            data = {}

        return Response({
            "errCode": 0,
            "message": "Truy vấn thành công",
            "data": data
        })

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "method": request.method,
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
@transaction.atomic
def update_cashier(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"errCode": 3, "message": "Thiếu hoặc sai định dạng token"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get('user_id')

        User = get_user_model()
        user = User.objects.get(id=user_id)

        if user.role != 'admin':
            return Response({"errCode": 4, "message": "Bạn không có quyền cập nhật bác sĩ"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        cashier_id = data.get("id")
        if not cashier_id:
            return Response({"errCode": 5, "message": "Thiếu id bác sĩ"}, status=status.HTTP_400_BAD_REQUEST)

        cashier = Cashier.objects.filter(id=cashier_id).first()
        if not cashier:
            return Response({"errCode": 6, "message": "Không tìm thấy bác sĩ"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Xoá ảnh cũ
        old_image_name = data.get("image_name")
        if old_image_name:
            old_path = os.path.join(IMAGE_CASHIER, old_image_name)
            if os.path.exists(old_path):
                os.remove(old_path)

        # ✅ Xử lý ảnh mới
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
                        "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:8]
                file_name = f"{timestamp}-{unique_id}.{ext}"

                os.makedirs(IMAGE_CASHIER, exist_ok=True)
                image_path = os.path.join(IMAGE_CASHIER, file_name)
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(imgstr))

                data["image"] = file_name  # cập nhật ảnh mới vào DB
            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh base64",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Cập nhật bác sĩ
        serializer = CashierSerializer(cashier, data=data, partial=True)
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

    except jwt.ExpiredSignatureError:
        return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
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
            image_path = os.path.join(IMAGE_DOCTOR, doc.image or "")
            image_base64 = None

            if os.path.isfile(image_path):
                mime_type, _ = mimetypes.guess_type(image_path)
                with open(image_path, 'rb') as img_file:
                    base64_str = base64.b64encode(img_file.read()).decode('utf-8')
                    if mime_type:
                        image_base64 = f"data:{mime_type};base64,{base64_str}"
                    else:
                        image_base64 = base64_str

            doctor_list.append({
                "id": doc.id,
                "name": doc.name,
                "user_id": doc.user_id,
                "degree": doc.degree,
                "image": image_base64,
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

        # Đọc ảnh và chuyển sang base64 định dạng chuẩn
        data['image_name']=doctor.image
        image_base64 = ""
        if doctor.image:
            image_path = os.path.join(IMAGE_DOCTOR, doctor.image)
            if os.path.exists(image_path):
                mime_type, _ = mimetypes.guess_type(image_path)
                if mime_type:
                    with open(image_path, 'rb') as img_file:
                        encoded = base64.b64encode(img_file.read()).decode('utf-8')
                        image_base64 = f"data:{mime_type};base64,{encoded}"

        data['image'] = image_base64

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
@transaction.atomic
def create_patient_record(request):
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
            user = User.objects.get(id=user_id)

        except jwt.ExpiredSignatureError:
            return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"errCode": 8, "message": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        # 📌 Chuẩn bị dữ liệu gửi sang serializer
        data = request.data.copy()
        data["user"] = user_id  # Gán ID người dùng vào trường user (ForeignKey)

        # 📌 Xử lý ảnh base64
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
                    "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                }, status=status.HTTP_400_BAD_REQUEST)

            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex[:8]
            file_name = f"{timestamp}-{unique_id}.{ext}"

            os.makedirs(IMAGE_PATIENT, exist_ok=True)
            image_path = os.path.join(IMAGE_PATIENT, file_name)
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(imgstr))

            data["image"] = file_name  # Gán tên ảnh mới vào data

        except Exception as e:
            return Response({
                "errCode": 12,
                "message": "Lỗi xử lý ảnh base64",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        # 📌 Gửi sang serializer để lưu Nurse
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
        logger.error(f"Lỗi tạo Hồ sơ bẹnh nhân: {e}")
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

        result = []
        for patient in patients:
            data = {
                "id": patient["id"],
                "name": patient["name"],
                "date_of_birth": patient["date_of_birth"],
                "image_name": patient["image"],
                "image": ""
            }

            if patient["image"]:
                image_path = os.path.join(IMAGE_PATIENT, patient["image"])
                if os.path.exists(image_path):
                    mime_type, _ = mimetypes.guess_type(image_path)
                    if mime_type:
                        with open(image_path, "rb") as img_file:
                            encoded = base64.b64encode(img_file.read()).decode("utf-8")
                            data["image"] = f"data:{mime_type};base64,{encoded}"

            result.append(data)

        return Response({
            "errCode": 0,
            "message": "Lấy danh sách hồ sơ bệnh nhân thành công",
            "data": result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Lỗi khi lấy hồ sơ bệnh nhân: {e}")
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
@api_view(['GET'])
def get_patient_record_by_id(request):
    try:
        # Lấy token từ header
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
            user = User.objects.get(id=user_id)  # Kiểm tra user tồn tại

        except jwt.ExpiredSignatureError:
            return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"errCode": 8, "message": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        # Lấy id từ query string
        patient_id = request.GET.get('id')  # Lấy giá trị id từ query string

        if not patient_id:
            return Response({"errCode": 1, "message": "Thiếu tham số id trong query string"}, status=status.HTTP_400_BAD_REQUEST)

        # Lấy hồ sơ bệnh nhân theo user_id và patient_id
        patient = Patient.objects.filter(user_id=user_id, id=patient_id).first()

        if not patient:
            return Response({"errCode": 9, "message": "Bệnh nhân không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize dữ liệu
        patient_data = PatientSerializer(patient).data

        # Trả về hình ảnh base64 và tên tệp hình ảnh gốc
        if patient.image:
            image_path = os.path.join(IMAGE_PATIENT, patient.image)
            
            # Xử lý hình ảnh base64
            if os.path.exists(image_path):
                mime_type, _ = mimetypes.guess_type(image_path)
                if mime_type:
                    with open(image_path, "rb") as img_file:
                        encoded = base64.b64encode(img_file.read()).decode("utf-8")
                        patient_data["image"] = f"data:{mime_type};base64,{encoded}"
            
            # Thêm trường 'image_name' chứa tên tệp gốc
            patient_data["image_name"] = patient.image

        return Response({
            "errCode": 0,
            "message": "Lấy hồ sơ bệnh nhân thành công",
            "data": patient_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Lỗi khi lấy hồ sơ bệnh nhân: {e}")
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@transaction.atomic
def update_patient_record(request):
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
            user = User.objects.get(id=user_id)

        except jwt.ExpiredSignatureError:
            return Response({"errCode": 5, "message": "Token đã hết hạn"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"errCode": 6, "message": "Token không hợp lệ"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"errCode": 8, "message": "Người dùng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        # 📌 Lấy ID hồ sơ cần sửa từ body
        data = request.data.copy()
        patient_id = data.get("id")

        if not patient_id:
            return Response({"errCode": 1, "message": "Thiếu ID bệnh nhân"}, status=status.HTTP_400_BAD_REQUEST)

        patient = Patient.objects.filter(id=patient_id, user_id=user_id).first()
        if not patient:
            return Response({"errCode": 9, "message": "Hồ sơ bệnh nhân không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        # 📌 Xoá ảnh cũ nếu có image_name
        old_image_name = data.get("image_name")
        if old_image_name:
            old_image_path = os.path.join(IMAGE_PATIENT, old_image_name)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        # 📌 Xử lý ảnh base64 mới nếu có
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
                        "message": f"Định dạng ảnh không được hỗ trợ: {ext}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:8]
                file_name = f"{timestamp}-{unique_id}.{ext}"

                os.makedirs(IMAGE_PATIENT, exist_ok=True)
                image_path = os.path.join(IMAGE_PATIENT, file_name)
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(imgstr))

                data["image"] = file_name  # Gán tên file ảnh mới
            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": "Lỗi xử lý ảnh base64",
                    "error": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            data["image"] = patient.image  # Không gửi ảnh mới thì giữ lại ảnh cũ

        # 📌 Cập nhật dữ liệu
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
        logger.error(f"Lỗi cập nhật hồ sơ bệnh nhân: {e}")
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
