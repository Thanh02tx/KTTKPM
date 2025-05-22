import React, { useEffect, useState, useRef } from 'react';
import DatePicker, { registerLocale } from "react-datepicker";
import vi from "date-fns/locale/vi";
import { getMedicalByPharmacistAndDate } from '../../service/appointmentService';
import { getPrescriptionByMedical, getActivePaymentMethods, createInvoice } from '../../service/pharmacist';
import { getMedicalById } from '../../service/appointmentService';
import { getWardDistricProvince } from '../../service/address';
import { getPharmacistByToken } from '../../service/userService';
import html2canvas from "html2canvas";
import "react-datepicker/dist/react-datepicker.css";
import Select from 'react-select'
import moment from 'moment';
import { format } from 'date-fns';
import { Modal, ModalBody, ModalHeader, Button } from 'reactstrap';
import { Triangle } from 'react-loader-spinner';
// import '../../asset/scss/PharmacistMedicalList.scss';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
const PharmacistMedicalList = () => {
    const resultRef = useRef();
    const user = useSelector((state) => state.auth.user);
    const [date, setDate] = useState(new Date())
    const [nameSearch, setNameSearch] = useState('')
    const [medicalData, setMedicalData] = useState([])
    const [medical, setMedical] = useState({})
    const [prescription, setPrescription] = useState({})
    const [totals, setTotals] = useState(0)
    const [isOpenModal, setIsOpenModal] = useState(false)
    const [isCreate, setIsCreate] = useState(false)
    const [technician, setTechnician] = useState(false)
    const [paymentData, setPaymentData] = useState([])
    const [payment, setPayment] = useState("")
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        loadData()
    }, [date, user])
    const loadData = async () => {
        const formattedDate = format(date, 'yyyy-MM-dd');
        if (user?.token) {
            let res = await getMedicalByPharmacistAndDate(formattedDate, user.token)
            if (res?.errCode === 0) {
                setMedicalData(res.data)
            }
            let re = await getPharmacistByToken(user.token)
            if (re?.errCode === 0) {
                setTechnician(re.data)
            }
            let resP = await getActivePaymentMethods()
            if (resP?.errCode === 0) {
                const paymentMethods = resP.data.map(item => ({
                    value: item.id,
                    label: item.name,
                }));
                setPaymentData(paymentMethods);
            }
        }

    }
    useEffect(() => {
        if (!isOpenModal) {
            setMedical({})
            setPrescription({})
            setIsCreate(false)
            setTotals(0)
            setPayment("")
        }
    }, [isOpenModal])

    const toggle = () => {
        setIsOpenModal(!setIsOpenModal)

    }

    const handleClickOpenModel = async (item) => {
        let resM = await getMedicalById(item.medical_record.id)
        let res = await getPrescriptionByMedical(item.medical_record.id)
        if (resM?.errCode === 0) {
            let address = getWardDistricProvince(resM.data.ward, resM.data.district, resM.data.province)
            let fullMedical = {
                ...resM.data,
                address
            };
            setMedical(fullMedical)
        }
        if (res?.errCode === 0) {
            if (res.data?.medicines) {
                res.data.medicines = res.data.medicines.map(item => ({
                    ...item,
                    check: false
                }));
            } else {
                res.data.medicines = [];
            }
            setPrescription(res.data);
        }

        setIsOpenModal(true)
    }
    const handleToggleCheck = (index) => {
        const updatedMedicines = prescription.medicines.map((item, i) =>
            i === index ? { ...item, check: !item.check } : item
        );

        // Gán lại prescription
        setPrescription({ ...prescription, medicines: updatedMedicines });

        // Tính totals dựa trên updatedMedicines
        let t = 0;
        updatedMedicines.forEach((item) => {
            if (item.check) {
                t += Number(item.price) * Number(item.quantity);
            }
        });
        setTotals(t);
    };
    const handleSubmit = (e) => {
        e.preventDefault();
        if (totals > 0) {
            setIsCreate(true)
        } else {
            alert('Không có thuốc nào được chọn mua!')
        }

    }
    useEffect(() => {
        if (isCreate && resultRef.current) {
            const timer = setTimeout(() => {
                html2canvas(resultRef.current, { scale: 2 }).then((canvas) => {
                    canvas.toBlob(async (blob) => {
                        if (!blob) {
                            toast.error("Không thể tạo file ảnh!");
                            return;
                        }

                        const file = new File([blob], 'result.png', { type: 'image/png' });
                        let presMedicine = prescription.medicines.filter(item => item.check === true)
                        console.log('sfaa', presMedicine)
                        const formData = new FormData();
                        formData.append('image', file)
                        formData.append('payment_method_id', payment.value);
                        formData.append('prescription_id', prescription.id);
                        formData.append('totals', totals);
                        formData.append('list_pres_med', JSON.stringify(presMedicine));
                        // console.log('esfs',presMedicine)
                        try {
                            setLoading(true)
                            const res = await createInvoice(formData, user.token);
                            if (res?.errCode === 0) {
                                setLoading(false)
                                toast.success('Thành công');
                                toggle();
                                loadData();
                            } else {
                                toast.error("Lỗi!");
                            }
                            setLoading(false)
                        } catch (error) {
                            console.error('Gửi request bị lỗi: ', error);
                            toast.error("Lỗi khi gửi dữ liệu!");
                        }
                        setLoading(false)
                        setIsCreate(false);
                    }, 'image/png');
                });

                return () => clearTimeout(timer);
            }, 100);
        }
    }, [isCreate]);
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
                                    <button
                                        className='btn btn-secondary'
                                        onClick={() => handleClickOpenModel(item)}
                                    >
                                        Xem
                                    </button>
                                </td>
                            </tr>
                        ))
                        : <tr colSpan={6} className='text-center'>Không có dữ liệu</tr>}
                </tbody>
            </table>
            <Modal isOpen={isOpenModal} toggle={toggle} className="modal-vitalsign-container" size="xl">
                <ModalHeader toggle={toggle}>Chỉ số sinh tồn</ModalHeader>
                <ModalBody>
                    <form onSubmit={handleSubmit}>
                        <div className="modal-prescription-body" ref={resultRef}>
                            <div className='fs-5 d-flex justify-content-between'>
                                <span>Phòng khám tim mạch TDT</span>
                                {isCreate ? <span>Hình thức thanh toán: {payment?.label || ""}</span> : "Đã mua"}
                            </div>
                            <h3 className='text-center my-2'>ĐƠN THUỐC</h3>
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
                                <div className='mb-2'>Đơn thuốc:</div>
                            </div>
                            {prescription?.status === 'pending' &&
                                <>
                                    <table className='table table-bordered'>
                                        <tbody>
                                            {prescription?.medicines?.length > 0 ? (
                                                <>
                                                    <tr>
                                                        <th>Tên thuốc</th>
                                                        <th>Số lượng</th>
                                                        <th>Giá</th>
                                                        <th>Thành tiền</th>
                                                        {!isCreate &&
                                                            <>
                                                                <th>Trạng thái</th>
                                                                <th></th>
                                                            </>
                                                        }

                                                    </tr>

                                                    {prescription.medicines.map((item, index) => {
                                                        if (!isCreate) {
                                                            return (
                                                                <tr key={index}>
                                                                    <td>{item.medicine_name}</td>
                                                                    <td>{item.quantity}</td>
                                                                    <td>{item.price} đ</td>
                                                                    <td>{Number(item.quantity) * Number(item.price)} đ</td>
                                                                    <td>{item.quantity > item.stock ? 'Không đủ thuốc' : 'Đủ thuốc'}</td>
                                                                    <td>
                                                                        <input
                                                                            type="checkbox"
                                                                            checked={item.check}
                                                                            onChange={() => handleToggleCheck(index)}
                                                                            disabled={item.quantity > item.stock}
                                                                        />
                                                                    </td>
                                                                </tr>
                                                            );
                                                        }

                                                        if (item.check) {
                                                            return (
                                                                <tr key={index}>
                                                                    <td>{item.medicine_name}</td>
                                                                    <td>{item.quantity}</td>
                                                                    <td>{item.price} đ</td>
                                                                    <td>{Number(item.quantity) * Number(item.price)} đ</td>
                                                                </tr>
                                                            );
                                                        }
                                                    })}



                                                    <tr>
                                                        <td colSpan={3}><b>Tổng:</b></td>
                                                        <td colSpan={isCreate ? 1 : 3}>
                                                            <b>{totals} đ</b>
                                                        </td>
                                                    </tr>
                                                </>
                                            ) : (
                                                <tr className='text-center'>
                                                    <td colSpan={6}>Không có dữ liệu</td>
                                                </tr>
                                            )}
                                        </tbody>
                                    </table>
                                    <div className='row'>
                                        <div className='col-5'>
                                            <div className="form-group">
                                                {!isCreate &&
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
                                        </div>
                                        <div className='col-7 text-center '>
                                            {isCreate &&
                                                <div>
                                                    <div className='fs-4' >
                                                        {moment(new Date()).locale('vi').format('[Hà Nội],[ngày] D [tháng] M [năm] YYYY')}
                                                    </div>
                                                    <p className='mb-5'>(Dược sĩ)</p>
                                                    <p>{technician?.name || "N/A"}</p>
                                                </div>
                                            }

                                        </div>
                                    </div>
                                </>
                            }
                            {prescription?.status !== 'pending' && prescription?.medicines?.length > 0 && (

                                <table className="table table-bordered">
                                    <thead>
                                        <tr>
                                            <th>Tên thuốc</th>
                                            <th>Giá</th>
                                            <th>Số lượng</th>
                                            <th>Thành tiền</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {prescription.medicines.map((item, index) => (
                                            <tr key={index}>
                                                <td>{item.medicine_name}</td>
                                                <td>{item.price}</td>
                                                <td>{item.quantity}</td>
                                                <td>{Number(item.price) * Number(item.quantity)}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}

                        </div>
                        <div className='d-flex my-3'>
                            {prescription?.status === 'pending' &&
                                <Button Button color="primary" type="submit">
                                    Thêm
                                </Button>
                            }
                            <Button color='secondary' className='mx-3' onClick={toggle}>
                                Huỷ
                            </Button>
                        </div>
                    </form>
                </ModalBody>
            </Modal>
            {/* Spinner sẽ hiển thị khi loading là true */}
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
        </div >
    );
};

export default PharmacistMedicalList;
