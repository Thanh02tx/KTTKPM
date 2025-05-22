import React, { useEffect, useState } from 'react';
import ModalRecord from './ModalRecord';
import { useSelector } from 'react-redux';
import { createPatientRecord, getAllPatientRecordByUser, updatePatientRecord } from '../../service/userService';
import { toast } from 'react-toastify';
import { format } from 'date-fns';
import '../../asset/scss/ManageRecord.scss'
import moment from 'moment';
const ManageRecord = () => {
    const user = useSelector((state) => state.auth.user);
    const [isOpenModal, setIsOpenModal] = useState(false);
    const [isCreate, setIsCreate] = useState(true);
    const [idRecord, setIdRecord] = useState('');
    const [recordData, setRecordData] = useState('');
    useEffect(() => {
        console.log('sâa', user)
    }, [user])

    useEffect(() => {
        loadDataRecord()
    }, [])
    const loadDataRecord = async () => {
        if (user?.token) {
            let res = await getAllPatientRecordByUser(user.token);
            if (res?.errCode === 0) {
                setRecordData(res.data)
            }
        }
    }
    const formatDate = (date) => {
        return format(date, 'dd-MM-yyyy');  // Định dạng lại theo kiểu dd-MM-yyyy
    };
    const changeModal = () => {
        if (isOpenModal === true) {
            setIdRecord('')
            setIsCreate(true)
        }

        setIsOpenModal(!isOpenModal);
    };
    const handleDataRecord = async (data) => {
        if (isCreate) {
            let res = await createPatientRecord(data, user.token)
            if (res?.errCode === 0) {
                setIsOpenModal(false)
                await loadDataRecord()
                toast.success("Tạo Hồ sơ thành công !")
            } else {
                toast.error("Thất bại !")
            }
        } else {
            let res = await updatePatientRecord(data, user.token)
            if (res?.errCode === 0) {
                setIsOpenModal(false);
                setIsCreate(true);
                await loadDataRecord()
                toast.success("Cập nhập thành công!")
            }
        }
    }
    // const handleActiveDoctor = async (idInput) => {
    //     let data ={
    //         id:idInput
    //     }
    //     let res = await changeActiveUser(data, user.token)
    //     if (res?.errCode === 0) {
    //         toast.success('Thành công!')
    //         await getDoctorsData()
    //     }
    // }
    const handleEditRecordPatient = (id) => {
        setIdRecord(id)
        setIsOpenModal(true)
        setIsCreate(false)
    }
    const calculateAge = (dob) => {
        return moment().diff(moment(dob, 'YYYY-MM-DD'), 'years');
    };
    return (
        <div className="manage-record-container">
            <div >
                <div>
                    <button className='btn btn-primary' onClick={changeModal}>
                        <i className="fa-solid fa-user-plus edit-icon"></i> Hồ sơ
                    </button>
                </div>
                <div className='content-mr'>
                    {recordData?.length > 0 && recordData.map((item, index) => (
                        <div
                            key={`pr-${index}`}
                            className="doctor-card"
                        >
                            <div className='icon'>
                                <i className="fa-solid fa-pen-fancy"
                                    onClick={() => handleEditRecordPatient(item.id)}
                                ></i>
                            </div>
                            <div className='d-flex'>
                                <div className="image-wrapper">
                                    <img
                                        src={item.image}
                                        alt="patient-record"
                                        className="doctor-img"
                                    />
                                </div>
                                <div className='ms-3 d-flex align-items-center'>
                                    <div>
                                    <div>{item.name}</div>
                                    <div>{`${calculateAge(item.date_of_birth)} Tuổi`}</div>
                                    </div>
                                </div>
                            </div>

                        </div>
                    ))}
                </div>
            </div>

            <ModalRecord
                isOpenModal={isOpenModal}
                toggle={changeModal}
                isCreate={isCreate}
                idRecord={idRecord}
                handleDataRecord={handleDataRecord}
            />
        </div>
    );
};

export default ManageRecord;
