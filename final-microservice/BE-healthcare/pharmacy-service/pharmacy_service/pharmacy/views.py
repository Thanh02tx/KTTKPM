import os
import time
import uuid
import json
import base64
import mimetypes
import requests
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import MedicineSerializer,PrescriptionSerializer,PrescriptionMedicineSerializer,PaymentMethodSerializer,InvoiceSerializer
from .models import Prescription, PrescriptionMedicine, Medicine,PaymentMethod,Invoice
from django.db import transaction
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader


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
        # ✅ 1. Kiểm tra token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'errCode': 2, 'message': 'Thiếu hoặc sai token'}, status=401)
        token = auth_header.split(' ')[1]

        # ✅ 2. Kiểm tra vai trò bác sĩ
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-doctor",
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code != 200 or response.json().get('errCode') != 0:
            return Response({'errCode': 1, 'message': 'Không phải bác sĩ'}, status=403)

        # ✅ 3. Lấy dữ liệu từ request
        medical_id = request.data.get('medical_id')
        note = request.data.get('note', '')
        image_file = request.FILES.get('image')
        medicines_data = request.data.get('prescription_medicines')

        if not medical_id or not image_file or not medicines_data:
            return Response({'errCode': 1, 'message': 'Thiếu thông tin bắt buộc'}, status=400)

        # ✅ 4. Kiểm tra định dạng ảnh
        ext = os.path.splitext(image_file.name)[-1].lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
            return Response({'errCode': 11, 'message': f'Định dạng ảnh không hỗ trợ: {ext}'}, status=400)

        # ✅ 5. Upload ảnh lên Cloudinary (vào thư mục 'prescriptions')
        file_name = f"prescription_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        upload_result = cloudinary.uploader.upload(
            image_file,
            public_id=file_name,
            folder="prescriptions",           # 🔥 Chỉ định đúng thư mục
            resource_type="image",
            overwrite=True
        )
        cloudinary_url = upload_result.get('secure_url')

        # ✅ 6. Tạo đơn thuốc
        prescription_data = {
            'medical_id': medical_id,
            'note': note,
            'image': cloudinary_url
        }
        prescription_serializer = PrescriptionSerializer(data=prescription_data)
        if not prescription_serializer.is_valid():
            return Response({
                'errCode': 2,
                'message': 'Dữ liệu đơn thuốc không hợp lệ',
                'errors': prescription_serializer.errors
            }, status=400)
        prescription_serializer.save()

        # ✅ 7. Tạo các thuốc trong đơn
        try:
            medicines_list = json.loads(medicines_data)
        except Exception as e:
            return Response({'errCode': 4, 'message': 'Dữ liệu thuốc không hợp lệ (không parse được JSON)'}, status=400)

        for item in medicines_list:
            pres_medicine_data = {
                'prescription': prescription_serializer.instance.id,
                'medicine': item.get('id'),
                'price': item.get('price'),
                'quantity': item.get('quantity'),
                'directions_for_use': item.get('directions_for_use')
            }

            pres_medicine_serializer = PrescriptionMedicineSerializer(data=pres_medicine_data)
            if not pres_medicine_serializer.is_valid():
                return Response({
                    'errCode': 3,
                    'message': 'Dữ liệu thuốc không hợp lệ',
                    'errors': pres_medicine_serializer.errors
                }, status=400)

            pres_medicine_serializer.save()

        # ✅ 8. Gọi API cập nhật trạng thái appointment
        status_res = requests.put(
            f"{URL_APPT_SV}/api/a/change-status-appointment",
            json={'medical_id': medical_id, 'status': 'done'}
        )
        if status_res.status_code != 200:
            return Response({'errCode': 5, 'message': 'Không cập nhật được trạng thái'}, status=500)

        return Response({'errCode': 0, 'message': 'Tạo đơn thuốc thành công'}, status=201)

    except Exception as e:
        return Response({'errCode': 500, 'message': f'Lỗi hệ thống: {str(e)}'}, status=500)



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
            "image":prescription.image,
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
        # Kiểm tra vai trò pharmacist
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
        # Lấy dữ liệu từ request
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

        # Kiểm tra định dạng ảnh
        ext = os.path.splitext(image_file.name)[-1].lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
            return Response({
                "errCode": 11,
                "message": f"Định dạng ảnh không hỗ trợ: {ext}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Upload ảnh lên Cloudinary (vào thư mục 'invoices')
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        file_name = f"invoice_{timestamp}-{unique_id}"

        upload_result = cloudinary.uploader.upload(
            image_file,
            public_id=file_name,
            folder="invoices",  # Lưu ảnh vào thư mục 'invoices' trên Cloudinary
            resource_type="image",
            overwrite=True
        )
        cloudinary_url = upload_result.get('secure_url')

        # Tạo hóa đơn
        invoice = Invoice.objects.create(
            pharmacist_id=pharmacist_id,
            totals=totals,
            prescription_id=prescription_id,
            payment_method_id=payment_method_id,
            image=cloudinary_url  # Lưu URL ảnh từ Cloudinary
        )

        # Cập nhật trạng thái của đơn thuốc
        prescription = Prescription.objects.get(id=prescription_id)
        prescription.status = 'sold'
        prescription.save()

        # Cập nhật trạng thái của từng thuốc trong đơn thuốc và trừ stock
        for item in list_pres_med:
            pres_med_id = item.get('prescription_medicine_id')
            medicine_id = item.get('medicine_id')
            quantity = item.get('quantity')

            try:
                # Chuyển stock_sold từ chuỗi thành kiểu int
                quantity = int(quantity)
                
                # Cập nhật trạng thái PrescriptionMedicine
                pres_med = PrescriptionMedicine.objects.get(id=pres_med_id)
                pres_med.status = 'sold'
                pres_med.save()
            except PrescriptionMedicine.DoesNotExist:
                continue
            except ValueError:
                return Response({
                    "errCode": 13,
                    "message": f"Giá trị stock không hợp lệ cho prescription_medicine_id {pres_med_id}"
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Cập nhật stock thuốc
                medicine = Medicine.objects.get(id=medicine_id)

                if medicine.stock < quantity:
                    return Response({
                        "errCode": 12,
                        "message": f"Không đủ thuốc trong kho cho {medicine.name}"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Trừ đi stock đã bán
                medicine.stock -= quantity
                medicine.save()
            except Medicine.DoesNotExist:
                continue
            except ValueError:
                return Response({
                    "errCode": 13,
                    "message": f"Giá trị stock không hợp lệ cho medicine_id {medicine_id}"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Trả về thành công khi đã xử lý xong tất cả
        return Response({
            "errCode": 0,
            "message": "Tạo hóa đơn thành công"
        })


    except Exception as e:
        return Response({
            "errCode": 13,
            "message": f"Lỗi xử lý dữ liệu: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def get_image_prescription_by_medical_id(request):
    medical_id = request.GET.get('medical_id')

    if not medical_id:
        return Response({
            "errCode": 1,
            "message": "medical_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    prescription = Prescription.objects.filter(medical_id=medical_id).first()

    if not prescription:
        return Response({
            "errCode": 2,
            "message": "Prescription not found"
        }, status=status.HTTP_404_NOT_FOUND)

    # Xử lý ảnh nếu có
    if prescription.image:
        image_path = os.path.join(IMAGE_PRES, prescription.image)
        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                mime_type, _ = mimetypes.guess_type(image_path)
                if mime_type:
                    prescription.image = f"data:{mime_type};base64,{encoded}"
                else:
                    prescription.image = None
        else:
            prescription.image = None

    return Response({
        "errCode": 0,
        "message": "Success",
        "data": {
            "image": prescription.image,
        }
    }, status=status.HTTP_200_OK)
