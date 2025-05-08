import os
import time
import uuid
import json
import requests
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import MedicineSerializer,PrescriptionSerializer,PrescriptionMedicineSerializer,PaymentMethodSerializer,InvoiceSerializer
from .models import Prescription, PrescriptionMedicine, Medicine,PaymentMethod,Invoice
from django.db import transaction
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser



IMAGE_INVOICE = r"D:\final-microservice\image\invoice"

IMAGE_PRES=r"D:\final-microservice\image\prescription"
URL_USER_SV = "http://localhost:8001"
URL_APPT_SV = "http://localhost:8002"
@api_view(['POST'])  
def create_medicine(request):
    if request.method == 'POST':
        # Tạo serializer từ dữ liệu request
        serializer = MedicineSerializer(data=request.data)
        
        if serializer.is_valid():  # Kiểm tra tính hợp lệ của dữ liệu
            serializer.save()  # Lưu dữ liệu vào database
            return Response({
                'errCode': 0,  # Trả về mã lỗi 0 nếu tạo thành công
                'message': 'Medicine created successfully',
                'data': serializer.data  # Dữ liệu đã tạo
            }, status=status.HTTP_201_CREATED)  # Trả về mã trạng thái HTTP 201 (Created)
        
        return Response({
            'errCode': 1,  # Trả về mã lỗi 1 nếu có lỗi
            'message': 'Invalid data',
            'errors': serializer.errors  # Trả về các lỗi nếu dữ liệu không hợp lệ
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_medicines(request):
    try:
        medicines = Medicine.objects.all()  # Lấy tất cả đối tượng từ DB
        serializer = MedicineSerializer(medicines, many=True)  # Serialize danh sách
        return Response({
            'errCode': 0,
            'message': 'Fetched all medicines successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'errCode': 1,
            'message': f'Error fetching medicines: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def get_all_medicines_active(request):
    try:
        medicines = Medicine.objects.filter(is_active=True).values('id', 'name', 'unit', 'stock', 'price')
        return Response({
            'errCode': 0,
            'message': 'Fetched all active medicines successfully',
            'data': list(medicines)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'errCode': 1,
            'message': f'Error fetching medicines: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@transaction.atomic
def create_prescription_and_prescription_medicines(request):
    try:
        # ✅ Kiểm tra Authorization và xác thực role bác sĩ
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({
                'errCode': 2,
                'message': 'Thiếu hoặc sai định dạng token',
                'data': []
            }, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        # Xác thực vai trò bác sĩ
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-doctor",
            headers={'Authorization': f'Bearer {token}'}
        )

        if response.status_code != 200:
            return Response({
                "errCode": 1,
                "message": "Không xác thực được vai trò bác sĩ (User Service lỗi)",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        response_data = response.json()
        if response_data.get('errCode') != 0:
            return Response({
                "errCode": 1,
                "message": "Bạn không có quyền truy cập với vai trò bác sĩ",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        # ✅ Lấy và kiểm tra dữ liệu
        medical_id = request.data.get('medical_id')
        note = request.data.get('note', '')
        image_file = request.FILES.get('image')
        medicines_data = request.data.get('prescription_medicines')

        if not medical_id or not image_file or not medicines_data:
            return Response({"errCode": 1, "message": "Thiếu thông tin bắt buộc"}, status=400)

        # ✅ Gọi API để thay đổi trạng thái lịch hẹn (done) trước khi tạo đơn thuốc
        change_status_response = requests.put(
            f"{URL_APPT_SV}/api/a/change-status-appointment",
            json={
                'medical_id': medical_id,
                'status': 'done'
            }
        )

        if change_status_response.status_code != 200:
            return Response({
                "errCode": 1,
                "message": "Không thể cập nhật trạng thái lịch hẹn",
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # ✅ Kiểm tra định dạng ảnh
        ext = os.path.splitext(image_file.name)[-1].lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
            return Response({"errCode": 11, "message": f"Định dạng ảnh không hỗ trợ: {ext}"}, status=400)

        os.makedirs(IMAGE_PRES, exist_ok=True)
        file_name = f"{int(time.time())}-{uuid.uuid4().hex[:8]}{ext}"
        file_path = os.path.join(IMAGE_PRES, file_name)

        with open(file_path, "wb+") as dest:
            for chunk in image_file.chunks():
                dest.write(chunk)

        # ✅ Tạo đơn thuốc
        prescription_data = {
            'medical_id': medical_id,
            'note': note,
            'image': file_name
        }

        prescription_serializer = PrescriptionSerializer(data=prescription_data)
        if not prescription_serializer.is_valid():
            return Response({
                "errCode": 2,
                "message": "Dữ liệu đơn thuốc không hợp lệ",
                "errors": prescription_serializer.errors
            }, status=400)

        prescription_serializer.save()

        # ✅ Tạo các thuốc trong đơn
        medicines_list = json.loads(medicines_data)
        for item in medicines_list:
            prescription_medicine_data = {
                'prescription': prescription_serializer.instance.id,
                'medicine': item.get('id'),
                'price': item.get('price'),
                'quantity': item.get('quantity'),
                'directions_for_use': item.get('directions_for_use')
            }

            prescription_medicine_serializer = PrescriptionMedicineSerializer(data=prescription_medicine_data)
            if not prescription_medicine_serializer.is_valid():
                return Response({
                    "errCode": 3,
                    "message": "Dữ liệu thuốc không hợp lệ",
                    "errors": prescription_medicine_serializer.errors
                }, status=400)

            prescription_medicine_serializer.save()

        return Response({"errCode": 0, "message": "Tạo đơn thuốc thành công"}, status=201)

    except Exception as e:
        return Response({
            "errCode": 500,
            "message": f"Lỗi hệ thống: {str(e)}"
        }, status=500)



@api_view(['GET'])
def get_prescription_by_medical_id(request):
    try:
        # Lấy medical_id từ query params
        medical_id = request.GET.get('medical_id')

        if not medical_id:
            return Response({
                "errCode": 1,
                "message": "Thiếu medical_id",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Truy vấn đơn thuốc và các thuốc trong đơn
        try:
            prescription = Prescription.objects.prefetch_related('medicines__medicine').get(medical_id=medical_id)
        except Prescription.DoesNotExist:
            return Response({
                "errCode": 0,
                "message": "Không tìm thấy đơn thuốc",
                "data": {}
            }, status=status.HTTP_200_OK)

        # Tạo response
        result = {
            "id": prescription.id,
            "medical_id": prescription.medical_id,
            "status": prescription.status,
            "note": prescription.note,
            "created_at": prescription.created_at,
            "medicines": []
        }

        # Duyệt qua các thuốc trong đơn và thêm vào response
        for pres_med in prescription.medicines.all():
            result["medicines"].append({
                "prescription_medicine_id": pres_med.id,
                "medicine_id": pres_med.medicine.id,
                "medicine_name": pres_med.medicine.name,
                "stock": pres_med.medicine.stock,
                "price": pres_med.price,
                "quantity": pres_med.quantity,
                "directions_for_use": pres_med.directions_for_use,
                "status": pres_med.status
            })

        # Trả về kết quả
        return Response({
            "errCode": 0,
            "message": "Lấy đơn thuốc thành công",
            "data": result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "errCode": -1,
            "message": f"Lỗi hệ thống: {str(e)}",
            "data": {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def get_active_payment_methods(request):
    try:
        methods = PaymentMethod.objects.filter(is_active=True)
        serializer = PaymentMethodSerializer(methods, many=True)
        return Response({
            "errCode": 0,
            "message": "Lấy danh sách phương thức thanh toán thành công",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "errCode": 1,
            "message": "Lỗi máy chủ: " + str(e),
            "data": []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@transaction.atomic
def create_invoice(request):
    token = request.headers.get('Authorization')
    if not token:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy token trong header"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-pharmacist",
            headers={'Authorization': token}
        )
    except requests.exceptions.RequestException as e:
        return Response({
            "errCode": 1,
            "message": f"Lỗi khi gọi User Service: {str(e)}"
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if response.status_code != 200 or response.json().get('errCode') != 0:
        return Response({
            "errCode": 1,
            "message": "Bạn không có quyền pharmacist"
        }, status=status.HTTP_403_FORBIDDEN)

    pharmacist_id = response.json().get('user_id')

    try:
        prescription_id = request.data.get('prescription_id')
        totals = request.data.get('totals')
        payment_method_id = request.data.get('payment_method_id')
        list_pres_med = json.loads(request.data.get('list_pres_med'))

        image_file = request.FILES.get('image')
        if not image_file:
            return Response({
                "errCode": 10,
                "message": "Không có ảnh được gửi lên"
            }, status=status.HTTP_400_BAD_REQUEST)

        ext = os.path.splitext(image_file.name)[-1].lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
            return Response({
                "errCode": 11,
                "message": f"Định dạng ảnh không hỗ trợ: {ext}"
            }, status=status.HTTP_400_BAD_REQUEST)

        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        file_name = f"{timestamp}-{unique_id}{ext}"

        os.makedirs(IMAGE_INVOICE, exist_ok=True)
        image_path = os.path.join(IMAGE_INVOICE, file_name)
        with open(image_path, 'wb+') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        invoice = Invoice.objects.create(
            pharmacist_id=pharmacist_id,
            totals=totals,
            prescription_id=prescription_id,
            payment_method_id=payment_method_id,
            image=file_name
        )

        prescription = Prescription.objects.get(id=prescription_id)
        prescription.status = 'sold'
        prescription.save()

        for item in list_pres_med:
            pres_med_id = item.get('prescription_medicine_id')
            try:
                pres_med = PrescriptionMedicine.objects.get(id=pres_med_id)
                pres_med.status = 'sold'
                pres_med.save()
            except PrescriptionMedicine.DoesNotExist:
                continue

        return Response({
            "errCode": 0,
            "message": "Tạo hóa đơn thành công"
        })

    except Exception as e:
        return Response({
            "errCode": 13,
            "message": f"Lỗi xử lý dữ liệu: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


