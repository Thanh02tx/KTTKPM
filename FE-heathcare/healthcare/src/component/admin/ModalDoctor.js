import React, { useEffect, useState } from 'react';
import { Button, Modal, ModalHeader, ModalBody } from 'reactstrap';
import { getAllProvince, getAllDistrict, getAllWard } from '../../service/address';
import Select from 'react-select';
import DatePicker, { registerLocale } from "react-datepicker";
import vi from "date-fns/locale/vi";
import "react-datepicker/dist/react-datepicker.css";
import '../../asset/scss/modal-doctor.scss';
import avatarTrang from '../../asset/img/avatar-trang.jpeg';
import { Editor } from 'react-draft-wysiwyg';
import { convertFromHTML, ContentState, EditorState ,convertToRaw} from 'draft-js';
import draftToHtml from 'draftjs-to-html';
import 'react-draft-wysiwyg/dist/react-draft-wysiwyg.css';
import { getAllGenderChoices, getDoctor } from '../../service/userService';
import { toast } from 'react-toastify';

registerLocale("vi", vi);

const ModalDoctor = ({ isOpenModal, idDoctor, toggle, isCreate, handleDataDoctor }) => {
  const [genderData, setGenderData] = useState([]);
  const [gender, setGender] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [date_of_birth, setDateOfBirth] = useState(new Date());
  const [degree, setDegree] = useState('');
  const [address_detail, setAddressDetail] = useState('');
  const [price, setPrice] = useState('');
  const [provinceData, setProvinceData] = useState([]);
  const [province, setProvince] = useState('');
  const [districtData, setDistrictData] = useState([]);
  const [district, setDistrict] = useState('');
  const [wardData, setWardData] = useState([]);
  const [ward, setWard] = useState('');
  const [bio_html, setBioHtml] = useState(EditorState.createEmpty());
  const [description_html, setDescriptionHtml] = useState(EditorState.createEmpty());

  const [image, setImage] = useState('');
  const [isChangeImage,setIsChangeImage]= useState(false)
  

  useEffect(() => {
    const fetchData = async () => {
      const provinces = await getAllProvince();
      setProvinceData(provinces);

      const resGenders = await getAllGenderChoices();
      if (resGenders?.errCode === 0) {
        setGenderData(resGenders.data);
      }
    };
    fetchData();


    fetchDefaultAvatar();
  }, []);
  const fetchDefaultAvatar = async () => {
    try {
      const response = await fetch(avatarTrang);
      const blob = await response.blob();

      const reader = new FileReader();
      reader.onloadend = () => {
        // Set the base64 image string to the state
        setImage(reader.result); // This will be the base64 string of the image
      };
      reader.readAsDataURL(blob); // Converts the blob to base64
    } catch (error) {
      console.error("Error fetching default avatar:", error);
    }
  };
  useEffect(() => {
    if (!isOpenModal) {
      setEmail('');
      setName('');
      setPassword('');
      setConfirmPassword('');
      setDegree('');
      setPhone('');
      setGender('');
      setDateOfBirth(new Date());
      setPrice('');
      setProvince('');
      setDistrict('');
      setWard('');
      setAddressDetail('');
      setDescriptionHtml(EditorState.createEmpty());
      setBioHtml(EditorState.createEmpty());
      setIsChangeImage(false);
      fetchDefaultAvatar();
    }
  }, [isOpenModal]);
  useEffect(() => {
    const fetchDoctor = async () => {
      if (idDoctor) {
        try {
          const res = await getDoctor(idDoctor);
          if (res?.errCode === 0) {
            let doctor = res.data;
            if (doctor) {
              setGender(genderData.find((g) => g.value === doctor.gender));
              const prov = provinceData.find((p) => p.value === doctor.province);
              setProvince(prov);

              const districts = await getAllDistrict(prov.value);
              setDistrictData(districts);

              const dist = districts.find(d => d.value === doctor.district);
              setDistrict(dist);

              const wards = await getAllWard(prov.value, dist.value);
              setWardData(wards);
              setWard(wards.find(w => w.value === doctor.ward));

              setImage(doctor.image)
              setEmail(doctor.email);
              setName(doctor.name);
              setDegree(doctor.degree);
              setPhone(doctor.phone);
              // setGender('');
              setDateOfBirth(new Date(doctor.date_of_birth));
              setPrice(doctor.price);
              // setProvince('');
              // setDistrict('');
              // setWard('');
              setAddressDetail(doctor.address_detail);
              setDescriptionHtml(EditorState.createWithContent(
                ContentState.createFromBlockArray(convertFromHTML(doctor.description_html))
              ));
              setBioHtml(EditorState.createWithContent(
                ContentState.createFromBlockArray(convertFromHTML(doctor.bio_html))
              ));
              setImage(doctor.image);
            }
          }
        } catch (error) {
          console.error('Lỗi lấy bác sĩ:', error);
        }
      }
    };

    fetchDoctor();
  }, [idDoctor]);
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result); // This will be the base64 string of the selected file
        setIsChangeImage(true)
        
      };
      reader.readAsDataURL(file); // Converts the file to base64
    }
  };


  const handleChangeGender = (option) => setGender(option);

  const handleChangeProvince = (option) => {
    setProvince(option);
    const districts = getAllDistrict(option.value);
    setDistrictData(districts);
    setDistrict('');
    setWard('');
    setWardData([]);
  };

  const handleChangeDistrict = (option) => {
    setDistrict(option);
    const wards = getAllWard(province.value, option.value);
    setWardData(wards);
    setWard('');
  };

  const handleChangeWard = (option) => setWard(option);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      toast.error("Kiểm tra lại mật khẩu!");
      return;
    }

    const bioHtml = draftToHtml(convertToRaw(bio_html.getCurrentContent()));
    const descriptionHtml = draftToHtml(convertToRaw(description_html.getCurrentContent()));
    let data = {
      name: name,
      degree: degree,
      phone: phone,
      gender: gender.value,
      date_of_birth: date_of_birth.toISOString().split("T")[0],
      price: price,
      province: province.value,
      district: district.value,
      ward: ward ? ward.value : '',
      address_detail: address_detail,
      description_html: descriptionHtml,
      bio_html: bioHtml,
    };
    if(isChangeImage) data['image'] =image
    if (isCreate) {
      data['email'] = email;
      data['password'] = password;
    }else{
      data['id']= idDoctor
    }
    await handleDataDoctor(data);
  };

  return (
    <Modal isOpen={isOpenModal} toggle={toggle} className="modal-user-container" size="lg">
      <ModalHeader toggle={toggle}>Doctor</ModalHeader>
      <ModalBody>
        <form onSubmit={handleSubmit}>
          <div className="modal-doctor-body">
            <div className="avatar-wrapper">
              <img src={image || avatarTrang} alt="Avatar" className="avatar" />
              <label htmlFor="avatarInput" className="upload-btn">+</label>
              <input
                type="file"
                id="avatarInput"
                accept="image/*"
                hidden
                onChange={handleImageChange}
              />
            </div>

            <div className="row">
              {isCreate && (
                <>
                  <div className="form-group col-4">
                    <label>Email Đăng nhập</label>
                    <input
                      className="form-control"
                      type="email"
                      placeholder="Nhập thông tin"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group col-4">
                    <label>Mật khẩu</label>
                    <input
                      className="form-control"
                      type="password"
                      pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$"
                      placeholder="Nhập thông tin"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group col-4">
                    <label>Xác nhận mật khẩu</label>
                    <input
                      className="form-control"
                      type="password"
                      pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$"
                      placeholder="Nhập thông tin"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>
                </>
              )}

              <div className="form-group col-4">
                <label>Họ và Tên</label>
                <input
                  className="form-control"
                  type="text"
                  placeholder="Nhập thông tin"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group col-4">
                <label>Học Vị</label>
                <input
                  className="form-control"
                  type="text"
                  placeholder="Nhập thông tin"
                  value={degree}
                  onChange={(e) => setDegree(e.target.value)}
                  required
                />
              </div>

              <div className="form-group col-4">
                <label>Số điện thoại</label>
                <input
                  className="form-control"
                  type="tel"
                  pattern="^[0-9]{10,15}$"
                  placeholder="Nhập thông tin"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                />
              </div>

              <div className="form-group col-4">
                <label>Giới tính</label>
                <Select
                  options={genderData}
                  placeholder="Chọn Giới tính"
                  value={gender}
                  onChange={handleChangeGender}
                  required
                />
              </div>

              <div className="form-group col-4">
                <label>Ngày Sinh</label>
                <DatePicker
                  className="form-control"
                  selected={date_of_birth}
                  onChange={(date) => setDateOfBirth(date)}
                  locale="vi"
                  dateFormat="dd/MM/yyyy"
                  maxDate={new Date()}
                />
              </div>

              <div className="form-group col-4">
                <label>Giá khám</label>
                <input
                  className="form-control"
                  type="number"
                  min={1}
                  placeholder="Nhập thông tin"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  required
                />
              </div>

              <div className="form-group col-4">
                <label>Tỉnh thành</label>
                <Select
                  options={provinceData}
                  placeholder="Chọn Tỉnh/Thành phố"
                  value={province}
                  onChange={handleChangeProvince}
                  required
                />
              </div>

              <div className="form-group col-4">
                <label>Quận Huyện</label>
                <Select
                  options={districtData}
                  placeholder="Chọn Quận/Huyện"
                  value={district}
                  onChange={handleChangeDistrict}
                  required
                />
              </div>

              <div className="form-group col-4">
                <label>Xã Phường</label>
                <Select
                  options={wardData}
                  placeholder="Chọn Xã/Phường"
                  value={ward}
                  onChange={handleChangeWard}
                />
              </div>

              <div className="form-group">
                <label>Địa chỉ chi tiết</label>
                <input
                  className="form-control"
                  type="text"
                  required
                  value={address_detail}
                  onChange={(e) => setAddressDetail(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Mô tả</label>
                <Editor
                  editorState={description_html}
                  onEditorStateChange={setDescriptionHtml}
                  placeholder="Nhập mô tả"
                />
              </div>
              <div className="form-group">
                <label>Tiểu sử</label>
                <Editor
                  editorState={bio_html}
                  onEditorStateChange={setBioHtml}
                  placeholder="Nhập tiểu sử"
                />
              </div>

              
            </div>
          </div>

          <div className='d-flex my-3'>
            <Button color="primary" type="submit" >{isCreate ? "Thêm mới" : "Lưu"}</Button>
            <Button color='secondary' className='mx-3' type='button' onClick={toggle}>Huỷ</Button>
          </div>
        </form>
      </ModalBody>
    </Modal>
  );
};

export default ModalDoctor;
