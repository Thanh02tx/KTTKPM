import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import '../../asset/scss/ManageRoom.scss';
import { Modal, ModalHeader, ModalBody, Button } from 'reactstrap';
import { createRoom, getRooms ,changeActiveRoom,getRoomById,updateRoom} from '../../service/appointmentService';
const ManageRoom = () => {
  const user = useSelector((state) => state.auth.user);
  const [roomData, setRoomData] = useState([]);
  const [isOpenModal, setIsOpenModal] = useState(false);
  const [name, setName] = useState('');
  const [isCreate, setIsCreate] = useState(true);
  const [editId, setEditId] = useState(null);

  useEffect(() => {
    loadData()
  },[])
  const loadData = async () => {
    let res = await getRooms();
    if (res?.errCode === 0) {
      setRoomData(res.data)
    }
  }
  useEffect(()=>{
    if(!isOpenModal){
      setIsCreate(true);
      setName('');
    }
  },[isOpenModal])
  // Toggle modal visibility
  const toggle = () => {
    setIsOpenModal(!isOpenModal);
    if (!isOpenModal) {
      // Reset form when opening
      setName('');
      setIsCreate(true);
      setEditId(null);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    const action = isCreate ? createRoom : updateRoom;
    const params = isCreate ? { name } : { name, id: editId };
  
    try {
      const res = await action(params, user.token);
      if (res?.errCode === 0) {
        toast.success('Thành công!');
        setIsOpenModal(false)
        await loadData();
      } else {
        toast.error('Lỗi!');
      }
    } catch (error) {
      toast.error('Có lỗi xảy ra');
    }
  };
  
  const handleEditRoom=async(id)=>{
    let res = await getRoomById(id);
    if(res?.errCode===0){
      setName(res.data.name)
      setEditId(res.data.id)
      setIsCreate(false)
      setIsOpenModal(!isOpenModal)
    }
  }
  const handleChangeActiveRoom=async(idInput)=>{
    let res = await changeActiveRoom({
      id:idInput
    },user.token)
    if(res?.errCode===0){
      toast.success("Sửa thành công!")
      await loadData()
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
            <th>Trạng thái</th>
            <th>Hành động</th>
          </tr>
        </thead>
        <tbody>
          {roomData?.length > 0 && roomData.map((item, index) => (
            <tr key={`room-${index}`}>
              <td>{index + 1}</td>
              <td>{item.name}</td>
              <td>{item.is_active ? "Hoạt động" : "Không hoạt động"}</td>
              <td className="td-action">
                <span className='mx-3 btn-update' onClick={() => handleEditRoom(item.id)}> <i className="fa-solid fa-pencil"></i> </span>
                <span className='btn-active' onClick={() => handleChangeActiveRoom(item.id)}>
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
      <Modal isOpen={isOpenModal} toggle={toggle} className="modal-user-container" size="lg">
        <ModalHeader toggle={toggle}>Phòng khám</ModalHeader>
        <ModalBody>
          <form onSubmit={handleSubmit}>
            <div className="modal-room-body">
              <div className="form-group ip-name">
                <label>Tên phòng</label>
                <input
                  className="form-control"
                  type="text"
                  placeholder="Nhập tên phòng"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
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

export default ManageRoom;
