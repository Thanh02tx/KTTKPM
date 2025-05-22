import React, { useEffect, useState, useRef } from 'react';
import DatePicker, { registerLocale } from "react-datepicker";
import TextareaAutosize from 'react-textarea-autosize';
import vi from "date-fns/locale/vi";
import { getMedicalByDoctorAndDate } from '../../service/appointmentService';
import { createDiagnosisAndTestRequests, getVitalSignByMedical, getDiagnosisByMedical, doctorUpdateDiagnosisAndStatus } from '../../service/erhService';
import { getAllTypeTest, getTestRequestsByMedicalRecord, getAnnotatedImageTestResultByTestRequest } from '../../service/laboratoryService';
import { getAllMedicinesActive, createPrescriptionAndPrescriptionMedicines } from '../../service/pharmacist';
import { getDoctorByToken } from '../../service/userService';
import "react-datepicker/dist/react-datepicker.css";
import { format } from 'date-fns';
import { Modal, ModalBody, ModalHeader, Button } from 'reactstrap';
import html2canvas from "html2canvas";
import moment from "moment";
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import Lightbox from 'yet-another-react-lightbox';
import 'yet-another-react-lightbox/styles.css';
import Fullscreen from 'yet-another-react-lightbox/plugins/fullscreen';
import Zoom from 'yet-another-react-lightbox/plugins/zoom';
import { Triangle } from 'react-loader-spinner';
const DoctorMedicalList = () => {
    const user = useSelector((state) => state.auth.user);
    const resultRef = useRef();
    const [loading, setLoading] = useState(false);
    const [date, setDate] = useState(new Date())
    const [nameSearch, setNameSearch] = useState('')
    const [medicalData, setMedicalData] = useState([])
    const [medicinesData, setMedicinesData] = useState([])
    const [doctor, setDoctor] = useState([])
    const [typeTestData, setTypeTestData] = useState([])
    const [isOpenModal, setIsOpenModal] = useState(false)
    const [medical_history, setMedicalHistory] = useState("")
    const [family_history, setFamilyHistory] = useState("")
    const [drug_allergy, setDrugAllergy] = useState("")
    const [preliminary_diagnosis, setPreliminaryDiagnosis] = useState("")
    const [final_diagnosis, setFinalDiagnosis] = useState("")
    const [medical, setMedical] = useState({})
    const [vitalSign, setVitalSign] = useState({})
    const [diagnosis, setDiagnosis] = useState({})
    const [testRequestData, setTestRequestData] = useState([])
    const [listTypeTest, setListTypeTest] = useState([])
    const [selectedTest, setSelectedTest] = useState('');
    const [imageTestResult, setImageTestResult] = useState('');
    const [openPreview, setOpenpreview] = useState(false);
    const [isCreateIamge, setIsCreateImage] = useState(false)
    const [isShowDoctor, setIsShowDoctor] = useState(false)
    const [isCreatePrescription, setCreatePrescription] = useState(false)
    const [medicine, setMedicine] = useState("")
    const [selectedMedicines, setSelectedMedicines] = useState([]);
    const [note, setNote] = useState('');
    useEffect(() => {
        loadData()
    }, [date, user])
    const loadData = async () => {
        const formattedDate = format(date, 'yyyy-MM-dd');
        if (user?.token) {
            let res = await getMedicalByDoctorAndDate(formattedDate, user.token)
            if (res?.errCode === 0) {
                setMedicalData(res.data)
            }
            let r = await getAllTypeTest();
            if (r?.errCode === 0) {
                setTypeTestData(r.data)
            }
            let re = await getDoctorByToken(user.token)
            if (re?.errCode === 0) {
                setDoctor(re.data)
            }
            let resM = await getAllMedicinesActive()
            if (resM?.errCode === 0) {
                setMedicinesData(resM.data)
            }
        }

    }
    useEffect(() => {
        if (!isOpenModal) {
            setMedicalHistory('');
            setFamilyHistory('');
            setDrugAllergy('');
            setPreliminaryDiagnosis('');
            setFinalDiagnosis('');
            setMedical({});
            setVitalSign({});
            setDiagnosis({})
            setTestRequestData([])
            setMedicinesData([])
            setIsShowDoctor(false)
            setIsCreateImage(false)
            setSelectedMedicines([])
            setCreatePrescription(false)
            setListTypeTest([])
            setMedicine('')
            setNote('')
        }
    }, [isOpenModal])

    const toggle = () => {
        setIsOpenModal(!isOpenModal);
    };
    const handleClickCreateDiagnosis = async (item) => {
        setMedical(item)
        let res = await getVitalSignByMedical(item.medical_record.id)
        if (res?.errCode === 0) {
            setVitalSign(res.data)
        }
        let r = await getDiagnosisByMedical(item.medical_record.id)
        if (r?.errCode === 0) {
            setDiagnosis(r.data)
        }
        let re = await getTestRequestsByMedicalRecord(item.medical_record.id)
        if (re?.errCode === 0) {
            setTestRequestData(re.data)
        }
        toggle()
    }
    const handleSubmit = async (e) => {
        e.preventDefault();

        const status = e.nativeEvent.submitter?.name;
        if (status === 'waiting_result') {
            const check = testRequestData.filter(item => item.process_status !== 'completed');
            if (check.length === 0) {
                setIsShowDoctor(true)
                setIsCreateImage(true)

            } else {
                alert("Còn xét nghiệm chưa có kết quả")
            }
        }
        if (status === 'ready_for_doctor') {
            let data = {
                medical_id: medical.medical_record.id,
                vital_sign_id: vitalSign.id,
                medical_history,
                family_history,
                drug_allergy,
                preliminary_diagnosis,
                final_diagnosis,
                listTypeTest
            };
            setLoading(true)
            let res = await createDiagnosisAndTestRequests(data, user.token);

            if (res?.errCode === 0) {
                toast.success('Thêm thành công!');
                setLoading(false)
                toggle();
                await loadData();
            } else {
                toast.error('Lỗi');
            }
        }
        if (status === 'prescribed') {
            setIsShowDoctor(true)
            setCreatePrescription(true)
        }

    };
    useEffect(() => {
        if (isCreatePrescription && resultRef.current) {
            const timer = setTimeout(() => {
                html2canvas(resultRef.current, { scale: 2 }).then((canvas) => {
                    canvas.toBlob(async (blob) => {
                        if (!blob) {
                            toast.error("Không thể tạo file ảnh!");
                            return;
                        }

                        const file = new File([blob], 'result.png', { type: 'image/png' });

                        const formData = new FormData();
                        formData.append('medical_id', medical.medical_record.id);
                        formData.append('note', note);
                        formData.append('prescription_medicines', JSON.stringify(selectedMedicines));
                        formData.append('image', file)
                        console.log('sfsawrr', selectedMedicines)
                        try {
                            setLoading(true)
                            const res = await createPrescriptionAndPrescriptionMedicines(formData, user.token);
                            if (res?.errCode === 0) {
                                setLoading(false)
                                toast.success('Thành công');
                                toggle();
                                loadData();
                            } else {
                                toast.error("Lỗi!");
                            }
                        } catch (error) {
                            console.error('Gửi request bị lỗi: ', error);
                            toast.error("Lỗi khi gửi dữ liệu!");
                        }
                        setLoading(false)
                        setCreatePrescription(false);
                    }, 'image/png');
                });

                return () => clearTimeout(timer);
            }, 100);
        }
    }, [isCreatePrescription]);
    useEffect(() => {
        if (isCreateIamge && resultRef.current) {
            const timer = setTimeout(() => {
                html2canvas(resultRef.current, { scale: 2 }).then((canvas) => {
                    canvas.toBlob(async (blob) => {
                        if (!blob) {
                            toast.error("Không thể tạo file ảnh!");
                            return;
                        }

                        const file = new File([blob], 'result.png', { type: 'image/png' });

                        const formData = new FormData();
                        formData.append('medical_id', medical.medical_record.id);
                        formData.append('final_diagnosis', final_diagnosis);
                        formData.append('image', file)
                        try {
                            setLoading(true)
                            const res = await doctorUpdateDiagnosisAndStatus(formData, user.token);
                            if (res?.errCode == 0) {
                                setLoading(false)
                                toast.success('Thành công');
                                toggle();
                                loadData();
                            } else {
                                toast.error("Lỗi!");
                            }
                        } catch (error) {
                            console.error('Gửi request bị lỗi: ', error);
                            toast.error("Lỗi khi gửi dữ liệu!");
                        }
                        setLoading(false)
                        setIsCreateImage(false);
                    }, 'image/png');
                });

                return () => clearTimeout(timer);
            }, 100);
        }
    }, [isCreateIamge]);

    const handleSelectChange = (e) => {
        const selectedId = e.target.value; // selectedId sẽ là chuỗi, không cần parseInt nữa
        const selectedItem = typeTestData.find(item => item.id === selectedId);

        // Reset selectedTest khi có sự thay đổi
        setSelectedTest(e.target.value);

        if (selectedItem) {
            const { id, name, price } = selectedItem;

            // Kiểm tra nếu xét nghiệm đã có trong listTypeTest chưa
            const isExist = listTypeTest.some(item => item.id === id);

            if (!isExist) {
                // Thêm vào listTypeTest nếu chưa tồn tại
                setListTypeTest(prev => [...prev, { id, name, price }]);
            } else {
                // Cảnh báo nếu dịch vụ đã tồn tại trong listTypeTest
                alert('Dịch vụ này đã tồn tại trong danh sách!');
                // Reset selectedTest nếu dịch vụ đã tồn tại
                setSelectedTest("");
            }
        }
    };
    const handleDelete = (id) => {
        setListTypeTest(prev => prev.filter(item => item.id !== id));
    };
    const handleClickViewTestResult = async (item) => {
        const url = item?.test_result?.annotated_image;
        if (!url) return;

        const img = new Image();
        img.src = url;

        img.onload = () => {
            setImageTestResult(url);
            setOpenpreview(true);
        };

        img.onerror = () => {
            console.error("Ảnh không thể tải được:", url);
            // Có thể hiển thị thông báo lỗi ở đây
        };
    };
    const handleSelectMedicine = (e) => {
        const selectedId = e.target.value;
        setMedicine(selectedId);
        const alreadySelected = selectedMedicines.find(m => m.id == selectedId);
        if (alreadySelected) return;
        const selected = medicinesData.find((med) => med.id == selectedId);
        console.log('ăq', selected)
        if (selected) {
            setSelectedMedicines([...selectedMedicines, { ...selected, quantity: "", directions_for_use: "" }]);
        }
    };


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
                                    {item?.appointment?.status === 'waiting_result' && 'Tạo kết quả'}
                                    {item?.appointment?.status === 'prescribed' && 'Chờ đơn thuốc'}
                                    {item?.appointment?.status === 'done' && 'Đã khám xong'}
                                    {item?.appointment?.status === 'rated' && 'Đã đánh giá'}
                                    {item?.appointment?.status === 'cancelled' && 'Đã huỷ'}
                                </td>
                                <td>
                                    <button className='btn btn-secondary'
                                        onClick={() => handleClickCreateDiagnosis(item)}
                                        disabled={item?.appointment?.status === 'done'}
                                    >
                                        {item?.appointment?.status === 'ready_for_doctor' && 'Khai thác'}
                                        {item?.appointment?.status === 'waiting_result' && 'Tạo kết quả'}
                                        {item?.appointment?.status === 'prescribed' && 'Tạo đơn thuốc'}
                                        {item?.appointment?.status === 'done' && 'Đã xong'}
                                    </button>
                                </td>
                            </tr>
                        ))
                        : <tr colSpan={6} className='text-center'>Không có dữ liệu</tr>}
                </tbody>
            </table>
            <Modal isOpen={isOpenModal} toggle={toggle} className="modal-vitalsign-container" size="xl">
                <ModalHeader toggle={toggle}>{medical?.appointment?.status === 'ready_for_doctor' ? 'Khai thác thông tin' : 'Tạo kết quả'}</ModalHeader>
                <ModalBody>
                    <form onSubmit={handleSubmit}>
                        <div className="modal-vitalsign-body row" ref={resultRef}>
                            <div className='fs-5 mb-2'>
                                <span>Phòng khám tim mạch TDT</span>
                            </div>
                            {medical?.appointment?.status === "prescribed" && <h3 className='text-center my-2'>ĐƠN THUỐC</h3>}
                            {medical?.appointment?.status === "waiting_result" && <h3 className='text-center my-2'>KẾT QUẢ</h3>}
                            {/* <p className='text-center'>{medical?.payment?.payment_status ? "(Đã thanh toán)" : "(Chưa thanh toán)"}</p> */}
                            <div className='form-group col-6'>
                                <p>Họ và tên: {medical?.medical_record?.name || ''}</p>
                                <p>Huyết áp: {vitalSign?.blood_pressure || ""}</p>
                                <p>Nhịp tim: {vitalSign?.heart_rate || ""}</p>
                            </div>
                            <div className='form-group col-6'>
                                <p> Ngày sinh: {medical?.medical_record?.date_of_birth ? format(medical.medical_record.date_of_birth, 'dd-MM-yyyy') : ''}</p>
                                <p>Chiều cao: {vitalSign?.height ? `${vitalSign.height} (cm)` : ""}</p>
                                <p>Cân nặng: {vitalSign?.weight ? `${vitalSign.weight} (kg)` : ""}</p>
                            </div>
                            {medical?.appointment?.status === 'ready_for_doctor' &&
                                <>
                                    <div className='border-top border-bottom border-3  py-2 my-2'>
                                        <div className="form-group mt-1 ">
                                            <label>Tiền sử bệnh:</label>
                                            <input
                                                className="form-control"
                                                type="text"
                                                placeholder="Nhập thông tin (nếu có)"
                                                value={medical_history}
                                                onChange={(e) => setMedicalHistory(e.target.value)}

                                            />
                                        </div>
                                        <div className="form-group mt-1 ">
                                            <label>Tiền sử gia đình:</label>
                                            <input
                                                className="form-control"
                                                type="text"
                                                placeholder="Nhập thông tin (nếu có)"
                                                value={family_history}
                                                onChange={(e) => setFamilyHistory(e.target.value)}

                                            />
                                        </div>
                                        <div className="form-group mt-1">
                                            <label>Dị ứng thuốc:</label>
                                            <input
                                                className="form-control"
                                                type="text"
                                                placeholder="Nhập thông tin (nếu có)"
                                                value={drug_allergy}
                                                onChange={(e) => setDrugAllergy(e.target.value)}

                                            />
                                        </div>
                                        <div className="form-group mt-1">
                                            <label>Chuẩn đoán sơ bộ:</label>
                                            <input
                                                className="form-control"
                                                type="text"
                                                placeholder="Nhập thông tin"
                                                value={preliminary_diagnosis}
                                                onChange={(e) => setPreliminaryDiagnosis(e.target.value)}
                                                required
                                            />
                                        </div>

                                    </div>
                                    <div className='my-2'>
                                        <label>
                                            Xét nghiệm/Siêu âm:
                                            <select defaultValue="" value={selectedTest} onChange={handleSelectChange} className='rounded-2 p-1 mx-3'>
                                                <option value="" disabled>Chọn loại xét nghiệm...</option>
                                                {typeTestData?.length > 0 && typeTestData.map((item, index) => (
                                                    <option key={`tt-${index}`} value={item.id}>
                                                        {item.name} - {item.price}đ
                                                    </option>
                                                ))}
                                            </select>
                                        </label>
                                        <table className='table table-bordered mt-2'>
                                            {listTypeTest?.length > 0 ? listTypeTest.map((item, index) => (
                                                <tbody>
                                                    <tr key={`ty-${index}`}>
                                                        <td>{item.name}</td>
                                                        <td>{item.price} đ</td>
                                                        <td>
                                                            <button className='btn btn-secondary'
                                                                onClick={() => handleDelete(item.id)}
                                                            >Xoá</button>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            ))
                                                :
                                                <tr className='text-center'><td colSpan={3}>Chưa có dịch vụ</td></tr>
                                            }
                                        </table>
                                    </div>
                                </>
                            }
                            {medical?.appointment?.status === 'waiting_result' &&
                                <>
                                    <p>Tiền sử bênh: {diagnosis?.medical_history || "Không có"}</p>
                                    <p>Tiền sử gia đinh: {diagnosis?.family_history || "chưa có phát hiện đặc biệt"} </p>
                                    <p>Dị ứng thuốc: {diagnosis?.drug_allergy || "Chua có phát hiện đặc biệt"}</p>
                                    <p>Chuẩn đoán sơ bộ: {diagnosis?.preliminary_diagnosis || 'K có bệnh'}</p>
                                    <p>Dịch vụ xét nghiệm/siêu âm: {!(testRequestData?.length > 0) && "Không có"}</p>
                                    {!isCreateIamge &&
                                        <table className='table table-bordered'>
                                            <tbody>
                                                {testRequestData?.length > 0 && testRequestData.map((item, index) => {
                                                    return (
                                                        <>
                                                            {index === 0 &&
                                                                <tr>
                                                                    <th>Dịch vụ</th>
                                                                    <th>Giá</th>
                                                                    <th>Trạng thái</th>
                                                                    <th>Hành động</th>
                                                                </tr>
                                                            }
                                                            <tr key={`tqe-${index}`}>
                                                                <td>{item?.name || "N/A"}</td>
                                                                <td>{item?.price ? `${item.price}đ` : "N/A"}</td>
                                                                <td>
                                                                    {item?.process_status && item.process_status === "not_started" && "Chưa bắt đầu"}
                                                                    {item?.process_status && item.process_status === "processing" && "Đang thực hiện"}
                                                                    {item?.process_status && item.process_status === "completed" && "Hoàn thành"}
                                                                </td>
                                                                <td>
                                                                    {item?.process_status && item.process_status === "completed" &&
                                                                        <button className='btn btn-secondary' type='button' onClick={() => handleClickViewTestResult(item)}>Xem</button>
                                                                    }
                                                                </td>
                                                            </tr>
                                                        </>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    }
                                    <div className="form-group mt-1">
                                        <label>Chuẩn đoán cuối cùng: </label>
                                        {isCreateIamge ?
                                            <p>{final_diagnosis}</p>
                                            :
                                            <input
                                                className="form-control"
                                                type="text"
                                                placeholder="Nhập kết quả chuẩn đoán"
                                                value={final_diagnosis}
                                                onChange={(e) => setFinalDiagnosis(e.target.value)}
                                                required
                                            />
                                        }
                                    </div>

                                </>
                            }
                            {medical?.appointment?.status === 'prescribed' && (
                                <div>
                                    <div className='form-group'>
                                        <div className='d-flex'>
                                            <label>Đơn thuốc: </label>
                                            {!isShowDoctor &&
                                                <select
                                                    value={medicine}
                                                    className='rounded-2 p-1 mx-3 text-center'
                                                    onChange={handleSelectMedicine}
                                                >
                                                    <option value="">-------- Chọn thuốc --------</option>
                                                    {medicinesData?.length > 0 && medicinesData.map((med, index) => (
                                                        <option key={`med-${index}`} value={med.id}>
                                                            {`${med.name} - Giá: ${med.price} - Tồn: ${med.stock}`}
                                                        </option>
                                                    ))}
                                                </select>
                                            }
                                        </div>
                                    </div>
                                    <table className='table table-bordered mt-1'>
                                        <tbody>
                                            {selectedMedicines?.length > 0 && selectedMedicines.map((seM, index) => (
                                                <>
                                                    {index === 0 &&
                                                        <tr>
                                                            <th>Tên Thuốc</th>
                                                            <th>Giá</th>
                                                            <th>Số lượng</th>
                                                            <th>Cách dùng</th>
                                                            {!isShowDoctor && <th></th>}
                                                        </tr>
                                                    }
                                                    <tr key={`sem-${index}`}>
                                                        <td>{seM.name}</td>
                                                        <td>{seM.price}đ</td>
                                                        <td>
                                                            <input
                                                                className='border-0 border-bottom w-100'
                                                                placeholder='Nhập số lượng'
                                                                value={seM.quantity}
                                                                defaultValue={0}
                                                                type='number'
                                                                min={1}
                                                                onChange={(e) => {
                                                                    const updated = [...selectedMedicines];
                                                                    updated[index].quantity = e.target.value;
                                                                    setSelectedMedicines(updated);
                                                                }}
                                                                required
                                                            />

                                                        </td>
                                                        <td>
                                                            <TextareaAutosize
                                                                className='border-0 border-bottom w-100'
                                                                placeholder='Nhập cách dùng'
                                                                value={seM.directions_for_use}
                                                                onChange={(e) => {
                                                                    const updated = [...selectedMedicines];
                                                                    updated[index].directions_for_use = e.target.value;
                                                                    setSelectedMedicines(updated);
                                                                }}
                                                                required
                                                            />
                                                        </td>
                                                        {!isShowDoctor &&
                                                            <td>
                                                                <i
                                                                    className="fa-solid fa-minus fs-2 text-danger"
                                                                    style={{ cursor: 'pointer' }}
                                                                    onClick={() => {
                                                                        const updated = selectedMedicines.filter((_, i) => i !== index);
                                                                        setSelectedMedicines(updated);
                                                                    }}
                                                                ></i>
                                                            </td>
                                                        }
                                                    </tr>
                                                </>
                                            ))}
                                        </tbody>
                                    </table>
                                    <div className='form-group'>
                                        <label>Chú ý:</label>
                                        {isShowDoctor
                                            ?
                                            <p style={{ whiteSpace: 'pre-line' }}>{note}</p>
                                            :
                                            <TextareaAutosize

                                                className="form-control"
                                                value={note}
                                                onChange={(e) => setNote(e.target.value)}
                                                placeholder="Nhập Thông tin"
                                                required
                                            />
                                        }

                                    </div>

                                </div>
                            )}

                            {isShowDoctor &&
                                <div className='row mt-4'>
                                    <div className='col-5'>

                                    </div>
                                    <div className='col-7 text-center '>

                                        <div>
                                            <div className='fs-4' >
                                                {moment(new Date()).locale('vi').format('[Hà Nội],[ngày] D [tháng] M [năm] YYYY')}
                                            </div>
                                            <p className='mb-5'>(Bác sĩ)</p>
                                            <p>{doctor?.name || "N/A"}</p>
                                        </div>



                                    </div>

                                </div>
                            }
                        </div>
                        <div className='d-flex my-3'>
                            {(medical?.appointment?.status === 'waiting_result' || medical?.appointment?.status === 'ready_for_doctor' || medical?.appointment?.status === 'prescribed') &&
                                <Button color="primary" type="submit" name={medical?.appointment?.status}>
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
            <Lightbox
                open={openPreview}
                close={() => setOpenpreview(false)}
                slides={[{ src: imageTestResult }]}
                plugins={[Fullscreen, Zoom]}
            />
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

export default DoctorMedicalList;
