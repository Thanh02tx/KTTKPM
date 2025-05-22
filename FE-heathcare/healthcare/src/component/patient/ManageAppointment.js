import React, { useEffect, useState } from 'react';
import '../../asset/scss/ManageAppointment.scss';
import { useSelector } from 'react-redux';
import { getAllPatientRecordByUser } from '../../service/userService'
import { getHistoryAppointmentByPatient, getMedicalById } from '../../service/appointmentService';
import { getWardDistricProvince } from '../../service/address';
import { getTestRequestsByMedicalRecord,} from '../../service/laboratoryService';
import { getDiagnosisByMedical,getVitalSignByMedical } from '../../service/erhService';
import { getPrescriptionByMedical} from '../../service/pharmacist';
import moment from 'moment';
import { Modal, ModalBody, ModalHeader, Button } from 'reactstrap';
import Lightbox from 'yet-another-react-lightbox';
import 'yet-another-react-lightbox/styles.css';
import Fullscreen from 'yet-another-react-lightbox/plugins/fullscreen';
import Zoom from 'yet-another-react-lightbox/plugins/zoom';
const ManageAppointment = () => {
    const user = useSelector((state) => state.auth.user);
    const [patientData, setPatientData] = useState([])
    const [appointments, setAppointments] = useState([])
    const [isOpenModal, setIsOpenModal] = useState(false)
    const [medical, setMedical] = useState({})
    const [testRequests, setTestRequests] = useState([])
    const [diagnosis, setDiagnosis] = useState({})
    const [vitalSign, setVitalSign] = useState({})
    const [prescription, setPrescription] = useState({})
    const [image, setImage] = useState([])
    const [openPreview, setOpenPreview] = useState(false)
    useEffect(() => {
        const loadData = async () => {
            if (user?.token) {
                let res = await getAllPatientRecordByUser(user.token)
                if (res?.errCode === 0) {
                    setPatientData(res.data)
                }
            }
        }
        loadData()
    }, [])
    useEffect(() => {
        if (!isOpenModal) {
            setMedical({})
            setTestRequests([])
            setDiagnosis({})
            setVitalSign({})
            setPrescription({})
        }
    }, [isOpenModal])
    const calculateAge = (dob) => {
        return moment().diff(moment(dob, 'YYYY-MM-DD'), 'years');
    };
    const handleClickPatient = async (id) => {
        let res = await getHistoryAppointmentByPatient(id)
        if (res?.errCode === 0) {
            if(res?.data?.length===0) alert('Hồ sơ chưa từng đặt lịch khám')
            setAppointments(res.data)
        }
    }
    const toggle = () => {
        setIsOpenModal(!isOpenModal)
    }
    const handleViewResult = async (id) => {
        let res = await getMedicalById(id)
        if (res?.errCode === 0) {
            let address = getWardDistricProvince(res.data.ward, res.data.district, res.data.province)
            let fullMedical = {
                ...res.data,
                address
            };
            setMedical(fullMedical)
        }
        let re = await getTestRequestsByMedicalRecord(id)
        if (re?.errCode === 0) {
            setTestRequests(re.data)
        }
        let r = await getDiagnosisByMedical(id)
        if(r?.errCode===0) {
            setDiagnosis(r.data)
        }
        let rV = await getVitalSignByMedical(id)
        if(rV?.errCode===0) {
            setVitalSign(rV.data)
        }
        let resP = await getPrescriptionByMedical(id)
        if(resP?.errCode===0) {
            setPrescription(resP.data)
        }
        toggle()
    };
    const handleViewTestResult=async(item)=>{
        if(item?.test_result?.annotated_image){
            setImage(item.test_result.annotated_image)
            setTimeout(() => setOpenPreview(true), 10);
        }
    }
    const handleViewImageDiagnosis=async()=>{
        if(diagnosis?.image) {
            setImage(diagnosis.image)
            setTimeout(()=>setOpenPreview(true),10)
        }
    }
    const handleViewImagePrescription =async()=>{
        if(prescription?.image) {
            setImage(prescription.image)
            setTimeout(()=>setOpenPreview(true),10)
        }
    }
    return (
        <div>
            <div className="p-manage-appointment-container">
                <div className='mt-4 container'>
                    <div className="ct-record">
                        <label>Chọn Hồ sơ:</label>
                        {patientData?.length > 0 ? (
                            <div className="record-scroll mt-1">
                                {patientData.map((item, index) => (
                                    <div className="item-patient" key={index}
                                        onClick={() => handleClickPatient(item.id)}
                                    >
                                        <div className="image-wrapper">
                                            <img
                                                src={item.image}
                                                alt="patient-record"
                                                className="doctor-img"
                                            />
                                        </div>
                                        <div className="info-wrapper">
                                            <div>{item.name}</div>
                                            <div>{`${calculateAge(item.date_of_birth)} Tuổi`}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>

                        ) : (
                            <div>Không có hồ sơ bệnh nhân.</div>
                        )}
                    </div>
                    <div >
                        {appointments?.length > 0 && (
                            <div>
                                <label>Danh sách lịch hẹn</label>
                                <div className="d-flex flex-wrap gap-2">

                                    {appointments.map((item, index) => (
                                        <div key={`ap-${index}`} className="item-app p-2 border rounded">
                                            <div>
                                                {`Ngày: ${moment(item.schedule_date, 'YYYY-MM-DD').format('DD-MM-YYYY')}`}
                                            </div>
                                            <div>
                                                {item?.status === 'booked' && 'Đã đặt'}
                                                {item?.status === 'ready_for_doctor' && 'Chờ bác sĩ'}
                                                {item?.status === 'waiting_result' && 'Chờ kết quả'}
                                                {item?.status === 'prescribed' && 'Kê đơn thuốc'}

                                                {item?.status === 'rated' && 'Đã đánh giá'}
                                                {item?.status === 'cancelled' && 'Đã huỷ'}
                                                {item?.status === 'done' && (
                                                    <div>
                                                        Đã khám xong <button className="btn-view" type='button'
                                                            onClick={() => handleViewResult(item.medical_id)}
                                                        >
                                                            Xem
                                                        </button>
                                                    </div>
                                                )}

                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                </div>
            </div>
            
            <Modal isOpen={isOpenModal} toggle={toggle} className="modal-history-container" size="xl">
                <ModalHeader toggle={toggle}>Thông tin</ModalHeader>
                <ModalBody>
                    <div>
                        <div className="modal-history-body" >
                            <div className='fs-5 d-flex justify-content-between'>
                                <span>Phòng khám tim mạch TDT</span>
                            </div>
                            <h3 className='text-center my-2'>THÔNG TIN</h3>
                            <div className='row fs-5'>
                                <div className='col-7'>
                                    <div>Họ và tên: {medical?.name || "N/A"}</div>
                                    <div>Ngày sinh: {medical?.date_of_birth ? moment(medical.date_of_birth).format('DD-MM-YYYY') : "N/A"}</div>
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


                            </div>
                            <div >
                                <span className='fs-5'>Kết quả: </span> 
                                <a href='#'  onClick={handleViewImageDiagnosis}>Xem chi tiết</a>
                            </div>
                            <div className='ms-3 fs-5'>Huyết áp: {vitalSign?.blood_pressure ||""}</div>
                            <div className='ms-3 fs-5'>Nhịp tim: {vitalSign?.heart_rate ||""}</div>
                            <div className='ms-3 fs-5'>Kết luận: {diagnosis?.final_diagnosis || ""}</div>
                            <div className='mb-2 fs-5'>Dịch vụ xét nghiệm:</div>
                            <table className='table table-bordered'>
                                {testRequests?.length > 0 && (
                                    <thead>
                                        <tr>
                                            <th>Tên dịch vụ</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                )}
                                <tbody>
                                    {testRequests?.length > 0 ? (
                                        testRequests.map((item, index) => (
                                            <tr key={index}>
                                                <td>{item.name}</td>
                                                <td><a href='#' onClick={()=>handleViewTestResult(item)}>Xem chi tiết</a></td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="2" className="text-center">Không có dịch vụ nào</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                        <label className='fs-5'>Đơn thuốc: </label> <a href='#'  onClick={handleViewImagePrescription} >Xem chi tiết</a>
                        <table className='table table-bordered'>
                            {prescription?.medicines?.length > 0 && (
                                    <thead>
                                        <tr>
                                            <th>Tên thuốc</th>
                                            <th>Số lượng</th>
                                            <th>Cách dùng</th>
                                        </tr>
                                    </thead>
                                )}
                                <tbody>
                                    {prescription?.medicines?.length > 0 ? (
                                        prescription?.medicines?.map((item, index) => (
                                            <tr key={`pr-${index}`}>
                                                <td>{item.medicine_name}</td>
                                                <td>{item.quantity}</td>
                                                <td>{item.directions_for_use}</td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="3" className="text-center">Không có thuốc</td>
                                        </tr>
                                    )}
                                </tbody>

                        </table>
                        <div className='d-flex my-3'>
                            <Button color='secondary' onClick={toggle}>
                                Đóng
                            </Button>
                        </div>
                    </div>
                </ModalBody>
            </Modal>
            <Lightbox
                open={openPreview}
                close={() => setOpenPreview(false)}
                slides={[{ src: image }]}
                plugins={[Fullscreen, Zoom]}
            />
        </div>
    );
};

export default ManageAppointment;
