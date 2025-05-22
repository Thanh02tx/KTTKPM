import React, { useEffect, useState } from 'react';
import ModalNurse from './ModalNurse';
import { useSelector } from 'react-redux';
import { createPharmacist, getAllPharmacistAdmin, changeActiveUser, updatePharmacist } from '../../service/userService';
import { toast } from 'react-toastify';
import { format } from 'date-fns';
import '../../asset/scss/ManagePharmacist.scss'
import { Triangle } from 'react-loader-spinner';
import ModalPharmacist from './ModalPharmacist';
const ManagePharmacist = () => {
    const user = useSelector((state) => state.auth.user);
    const [isOpenModal, setIsOpenModal] = useState(false);
    const [isCreate, setIsCreate] = useState(true);
    const [idPharmacist, setIdPharmacist] = useState('');
    const [nurseData, setNurseData] = useState('');
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        console.log('sâa', user)
    }, [user])

    useEffect(() => {
        getPharmacistsData()
    }, [])
    const getPharmacistsData = async () => {
        let res = await getAllPharmacistAdmin();
        if (res?.errCode === 0) {
            setNurseData(res.data)
        }
    }
    const formatDate = (date) => {
        return format(date, 'dd-MM-yyyy');  // Định dạng lại theo kiểu dd-MM-yyyy
    };
    const changeModal = () => {
        if (isOpenModal === true) {
            setIdPharmacist('')
            setIsCreate(true)
        }

        setIsOpenModal(!isOpenModal);
    };
    const handleData = async (data) => {
        setLoading(true)
        if (isCreate) {
            let res = await createPharmacist(data, user.token)
            if (res?.errCode === 0) {
                setLoading(false)
                setIsOpenModal(false)
                await getPharmacistsData()
                toast.success("Tạo Bác sĩ thành công !")
            } else {
                toast.error("Thất bại !")
            }
        } else {
            let res = await updatePharmacist(data, user.token)
            if (res?.errCode === 0) {
                setLoading(false)
                setIsOpenModal(false);
                setIsCreate(true);
                await getPharmacistsData()
                toast.success("Thành công!")
            }
        }
        setLoading(false)
    }
    const handleActivePharmacist = async (idInput) => {
        setLoading(false)
        let data = {
            id: idInput
        }
        let res = await changeActiveUser(data, user.token)
        if (res?.errCode === 0) {
            setLoading(false)
            toast.success('Thành công!')
            await getPharmacistsData()
        }
        setLoading(false)
    }
    const handleEditPharmacist = (id) => {
        console.log('assse', id)
        setIdPharmacist(id)
        setIsOpenModal(true)
        setIsCreate(false)
    }
    useEffect(() => {
        console.log('idtec', idPharmacist)
    }, [idPharmacist])
    return (
        <div className="manage-technician-container">
            <div className='container'>
                <div>
                    <button className='btn btn-primary' onClick={changeModal}>
                        <i className="fa-solid fa-user-plus"></i> Dược sĩ
                    </button>
                </div>
                <table className='table mt-3'>
                    <thead>
                        <tr>
                            <th>STT</th>
                            <th>Họ Tên</th>
                            <th>Ngày sinh</th>
                            <th>Số điện thoại</th>
                            <th>Trạng thái</th>
                            <th>Hành động</th>
                        </tr>
                    </thead>
                    <tbody>
                        {nurseData?.length > 0 && nurseData.map((item, index) => {
                            return (
                                <tr key={`dt-${index}`}>
                                    <td>{index + 1}</td>
                                    <td>{item.name}</td>
                                    <td>{formatDate(item.date_of_birth)}</td>
                                    <td>{item.phone}</td>
                                    <td>{item.user.is_active ? "Hoạt động" : "Không hoạt động"}</td>
                                    <td className="td-action">
                                        <span className='mx-3 btn-update' onClick={() => handleEditPharmacist(item.id)}> <i className="fa-solid fa-pencil"></i> </span>
                                        <span className='btn-active' onClick={() => handleActivePharmacist(item.user_id)}>
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

            <ModalPharmacist
                isOpenModal={isOpenModal}
                toggle={changeModal}
                isCreate={isCreate}
                idPharmacist={idPharmacist}
                handleData={handleData}
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

export default ManagePharmacist;
