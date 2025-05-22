import React, { useEffect, useState } from 'react';
import moment from 'moment';
import 'moment/locale/vi';
import '../../asset/scss/ManageSchedule.scss';
import Select from 'react-select';
import { getSelectAllDoctor, getSelectAllNurse } from '../../service/userService';
import { getRooms, createSchedulesAndTimeSlots, getSchedulesWeek } from '../../service/appointmentService';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';

const ManageSchedule = () => {
  const user = useSelector((state) => state.auth.user);
  const [startOfWeek, setStartOfWeek] = useState(moment().startOf('isoWeek'));
  const [doctorsData, setDoctorsData] = useState([]);
  const [nursesData, setNursesData] = useState([]);
  const [roomData, setRoomData] = useState([]);
  const [scheduleSelection, setScheduleSelection] = useState({});

  const getWeekDates = () => Array.from({ length: 6 }, (_, i) => moment(startOfWeek).add(i, 'days'));
  const weekDates = getWeekDates();

  const handlePrevWeek = () => setStartOfWeek(prev => moment(prev).subtract(7, 'days'));
  const handleNextWeek = () => setStartOfWeek(prev => moment(prev).add(7, 'days'));

  useEffect(() => {
    const fetchData = async () => {
      const [resDoctor, resNurse, resRoom] = await Promise.all([
        getSelectAllDoctor(),
        getSelectAllNurse(),
        getRooms()
      ]);

      if (resDoctor?.errCode === 0) {
        const formattedDoctors = resDoctor.data.map(doc => ({
          value: doc.value.toString(),
          label: doc.label
        }));
        setDoctorsData(formattedDoctors);
      }

      if (resNurse?.errCode === 0) {
        const formattedNurses = resNurse.data.map(n => ({
          value: n.value.toString(),
          label: n.label
        }));
        setNursesData(formattedNurses);
      }

      if (resRoom?.errCode === 0) {
        const formattedRooms = resRoom.data.map(room => ({
          room_id: room.id,
          name: room.name
        }));
        setRoomData(formattedRooms);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    const fetchSchedules = async () => {
      if (roomData.length === 0 || doctorsData.length === 0 || nursesData.length === 0) return;

      const start = moment(startOfWeek).format('YYYY-MM-DD');
      const res = await getSchedulesWeek(start);

      if (res?.errCode === 0) {
        const scheduleMap = {};

        roomData.forEach(room => {
          scheduleMap[room.room_id] = {};
          weekDates.forEach((_, idx) => {
            scheduleMap[room.room_id][idx] = { doctor: null, nurse: null };
          });
        });

        res.data.forEach(item => {
          const roomId = item.room_id;
          const dateIdx = weekDates.findIndex(date => date.format('YYYY-MM-DD') === item.date);

          if (roomId && dateIdx !== -1) {
            const doctorOption = doctorsData.find(doc => doc.value === item.doctor_id.toString()) || null;
            const nurseOption = nursesData.find(n => n.value === item.nurse_id.toString()) || null;

            scheduleMap[roomId][dateIdx] = {
              doctor: doctorOption,
              nurse: nurseOption
            };
          }
        });

        setScheduleSelection(scheduleMap);
      }
    };

    fetchSchedules();
  }, [startOfWeek, roomData, doctorsData, nursesData]);

  useEffect(() => {
    const init = {};
    roomData.forEach(room => {
      init[room.room_id] = {};
      weekDates.forEach((_, dIdx) => {
        init[room.room_id][dIdx] = { doctor: null, nurse: null };
      });
    });
    setScheduleSelection(init);
  }, [startOfWeek, roomData]);

  const handleChange = (type, roomId, dayIdx, selectedOption) => {
    setScheduleSelection(prev => ({
      ...prev,
      [roomId]: {
        ...prev[roomId],
        [dayIdx]: {
          ...prev[roomId][dayIdx],
          [type]: selectedOption || null
        }
      }
    }));
  };

  const handleSubmitColumn = async (dayIdx) => {
    const date = weekDates[dayIdx].format('YYYY-MM-DD');

    const doctorsSet = new Set();
    const nursesSet = new Set();
    const duplicates = [];
    let missingInfo = false;

    const dataForDay = roomData.map(room => {
      const { doctor, nurse } = scheduleSelection[room.room_id]?.[dayIdx] || {};

      if (doctor?.value) {
        if (doctorsSet.has(doctor.value)) {
          duplicates.push({ doctor_id: doctor.value, room_id: room.room_id });
        } else {
          doctorsSet.add(doctor.value);
        }
      } else {
        missingInfo = true;
      }

      if (nurse?.value) {
        if (nursesSet.has(nurse.value)) {
          duplicates.push({ nurse_id: nurse.value, room_id: room.room_id });
        } else {
          nursesSet.add(nurse.value);
        }
      } else {
        missingInfo = true;
      }

      return {
        date,
        room_id: room.room_id,
        doctor_id: doctor?.value || null,
        nurse_id: nurse?.value || null
      };
    });

    if (missingInfo) {
      alert("⚠️ Vui lòng nhập đủ thông tin Bác sĩ và Y tá");
    } else if (duplicates.length > 0) {
      alert("⚠️ Có Bác sĩ hoặc Y tá trùng lịch");
    } else {
      let data = {
        schedules: dataForDay,
        maxNumber: 5,
        date: date
      };
      let res = await createSchedulesAndTimeSlots(data, user.token);
      if (res?.errCode === 0) {
        toast.success('Thành công !');
      } else {
        toast.error("Lỗi!");
      }
    }
  };

  const handleSubmitAllWeek = () => {
    const result = weekDates.map((date, dayIdx) => {
      const daily = roomData.map(room => {
        const { doctor, nurse } = scheduleSelection[room.room_id]?.[dayIdx] || {};
        return {
          date: date.format('YYYY-MM-DD'),
          room_id: room.room_id,
          doctor_id: doctor?.value || null,
          nurse_id: nurse?.value || null
        };
      });
      return daily;
    }).flat();

    console.log('📆 Toàn bộ lịch trong tuần:', result);
  };

  // Sửa lại điều kiện để bao gồm cả hôm nay
  const isPastOrToday = (date) => moment(date).isSameOrBefore(moment(), 'day');

  return (
    <div className="manage-schedule m-5">
      <div className="schedule-header my-3 d-flex justify-content-between align-items-center">
        <button className="btn btn-outline-secondary" onClick={handlePrevWeek}>←</button>
        <h5 className="mb-0">
          Tuần: {startOfWeek.format('DD/MM')} - {moment(startOfWeek).add(5, 'days').format('DD/MM/YYYY')}
        </h5>
        <button className="btn btn-outline-secondary" onClick={handleNextWeek}>→</button>
      </div>

      <table className="table table-bordered text-center">
        <thead className="table-light">
          <tr>
            <th>Phòng</th>
            {weekDates.map((date, index) => (
              <th key={index}>
                <div className="fw-bold">{date.format('dddd').toUpperCase()}</div>
                <div>{date.format('DD/MM')}</div>
              </th>
            ))}
          </tr>
        </thead>

        <tbody className="text-start">
          {roomData.map((room) => (
            <tr key={room.room_id}>
              <td className="fw-bold">{room.name}</td>
              {weekDates.map((date, colIdx) => (
                <td key={colIdx}>
                  <div>
                    <Select
                      value={scheduleSelection[room.room_id]?.[colIdx]?.doctor || null}
                      onChange={(selectedOption) => handleChange('doctor', room.room_id, colIdx, selectedOption)}
                      options={doctorsData}
                      placeholder="-- Chọn bác sĩ --"
                      isDisabled={isPastOrToday(date)}
                    />
                  </div>
                  <div className="mt-1">
                    <Select
                      value={scheduleSelection[room.room_id]?.[colIdx]?.nurse || null}
                      onChange={(selectedOption) => handleChange('nurse', room.room_id, colIdx, selectedOption)}
                      options={nursesData}
                      placeholder="-- Chọn y tá --"
                      isDisabled={isPastOrToday(date)}
                    />
                  </div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>

        <tfoot>
          <tr>
            <td></td>
            {weekDates.map((date, colIdx) => (
              <td key={colIdx}>
                {!isPastOrToday(date) && (
                  <button className="btn btn-sm btn-primary" onClick={() => handleSubmitColumn(colIdx)}>
                    Gửi
                  </button>
                )}
              </td>
            ))}
          </tr>
        </tfoot>
      </table>

      <div className="d-flex justify-content-end my-3">
        <button className="btn btn-success" onClick={handleSubmitAllWeek}>
          Gửi toàn bộ tuần
        </button>
      </div>
    </div>
  );
};

export default ManageSchedule;
