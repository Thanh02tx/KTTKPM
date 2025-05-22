import React, { useEffect, useState } from 'react';
import DatePicker, { registerLocale } from "react-datepicker";
import vi from "date-fns/locale/vi";
import { getMedicalByNurseAndDate } from '../../service/appointmentService';
import { createVitalSign } from '../../service/erhService';
import "react-datepicker/dist/react-datepicker.css";
import { format } from 'date-fns';
import { Modal, ModalBody, ModalHeader, Button } from 'reactstrap';
// import '../../asset/scss/NurseMedicalList.scss';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import { Triangle } from 'react-loader-spinner';
const NurseMedicalList = () => {
    const user = useSelector((state) => state.auth.user);
    const [date, setDate] = useState(new Date())
    const [nameSearch, setNameSearch] = useState('')
    const [medicalData, setMedicalData] = useState([])
    const [isOpenModal, setIsOpenModal] = useState(false)
    const [blood_pressure, setBloodPressure] = useState([])
    const [heart_rate, setHeartRate] = useState([])
    const [height, setHeight] = useState([])
    const [weight, setWeight] = useState([])
    const [medical, setMedical] = useState({})
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        loadData()
    }, [date, user])
    const loadData = async () => {
        const formattedDate = format(date, 'yyyy-MM-dd');
        if (user?.token) {
            let res = await getMedicalByNurseAndDate(formattedDate, user.token)
            if (res?.errCode === 0) {
                setMedicalData(res.data)
            }
        }

    }
    useEffect(() => {
        if (!isOpenModal) {
            setBloodPressure('');
            setHeartRate('');
            setHeight('');
            setWeight('');
            setMedical({});
        }
    }, [isOpenModal])

    const toggle = () => {
        setIsOpenModal(!isOpenModal);
    };
    const handleClickCreateVitalSign = (item) => {
        setMedical(item)
        toggle()
        console.log('sdaitem', item)
    }
    const handleSubmitCreateVitalSign = async (e) => {
        e.preventDefault(); // Ngăn reload trang
        setLoading(true)
        let res = await createVitalSign({
            medical_id: medical.medical_record.id,
            blood_pressure,
            heart_rate,
            height,
            weight
        }, user.token);

        if (res?.errCode === 0) {
            setLoading(false)
            toast.success('Thêm thành công!');
            toggle();
            await loadData()
        } else {
            toast.error('Lỗi');
        }
        setLoading(false)
    };
    return (
        <div className='nurse-medical-list-container container'>
            <div className='row mt-4' >
                <div className="form-group col-2">
                    <DatePicker
                        className="form-control"
                        selected={date}
                        onChange={(date) => setDate(date)}
                        locale="vi"
                        dateFormat="dd/MM/yyyy"
                        maxDate={new Date()}
                    />
                </div>
                <div className='col-4'>
                    <input
                        className='form-control '
                        type='text'
                        value={nameSearch}
                        onChange={(e) => setNameSearch(e.target.value)}
                        placeholder='Nhập tên để tìm kiếm'
                    />
                </div>
                <div className='col-2'>
                    <button className='btn btn-primary'>Tìm kiếm</button>
                </div>
            </div>
            <table className='table table-border mt-3'>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Họ và Tên</th>
                        <th>Ngày sinh</th>
                        <th>Thời gian</th>
                        <th>Trạng Thái</th>
                        <th>Hành động</th>
                    </tr>
                </thead>
                <tbody>
                    {medicalData?.length > 0 ?
                        medicalData.map((item, index) => (
                            <tr key={`m-${index}`}>
                                <td>{index + 1}</td>
                                <td>{item?.medical_record?.name ? item.medical_record.name : ''}</td>
                                <td>{item?.medical_record?.date_of_birth ? format(item.medical_record.date_of_birth, 'dd-MM-yyyy') : ''}</td>
                                <td>{item?.time ? item.time : ''}</td>
                                <td>
                                    {item?.appointment?.status === 'booked' && 'Đã đặt'}
                                    {item?.appointment?.status === 'ready_for_doctor' && 'Chờ bác sĩ'}
                                    {item?.appointment?.status === 'prescribed' && 'Chờ đơn thuốc'}
                                    {item?.appointment?.status === 'done' && 'Đã khám xong'}
                                    {item?.appointment?.status === 'rated' && 'Đã đánh giá'}
                                    {item?.appointment?.status === 'cancelled' && 'Đã huỷ'}
                                </td>
                                <td>
                                    <button
                                        className='btn btn-secondary'
                                        onClick={() => handleClickCreateVitalSign(item)}
                                        disabled={item?.appointment?.status !== 'booked'}
                                    >
                                        <i className="fa-solid fa-plus fs-5"></i> Chỉ số
                                    </button>
                                </td>
                            </tr>
                        ))
                        : <tr colSpan={6} className='text-center'>Không có dữ liệu</tr>}
                </tbody>
            </table>
            <Modal isOpen={isOpenModal} toggle={toggle} className="modal-vitalsign-container" size="lg">
                <ModalHeader toggle={toggle}>Chỉ số sinh tồn</ModalHeader>
                <ModalBody>
                    <form onSubmit={handleSubmitCreateVitalSign}>
                        <div className="modal-vitalsign-body row">
                            <div className="form-group col-6">
                                <label>Huyết áp</label>
                                <input
                                    className="form-control"
                                    type="text"
                                    placeholder="Nhập thông tin"
                                    value={blood_pressure}
                                    onChange={(e) => setBloodPressure(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="form-group col-6">
                                <label>Nhịp tim</label>
                                <input
                                    className="form-control"
                                    type="text"
                                    placeholder="Nhập thông tin"
                                    value={heart_rate}
                                    onChange={(e) => setHeartRate(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="form-group col-6">
                                <label>Chiều cao</label>
                                <input
                                    className="form-control"
                                    type="text"
                                    placeholder="Nhập thông tin"
                                    value={height}
                                    onChange={(e) => setHeight(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="form-group col-6">
                                <label>Cân nặng</label>
                                <input
                                    className="form-control"
                                    type="text"
                                    placeholder="Nhập thông tin"
                                    value={weight}
                                    onChange={(e) => setWeight(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        <div className='d-flex my-3'>
                            <Button color="primary" type="submit">
                                Thêm chỉ số
                            </Button>
                            <Button color='secondary' className='mx-3' onClick={toggle}>
                                Huỷ
                            </Button>
                        </div>
                    </form>
                </ModalBody>
            </Modal>
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

export default NurseMedicalList;
