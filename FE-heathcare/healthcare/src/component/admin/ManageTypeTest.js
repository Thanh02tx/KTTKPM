import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import '../../asset/scss/ManageTypeTest.scss';
import { Modal, ModalHeader, ModalBody, Button } from 'reactstrap';
import { getTypeTypeTest, createTypeTest, getAllTypeTest, getTypeTestById ,changeActiveTypeTestById,updateTypeTest} from '../../service/laboratoryService';
import Select from 'react-select';
import { Editor } from 'react-draft-wysiwyg';
import { convertFromHTML, ContentState, EditorState, convertToRaw } from 'draft-js';
import draftToHtml from 'draftjs-to-html';
import 'react-draft-wysiwyg/dist/react-draft-wysiwyg.css';
const ManageTypeTest = () => {
    const user = useSelector((state) => state.auth.user);
    const [typetestData, setTypetestData] = useState(false);
    const [isOpenModal, setIsOpenModal] = useState(false);
    const [name, setName] = useState('');
    const [typeData, setTypeData] = useState([]);
    const [type, setType] = useState('');
    const [price, setPrice] = useState('');
    const [estimated_time, setEstimatedTime] = useState('');
    const [sample_type, setSampleType] = useState('');
    const [preparation, setPreparation] = useState('');
    const [isCreate, setIsCreate] = useState(true);
    const [typeTestId, setTypeTestId] = useState(null);

    useEffect(() => {
        loadTypeTypeTest()
        loadData()
    }, [])
    const loadData = async () => {
        let res = await getAllTypeTest();
        if (res?.errCode === 0) {
            setTypetestData(res.data)
        }
    }
    const loadTypeTypeTest = async () => {
        let res = await getTypeTypeTest();
        if (res?.errCode === 0) {
            setTypeData(res.data)
        }
    }
    useEffect(() => {
        if (!isOpenModal) {
            setIsCreate(true);
            setName('');
            setType('');
            setPrice('');
            setEstimatedTime('');
            setSampleType('')
            setPreparation('')
            setTypeTestId(null);
        }
    }, [isOpenModal])
    // Toggle modal visibility
    const toggle = () => {
        setIsOpenModal(!isOpenModal);
    };

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();
        const preparationHtml = draftToHtml(convertToRaw(preparation.getCurrentContent()));
        let data = {
            name,
            price,
            type: type.value,
            estimated_time,
            sample_type,
            preparation: preparationHtml
        }
        if (!isCreate) {
            data['id'] = typeTestId
            let res = await updateTypeTest(data,user.token)
            if (res?.errCode === 0) {
                setIsOpenModal(false)
                await loadData()
                toast.success("Cập nhập thành công")
            } else {
                toast.error("Thất bại")
            }
        } else {
            let res = await createTypeTest(data, user.token)
            if (res?.errCode === 0) {
                setIsOpenModal(false)
                await loadData()
                toast.success("Tạo thành công")
            } else {
                toast.error("Thất bại")
            }
        }

    };

    const handleEditTypeTest = async (id) => {
        let res = await getTypeTestById(id);
        if (res?.errCode === 0) {
            let tt = res.data
            const selectedType = typeData.find(item => item.value === tt.type);
            const editorState = EditorState.createWithContent(
                ContentState.createFromBlockArray(convertFromHTML(tt.preparation || ''))
            );
            // viết nốt code lấy ra type dựa vào typeData và 
            setTypeTestId(tt.id)
            setName(tt.name)
            setType(selectedType)
            setPrice(tt.price)
            setEstimatedTime(tt.estimated_time)
            setSampleType(tt.sample_type)
            setPreparation(editorState);
            setIsCreate(false)
            setIsOpenModal(true)
        }
    }
    const handleChangeActiveTypeTest = async (idInput) => {
        let res = await changeActiveTypeTestById({id:idInput},user.token)
        if(res?.errCode===0){
          toast.success("Sửa thành công!")
          await loadData()
        }else{
            toast.error('Thất bại')
        }
    }
    return (
        <div className="manage-room-container container">
            <div className='container my-3'>
                <Button color="primary" onClick={toggle}>
                    <i className="fa-solid fa-plus" /> Phòng
                </Button>
            </div>
            <table className='table '>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Tên</th>
                        <th>Giá</th>
                        <th>Loại</th>
                        <th>Trạng thái</th>
                        <th>Hành động</th>
                    </tr>
                </thead>
                <tbody>
                    {typetestData?.length > 0 && typetestData.map((item, index) => (
                        <tr key={`typetest-${index}`}>
                            <td>{index + 1}</td>
                            <td>{item?.name}</td>
                            <td>{item?.price}</td>
                            <td>{item.type === 'lab_test' ? "Xét nghiệm" : "Siêu âm"}</td>
                            <td>{item.is_active ? "Hoạt động" : "Không hoạt động"}</td>
                            <td className="td-action">
                                <span className='mx-3 btn-update' onClick={() => handleEditTypeTest(item.id)}> <i className="fa-solid fa-pencil"></i> </span>
                                <span className='btn-active' onClick={() => handleChangeActiveTypeTest(item.id)}>
                                    {item.is_active ?
                                        <i class="fa-solid fa-lock"></i>
                                        :
                                        <i class="fa-solid fa-lock-open"></i>
                                    }
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <Modal isOpen={isOpenModal} toggle={toggle} className="modal-user-container" size="xl">
                <ModalHeader toggle={toggle}>Phòng khám</ModalHeader>
                <ModalBody>
                    <form onSubmit={handleSubmit}>
                        <div className="modal-room-body row">
                            <div className="form-group col-6 mt-3">
                                <label>Tên loại kiểm tra</label>
                                <input
                                    className="form-control mt-2"
                                    type="text"
                                    placeholder="Nhập thông tin"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="form-group col-6 mt-3">
                                <label>Loại</label>
                                <Select
                                    className='mt-2'
                                    options={typeData}
                                    placeholder="Chọn Loại"
                                    value={type}
                                    onChange={(selectedOption) => setType(selectedOption)}
                                    required
                                />
                            </div>
                            <div className="form-group col-4 mt-3">
                                <label>Thời gian thực hiện (Phút)</label>
                                <input
                                    className="form-control mt-2"
                                    type="text"
                                    placeholder="Nhập thông tin"
                                    value={estimated_time}
                                    onChange={(e) => setEstimatedTime(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="form-group col-4 mt-3">
                                <label>Giá</label>
                                <input
                                    className="form-control mt-2"
                                    type="text"
                                    placeholder="Nhập thông tin"
                                    value={price}
                                    onChange={(e) => setPrice(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="form-group col-4 mt-3">
                                <label>Mẫu bệnh phẩm</label>
                                <input
                                    className="form-control mt-2"
                                    type="text"
                                    placeholder="Nhập thông tin (nếu có)"
                                    value={sample_type}
                                    onChange={(e) => setSampleType(e.target.value)}
                                />
                            </div>
                            <div className="form-group">
                                <label>Hướng dẫn chuẩn bị</label>
                                <Editor
                                    editorState={preparation}
                                    onEditorStateChange={setPreparation}
                                    placeholder="Nhập tiểu sử"
                                    required
                                />
                            </div>
                        </div>

                        <div className='d-flex my-3'>
                            <Button color="primary" type="submit">
                                {isCreate ? 'Thêm mới' : 'Lưu'}
                            </Button>
                            <Button color='secondary' className='mx-3' onClick={toggle}>
                                Huỷ
                            </Button>
                        </div>
                    </form>
                </ModalBody>
            </Modal>
        </div>
    );
};

export default ManageTypeTest;
