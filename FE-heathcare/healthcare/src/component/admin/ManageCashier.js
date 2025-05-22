import React, { useEffect, useState } from 'react';
import ModalCashier from './ModalCashier';
import { useSelector } from 'react-redux';
import { createCashier, getAllCashierAdmin, changeActiveUser, updateCashier } from '../../service/userService';
import { toast } from 'react-toastify';
import { format } from 'date-fns';
import { Triangle } from 'react-loader-spinner'; // Import spinner
import '../../asset/scss/ManageCashier.scss'

const ManageCashier = () => {
    const user = useSelector((state) => state.auth.user);
    const [isOpenModal, setIsOpenModal] = useState(false);
    const [isCreate, setIsCreate] = useState(true);
    const [idCashier, setIdCashier] = useState('');
    const [CashiersData, setCashiersData] = useState('');
    const [loading, setLoading] = useState(false);  // Thêm state cho spinner loading


    useEffect(() => {
        getCashiersData();
    }, []);

    const getCashiersData = async () => {
        let res = await getAllCashierAdmin();
        if (res?.errCode === 0) {
            setCashiersData(res.data);
        }
    };

    const formatDate = (date) => {
        return format(date, 'dd-MM-yyyy');  // Định dạng lại theo kiểu dd-MM-yyyy
    };

    const changeModal = () => {
        if (isOpenModal === true) {
            setIdCashier('');
            setIsCreate(true);
        }
        setIsOpenModal(!isOpenModal);
    };

    const handleData = async (data) => {
        setLoading(true);  // Bật spinner khi gọi API
        if (isCreate) {
            let res = await createCashier(data, user.token);
            if (res?.errCode === 0) {
                setLoading(false);
                setIsOpenModal(false);
                await getCashiersData();
                toast.success("Tạo Bác sĩ thành công !");
            } else {
                toast.error("Thất bại !");
            }
        } else {
            let res = await updateCashier(data, user.token);
            if (res?.errCode === 0) {
                setLoading(false);
                setIsOpenModal(false);
                setIsCreate(true);
                await getCashiersData();
                toast.success("Thành công!");
            }
        }
        setLoading(false);
        // Tắt spinner sau khi API gọi xong
    };

    const handleActiveTechnician = async (idInput) => {
        setLoading(true);  // Bật spinner khi gọi API
        let data = {
            id: idInput
        };
        let res = await changeActiveUser(data, user.token);
        if (res?.errCode === 0) {
            setLoading(false);
            toast.success('Thành công!');
            await getCashiersData();
        }
        setLoading(false)
    };

    const handleEditCashier = (id) => {
        console.log('assse', id);
        setIdCashier(id);
        setIsOpenModal(true);
        setIsCreate(false);
    };

    useEffect(() => {
        console.log('idtec', idCashier);
    }, [idCashier]);

    return (
        <div className="manage-technician-container">
            <div className='container'>
                <div>
                    <button className='btn btn-primary' onClick={changeModal}>
                        <i className="fa-solid fa-user-plus"></i> Thu ngân
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
                        {CashiersData?.length > 0 && CashiersData.map((item, index) => {
                            return (
                                <tr key={`dt-${index}`}>
                                    <td>{index + 1}</td>
                                    <td>{item.name}</td>
                                    <td>{formatDate(item.date_of_birth)}</td>
                                    <td>{item.phone}</td>
                                    <td>{item.user.is_active ? "Hoạt động" : "Không hoạt động"}</td>
                                    <td className="td-action">
                                        <span className='mx-3 btn-update' onClick={() => handleEditCashier(item.id)}> <i className="fa-solid fa-pencil"></i> </span>
                                        <span className='btn-active' onClick={() => handleActiveTechnician(item.user_id)}>
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

            <ModalCashier
                isOpenModal={isOpenModal}
                toggle={changeModal}
                isCreate={isCreate}
                idCashier={idCashier}
                handleData={handleData}
            />
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
        </div>
    );
};

export default ManageCashier;
