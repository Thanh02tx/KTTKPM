import React, { useEffect, useState } from 'react';
import moment from 'moment';
// import '../../asset/scss/DoctorSchedule.scss';
import { getDoctorWeeklySchedule } from '../../service/appointmentService';
import { useSelector } from 'react-redux';
import { Triangle } from 'react-loader-spinner';
const DoctorSchedule = () => {
    const user = useSelector((state) => state.auth.user);
    const [startOfWeek, setStartOfWeek] = useState(moment().startOf('isoWeek'));
    const [schedules, setSchedules] = useState([]);
    const [loading, setLoading] = useState(false);
    const handlePrevWeek = () => setStartOfWeek(prev => moment(prev).subtract(7, 'days'));
    const handleNextWeek = () => setStartOfWeek(prev => moment(prev).add(7, 'days'));

    useEffect(() => {
        const loadData = async () => {
            if (user?.token) {
                // Format ngày startOfWeek theo 'YYYY-MM-DD'
                setLoading(true)
                const formattedDate = startOfWeek.format('YYYY-MM-DD');
                let res = await getDoctorWeeklySchedule(formattedDate, user.token);
                if (res?.errCode === 0) {
                    setSchedules(res.data);
                    setLoading(false)
                } else {
                    setSchedules([]);
                }
                setLoading(false)
            }
        }
        loadData();
    }, [startOfWeek]);
    const formatDate = (dateStr) => {
        const days = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
        const date = new Date(dateStr);
        const dayName = days[date.getDay()];
        const day = date.getDate();
        const month = date.getMonth() + 1;
        return `${dayName} - ${day}/${month}`;
    };

    return (
        <div className='doctor-schedule-container container mt-4'>
            <div className="schedule-header my-3 d-flex justify-content-between align-items-center">
                <button className="btn btn-outline-secondary" onClick={handlePrevWeek}>←</button>
                <h5 className="mb-0">
                    Tuần: {startOfWeek.format('DD/MM')} - {moment(startOfWeek).add(5, 'days').format('DD/MM/YYYY')}
                </h5>
                <button className="btn btn-outline-secondary" onClick={handleNextWeek}>→</button>
            </div>
            <table className='table table-bordered'>
                <thead>
                    <tr>
                        <th></th>
                        {schedules?.length > 0 && schedules.map((item, index) => (
                            <th>{formatDate(item.date)}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th className='text-center'>Y tá</th>
                        {schedules?.length > 0 && schedules.map((item, index) => {
                            if (item.id) return <td>{item.nurse_name}</td>
                            return <td rowSpan={2} className='text-center align-middle'>Nghỉ</td>
                        })}
                    </tr>
                    <tr>
                        <th className='text-center'>Phòng</th>
                        {schedules?.length > 0 && schedules.map((item, index) => {
                            if (item.id) return <td>{item.room_name}</td>
                            return null;
                        })}
                    </tr>
                </tbody>
            </table>
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

export default DoctorSchedule;
