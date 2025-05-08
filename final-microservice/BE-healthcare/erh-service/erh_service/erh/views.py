import requests
import base64
import mimetypes
import os
import uuid
import time
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import VitalSign,Diagnosis
from .serializers import VitalSignSerializer,DiagnosisSerializer
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
        medical_record_id = serializer.validated_data.get("medical_record_id")
        try:
            res = requests.put(
                f"{URL_APM_SV}/api/a/change-status-appointment",
                json={"medical_id": medical_record_id, "status": "ready_for_doctor"}
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
    medical_record_id = request.GET.get('id')
    if not medical_record_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu medical_record_id"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        vital_sign = VitalSign.objects.filter(
            medical_record_id=medical_record_id
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
        medical_record_id = diagnosis_serializer.validated_data.get('medical_record_id')
        list_type_test = request.data.get('listTypeTest', [])

        # Nếu có danh sách xét nghiệm, gọi Lab Service để tạo TestRequest
        if list_type_test:
            try:
                res = requests.post(
                    f"{URL_LAB_SV}/api/l/create-test-requests",
                    json={
                        "medical_record_id": medical_record_id,
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
                json={"medical_id": medical_record_id, "status": "waiting_result"}
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
    medical_record_id = request.GET.get('id')
    if not medical_record_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu medical_record_id"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        diag = Diagnosis.objects.filter(
            medical_record_id=medical_record_id
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
def doctor_update_diagnosis_and_status(request):
    try:
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
        medical_id = request.data.get('medical_record_id')
        final_diagnosis = request.data.get('final_diagnosis')
        uploaded_file = request.FILES.get('image')

        if not medical_id:
            return Response({"errCode": 1, "message": "Thiếu medical_record_id"}, status=400)

        diagnosis = Diagnosis.objects.filter(medical_record_id=medical_id).first()
        if not diagnosis:
            return Response({"errCode": 2, "message": "Không tìm thấy Diagnosis"}, status=200)

        # Gọi API đổi trạng thái appointment
        url = f"{URL_APM_SV}/api/a/change-status-appointment"  # lấy URL từ settings
        response = requests.put(
            url,
            json={"medical_id": medical_id, "status": "prescribed"}
        )
        res_json = response.json()
        if res_json.get("errCode") != 0:
            return Response({"errCode": 3, "message": "Cập nhật trạng thái appointment thất bại"}, status=200)

        # Nếu OK thì tiếp tục cập nhật final_diagnosis và ảnh
        if final_diagnosis:
            diagnosis.final_diagnosis = final_diagnosis

        if uploaded_file:
            ext = os.path.splitext(uploaded_file.name)[-1].lower()
            if ext not in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                return Response({"errCode": 11, "message": f"Định dạng ảnh không hỗ trợ: {ext}"}, status=400)

            os.makedirs(IMAGE_DIAGNOSIS, exist_ok=True)
            file_name = f"{int(time.time())}-{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(IMAGE_DIAGNOSIS, file_name)

            with open(file_path, "wb+") as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)

            diagnosis.image = file_name

        diagnosis.save()
        return Response({"errCode": 0, "message": "Cập nhật diagnosis thành công"}, status=200)

    except Exception as e:
        return Response({
            "errCode": 500,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=500)