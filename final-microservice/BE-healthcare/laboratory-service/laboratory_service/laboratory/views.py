import requests
import base64
import mimetypes
import os
import uuid
import time
from django.conf import settings
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from .models import TypeTest,TestRequest,TestResult
from .serializers import TypeTestSerializer,TestRequestSerializer,TestResultSerializer
from bson import ObjectId,errors
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TestRequest, TypeTest
from rest_framework import status
from bson import ObjectId

URL_USER_SV = "http://localhost:8001"
IMAGE_TESTRESULT=r"D:\final-microservice\image\test_result"

@api_view(['GET'])
def get_typetest_types(request):
    types = []
    for value, label in TypeTest._meta.get_field('type').choices:
        types.append({
            "value": value,
            "label": label
        })
    return Response({
        "errCode": 0,
        "message": "Lấy danh sách type thành công",
        "data": types
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_typetest(request):
    # 1. Lấy token từ Authorization Header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Missing or invalid token format'
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # 2. Gửi request kiểm tra quyền admin
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-admin",
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        if data.get('errCode') != 0:
            return Response({
                'errCode': 3,
                'message': 'You do not have admin rights'
            }, status=status.HTTP_403_FORBIDDEN)
    except requests.exceptions.RequestException:
        return Response({
            'errCode': 4,
            'message': 'Error connecting to user service'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 3. Nếu là admin → Tạo mới TypeTest
    serializer = TypeTestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'errCode': 0,
            'message': 'Successfully created type test',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'errCode': 1,
        'message': 'Failed to create type test',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_all_typetests(request):
    try:
        typetests = TypeTest.objects.all()
        serializer = TypeTestSerializer(typetests, many=True)
        return Response({
            "errCode": 0,
            "message": "Lấy tất cả TypeTest thành công",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['PUT'])  # PUT chuẩn nè
def change_typetest_active(request):
    # 1. Lấy token từ Authorization Header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Missing or invalid token format'
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # 2. Gửi request kiểm tra quyền admin
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-admin",
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        if data.get('errCode') != 0:
            return Response({
                'errCode': 3,
                'message': 'You do not have admin rights'
            }, status=status.HTTP_403_FORBIDDEN)
    except requests.exceptions.RequestException:
        return Response({
            'errCode': 4,
            'message': 'Error connecting to user service'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 3. Lấy id từ request
    typetest_id = request.data.get('id')
    if not typetest_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu id trong yêu cầu"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        object_id = ObjectId(typetest_id)
    except Exception:
        return Response({
            "errCode": 1,
            "message": "Id không hợp lệ"
        }, status=status.HTTP_400_BAD_REQUEST)

    # 4. Tìm và cập nhật typetest
    typetest = TypeTest.objects.filter(id=object_id).first()
    if not typetest:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy TypeTest"
        }, status=status.HTTP_404_NOT_FOUND)

    typetest.is_active = not typetest.is_active
    typetest.save()

    # 5. Trả response thành công
    return Response({
        "errCode": 0,
        "message": "Cập nhật trạng thái thành công",
        "data": {
            "id": str(typetest.id),
            "is_active": typetest.is_active
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_typetest_by_id(request):
    try:
        typetest_id = request.GET.get('id')
        if not typetest_id:
            return Response({
                "errCode": 1,
                "message": "Thiếu id trong yêu cầu"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Chuyển id thành ObjectId
        try:
            object_id = ObjectId(typetest_id)
        except Exception:
            return Response({
                "errCode": 1,
                "message": "Id không hợp lệ"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Tìm kiếm TypeTest
        typetest = TypeTest.objects.filter(id=object_id).first()
        if not typetest:
            return Response({
                "errCode": 1,
                "message": "Không tìm thấy TypeTest"
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize dữ liệu
        serializer = TypeTestSerializer(typetest)
        return Response({
            "errCode": 0,
            "message": "Lấy TypeTest thành công",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "errCode": 2,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['PUT'])
def update_typetest(request):
    # 1. Lấy token từ Authorization Header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Missing or invalid token format'
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # 2. Gửi request kiểm tra quyền admin
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-admin",
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        if data.get('errCode') != 0:
            return Response({
                'errCode': 3,
                'message': 'You do not have admin rights'
            }, status=status.HTTP_403_FORBIDDEN)
    except requests.exceptions.RequestException:
        return Response({
            'errCode': 4,
            'message': 'Error connecting to user service'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 3. Lấy id từ request body (trong trường hợp sửa thông tin)
    typetest_id = request.data.get('id')
    if not typetest_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu id trong yêu cầu"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        object_id = ObjectId(typetest_id)
    except Exception:
        return Response({
            "errCode": 1,
            "message": "Id không hợp lệ"
        }, status=status.HTTP_400_BAD_REQUEST)

    # 4. Tìm và cập nhật đối tượng TypeTest
    typetest = TypeTest.objects.filter(id=object_id).first()
    if not typetest:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy TypeTest"
        }, status=status.HTTP_404_NOT_FOUND)

    # 5. Cập nhật thông tin TypeTest từ request data
    serializer = TypeTestSerializer(typetest, data=request.data, partial=True)  # partial=True để không cần gửi hết tất cả trường
    if serializer.is_valid():
        serializer.save()
        return Response({
            'errCode': 0,
            'message': 'Successfully updated type test',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        'errCode': 1,
        'message': 'Failed to update type test',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
def create_test_requests(request):
    # 1. Lấy token từ Authorization Header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Missing or invalid token format'
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # 2. Gửi request kiểm tra quyền bác sĩ
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-doctor",
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        if data.get('errCode') != 0:
            return Response({
                'errCode': 3,
                'message': 'You do not have doctor rights'
            }, status=status.HTTP_403_FORBIDDEN)
    except requests.exceptions.RequestException:
        return Response({
            'errCode': 4,
            'message': 'Error connecting to user service'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 3. Xử lý dữ liệu request
    data = request.data
    medical_record_id = data.get("medical_record_id")
    list_type_test = data.get("listTypeTest", [])

    if not medical_record_id or not list_type_test:
        return Response({
            "errCode": 1,
            "message": "Thiếu medical_record_id hoặc listTypeTest"
        }, status=status.HTTP_400_BAD_REQUEST)

    created_requests = []
    for item in list_type_test:
        test_request = TestRequest.objects.create(
            medical_record_id=medical_record_id,
            typetest_id=item.get("id"),
            price=item.get("price")
        )
        created_requests.append({
            "id": str(test_request.id),
            "typetest_id": test_request.typetest_id,
            "price": test_request.price
        })

    return Response({
        "errCode": 0,
        "message": "Tạo thành công",
        "data": created_requests
    }, status=status.HTTP_201_CREATED)




@api_view(['GET'])
def get_test_requests_by_medical_record(request):
    # Lấy medical_record_id từ query parameters
    medical_record_id = request.GET.get('id')
    
    if not medical_record_id:
        return Response({
            'errCode': 1,
            'message': 'Thiếu medical_record_id trong yêu cầu'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Lấy tất cả TestRequest có medical_record_id tương ứng
    test_requests = TestRequest.objects.filter(medical_record_id=medical_record_id)

    # Nếu không tìm thấy bản ghi nào, trả về errCode: 0 và status 2xx, data là mảng rỗng
    if not test_requests:
        return Response({
            'errCode': 0,
            'message': 'Không tìm thấy TestRequest với medical_record_id này',
            'data': []  # Data là mảng rỗng
        }, status=status.HTTP_200_OK)

    # Dữ liệu cần trả về
    test_requests_data = []
    
    for test_request in test_requests:
        # Lấy TypeTest object từ typetest_id
        try:
            type_test = TypeTest.objects.get(id=ObjectId(test_request.typetest_id))
            type_test_name = type_test.name
        except TypeTest.DoesNotExist:
            type_test_name = 'N/A'  # Nếu không tìm thấy TypeTest, trả về 'N/A'

        test_requests_data.append({
            'id': str(test_request.id),
            'price': test_request.price,
            'process_status': test_request.process_status,
            'payment_status':test_request.payment_status,
            'name': type_test_name  # Thêm name của typeTest vào dữ liệu trả về
        })

    return Response({
        'errCode': 0,
        'message': 'Lấy dữ liệu thành công',
        'data': test_requests_data  # Trả về dữ liệu đã xử lý
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
def mark_test_requests_paid(request):
    medical_record_id = request.data.get('id')

    if not medical_record_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu medical_record_id"
        }, status=status.HTTP_400_BAD_REQUEST)

    test_requests = TestRequest.objects.filter(medical_record_id=medical_record_id)

    if not test_requests.exists():
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy yêu cầu xét nghiệm nào với medical_record_id này"
        }, status=status.HTTP_404_NOT_FOUND)

    for tr in test_requests:
        tr.process_status = "processing"
        tr.payment_status = "paid"
        tr.save()
    return Response({
        "errCode": 0,
        "message": f"Đã cập nhật  TestRequest thành công",
    }, status=status.HTTP_200_OK)
    
    
@api_view(['POST'])
@parser_classes([FormParser, MultiPartParser])
def create_test_result(request):
    try:
        # 1. Xác thực token
        token = request.headers.get('Authorization')
        if not token:
            return Response({"errCode": 1, "message": "Thiếu token"}, status=401)

        resp = requests.get(
            f"{URL_USER_SV}/api/u/check-role-technician",
            headers={'Authorization': token}
        )
        data_check = resp.json()
        if resp.status_code != 200 or data_check.get("errCode") != 0:
            return Response({"errCode": 1, "message": "Không có quyền kỹ thuật viên"}, status=403)

        technician_id = data_check.get("user_id")
        test_request_id = request.data.get("test_request_id")
        if not test_request_id:
            return Response({"errCode": 1, "message": "Thiếu test_request_id"}, status=400)

        test_request = TestRequest.objects.filter(id=ObjectId(test_request_id)).first()
        if not test_request:
            return Response({"errCode": 1, "message": "TestRequest không tồn tại"}, status=404)

        # 2. Tạo bản sao dữ liệu để xử lý
        data = request.data.copy()
        data["technician_id"] = technician_id

        # 3. Xử lý 2 ảnh: raw_image và annotated_image
        save_dir = IMAGE_TESTRESULT
        os.makedirs(save_dir, exist_ok=True)

        for image_field in ['raw_image', 'annotated_image']:
            uploaded_file = request.FILES.get(image_field)
            if uploaded_file:
                try:
                    ext = os.path.splitext(uploaded_file.name)[-1].lower()
                    if ext not in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                        return Response({
                            "errCode": 11,
                            "message": f"Định dạng ảnh không hỗ trợ: {ext}"
                        }, status=400)

                    timestamp = int(time.time())
                    unique_id = uuid.uuid4().hex[:8]
                    file_name = f"{timestamp}-{unique_id}{ext}"
                    file_path = os.path.join(save_dir, file_name)

                    with open(file_path, "wb+") as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)

                    data[image_field] = file_name
                except Exception as e:
                    return Response({
                        "errCode": 12,
                        "message": f"Lỗi xử lý file {image_field}: {str(e)}"
                    }, status=400)
            else:
                data[image_field] = ""

        # 4. Lưu kết quả xét nghiệm
        serializer = TestResultSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            test_request.process_status = "completed"
            test_request.save()
            return Response({
                "errCode": 0,
                "message": "Tạo kết quả xét nghiệm thành công",
                "data": serializer.data
            }, status=201)

        return Response({
            "errCode": 1,
            "message": "Dữ liệu không hợp lệ",
            "errors": serializer.errors
        }, status=400)

    except Exception as e:
        return Response({"errCode": -1, "message": f"Lỗi: {str(e)}"}, status=500)
    

@api_view(['GET'])
def get_annotated_image_test_result_by_test_request(request):
    try:
        # Lấy test_request_id từ query string
        test_request_id = request.GET.get('id')
        
        if not test_request_id:
            return Response({
                'errCode': 0,  # Không có lỗi, không tìm thấy
                'status': 'success',
                'message': 'Test request ID not provided',
                'data': []
            }, status=status.HTTP_200_OK)
        
        # Lấy duy nhất một kết quả TestResult theo test_request_id
        test_result = TestResult.objects.filter(test_request_id=test_request_id).first()
        
        if not test_result:
            return Response({
                'errCode': 0,  # Không có lỗi, không tìm thấy kết quả
                'status': 'success',
                'message': 'No test result found for this test_request_id',
                'data': []
            }, status=status.HTTP_200_OK)
        
        # Đọc ảnh từ đường dẫn IMAGE_TESTRESULT và chuyển thành base64
        try:
            image_path = os.path.join(IMAGE_TESTRESULT, test_result.annotated_image)
            if os.path.exists(image_path):
                # Lấy MIME type của file ảnh
                mime_type, _ = mimetypes.guess_type(image_path)
                
                if mime_type:
                    with open(image_path, 'rb') as img_file:
                        # Đọc file ảnh và chuyển thành base64
                        encoded = base64.b64encode(img_file.read()).decode('utf-8')
                        # Tạo data URI cho ảnh
                        image_base64 = f"data:{mime_type};base64,{encoded}"
                else:
                    image_base64 = None
            else:
                image_base64 = None

        except Exception as e:
            return Response({
                'errCode': 3,  # Lỗi hệ thống khi lấy ảnh
                'status': 'failure',
                'message': f'System error: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if image_base64 is None:
            return Response({
                'errCode': 3,  # Lỗi không tìm thấy ảnh
                'status': 'failure',
                'message': 'Image file not found',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Trả về kết quả với ảnh đã chuyển thành base64
        return Response({
            'errCode': 0,  # Thành công
            'status': 'success',
            'message': 'Test result found',
            'data': {
                'annotated_image': image_base64,
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Nếu gặp lỗi hệ thống
        return Response({
            'errCode': 3,  # Lỗi hệ thống
            'status': 'failure',
            'message': f'System error: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
