import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import { useParams } from 'react-router-dom';
import moment from 'moment';

import '../../asset/scss/ScheduleDoctor.scss';
import Header from './Header';
import { getScheduleDoctorByTimeslotId, checkDuplicateAppointment, createAppointmentWithMedicalRecord } from '../../service/appointmentService';
import { getAllPatientRecordByUser } from '../../service/userService';
import { Triangle } from 'react-loader-spinner';
const ScheduleDoctor = () => {
  const user = useSelector((state) => state.auth.user);
  const [dataSchedule, setDataSchedule] = useState({});
  const [recordData, setRecordData] = useState([]);
  const [selectedRecordId, setSelectedRecordId] = useState(null);
  const [record, setRecord] = useState(null);
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [isShow, setIsShow] = useState(false);
  const { id } = useParams();

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      const res = await getScheduleDoctorByTimeslotId(id);
      if (res?.errCode === 0) {
        setDataSchedule(res.data);
      }

      if (user?.token) {
        const resPatients = await getAllPatientRecordByUser(user.token);
        if (resPatients?.errCode === 0) {
          setRecordData(resPatients.data);
        }
      }
      setLoading(false)
      setIsShow(true)
    };
    loadData();
  }, [id, user?.token]);

  const calculateAge = (dob) => {
    return moment().diff(moment(dob, 'YYYY-MM-DD'), 'years');
  };

  const handleSelectRecord = async (item) => {
    setSelectedRecordId(item.id);
    setRecord(item)
  };

  const handleBackSelectPatient = () => {
    setSelectedRecordId(null);
    setRecord(null);
  };
  const handleAppointment = async () => {
    let res = await checkDuplicateAppointment({
      patient_id: selectedRecordId,
      timeslot_id: id
    })
    if (res?.errCode === 0) {
      alert("Bạn đã có lịch hẹn vào ngày này rồi")
    } else {
      let data = {
        timeslot_id: id,
        reason: reason,
        patient_id: selectedRecordId,
        doctor_fee: dataSchedule.doctor.price,
        email_data: {
          doctor_name: dataSchedule.doctor.name,
          date: moment(dataSchedule.schedule.date).format('DD-MM-YYYY'),
          room_name: dataSchedule.room.name,
          time: dataSchedule.time.time,
          patient_name: record.name
        }
      }
      let resA = await createAppointmentWithMedicalRecord(data, user.token)
      if (resA?.errCode === 0) {
        toast.success("Đặt lịch thành công")
      } else {
        toast.error("Thất bại")
      }
    }

  }
  return (
    <div className="schedule-doctor-container">
      <Header />

      {isShow && <div>
        {dataSchedule ? (
          <div className="container my-3 content">
            <div>
              <i className="fa-solid fa-house"></i> / Đặt lịch khám
            </div>

            <div className="content-up my-3">
              <div className="img-wrapper">
                <img
                  src={dataSchedule?.doctor?.image}
                  alt="doctor"
                  className="doctor-img"
                />
              </div>

              <div className="title">
                <h2>{`${dataSchedule?.doctor?.degree} ${dataSchedule?.doctor?.name}`}</h2>
                <div
                  className="description-dt"
                  dangerouslySetInnerHTML={{
                    __html: dataSchedule?.doctor?.description_html,
                  }}
                />
                <p className="price">{`Giá khám: ${dataSchedule?.doctor?.price} VND`}</p>
                <p className="room">{`Phòng: ${dataSchedule?.room?.name} - Giờ: ${dataSchedule?.time?.time}`}</p>
              </div>
            </div>

            {selectedRecordId ? (
              <div>
                <div className="icon-left">
                  <i
                    className="fa-solid fa-chevron-left"
                    onClick={handleBackSelectPatient}
                  />
                </div>
                <div className="form-group reason mt-3">
                  <p className='text-danger'>Họ và tên: {record?.name || ''}</p>
                  <p className='text-danger'>Ngày sinh: {record?.date_of_birth ? moment(record.date_of_birth).format('DD/MM/YYYY') : ''}</p>
                  <label>Lý do khám (Reason for Visit)</label>
                  <input
                    className="form-control mt-2"
                    type="text"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Nhập thông tin lý do khám"
                    required
                  />
                  <button className='btn btn-secondary mt-2'
                    onClick={handleAppointment}
                  >Đặt lịch</button>
                </div>
              </div>
            ) : (
              <div className="sl-appointment">
                <div className="text-center text-danger">Chọn hồ sơ</div>

                <div className="ct-record">
                  {recordData?.length > 0 ? (
                    <div className="record-scroll d-flex gap-3">
                      {recordData.map((item, index) => (
                        <label
                          key={`pr-${index}`}
                          className={`doctor-card ${selectedRecordId === item.id ? 'selected' : ''
                            }`}
                        >
                          <input
                            type="radio"
                            name="patientRecord"
                            value={item.id}
                            onChange={() => handleSelectRecord(item)}
                            checked={selectedRecordId === item.id}
                            style={{ display: 'none' }}
                          />
                          <div className="image-wrapper">
                            <img
                              src={item.image}
                              alt="patient-record"
                              className="doctor-img"
                            />
                          </div>
                          <div className="text-center mt-2">
                            {`${item.name} - ${calculateAge(item.date_of_birth)} Tuổi`}
                          </div>
                        </label>
                      ))}
                    </div>
                  ) : (
                    <div>Không có hồ sơ bệnh nhân.</div>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center mt-5">Không có dữ liệu lịch khám</div>
        )}

      </div>
      }
      {loading && (
        <div style={{
          position: "fixed",
          top: 0, left: 0,
          width: "100vw",
          height: "100vh",
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          zIndex: 9999,
        }}>
          <Triangle height={100} width={100} color="#00BFFF" />
        </div>
      )}
    </div>
  );
};

export default ScheduleDoctor;
