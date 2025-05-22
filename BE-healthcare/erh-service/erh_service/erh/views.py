import requests
import base64
import mimetypes
import os
import uuid
import time
import numpy as np
import joblib
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import VitalSign,Diagnosis
from .serializers import VitalSignSerializer,DiagnosisSerializer
import cloudinary.uploader
URL_APM_SV ='http://localhost:8002'
URL_USER_SV = "http://localhost:8001"
URL_LAB_SV = "http://localhost:8003"

IMAGE_DIAGNOSIS=r"D:\final-microservice\image\diagnosis"
@api_view(['POST'])
@transaction.atomic
def create_vital_sign(request):
    # Lấy token và kiểm tra định dạng
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Thiếu hoặc sai định dạng token',
            'data': []
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # Gọi User Service để kiểm tra vai trò y tá
    try:
        res = requests.get(
            f"{URL_USER_SV}/api/u/check-role-nurse",
            headers={'Authorization': f'Bearer {token}'}
        )
        if res.status_code != 200 or res.json().get("errCode") != 0:
            return Response({
                'errCode': 1,
                'message': 'Không có quyền truy cập với vai trò y tá',
                'data': []
            }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({
            'errCode': 1,
            'message': 'Lỗi khi xác thực vai trò y tá',
            'data': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Xử lý tạo vital sign
    serializer = VitalSignSerializer(data=request.data)
    if serializer.is_valid():
        medical_id = serializer.validated_data.get("medical_id")
        try:
            res = requests.put(
                f"{URL_APM_SV}/api/a/change-status-appointment",
                json={"medical_id": medical_id, "status": "ready_for_doctor"}
            )
            if res.status_code != 200:
                raise Exception("Không thể cập nhật trạng thái lịch hẹn")
        except Exception as e:
            transaction.set_rollback(True)
            return Response({
                "errCode": 1,
                "errMessage": "Không thể cập nhật trạng thái lịch hẹn. Vital sign chưa được lưu.",
                "detail": str(e)
            }, status=400)

        vital_sign = serializer.save()
        return Response({
            "errCode": 0,
            "message": "Tạo thành công và đã cập nhật trạng thái lịch hẹn.",
            "data": VitalSignSerializer(vital_sign).data
        }, status=201)

    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_vital_sign_by_medical_record(request):
    medical_id = request.GET.get('id')
    if not medical_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu medical_id"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        vital_sign = VitalSign.objects.filter(
            medical_id=medical_id
        ).order_by('-created_at').first()

        if not vital_sign:
            return Response({
                "errCode": 0,
                "message": "Không có dữ liệu",
                "data": []  # ✅ Trả về danh sách rỗng
            }, status=status.HTTP_200_OK)

        serializer = VitalSignSerializer(vital_sign)
        return Response({
            "errCode": 0,
            "message": "Lấy dữ liệu thành công",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "errCode": 1,
            "message": "Lỗi khi lấy dữ liệu",
            "detail": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
@transaction.atomic
def create_diagnosis_and_test_requests(request):
    # Lấy token và kiểm tra định dạng
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Thiếu hoặc sai định dạng token',
            'data': []
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # Gọi User Service để kiểm tra vai trò Bác sĩ
    try:
        res = requests.get(
            f"{URL_USER_SV}/api/u/check-role-doctor",
            headers={'Authorization': f'Bearer {token}'}
        )
        if res.status_code != 200 or res.json().get("errCode") != 0:
            return Response({
                'errCode': 1,
                'message': 'Không có quyền truy cập với vai trò Bác sĩ',
                'data': []
            }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({
            'errCode': 1,
            'message': 'Lỗi khi xác thực vai trò Bác sĩ',
            'data': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Sử dụng serializer để kiểm tra tính hợp lệ của dữ liệu
    diagnosis_serializer = DiagnosisSerializer(data=request.data)

    if diagnosis_serializer.is_valid():
        medical_id = diagnosis_serializer.validated_data.get('medical_id')
        list_type_test = request.data.get('listTypeTest', [])

        # Nếu có danh sách xét nghiệm, gọi Lab Service để tạo TestRequest
        if list_type_test:
            try:
                res = requests.post(
                    f"{URL_LAB_SV}/api/l/create-test-requests",
                    json={
                        "medical_id": medical_id,
                        "listTypeTest": list_type_test
                    },
                    headers={'Authorization': f'Bearer {token}'}
                )
                res_data = res.json()

                if res.status_code != 201 or res_data.get("errCode") != 0:
                    return Response({
                        'errCode': 1,
                        'message': 'Tạo TestRequest thất bại từ Lab Service',
                        'data': res_data
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except requests.RequestException as e:
                return Response({
                    'errCode': 1,
                    'message': 'Lỗi khi gọi Lab Service',
                    'data': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Gọi Appointment Service để đổi trạng thái thành "waiting_result"
        try:
            res = requests.put(
                f"{URL_APM_SV}/api/a/change-status-appointment",
                json={"medical_id": medical_id, "status": "waiting_result"}
            )
            if res.status_code != 200 or res.json().get("errCode") != 0:
                return Response({
                    'errCode': 1,
                    'message': 'Không thể cập nhật trạng thái appointment',
                    'data': res.json()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except requests.RequestException as e:
            return Response({
                'errCode': 1,
                'message': 'Lỗi khi gọi Appointment Service',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Tạo diagnosis
        diagnosis = diagnosis_serializer.save()

        return Response({
            'errCode': 0,
            'message': 'Tạo Diagnosis thành công.',
            'data': DiagnosisSerializer(diagnosis).data
        }, status=status.HTTP_201_CREATED)

    else:
        return Response({
            'errCode': 1,
            'message': 'Dữ liệu không hợp lệ.',
            'data': diagnosis_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_diagnosis_by_medical_record(request):
    medical_id = request.GET.get('id')
    if not medical_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu medical_id"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        diag = Diagnosis.objects.filter(
            medical_id=medical_id
        ).order_by('-created_at').first()

        if not diag:
            return Response({
                "errCode": 0,
                "message": "Không có dữ liệu",
                "data": []   # ✅ Trả về danh sách rỗng
            }, status=status.HTTP_200_OK)

        serializer = DiagnosisSerializer(diag)
        return Response({
            "errCode": 0,
            "message": "Lấy dữ liệu thành công",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "errCode": 1,
            "message": "Lỗi khi lấy dữ liệu",
            "detail": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
@api_view(['PUT'])
@transaction.atomic
def doctor_update_diagnosis_and_status(request):
    try:
        # 1. Kiểm tra token và role bác sĩ
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({
                'errCode': 2,
                'message': 'Thiếu hoặc sai định dạng token',
                'data': []
            }, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        res = requests.get(
            f"{URL_USER_SV}/api/u/check-role-doctor",
            headers={'Authorization': f'Bearer {token}'}
        )
        if res.status_code != 200 or res.json().get("errCode") != 0:
            return Response({
                'errCode': 1,
                'message': 'Không có quyền truy cập với vai trò Bác sĩ',
                'data': []
            }, status=status.HTTP_403_FORBIDDEN)

        # 2. Lấy dữ liệu từ request
        medical_id = request.data.get('medical_id')
        final_diagnosis = request.data.get('final_diagnosis')
        uploaded_file = request.FILES.get('image')
        print(uploaded_file)
        if not medical_id:
            return Response({"errCode": 1, "message": "Thiếu medical_id"}, status=400)

        # 3. Tìm diagnosis theo medical_id
        diagnosis = Diagnosis.objects.filter(medical_id=medical_id).first()
        if not diagnosis:
            return Response({"errCode": 2, "message": "Không tìm thấy Diagnosis"}, status=404)

        # 4. Cập nhật final_diagnosis nếu có
        if final_diagnosis:
            diagnosis.final_diagnosis = final_diagnosis

        # 5. Upload ảnh nếu có
        if uploaded_file:
            ext = os.path.splitext(uploaded_file.name)[-1].lower()
            if ext not in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                return Response({"errCode": 11, "message": f"Định dạng ảnh không hỗ trợ: {ext}"}, status=400)

            try:
                timestamp = int(time.time())
                unique_id = uuid.uuid4().hex[:12]
                public_id = f"diagnosis_{timestamp}-{unique_id}"  # Không cần đuôi .png

                result = cloudinary.uploader.upload(
                    uploaded_file,
                    public_id=public_id,
                    folder="diagnosis",              # ✅ Chỉ định thư mục diagnosis
                    resource_type="image"
                )
                diagnosis.image = result.get("secure_url")

            except Exception as e:
                return Response({
                    "errCode": 12,
                    "message": f"Lỗi upload ảnh lên Cloudinary: {str(e)}"
                }, status=500)

        # 6. Gọi API cập nhật trạng thái appointment
        response = requests.put(
            f"{URL_APM_SV}/api/a/change-status-appointment",
            json={"medical_id": medical_id, "status": "prescribed"}
        )
        res_json = response.json()
        if res_json.get("errCode") != 0:
            return Response({"errCode": 3, "message": "Cập nhật trạng thái appointment thất bại"}, status=200)

        # 7. Lưu thay đổi
        diagnosis.save()

        return Response({"errCode": 0, "message": "Cập nhật diagnosis thành công"}, status=200)

    except Exception as e:
        return Response({
            "errCode": 500,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=500)
      
        
        
@api_view(['GET'])
def get_image_diagnosi_by_medical_id(request):
    medical_id = request.GET.get('medical_id')

    if not medical_id:
        return Response({
            "errCode": 1,
            "message": "medical_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    diagnosis = Diagnosis.objects.filter(medical_id=medical_id).first()

    if not diagnosis:
        return Response({
            "errCode": 2,
            "message": "Diagnosis not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Nếu có ảnh thì đọc và chuyển base64
    if diagnosis.image:
        image_path = os.path.join(IMAGE_DIAGNOSIS, diagnosis.image)
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
                mime_type, _ = mimetypes.guess_type(image_path)
                if mime_type:
                    diagnosis.image = f"data:{mime_type};base64,{encoded}"
                else:
                    diagnosis.image = None
        else:
            diagnosis.image = None

    # Trả về kết quả
    return Response({
        "errCode": 0,
        "message": "Success",
        "data": {      
            "image": diagnosis.image,
        }
    }, status=status.HTTP_200_OK)
    

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Đường dẫn file model trong thư mục ml_model (cùng cấp với app)
MODEL_PATH = os.path.join(BASE_DIR, 'ml_model', 'best_heart_model.pkl')

# Load model
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print(f"File model không tìm thấy tại: {MODEL_PATH}")

def predict_heart_disease(features):
    if model is None:
        raise Exception("Model chưa được load, vui lòng kiểm tra lại file model.")
    data = np.array(features).reshape(1, -1)
    pred = model.predict(data)[0]
    if pred == 1:
        return 1, "Có nguy cơ mắc bệnh tim 💔"
    else:
        return 0, "Không bị bệnh tim ❤️"

@api_view(['POST'])
def predict_heart(request):
    features = request.data.get('features', [])

    if not isinstance(features, list):
        return Response(
            {"errCode": 1,
             "error": "Trường 'features' phải là một danh sách."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(features) != 13:
        return Response(
            {"errCode": 1,
             "error": "Cần cung cấp đúng 13 giá trị đặc trưng để dự đoán."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        label, message = predict_heart_disease(features)
        return Response({
            "errCode": 0,
            "data": {
                "label": label,       # 0 hoặc 1
                "message": message    # Chuỗi mô tả
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"errCode": 1,
             "error": f"Lỗi dự đoán: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
