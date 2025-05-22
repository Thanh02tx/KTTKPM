import React, { useEffect, useState, useRef } from 'react';
import DatePicker from "react-datepicker";
import { getApptMedicalTestRequestPaidByDate, getMedicalById } from '../../service/appointmentService';
import { getDiagnosisByMedical } from '../../service/erhService';
import { getTechnicianByToken } from '../../service/userService';
import { createTestResult } from '../../service/laboratoryService';
import '../../asset/scss/TechMedicalList.scss'
import "react-datepicker/dist/react-datepicker.css";
import html2canvas from "html2canvas";
import TextareaAutosize from 'react-textarea-autosize';
import { format } from 'date-fns';
import { Modal, ModalBody, ModalHeader, Button } from 'reactstrap';
import { useSelector } from 'react-redux';
import moment from 'moment';
import { toast } from 'react-toastify';
import { Triangle } from 'react-loader-spinner';
const TechMedicalList = () => {
    const user = useSelector((state) => state.auth.user);
    const fileInputRef = useRef(null);
    const resultRef = useRef();
    const [date, setDate] = useState(new Date())
    const [nameSearch, setNameSearch] = useState('')
    const [medicalData, setMedicalData] = useState([])
    const [isOpenModal, setIsOpenModal] = useState(false)
    const [medical, setMedical] = useState({})
    const [testRequest, setTestRequest] = useState({})
    const [diagnosis, setDiagnosis] = useState({})
    const [technician, setTechnician] = useState({})
    const [isCreate, setIsCreate] = useState(false)
    const [conclusion, setConclusion] = useState("")
    const [image, setImage] = useState("")
    const [imageBase64, setImageBase64] = useState("")
    const [loading, setLoading] = useState(false);
    const handleClickImage = () => {
        fileInputRef.current.click(); // Kích hoạt input ẩn
    }
    const handleFileChange = (e) => {
        const file = e.target.files?.[0];
        if (!file?.type.startsWith('image/')) {
            return alert('Vui lòng chọn đúng định dạng ảnh!');
        }
        setImage(file)
        const reader = new FileReader();
        reader.onloadend = () => setImageBase64(reader.result);
        reader.readAsDataURL(file);
    };
    useEffect(() => {
        loadData()
    }, [date])
    const loadData = async () => {
        const formattedDate = format(date, 'yyyy-MM-dd');
        let res = await getApptMedicalTestRequestPaidByDate(formattedDate)
        if (res?.errCode === 0) {
            setMedicalData(res.data)
        }
        if (user?.token) {
            let re = await getTechnicianByToken(user.token)
            if (re?.errCode === 0) setTechnician(re.data)
        }

    }
    useEffect(() => {
        if (!isOpenModal) {
            setMedical({});
            setDiagnosis({})
            setIsCreate(false)
            setConclusion("")
            setImage("")
            setImageBase64()
        }
    }, [isOpenModal])

    const toggle = () => {
        setIsOpenModal(!isOpenModal);
    }
    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsCreate(true);
    };
    useEffect(() => {
        if (isCreate && resultRef.current) {
            const timer = setTimeout(() => {
                html2canvas(resultRef.current, { scale: 2 }).then((canvas) => {
                    canvas.toBlob(async (blob) => {
                        if (!blob) {
                            toast.error("Không thể tạo file ảnh!");
                            return;
                        }

                        // Tạo file từ blob nếu cần (optional)
                        const file = new File([blob], 'result.png', { type: 'image/png' });

                        // Dùng FormData để gửi ảnh
                        const formData = new FormData();
                        formData.append('medical_id', medical.id);
                        formData.append('test_request_id', testRequest.id);
                        formData.append('conclusion', conclusion);
                        formData.append('raw_image', image);  // file ảnh ở dạng 'image/png'
                        formData.append('annotated_image', file)

                        try {
                            setLoading(true)
                            const res = await createTestResult(formData, user.token); // chú ý API phải nhận dạng multipart/form-data
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

                        setIsCreate(false);
                    }, 'image/png');
                });

                return () => clearTimeout(timer);
            }, 100);
        }
    }, [isCreate]);

    const handleClickCreateResult = async (item, test) => {
        let res = await getMedicalById(item.medical_record.id)
        setTestRequest(test)
        if (res?.errCode === 0) {
            setMedical(res.data)
        }
        let re = await getDiagnosisByMedical(item.medical_record.id)
        if (re?.errCode === 0) {
            setDiagnosis(re.data)
        }
        toggle()
    }
    return (
        <div className='nurse-medical-list-container container'>
            <div className='row mt-4' >
                <div className="form-group mt-1 col-2">
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
            <table className='table table-bordered align-middle mt-3'>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Họ và Tên</th>
                        <th>Ngày sinh</th>
                        <th>Thời gian</th>
                        <th>Dịch vụ</th>
                        <th>Trạng thái</th>
                        <th>Hành động</th>
                    </tr>
                </thead>
                <tbody>
                    {medicalData?.length > 0 ?
                        medicalData.map((item, index) => (
                            item?.test_request?.length > 0 &&
                            item.test_request.map((test, inx) => (
                                <tr key={`m-tq-${index}-${inx}`}>
                                    {inx === 0 && (
                                        <>
                                            <td rowSpan={item.test_request.length}>{index + 1}</td>
                                            <td rowSpan={item.test_request.length}>{item?.medical_record?.name || ''}</td>
                                            <td rowSpan={item.test_request.length}>
                                                {item?.medical_record?.date_of_birth ? format(item.medical_record.date_of_birth, 'dd-MM-yyyy') : ''}
                                            </td>
                                            <td rowSpan={item.test_request.length}>{item?.time || ''}</td>
                                        </>
                                    )}
                                    <td>{test?.name || ''}</td>
                                    <td>
                                        {test?.process_status === "processing" && "Chưa xử lý"}
                                        {test?.process_status === "completed" && "Hoàn thành"}
                                    </td>
                                    <td>
                                        <button
                                            className='btn btn-secondary'
                                            onClick={() => handleClickCreateResult(item, test)}
                                            disabled={test?.process_status === 'completed'}
                                        >
                                            + kết quả
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ))
                        : <tr>
                            <td colSpan={7} className='text-center'>Không có</td>
                        </tr>
                    }
                </tbody>
            </table>
            <Modal isOpen={isOpenModal} toggle={toggle} className="modal-tech-medicalist-container" size="xl">
                <ModalHeader toggle={toggle}>Kết quả</ModalHeader>
                <ModalBody>
                    <form onSubmit={handleSubmit}>
                        <div className='px-3 py-4' ref={resultRef} >
                            <div className='fs-5 mb-2'>
                                <span>Phòng khám tim mạch TDT</span>
                            </div>
                            <h3 className='text-center m-0'>KẾT QUẢ</h3>
                            <div className='text-center mb-4'>{testRequest?.name ? `(${testRequest.name})` : ""}</div>
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
                                <div>Chuẩn đoán sơ bộ: {diagnosis?.preliminary_diagnosis || ""}</div>
                                <div >
                                    <label>Chuẩn đoán:</label>
                                    {isCreate ?
                                        <p>{conclusion}</p>
                                        :
                                        <TextareaAutosize

                                            className="form-control"
                                            value={conclusion}
                                            onChange={(e) => setConclusion(e.target.value)}
                                            placeholder="Nhập Thông tin"
                                            required
                                        />
                                    }

                                </div>
                                <div className='d-flex mt-1'>
                                    <label>Hình ảnh(nếu có):</label>
                                    {!isCreate &&
                                        <>
                                            <button className='btn btn-secondary m-0' type="button" onClick={handleClickImage}>Thêm</button>
                                            <input
                                                type='file'
                                                accept='image/*' // ✅ Chỉ cho chọn ảnh
                                                ref={fileInputRef}
                                                style={{ display: 'none' }}
                                                onChange={handleFileChange}
                                            />
                                        </>}

                                </div>
                                <div className='d-image'>
                                    <img src={imageBase64} />
                                </div>
                            </div>
                            <div className='row'>
                                <div className='col-5'></div>
                                <div className='col-7 text-center '>
                                    {isCreate &&
                                        <div>
                                            <div className='fs-4' >
                                                {moment(new Date()).locale('vi').format('[Hà Nội],[ngày] D [tháng] M [năm] YYYY')}
                                            </div>
                                            <p className='mb-5'>(Kĩ thuật viên)</p>
                                            <p>{technician?.name || "N/A"}</p>
                                        </div>
                                    }

                                </div>
                            </div>

                        </div>
                        <div className='d-flex my-3 mx-3'>

                            <Button color="primary" type="submit">
                                Thêm
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

export default TechMedicalList;
