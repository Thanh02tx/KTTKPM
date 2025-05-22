
import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Room,Time,Schedule,TimeSlot,Appointment,MedicalRecord
from .serializers import RoomSerializer,TimeSerializer,ScheduleSerializer,TimeSlotSerializer,AppointmentSerializer,MedicalRecordSerializer
from bson import ObjectId,errors
from django.db import transaction
from datetime import datetime, timedelta,date
from django.utils.dateparse import parse_date
from django.db.models import Q

URL_USER_SV = "http://localhost:8001"
URL_NOTIFICATION_SV = "http://localhost:8004"
URL_LAB_SV = "http://localhost:8003"
URL_ERH_SV = "http://localhost:8005"
def to_object_id(id_str):
    try:
        return ObjectId(id_str)
    except Exception:
        return None
    
@api_view(['POST'])
def create_room(request):
    # Lấy token từ header Authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Thiếu hoặc sai định dạng token'
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # Gửi request kiểm tra quyền admin
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-admin",
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        if data.get('errCode') != 0:
            return Response({
                'errCode': 3,
                'message': 'Bạn không có quyền admin'
            }, status=status.HTTP_403_FORBIDDEN)
    except requests.exceptions.RequestException:
        return Response({
            'errCode': 4,
            'message': 'Lỗi kết nối đến user service'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Nếu là admin thì tạo phòng
    serializer = RoomSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'errCode': 0,
            'message': 'Tạo phòng thành công',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'errCode': 1,
        'message': 'Tạo phòng thất bại',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_rooms(request):
    # Lấy tất cả các phòng
    rooms = Room.objects.all()

    # Serialize dữ liệu
    serializer = RoomSerializer(rooms, many=True)
    
    # Trả về danh sách phòng dưới dạng JSON
    return Response({
        'errCode': 0,
        'message': 'Lấy danh sách phòng thành công',
        'data': serializer.data
    }, status=status.HTTP_200_OK)
    


@api_view(['PUT'])
def change_active_room(request):
    # Lấy token từ header Authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Thiếu hoặc sai định dạng token'
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # Gửi request kiểm tra quyền admin
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-admin",
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        if data.get('errCode') != 0:
            return Response({
                'errCode': 3,
                'message': 'Bạn không có quyền admin'
            }, status=status.HTTP_403_FORBIDDEN)
    except requests.exceptions.RequestException:
        return Response({
            'errCode': 4,
            'message': 'Lỗi kết nối đến user service'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Lấy id phòng từ body
    room_id = request.data.get('id')
    if not room_id:
        return Response({
            'errCode': 6,
            'message': 'Thiếu id phòng'
        }, status=status.HTTP_400_BAD_REQUEST)

    obj_id = to_object_id(room_id)
    if not obj_id:
        return Response({
            'errCode': 7,
            'message': 'ID không hợp lệ (không phải ObjectId)'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        room = Room.objects.get(id=obj_id)
    except Room.DoesNotExist:
        return Response({
            'errCode': 5,
            'message': 'Phòng không tồn tại'
        }, status=status.HTTP_404_NOT_FOUND)

    # Đảo trạng thái is_active
    room.is_active = not room.is_active
    room.save()

    return Response({
        'errCode': 0,
        'message': f"Trạng thái phòng đã được thay đổi thành {'kích hoạt' if room.is_active else 'khóa'}",
        'data': RoomSerializer(room).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_room_by_id(request):
    room_id = request.GET.get('id')

    if not room_id:
        return Response({
            'errCode': 1,
            'message': 'Thiếu id phòng trong request'
        }, status=status.HTTP_400_BAD_REQUEST)

    object_id = to_object_id(room_id)
    if not object_id:
        return Response({
            'errCode': 2,
            'message': 'Id không hợp lệ'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        room = Room.objects.get(id=object_id)
    except Room.DoesNotExist:
        return Response({
            'errCode': 3,
            'message': 'Phòng không tồn tại'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = RoomSerializer(room)
    return Response({
        'errCode': 0,
        'message': 'Lấy phòng thành công',
        'data': serializer.data
    }, status=status.HTTP_200_OK)
    
@api_view(['PUT'])
def update_room(request):
    # Lấy token từ header Authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Thiếu hoặc sai định dạng token'
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # Gửi request kiểm tra quyền admin
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-admin",
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        if data.get('errCode') != 0:
            return Response({
                'errCode': 3,
                'message': 'Bạn không có quyền admin'
            }, status=status.HTTP_403_FORBIDDEN)
    except requests.exceptions.RequestException:
        return Response({
            'errCode': 4,
            'message': 'Lỗi kết nối đến user service'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Kiểm tra xem phòng có tồn tại không
    room_id = request.data.get('id')  # Nhận id từ request body

    if not room_id:
        return Response({
            'errCode': 6,
            'message': 'Thiếu id phòng'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        room = Room.objects.get(id=to_object_id(room_id))  # Chuyển id thành ObjectId
    except Room.DoesNotExist:
        return Response({
            'errCode': 5,
            'message': 'Phòng không tồn tại'
        }, status=status.HTTP_404_NOT_FOUND)

    # Cập nhật phòng
    serializer = RoomSerializer(room, data=request.data, partial=True)  # partial=True để cập nhật một số trường
    if serializer.is_valid():
        serializer.save()
        return Response({
            'errCode': 0,
            'message': 'Cập nhật phòng thành công',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        'errCode': 1,
        'message': 'Cập nhật phòng thất bại',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_times(request):
    # Lấy tất cả các phòng
    rooms = Time.objects.all()

    # Serialize dữ liệu
    serializer = TimeSerializer(rooms, many=True)
    
    # Trả về danh sách phòng dưới dạng JSON
    return Response({
        'errCode': 0,
        'message': 'Lấy danh sách phòng thành công',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_schedules_and_timeslot(request):
    # 1. Kiểm tra token và quyền admin
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Thiếu hoặc sai định dạng token'
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-admin",
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        if data.get('errCode') != 0:
            return Response({
                'errCode': 3,
                'message': 'Bạn không có quyền admin'
            }, status=status.HTTP_403_FORBIDDEN)
    except requests.exceptions.RequestException:
        return Response({
            'errCode': 4,
            'message': 'Lỗi kết nối đến user service'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 2. Lấy dữ liệu từ request
    schedule_data = request.data.get('schedules', [])
    current_max = request.data.get('maxNumber', 0)
    schedule_date_str = request.data.get('date')

    if not schedule_data or not schedule_date_str:
        return Response({
            'errCode': 1,
            'message': 'Thiếu dữ liệu lịch hoặc ngày'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 3. Parse ngày
    try:
        schedule_date = datetime.strptime(schedule_date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({
            'errCode': 5,
            'message': 'Định dạng ngày không hợp lệ (đúng: YYYY-MM-DD)'
        }, status=status.HTTP_400_BAD_REQUEST)
    if schedule_date_str:
        try:
            schedule_date = datetime.strptime(schedule_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({
                'errCode': 5,
                'message': 'Định dạng ngày không hợp lệ (đúng: YYYY-MM-DD)'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Xóa tất cả TimeSlot và Schedule theo ngày
        old_schedules = Schedule.objects.filter(date=schedule_date)
        for old_sch in old_schedules:
            print('ok',old_sch)
            timeslots_old=TimeSlot.objects.filter(schedule_id=str(old_sch.id)) #lỗi chưa xoá
            timeslots_old.delete()
        old_schedules.delete()

    # 4. Lấy danh sách Time
    times = list(Time.objects.all())
    if len(times) == 0:
        return Response({
            'errCode': 2,
            'message': 'Không có dữ liệu thời gian'
        }, status=status.HTTP_404_NOT_FOUND)

    # 5. Tạo các Schedule
    for schedule in schedule_data:
        schedule_serializer = ScheduleSerializer(data=schedule)
        if schedule_serializer.is_valid():
            schedule_serializer.save()
        else:
            return Response({
                'errCode': 3,
                'message': 'Dữ liệu lịch không hợp lệ',
                'errors': schedule_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    # 6. Gọi lại tất cả Schedule theo ngày để tạo TimeSlot
    schedules_created = Schedule.objects.filter(date=schedule_date)
    for sch in schedules_created:
        for ti in times:
            timeslot_data = {
                'schedule_id': str(sch.id),
                'time_id': str(ti.id),
                'current_number': 0,
                'max_number': current_max
            }
            timeslot_serializer = TimeSlotSerializer(data=timeslot_data)
            if timeslot_serializer.is_valid():
                timeslot_serializer.save()
            else:
                return Response({
                    'errCode': 4,
                    'message': 'Dữ liệu timeslot không hợp lệ',
                    'errors': timeslot_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

    # 7. Trả kết quả
    return Response({
        'errCode': 0,
        'message': 'Tạo lịch và time slot thành công',
    }, status=status.HTTP_201_CREATED)
    
    
@api_view(['GET'])
def get_schedules(request):
    # Lấy tất cả các phòng
    rooms = Schedule.objects.all()

    # Serialize dữ liệu
    serializer = ScheduleSerializer(rooms, many=True)
    
    # Trả về danh sách phòng dưới dạng JSON
    return Response({
        'errCode': 0,
        'message': 'Lấy danh sách phòng thành công',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_schedules_week(request):
    # Lấy ngày bắt đầu từ query param
    start_date_str = request.GET.get('startDate')
    if not start_date_str:
        return Response({
            'errCode': 1,
            'message': 'Thiếu startDate trong query'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        start_date = parse_date(start_date_str)
        if not start_date:
            raise ValueError
    except ValueError:
        return Response({
            'errCode': 2,
            'message': 'startDate không hợp lệ. Định dạng phải là YYYY-MM-DD'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Tính ngày thứ 2 và thứ 7 trong tuần của start_date
    weekday = start_date.weekday()  # Monday = 0, Sunday = 6
    monday = start_date - timedelta(days=weekday)
    saturday = monday + timedelta(days=5)

    # Lọc schedule theo khoảng ngày
    schedules = Schedule.objects.filter(date__range=[monday, saturday]).order_by('date')

    # Serialize
    serializer = ScheduleSerializer(schedules, many=True)
    return Response({
        'errCode': 0,
        'message': f'Lấy lịch từ {monday} đến {saturday} thành công',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_timeslots(request):
    # Lấy tất cả các phòng
    timeslots = TimeSlot.objects.all()

    # Serialize dữ liệu
    serializer = TimeSlotSerializer(timeslots, many=True)
    
    # Trả về danh sách phòng dưới dạng JSON
    return Response({
        'errCode': 0,
        'message': 'Lấy danh sách phòng thành công',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_timeslots_by_date_and_doctorid(request):
    dateX = request.GET.get('date')
    doctor_id = request.GET.get('doctor_id')

    if not dateX or not doctor_id:
        return Response({
            'errCode': 1,
            'message': 'Thiếu tham số date hoặc doctor_id'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Lấy Schedule nếu tồn tại
        schedule = Schedule.objects.filter(date=dateX, doctor_id=doctor_id).first()

        if not schedule:
            return Response({
                'errCode': 0,
                'message': 'Không có lịch cho ngày này',
                'data': []  # Trả về mảng rỗng
            }, status=status.HTTP_200_OK)

        schedule_id_str = str(schedule.id)
        timeslots = TimeSlot.objects.filter(schedule_id=schedule_id_str)

        timeslot_data = []
        for ts in timeslots:
            try:
                time_obj = Time.objects.get(id=ObjectId(ts.time_id))
                time_data = time_obj.time
            except Time.DoesNotExist:
                time_data = None

            timeslot_data.append({
                'id': str(ts.id),
                'time': time_data,
                'current_number': ts.current_number,
                'max_number': ts.max_number
            })

        return Response({
            'errCode': 0,
            'message': 'Lấy thành công',
            'data': timeslot_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'errCode': 500,
            'message': f'Lỗi server: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_schedule_doctor_by_timeslotid(request):
    timeslot_id = request.GET.get('timeslot_id')

    if not timeslot_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu tham số timeslot_id",
            "data": None
        }, status=400)

    try:
        timeslot = TimeSlot.objects.get(id=ObjectId(timeslot_id))
        time = Time.objects.get(id=ObjectId(timeslot.time_id))
        schedule = Schedule.objects.get(id=ObjectId(timeslot.schedule_id))
        
        # Thêm lấy Room
        room = Room.objects.get(id=ObjectId(schedule.room_id))

        doctor_info = None
        try:
            res_json = requests.get(
                f"{URL_USER_SV}/api/u/get-doctor-by-user-id",
                params={"id": schedule.doctor_id}
            ).json()

            if res_json.get("errCode") == 0:
                doctor_info = res_json.get("data")
        except Exception as e:
            doctor_info = None

        return Response({
            "errCode": 0,
            "message": "Lấy thông tin thành công",
            "data": {
                "timeslot": {
                    "id": str(timeslot.id),
                    "current_number": timeslot.current_number,
                    "max_number": timeslot.max_number,
                },
                "time": {
                    "id": str(time.id),
                    "time": time.time,
                },
                "schedule": {
                    "id": str(schedule.id),
                    "doctor_id": schedule.doctor_id,
                    "nurse_id": schedule.nurse_id,
                    "date": schedule.date.strftime("%Y-%m-%d"),
                    "room_id": schedule.room_id,
                },
                "room": {
                    "id": str(room.id),
                    "name": room.name,
                },
                "doctor": doctor_info
            }
        })

    except TimeSlot.DoesNotExist:
        return Response({
            "errCode": 2,
            "message": "Không tìm thấy TimeSlot",
            "data": None
        }, status=404)
    except Time.DoesNotExist:
        return Response({
            "errCode": 3,
            "message": "Không tìm thấy Time",
            "data": None
        }, status=404)
    except Schedule.DoesNotExist:
        return Response({
            "errCode": 4,
            "message": "Không tìm thấy Schedule",
            "data": None
        }, status=404)
    except Room.DoesNotExist:
        return Response({
            "errCode": 5,
            "message": "Không tìm thấy Room",
            "data": None
        }, status=404)

@api_view(['POST'])
def check_duplicate_appointment(request):
    try:
        data = request.data
        patient_id = data.get('patient_id')
        new_timeslot_id = data.get('timeslot_id')

        if not all([patient_id, new_timeslot_id]):
            return Response({"errCode": 1, "message": "Thiếu dữ liệu đầu vào"}, status=status.HTTP_200_OK)

        new_timeslot = TimeSlot.objects.filter(id=ObjectId(new_timeslot_id)).first()
        if not new_timeslot:
            return Response({"errCode": 4, "message": "Không tìm thấy khung giờ mới (timeslot)"}, status=status.HTTP_200_OK)

        medical_records = MedicalRecord.objects.filter(patient_id=patient_id)

        if not medical_records.exists():
            return Response({"errCode": 2, "message": "Không tìm thấy hồ sơ bệnh án"}, status=status.HTTP_200_OK)

        for medical_record in medical_records:
            appointment = Appointment.objects.filter(medical_id=str(medical_record.id)).first()
            if not appointment:
                continue  # Bỏ qua nếu không có lịch hẹn với hồ sơ này

            old_timeslot = TimeSlot.objects.filter(id=ObjectId(appointment.timeslot_id)).first()
            if not old_timeslot:
                continue  # Bỏ qua nếu khung giờ cũ không tồn tại

            if old_timeslot.schedule_id != new_timeslot.schedule_id:
                return Response({
                    "errCode": 5,
                    "message": "Lịch khám khác ngày (khác schedule)"
                }, status=status.HTTP_200_OK)

        # Nếu tất cả đều cùng schedule hoặc không có lịch để so sánh
        return Response({
            "errCode": 0,
            "message": "Lịch khám hợp lệ (cùng schedule hoặc chưa từng đặt)"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "errCode": 6,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_200_OK)



@api_view(['POST'])
@transaction.atomic
def create_appointment_with_medical_record(request):
    try:
        data = request.data

        timeslot_id = data.get('timeslot_id')
        reason = data.get('reason')
        patient_id = data.get('patient_id')
        email_data = data.get('email_data')
        doctor_fee = data.get('doctor_fee')
        if not all([timeslot_id, reason, patient_id, email_data]):
            return Response({"errCode": 1, "message": "Thiếu dữ liệu đầu vào"}, status=status.HTTP_200_OK)

        token = request.headers.get('Authorization')
        if not token:
            return Response({"errCode": 2, "message": "Thiếu token trong header"}, status=status.HTTP_200_OK)

        # Gọi API lấy thông tin bệnh nhân
        response = requests.get(
            f"{URL_USER_SV}/api/u/get-patient-record-by-id",
            params={"id": patient_id},
            headers={"Authorization": token}
        )
        try:
            patient_data = response.json()
        except ValueError:
            return Response({
                "errCode": 3,
                "message": "Không nhận được dữ liệu JSON hợp lệ từ server user"
            }, status=status.HTTP_200_OK)

        if response.status_code != 200 or patient_data.get('errCode') != 0:
            return Response({
                "errCode": 4,
                "message": "Không thể lấy thông tin bệnh nhân hoặc bệnh nhân không tồn tại",
                "details": patient_data
            }, status=status.HTTP_200_OK)

        patient_info = patient_data.get('data')

        # Lấy email từ token
        email_response = requests.get(
            f"{URL_USER_SV}/api/u/get-email-from-token",
            headers={"Authorization": token}
        )
        try:
            email_data_response = email_response.json()
        except ValueError:
            return Response({
                "errCode": 5,
                "message": "Không nhận được JSON khi lấy email"
            }, status=status.HTTP_200_OK)

        if email_response.status_code != 200 or email_data_response.get('errCode') != 0:
            return Response({
                "errCode": 5,
                "message": "Không thể lấy email từ token",
                "details": email_data_response
            }, status=status.HTTP_200_OK)

        email_data['recipient_email'] = email_data_response.get('data', {}).get('email')

        # Kiểm tra timeslot tồn tại và còn trống
        try:
            timeslot = TimeSlot.objects.get(id=ObjectId(timeslot_id))
        except TimeSlot.DoesNotExist:
            return Response({
                "errCode": 8,
                "message": "Không tìm thấy timeslot"
            }, status=status.HTTP_200_OK)

        if timeslot.current_number >= timeslot.max_number:
            return Response({
                "errCode": 9,
                "message": "Lịch hẹn đã đầy, không thể đặt thêm"
            }, status=status.HTTP_200_OK)

        # Tạo MedicalRecord
        medical_record_id = ObjectId()
        medical_record = MedicalRecord(
            id=medical_record_id,
            patient_id=patient_info.get('id', ''),
            name=patient_info.get('name', ''),
            gender=patient_info.get('gender', ''),
            phone=patient_info.get('phone', ''),
            date_of_birth=patient_info.get('date_of_birth', None),
            province=patient_info.get('province', ''),
            district=patient_info.get('district', ''),
            ward=patient_info.get('ward', ''),
            address_detail=patient_info.get('address_detail', ''),
            national_id=patient_info.get('national_id', ''),
            health_insurance=patient_info.get('health_insurance', '')
        )

        # Chuẩn bị dữ liệu appointment
        appointment_data = {
            'medical_id': str(medical_record_id),
            'timeslot_id': timeslot_id,
            'doctor_fee': doctor_fee,
            'reason': reason,
        }

        appointment_serializer = AppointmentSerializer(data=appointment_data)
        if not appointment_serializer.is_valid():
            return Response({
                "errCode": 6,
                "message": "Dữ liệu lịch hẹn không hợp lệ",
                "errors": appointment_serializer.errors
            }, status=status.HTTP_200_OK)

        # Gửi email
        email_send_response = requests.post(
            f"{URL_NOTIFICATION_SV}/api/send-email",
            json=email_data
        )
        try:
            email_response_data = email_send_response.json()
        except ValueError:
            return Response({
                "errCode": 7,
                "message": "Không nhận được JSON khi gửi email"
            }, status=status.HTTP_200_OK)

        # Lưu vào DB
        medical_record.save()
        appointment_serializer.save()

        # Cập nhật số lượng đã đặt của timeslot
        timeslot.current_number += 1
        timeslot.save()

        return Response({
            "errCode": 0,
            "message": "Tạo lịch hẹn thành công và đã gửi email"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "errCode": 99,
            "message": "Lỗi hệ thống",
            "error": str(e)
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_medicals(request):
    # Lấy tất cả các phòng
    rooms = MedicalRecord.objects.all()

    # Serialize dữ liệu
    serializer = MedicalRecordSerializer(rooms, many=True)
    
    # Trả về danh sách phòng dưới dạng JSON
    return Response({
        'errCode': 0,
        'message': 'Lấy danh sách phòng thành công',
        'data': serializer.data
    }, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def get_appointments(request):
    # Lấy tất cả các phòng
    rooms = Appointment.objects.all()

    # Serialize dữ liệu
    serializer = AppointmentSerializer(rooms, many=True)
    
    # Trả về danh sách phòng dưới dạng JSON
    return Response({
        'errCode': 0,
        'message': 'Lấy danh sách phòng thành công',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_appointment_medical_by_nurse_date(request):
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Thiếu hoặc sai định dạng token',
            'data': []
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # Xác thực vai trò y tá
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-nurse",
            headers={'Authorization': f'Bearer {token}'}
        )

        if response.status_code != 200:
            return Response({
                "errCode": 1,
                "message": "Không xác thực được vai trò y tá (User Service lỗi)",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        response_data = response.json()
        if response_data.get('errCode') != 0:
            return Response({
                "errCode": 1,
                "message": "Bạn không có quyền truy cập với vai trò y tá",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        nurse_id = response_data.get('user_id')

    except requests.RequestException as e:
        return Response({
            "errCode": 1,
            "message": "Lỗi khi gọi User Service",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except ValueError as e:
        return Response({
            "errCode": 1,
            "message": "Không phân tích được phản hồi từ User Service",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Lấy tham số ngày
    dateX = request.GET.get('date')
    if not nurse_id or not dateX:
        return Response({
            "errCode": 1,
            "message": "Thiếu tham số nurse_id hoặc date",
            "data": []
        }, status=status.HTTP_400_BAD_REQUEST)

    # Tìm lịch của y tá theo ngày
    schedule = Schedule.objects.filter(nurse_id=nurse_id, date=dateX).first()
    if not schedule:
        return Response({
            "errCode": 0,
            "message": "Y tá không có lịch trong ngày đã chọn",
            "data": []
        }, status=status.HTTP_200_OK)

    # Lấy các khung giờ từ lịch
    timeslots = TimeSlot.objects.filter(schedule_id=str(schedule.id))
    if not timeslots.exists():
        return Response({
            "errCode": 0,
            "message": "Không có khung giờ làm việc cho lịch này",
            "data": []
        }, status=status.HTTP_200_OK)

    result = []

    for slot in timeslots:
        try:
            time = Time.objects.get(id=ObjectId(slot.time_id))
        except Time.DoesNotExist:
            continue

        appointments = Appointment.objects.filter(timeslot_id=str(slot.id))
        for appt in appointments:
            try:
                medical = MedicalRecord.objects.get(id=ObjectId(appt.medical_id))
            except MedicalRecord.DoesNotExist:
                continue

            result.append({
                "appointment": {
                    "id": str(appt.id),
                    "reason": appt.reason,
                    "doctor_fee": appt.doctor_fee,
                    "status": appt.status,
                    "created_at": appt.created_at.strftime('%Y-%m-%d %H:%M:%S')
                },
                "time": time.time,
                "medical_record": {
                    "id": str(medical.id),
                    "name": medical.name,
                    "gender": medical.gender,
                    "phone": medical.phone,
                    "date_of_birth": medical.date_of_birth.strftime('%Y-%m-%d'),
                }
            })

    # Sắp xếp theo thời gian
    result.sort(key=lambda x: x['time'])

    return Response({
        "errCode": 0,
        "message": "Lấy dữ liệu thành công",
        "data": result
    }, status=status.HTTP_200_OK)
    
@api_view(['PUT'])
def change_status_appointment(request):
    try:
        medical_id = request.data.get('medical_id')
        status = request.data.get('status')

        if not medical_id or not status:
            return Response({
                "errCode": 1,
                "errMessage": "Thiếu medical_id hoặc status."
            }, status=400)

        appointment = Appointment.objects.filter(medical_id=medical_id).order_by('-created_at').first()

        if not appointment:
            return Response({
                "errCode": 2,
                "errMessage": "Không tìm thấy lịch hẹn với medical_id đã cho."
            }, status=404)

        appointment.status = status
        appointment.save()

        return Response({
            "errCode": 0,
            "message": "Cập nhật trạng thái thành công.",
            "data": {
                "medical_id": medical_id,
                "status": status
            }
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 3,
            "errMessage": "Đã xảy ra lỗi.",
            "detail": str(e)
        }, status=500)
        
   
@api_view(['PUT'])
def change_payment_status_appointment(request):
    try:
        medical_id = request.data.get('medical_id')
        status = request.data.get('payment_status')

        if not medical_id or not status:
            return Response({
                "errCode": 1,
                "errMessage": "Thiếu medical_id hoặc status."
            }, status=400)

        appointment = Appointment.objects.filter(medical_id=medical_id).order_by('-created_at').first()

        if not appointment:
            return Response({
                "errCode": 2,
                "errMessage": "Không tìm thấy lịch hẹn với medical_id đã cho."
            }, status=404)

        appointment.payment_status = status
        appointment.save()

        return Response({
            "errCode": 0,
            "message": "Cập nhật trạng thái thành công.",
            "data": {
                "medical_id": medical_id,
                "status": status
            }
        }, status=200)

    except Exception as e:
        return Response({
            "errCode": 3,
            "errMessage": "Đã xảy ra lỗi.",
            "detail": str(e)
        }, status=500)

@api_view(['GET'])
def get_appointment_medical_by_doctor_date(request):
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Thiếu hoặc sai định dạng token',
            'data': []
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # Xác thực vai trò 
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-doctor",
            headers={'Authorization': f'Bearer {token}'}
        )

        if response.status_code != 200:
            return Response({
                "errCode": 1,
                "message": "Không xác thực được vai trò bac sĩ (User Service lỗi)",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        response_data = response.json()
        if response_data.get('errCode') != 0:
            return Response({
                "errCode": 1,
                "message": "Bạn không có quyền truy cập với vai trò bác sĩ",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        doctor_id = response_data.get('user_id')

    except requests.RequestException as e:
        return Response({
            "errCode": 1,
            "message": "Lỗi khi gọi User Service",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except ValueError as e:
        return Response({
            "errCode": 1,
            "message": "Không phân tích được phản hồi từ User Service",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Lấy tham số ngày
    dateX = request.GET.get('date')
    if not doctor_id or not dateX:
        return Response({
            "errCode": 1,
            "message": "Thiếu tham số doctor_id hoặc date",
            "data": []
        }, status=status.HTTP_400_BAD_REQUEST)

    # Tìm lịch của y tá theo ngày
    schedule = Schedule.objects.filter(doctor_id=doctor_id, date=dateX).first()
    if not schedule:
        return Response({
            "errCode": 0,
            "message": "Y tá không có lịch trong ngày đã chọn",
            "data": []
        }, status=status.HTTP_200_OK)

    # Lấy các khung giờ từ lịch
    timeslots = TimeSlot.objects.filter(schedule_id=str(schedule.id))
    if not timeslots.exists():
        return Response({
            "errCode": 0,
            "message": "Không có khung giờ làm việc cho lịch này",
            "data": []
        }, status=status.HTTP_200_OK)

    result = []

    for slot in timeslots:
        try:
            time = Time.objects.get(id=ObjectId(slot.time_id))
        except Time.DoesNotExist:
            continue

        # Chỉ lấy các cuộc hẹn có trạng thái hợp lệ
        appointments = Appointment.objects.filter(
            timeslot_id=str(slot.id),
            status__in=['ready_for_doctor','waiting_result' ,'done','prescribed']
        )

        for appt in appointments:
            try:
                medical = MedicalRecord.objects.get(id=ObjectId(appt.medical_id))
            except MedicalRecord.DoesNotExist:
                continue

            result.append({
                "appointment": {
                    "id": str(appt.id),
                    "reason": appt.reason,
                    "doctor_fee": appt.doctor_fee,
                    "status": appt.status,
                    "payment_status": appt.payment_status,
                    "created_at": appt.created_at.strftime('%Y-%m-%d %H:%M:%S')
                },
                "time": time.time,
                "medical_record": {
                    "id": str(medical.id),
                    "name": medical.name,
                    "gender": medical.gender,
                    "phone": medical.phone,
                    "date_of_birth": medical.date_of_birth.strftime('%Y-%m-%d'),
                }
            })

    # Sắp xếp theo thời gian và thời điểm tạo cuộc hẹn
    result.sort(key=lambda x: (x['time'], x['appointment']['created_at']))

    return Response({
        "errCode": 0,
        "message": "Lấy dữ liệu thành công",
        "data": result
    }, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def get_appointment_medical_by_pharmacist_date(request):
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'errCode': 2,
            'message': 'Thiếu hoặc sai định dạng token',
            'data': []
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header.split(' ')[1]

    # Xác thực vai trò 
    try:
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-pharmacist",
            headers={'Authorization': f'Bearer {token}'}
        )

        if response.status_code != 200:
            return Response({
                "errCode": 1,
                "message": "Không xác thực được vai trò dược sĩ (User Service lỗi)",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        response_data = response.json()
        if response_data.get('errCode') != 0:
            return Response({
                "errCode": 1,
                "message": "Bạn không có quyền truy cập với vai trò dược sĩ",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        doctor_id = response_data.get('user_id')

    except requests.RequestException as e:
        return Response({
            "errCode": 1,
            "message": "Lỗi khi gọi User Service",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except ValueError as e:
        return Response({
            "errCode": 1,
            "message": "Không phân tích được phản hồi từ User Service",
            "data": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Lấy tham số ngày
    dateX = request.GET.get('date')

    # Tìm lịch của y tá theo ngày
    schedule = Schedule.objects.filter( date=dateX).first()
    if not schedule:
        return Response({
            "errCode": 0,
            "message": "Y tá không có lịch trong ngày đã chọn",
            "data": []
        }, status=status.HTTP_200_OK)

    # Lấy các khung giờ từ lịch
    timeslots = TimeSlot.objects.filter(schedule_id=str(schedule.id))
    if not timeslots.exists():
        return Response({
            "errCode": 0,
            "message": "Không có khung giờ làm việc cho lịch này",
            "data": []
        }, status=status.HTTP_200_OK)

    result = []

    for slot in timeslots:
        try:
            time = Time.objects.get(id=ObjectId(slot.time_id))
        except Time.DoesNotExist:
            continue

        # Chỉ lấy các cuộc hẹn có trạng thái hợp lệ
        appointments = Appointment.objects.filter(
            timeslot_id=str(slot.id),
            status__in=['done']
        )

        for appt in appointments:
            try:
                medical = MedicalRecord.objects.get(id=ObjectId(appt.medical_id))
            except MedicalRecord.DoesNotExist:
                continue

            result.append({
                "appointment": {
                    "id": str(appt.id),
                    "reason": appt.reason,
                    "doctor_fee": appt.doctor_fee,
                    "status": appt.status,
                    "payment_status": appt.payment_status,
                    "created_at": appt.created_at.strftime('%Y-%m-%d %H:%M:%S')
                },
                "time": time.time,
                "medical_record": {
                    "id": str(medical.id),
                    "name": medical.name,
                    "gender": medical.gender,
                    "phone": medical.phone,
                    "date_of_birth": medical.date_of_birth.strftime('%Y-%m-%d'),
                }
            })

    # Sắp xếp theo thời gian và thời điểm tạo cuộc hẹn
    result.sort(key=lambda x: (x['time'], x['appointment']['created_at']))

    return Response({
        "errCode": 0,
        "message": "Lấy dữ liệu thành công",
        "data": result
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_cashier_appointment_medical_by_date(request):
    dateX = request.GET.get('date')
    if not dateX:
        return Response({
            "errCode": 1,
            "message": "Thiếu ngày",
            "data": []
        }, status=status.HTTP_400_BAD_REQUEST)

    schedules = Schedule.objects.filter(date=dateX)
    result = []

    for schedule in schedules:
        timeslots = TimeSlot.objects.filter(schedule_id=str(schedule.id))
        for slot in timeslots:
            try:
                time = Time.objects.get(id=ObjectId(slot.time_id))
            except Time.DoesNotExist:
                continue

            appointments = Appointment.objects.filter(
                timeslot_id=str(slot.id),
                status__in=['waiting_result', 'done','prescribed']
            )

            for appt in appointments:
                try:
                    medical = MedicalRecord.objects.get(id=ObjectId(appt.medical_id))
                except MedicalRecord.DoesNotExist:
                    continue

                result.append({
                    "appointment": {
                        "id": str(appt.id),
                        "reason": appt.reason,
                        "doctor_fee": appt.doctor_fee,
                        "status": appt.status,
                        "payment_status": appt.payment_status,
                        "created_at": appt.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    "time": time.time,
                    "medical_record": {
                        "id": str(medical.id),
                        "name": medical.name,
                        "gender": medical.gender,
                        "phone": medical.phone,
                        "date_of_birth": medical.date_of_birth.strftime('%Y-%m-%d')
                    }
                })

    result.sort(key=lambda x: (x['time'], x['appointment']['created_at']))

    return Response({
        "errCode": 0,
        "message": "Lấy dữ liệu thành công",
        "data": result
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_medical_record_by_id(request):
    medical_id = request.GET.get('id')
    if not medical_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu id hồ sơ bệnh án",
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        medical = MedicalRecord.objects.get(id=ObjectId(medical_id))
    except MedicalRecord.DoesNotExist:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy hồ sơ bệnh án",
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)

    serialized_data = MedicalRecordSerializer(medical).data

    return Response({
        "errCode": 0,
        "message": "Lấy hồ sơ thành công",
        "data": serialized_data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
def mark_appointment_paid(request):
    medical_id = request.data.get('id')

    if not medical_id:
        return Response({
            "errCode": 1,
            "message": "Thiếu medical_id"
        }, status=status.HTTP_400_BAD_REQUEST)

    appointment = Appointment.objects.filter(medical_id=medical_id).first()

    if not appointment:
        return Response({
            "errCode": 1,
            "message": "Không tìm thấy lịch hẹn với medical_id này"
        }, status=status.HTTP_404_NOT_FOUND)

    # Cập nhật trạng thái thanh toán
    appointment.payment_status = True
    appointment.save()

    return Response({
        "errCode": 0,
        "message": "Cập nhật trạng thái thanh toán thành công",
        "data": {
            "appointment_id": str(appointment.id),
            "payment_status": appointment.payment_status
        }
    }, status=status.HTTP_200_OK)
    
    
    
@api_view(['GET'])
def get_appointment_medical_testrequest_paid_by_date(request):
    # Lấy tham số ngày
    dateX = request.GET.get('date')
    if not dateX:
        return Response({
            "errCode": 1,
            "message": "Thiếu tham số ngày",
            "data": []
        }, status=status.HTTP_400_BAD_REQUEST)

    schedule = Schedule.objects.filter(date=dateX).first()
    if not schedule:
        return Response({
            "errCode": 0,
            "message": "Y tá không có lịch trong ngày đã chọn",
            "data": []
        }, status=status.HTTP_200_OK)

    # Lấy các khung giờ từ lịch
    timeslots = TimeSlot.objects.filter(schedule_id=str(schedule.id))
    if not timeslots.exists():
        return Response({
            "errCode": 0,
            "message": "Không có khung giờ làm việc cho lịch này",
            "data": []
        }, status=status.HTTP_200_OK)

    result = []

    for slot in timeslots:
        try:
            time = Time.objects.get(id=ObjectId(slot.time_id))
        except Time.DoesNotExist:
            continue

        # Lấy các cuộc hẹn đã thanh toán
        all_appointments = Appointment.objects.filter(timeslot_id=str(slot.id))
        appointments = [appt for appt in all_appointments if appt.payment_status is True]

        for appt in appointments:
            try:
                medical = MedicalRecord.objects.get(id=ObjectId(appt.medical_id))
            except MedicalRecord.DoesNotExist:
                continue

            # Gọi API để lấy test_request từ lab_service
            test_request_data = []
            try:
                response = requests.get(
                    f"{URL_LAB_SV}/api/l/get-test-requests-by-medical-record",
                    params={"id": str(appt.medical_id)},
                )
               
                res_json = response.json()
                if res_json.get('errCode') == 0:
                    test_request_data = res_json.get('data', [])
            except Exception as e:
                print(f"Lỗi gọi API test_request: {e}")

            # Bỏ qua nếu test_request_data rỗng
            if not test_request_data:
                continue

            # Thêm dữ liệu vào kết quả
            result.append({
                "appointment": {
                    "id": str(appt.id),
                    "status": appt.status,
                    "payment_status": appt.payment_status,
                    "created_at": appt.created_at.strftime('%Y-%m-%d %H:%M:%S')
                },
                "time": time.time,
                "medical_record": {
                    "id": str(medical.id),
                    "name": medical.name,
                    "date_of_birth": medical.date_of_birth.strftime('%Y-%m-%d'),
                },
                'test_request': test_request_data
            })

    # Sắp xếp theo giờ và thời gian tạo
    result.sort(key=lambda x: (x['time'], x['appointment']['created_at']))

    return Response({
        "errCode": 0,
        "message": "Lấy dữ liệu thành công",
        "data": result
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_history_appointments_by_patient(request):
    # Lấy patient_id từ query params
    patient_id = request.GET.get('patient_id')
    
    if not patient_id:
        return Response({
            "errCode": 10,
            "message": "patient_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Lọc các MedicalRecord dựa trên patient_id
    medical_records = MedicalRecord.objects.filter(patient_id=patient_id)
    if not medical_records:
        return Response({
            "errCode": 0,
            "data":[]
        }, status=status.HTTP_200_OK)
    
    result = []
    
    for medical_record in medical_records:
        # Lọc các appointment dựa trên medical_id
        appointment = Appointment.objects.filter(medical_id=str(medical_record.id)).first()
        timeslot = TimeSlot.objects.filter(id=ObjectId(appointment.timeslot_id)).first()
            
        if timeslot:
            # Chuyển đổi schedule_id thành ObjectId và lấy schedule
            schedule = Schedule.objects.filter(id=ObjectId(timeslot.schedule_id)).first()
                
            if schedule:
                result.append({
                    "medical_id": str(medical_record.id),  # Thay appointment_id bằng medical_id
                    "status": appointment.status,                        
                    "schedule_date": schedule.date
                })
    
    return Response({
        "errCode": 0,
        "message": "Successfully fetched appointments and schedules",
        "data": result
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_doctor_weekly_schedule(request):
    # Lấy token từ header Authorization, chuẩn hóa dạng "Bearer <token>"
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({
            "errCode": 1,
            "message": "Missing Authorization token",
            "data": []
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header if auth_header.startswith("Bearer ") else f"Bearer {auth_header}"

    try:
        # Gọi User Service xác thực vai trò bác sĩ
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-doctor",
            headers={'Authorization': token}
        )
        json_resp = response.json()
        if response.status_code != 200 or json_resp.get('errCode') != 0:
            return Response({
                "errCode": 1,
                "message": "Bạn không có quyền truy cập với vai trò bác sĩ",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)
        doctor_id_input = json_resp.get('user_id')
    except Exception as e:
        return Response({
            "errCode": 1,
            "message": f"Lỗi xác thực người dùng: {str(e)}",
            "data": []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Lấy tham số start_date
    start_date_str = request.GET.get('start_date')
    if not start_date_str:
        return Response({
            "errCode": 1,
            "message": "Thiếu tham số start_date",
            "data": []
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({
            "errCode": 1,
            "message": "Định dạng ngày không hợp lệ. Dùng YYYY-MM-DD",
            "data": []
        }, status=status.HTTP_400_BAD_REQUEST)

    result = []

    # Lặp từng ngày trong tuần (7 ngày)
    for i in range(7):
        current_date = start_date + timedelta(days=i)

        # Lấy lịch cho ngày hiện tại
        schedules = Schedule.objects.filter(
            doctor_id=str(doctor_id_input),
            date=current_date
        )

        if schedules.exists():
            for s in schedules:
                # Lấy tên phòng (room_name)
                room_name = ""
                try:
                    if s.room_id:
                        room = Room.objects.get(id=ObjectId(s.room_id))
                        room_name = room.name
                except Exception:
                    room_name = ""

                nurse_name = ""
                if s.nurse_id:
                    try:
                        r = requests.get(
                            f"{URL_USER_SV}/api/u/get-nurse-by-user",
                            params={"id": s.nurse_id}
                        )
                        r_json = r.json()
                        if r_json.get("errCode") == 0:
                            nurse_name = r_json.get("data", {}).get("name", "")
                    except Exception:
                        nurse_name = ""

                result.append({
                    'id': str(s.id),
                    'doctor_id': s.doctor_id,
                    'nurse_id': s.nurse_id,
                    'date': current_date.strftime('%Y-%m-%d'),
                    'room_id': s.room_id,
                    'room_name': room_name,
                    'nurse_name': nurse_name
                })
        else:
            # Nếu không có lịch ngày đó thì trả về object rỗng
            result.append({
                'id': '',
                'doctor_id': "",
                'nurse_id': '',
                'date': current_date.strftime('%Y-%m-%d'),
                'room_id': '',
                'room_name': '',
                'nurse_name': ''
            })

    return Response({
        "errCode": 0,
        "message": "Lấy lịch làm việc thành công",
        "data": result
    }, status=status.HTTP_200_OK)
    


@api_view(['GET'])
def get_nurse_weekly_schedule(request):
    # Lấy token từ header Authorization, chuẩn hóa dạng "Bearer <token>"
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({
            "errCode": 1,
            "message": "Missing Authorization token",
            "data": []
        }, status=status.HTTP_401_UNAUTHORIZED)

    token = auth_header if auth_header.startswith("Bearer ") else f"Bearer {auth_header}"

    try:
        # Gọi User Service xác thực vai trò bác sĩ
        response = requests.get(
            f"{URL_USER_SV}/api/u/check-role-nurse",
            headers={'Authorization': token}
        )
        json_resp = response.json()
        if response.status_code != 200 or json_resp.get('errCode') != 0:
            return Response({
                "errCode": 1,
                "message": "Bạn không có quyền truy cập với vai trò bác sĩ",
                "data": []
            }, status=status.HTTP_403_FORBIDDEN)
        nurse_id_input = json_resp.get('user_id')
    except Exception as e:
        return Response({
            "errCode": 1,
            "message": f"Lỗi xác thực người dùng: {str(e)}",
            "data": []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Lấy tham số start_date
    start_date_str = request.GET.get('start_date')
    if not start_date_str:
        return Response({
            "errCode": 1,
            "message": "Thiếu tham số start_date",
            "data": []
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({
            "errCode": 1,
            "message": "Định dạng ngày không hợp lệ. Dùng YYYY-MM-DD",
            "data": []
        }, status=status.HTTP_400_BAD_REQUEST)

    result = []

    # Lặp từng ngày trong tuần (7 ngày)
    for i in range(7):
        current_date = start_date + timedelta(days=i)

        # Lấy lịch cho ngày hiện tại
        schedules = Schedule.objects.filter(
            nurse_id=str(nurse_id_input),
            date=current_date
        )

        if schedules.exists():
            for s in schedules:
                # Lấy tên phòng (room_name)
                room_name = ""
                try:
                    if s.room_id:
                        room = Room.objects.get(id=ObjectId(s.room_id))
                        room_name = room.name
                except Exception:
                    room_name = ""

                doctor_name = ""
                if s.doctor_id:
                    try:
                        r = requests.get(
                            f"{URL_USER_SV}/api/u/get-doctor-by-user",
                            params={"id": s.doctor_id}
                        )
                        r_json = r.json()
                        if r_json.get("errCode") == 0:
                            doctor_name = r_json.get("data", {}).get("name", "")
                    except Exception:
                        doctor_name = ""

                result.append({
                    'id': str(s.id),
                    'doctor_id': s.doctor_id,
                    'nurse_id': s.nurse_id,
                    'date': current_date.strftime('%Y-%m-%d'),
                    'room_id': s.room_id,
                    'room_name': room_name,
                    'doctor_name': doctor_name
                })
        else:
            # Nếu không có lịch ngày đó thì trả về object rỗng
            result.append({
                'id': '',
                'doctor_id': "",
                'nurse_id': '',
                'date': current_date.strftime('%Y-%m-%d'),
                'room_id': '',
                'room_name': '',
                'doctor_name': ''
            })

    return Response({
        "errCode": 0,
        "message": "Lấy lịch làm việc thành công",
        "data": result
    }, status=status.HTTP_200_OK)