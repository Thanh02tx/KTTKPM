import React, { useEffect, useState, useRef } from 'react';
import DatePicker, { registerLocale } from "react-datepicker";
import vi from "date-fns/locale/vi";
import { getMedicalCashier, getMedicalById } from '../../service/appointmentService';
import { getTestRequestsByMedicalRecord } from '../../service/laboratoryService';
import { getWardDistricProvince } from '../../service/address';
import { getDiagnosisByMedical } from '../../service/erhService';
import { getCashierByToken } from '../../service/userService';
import { getActivePaymentMethod, createBill } from '../../service/billService';
import "react-datepicker/dist/react-datepicker.css";
import html2canvas from "html2canvas";
import moment from 'moment';
import Select from 'react-select';
import { format } from 'date-fns';
import { Modal, ModalBody, ModalHeader, Button } from 'reactstrap';
// import '../../asset/scss/MedicalList.scss';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import { Triangle } from 'react-loader-spinner';
const MedicalList = () => {
    const billRef = useRef();
    const user = useSelector((state) => state.auth.user);
    const [date, setDate] = useState(new Date())
    const [nameSearch, setNameSearch] = useState('')
    const [medicalData, setMedicalData] = useState([])
    const [isOpenModal, setIsOpenModal] = useState(false)
    const [testRequestData, setTestRequestData] = useState([])
    const [medical, setMedical] = useState({})
    const [diagnosis, setDiognosis] = useState({})
    const [medicalItem, setMedicalItem] = useState("")
    const [paymentData, setPaymentData] = useState([])
    const [payment, setPayment] = useState("")
    const [cashier, setCashier] = useState({})
    const [isClickCreateBill, setIsClickCreatebill] = useState(false)
    const [total, setTotal] = useState("0")
    const [image, setImage] = useState("")
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        const loadPaymentData = async () => {
            let res = await getActivePaymentMethod();
            if (res?.errCode === 0) {
                // Dùng map để tạo một mảng mới với value và label
                const paymentMethods = res.data.map(item => ({
                    value: item.id,
                    label: item.name,
                }));
                setPaymentData(paymentMethods);
            }
            let re = await getCashierByToken(user.token)
            if (re?.errCode === 0) {
                setCashier(re.data)
            }
        }

        loadPaymentData();
    }, []);

    useEffect(() => {
        loadData()
    }, [date, user])
    const loadData = async () => {
        const formattedDate = format(date, 'yyyy-MM-dd');
        let res = await getMedicalCashier(formattedDate)

        if (res?.errCode === 0) {
            setMedicalData(res.data)
        }
    }
    useEffect(() => {
        if (!isOpenModal) {
            setTestRequestData({});
            setMedicalItem({});
            setMedical({});
            setDiognosis({});
            setPayment("");
            setIsClickCreatebill(false)
            setTotal("0")
        }
    }, [isOpenModal])

    const toggle = () => {
        setIsOpenModal(!isOpenModal);
    };
    const handleClickCreateBill = async (item) => {
        setLoading(true)
        setMedicalItem(item)
        let res = await getTestRequestsByMedicalRecord(item.medical_record.id)
        if (res?.errCode === 0) {
            setTestRequestData(res.data)
        }
        let resM = await getMedicalById(item.medical_record.id);
        if (resM?.errCode === 0) {

            let address = getWardDistricProvince(resM.data.ward, resM.data.district, resM.data.province)
            let fullMedical = {
                ...resM.data,
                address
            };
            setMedical(fullMedical)
        }
        let re = await getDiagnosisByMedical(item.medical_record.id)
        if (re?.errCode === 0) {
            setDiognosis(re.data)
        }
        setLoading(false)
        toggle()
    }
    const handleSubmitCreateBill = (e) => {
        e.preventDefault();
        setIsClickCreatebill(true);
    };
    useEffect(() => {
        if (isClickCreateBill && billRef.current) {
            const timer = setTimeout(async () => {
                const canvas = await html2canvas(billRef.current, { scale: 2 });
                const dataURL = canvas.toDataURL('image/png');
                setImage(dataURL);

                // Nếu không cần tải ảnh xuống, bỏ qua đoạn này
                // const link = document.createElement('a');
                // link.href = dataURL;
                // link.download = 'hoa-don.png';
                // link.click();
                let data = {
                    medical_id: medicalItem.medical_record.id,
                    payment_method: payment.value,
                    image: dataURL,
                    total: calculateTotalPrice()
                }
                setLoading(true)
                let res = await createBill(data, user.token)
                if (res?.errCode === 0) {
                    setLoading(false)
                    toast.success('Thành công')
                    toggle()
                    loadData()
                }
                else {
                    toast.error("Lỗi!")
                }
                setLoading(false)
                setIsClickCreatebill(false);
            }, 100); // delay nhỏ để DOM kịp render lại

            return () => clearTimeout(timer);
        }
    }, [isClickCreateBill]);
    const calculateTotalPrice = () => {
        const doctorFee = Number(medicalItem?.appointment?.doctor_fee) || 0;

        const testTotal = Array.isArray(testRequestData)
            ? testRequestData.reduce((sum, item) => sum + (Number(item?.price) || 0), 0)
            : 0;

        const totalPrice = doctorFee + testTotal;
        return totalPrice;
    };
    const handleChangePayment = (opt) => {
        setPayment(opt)
    }
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
                        <th>Thanh toán </th>
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
                                    {item?.appointment?.status === 'waiting_result' && 'Chờ kết quả'}
                                    {item?.appointment?.status === 'prescribed' && 'Chờ đơn thuốc'}
                                    {item?.appointment?.status === 'done' && 'Đã khám xong'}
                                    {item?.appointment?.status === 'rated' && 'Đã đánh giá'}
                                    {item?.appointment?.status === 'cancelled' && 'Đã huỷ'}
                                </td>
                                <td>
                                    {item?.appointment?.payment_status ? "Đã thanh toán" : " Chưa thanh toán"}
                                </td>
                                <td>
                                    <button
                                        className='btn btn-secondary'
                                        onClick={() => handleClickCreateBill(item)}
                                        disabled={item?.appointment?.payment_status}
                                    >
                                        <i className="fa-solid fa-plus fs-5"></i> Thanh toán
                                    </button>
                                </td>
                            </tr>
                        ))
                        : <tr className='text-center'>
                            <td colSpan={7}>Không có dữ liệu</td>
                        </tr>
                    }
                </tbody>
            </table>
            <Modal isOpen={isOpenModal} toggle={toggle} className="modal-vitalsign-container" size="xl">
                <ModalHeader toggle={toggle}>Hoá đơn</ModalHeader>
                <ModalBody>
                    <form onSubmit={handleSubmitCreateBill} className='mx-3'>
                        {/* div cần chuyển thanh ảnh đây */}
                        <div ref={billRef} className='px-3 py-4' >
                            <div className='fs-5 d-flex justify-content-between'>
                                <span>Phòng khám tim mạch TDT</span>
                                <span>Hình thức thanh toán: {payment?.label || ""}</span>
                            </div>
                            <h3 className='text-center'>HOÁ ĐƠN KHÁM BỆNH</h3>
                            <div className='row fs-5'>
                                <div className='col-7'>
                                    <div>Họ và tên: {medical?.name || "N/A"}</div>
                                    <div>Ngày sinh: {medical?.date_of_birth ? format(medical.date_of_birth, 'dd-MM-yyyy') : "N/A"}</div>
                                </div>
                                <div className='col-5'>
                                    <div>Số điện thoại: {medical?.phone || "N/A"}</div>
                                    <div>Giới tính: {medical?.gender === "male" && "Nam"}
                                        {medical?.gender === "female" && "Nữ"}
                                        {medical?.gender === "other" && "Khác"}
                                    </div>
                                </div>
                                <div>
                                    Địa chỉ: {medical?.address && medical?.address_detail ? `${medical.address_detail}, ${medical.address.ward}, ${medical.address.district}, ${medical.address.province}` : "N/A"}
                                </div>
                                <div>Số thẻ BHYT: {medical?.health_insurance || ""}</div>
                                <div>Chuẩn đoán: {diagnosis?.preliminary_diagnosis || ""}</div>
                                <div>Hoá đơn chi tiết: (Chưa thanh toán) </div>
                                <table className='table table-bordered border-black'>
                                    <thead>
                                        <tr>
                                            <th>Dịch vụ</th>
                                            <th>Giá (đồng)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Phí khám bác sĩ</td>
                                            <td>{medicalItem?.appointment?.doctor_fee || ""}</td>
                                        </tr>
                                        {testRequestData?.length > 0 && testRequestData.map((item, index) => {
                                            return (
                                                <tr key={`tq-${index}`}>
                                                    <td>{item?.name || ''}</td>
                                                    <td>{item?.price || ''}</td>
                                                </tr>
                                            );
                                        })}
                                        <tr>
                                            <td><strong>Tổng cộng:</strong></td>
                                            <td><strong>{calculateTotalPrice()}</strong></td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div className='row'>
                                <div className='col-5'>
                                    {!isClickCreateBill &&
                                        <div className='form-group'>
                                            <label>Phương thức thanh toán</label>
                                            <Select
                                                options={paymentData}
                                                value={payment}
                                                placeholder="Chọn Phương thức thanh toán"
                                                onChange={handleChangePayment}
                                            />
                                        </div>
                                    }
                                </div>
                                <div className='col-7 text-center '>
                                    {isClickCreateBill &&
                                        <div>
                                            <div className='fs-4' >
                                                {moment(new Date()).locale('vi').format('[Hà Nội],[ngày] D [tháng] M [năm] YYYY')}
                                            </div>
                                            <p className='mb-5'>(Dược sĩ)</p>
                                            <p>{cashier?.name || "N/A"}</p>
                                        </div>
                                    }

                                </div>
                            </div>
                        </div>

                        <div className='d-flex my-3'>
                            <Button color="primary" type="submit">
                                Tạo hoá đơn
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

export default MedicalList;
