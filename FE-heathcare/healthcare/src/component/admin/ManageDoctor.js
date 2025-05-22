import React, { useEffect, useState } from 'react';
import ModalDoctor from './ModalDoctor';
import { useSelector } from 'react-redux';
import { createDoctor, getAllDoctorAdmin, changeActiveUser, updateDoctor } from '../../service/userService';
import { toast } from 'react-toastify';
import { format } from 'date-fns';
import { Triangle } from 'react-loader-spinner';
import '../../asset/scss/ManageDoctor.scss'
const ManageDoctor = () => {
    const user = useSelector((state) => state.auth.user);
    const [isOpenModal, setIsOpenModal] = useState(false);
    const [isCreate, setIsCreate] = useState(true);
    const [idDoctor, setIdDoctor] = useState('');
    const [doctorData, setDoctorData] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        getDoctorsData()
    }, [])
    const getDoctorsData = async () => {
        let res = await getAllDoctorAdmin();
        if (res?.errCode === 0) {
            setDoctorData(res.data)
        }
    }
    const formatDate = (date) => {
        return format(date, 'dd-MM-yyyy');  // Định dạng lại theo kiểu dd-MM-yyyy
    };
    const changeModal = () => {
        if (isOpenModal === true) {
            setIdDoctor('')
            setIsCreate(true)
        }

        setIsOpenModal(!isOpenModal);
    };
    const handleDataDoctor = async (data) => {
        setLoading(true)
        if (isCreate) {
            let res = await createDoctor(data, user.token)
            if (res?.errCode === 0) {
                setLoading(false)
                setIsOpenModal(false)
                await getDoctorsData()
                toast.success("Tạo Bác sĩ thành công !")
            } else {
                toast.error("Thất bại !")
            }
        } else {
            let res = await updateDoctor(data, user.token)
            if (res?.errCode === 0) {
                setLoading(false)
                setIsOpenModal(false);
                setIsCreate(true);
                await getDoctorsData()
                toast.success("Thành công!")
            }
        }
        setLoading(false)
    }
    const handleActiveDoctor = async (idInput) => {
        setLoading(true);
        let data = {
            id: idInput
        }
        let res = await changeActiveUser(data, user.token)
        if (res?.errCode === 0) {
            setLoading(false);
            toast.success('Thành công!')
            await getDoctorsData()
        }
    }
    const handleEditDoctor = (id) => {
        setIdDoctor(id)
        setIsOpenModal(true)
        setIsCreate(false)
    }
    return (
        <div className="manage-doctor-container">
            <div className='container'>
                <div>
                    <button className='btn btn-primary' onClick={changeModal}>
                        <i className="fa-solid fa-user-plus"></i> Bác sĩ
                    </button>
                </div>
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
                <table className='table mt-3'>
                    <thead>
                        <tr>
                            <th>STT</th>
                            <th>Họ Tên</th>
                            <th>Ngày sinh</th>
                            <th>Học vị</th>
                            <th>Trạng thái</th>
                            <th>Hành động</th>
                        </tr>
                    </thead>
                    <tbody>
                        {doctorData?.length > 0 && doctorData.map((item, index) => {
                            return (
                                <tr key={`dt-${index}`}>
                                    <td>{index + 1}</td>
                                    <td>{item.name}</td>
                                    <td>{formatDate(item.date_of_birth)}</td>
                                    <td>{item.degree}</td>
                                    <td>{item.user.is_active ? "Hoạt động" : "Không hoạt động"}</td>
                                    <td className="td-action">
                                        <span className='mx-3 btn-update' onClick={() => handleEditDoctor(item.id)}> <i className="fa-solid fa-pencil"></i> </span>
                                        <span className='btn-active' onClick={() => handleActiveDoctor(item.user_id)}>
                                            {item.user.is_active ?
                                                <i class="fa-solid fa-lock"></i>
                                                :
                                                <i class="fa-solid fa-lock-open"></i>
                                            }
                                        </span>
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </div>

            <ModalDoctor
                isOpenModal={isOpenModal}
                toggle={changeModal}
                isCreate={isCreate}
                idDoctor={idDoctor}
                handleDataDoctor={handleDataDoctor}
            />
        </div>
    );
};

export default ManageDoctor;
