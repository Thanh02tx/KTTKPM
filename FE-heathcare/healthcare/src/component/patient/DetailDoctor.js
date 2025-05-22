import React, { useEffect, useState } from 'react';
import '../../asset/scss/DetailDoctor.scss';
import { useSelector } from 'react-redux';
import Header from './Header';
import { useParams } from 'react-router-dom';
import { getDoctorByUserId } from '../../service/userService';
import { getTimeslotsByDateAndDoctor } from '../../service/appointmentService';
import NotFound from '../../component/NotFound'
import { useNavigate } from 'react-router-dom';
import moment from 'moment';

const DetailDoctor = () => {
    const user = useSelector((state) => state.auth.user);
    const navigate = useNavigate();
    const { id } = useParams();
    const [doctorData, setDoctorData] = useState({});
    const [weekDates, setWeekDates] = useState([]);
    const [selectedDate, setSelectedDate] = useState(null);
    const [timeslotData, setTimeslotData] = useState('')
    const [isNotFound, setIsNotFound] = useState(false)
    useEffect(() => {
        const loadData = async () => {
            let res = await getDoctorByUserId(id);
            if (res?.errCode === 0) {
                setDoctorData(res.data);
                setIsNotFound(false)
            }
            else {
                setIsNotFound(true)
            }
        };
        loadData();
    }, [id]);

    useEffect(() => {
        const today = new Date();
        const dates = [];

        for (let i = 1; i <= 7; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i-1);
            dates.push({
                label: `${getWeekday(date.getDay())} - ${date.getDate()}/${date.getMonth() + 1}`,
                value: date,
            });
        }

        setWeekDates(dates);
        setSelectedDate(dates[0]);
    }, []);

    const getWeekday = (day) => {
        const days = ['CN', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
        return days[day];
    };


    useEffect(() => {
        const loadTimeSlot = async () => {
            if (!selectedDate) return;
            const date = moment(selectedDate.value).format('YYYY-MM-DD');
            try {
                const res = await getTimeslotsByDateAndDoctor(date, id);
                if (res?.errCode === 0) {
                    setTimeslotData(res.data); // res.data.data nếu res trả về { errCode, message, data }
                }
            } catch (error) {
                console.error('Lỗi load time slot:', error);
            }
        };
        loadTimeSlot();
    }, [selectedDate, id]);
    useEffect(() => {
        console.log('êa', timeslotData)
    }, [timeslotData])

    const handleClickSchedule = (id) => {
        navigate(`/schedule/${id}`);
    }

    return (
        <div className="detail-doctor-container">
            <Header />
            {isNotFound
                ?
                <NotFound />
                :
                <div className="container">
                    {doctorData && (
                        <div className="content">
                            <div className="content-up">
                                <div className="img-wrapper">
                                    <img
                                        src={doctorData.image}
                                        alt="doctor"
                                        className="doctor-img"
                                    />
                                </div>
                                <div className="title">
                                    <h2>{`${doctorData.degree} ${doctorData.name}`}</h2>
                                    <div
                                        className="description"
                                        dangerouslySetInnerHTML={{ __html: doctorData.description_html }}
                                    />
                                    <h5>{`Giá khám: ${doctorData.price} VND`}</h5>
                                </div>
                            </div>

                            <div className="date-select">
                                <select
                                    value={selectedDate?.label}
                                    onChange={(e) => {
                                        const selected = weekDates.find((d) => d.label === e.target.value);
                                        setSelectedDate(selected);
                                    }}
                                >
                                    {weekDates.map((d, i) => (
                                        <option key={i} value={d.label}>
                                            {d.label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className='timeslot-ct my-3'>
                                {timeslotData?.length > 0 ?
                                    timeslotData.map((item, index) => (
                                        <div key={`ts-${index}`}
                                            onClick={() => handleClickSchedule(item.id)}
                                            className={item.current_number >= item.max_number ? "item-timeslot is-full" : "item-timeslot"}
                                        >
                                            {item.time}
                                        </div>
                                    ))
                                    : <div>
                                        Hôm nay Bác sĩ không có lịch khám!
                                    </div>
                                }
                            </div>
                            <div
                                className="content-down"
                                dangerouslySetInnerHTML={{ __html: doctorData.bio_html }}
                            />
                        </div>
                    )}
                </div>
            }
        </div>
    );
};

export default DetailDoctor;
