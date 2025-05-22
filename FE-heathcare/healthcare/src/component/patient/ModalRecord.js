import React, { useEffect, useState } from 'react';
import { Button, Modal, ModalHeader, ModalBody } from 'reactstrap';
import { getAllProvince, getAllDistrict, getAllWard } from '../../service/address';
import Select from 'react-select';
import DatePicker, { registerLocale } from "react-datepicker";
import vi from "date-fns/locale/vi";
import "react-datepicker/dist/react-datepicker.css";
import '../../asset/scss/modal-doctor.scss';
import avatarTrang from '../../asset/img/avatar-trang.jpeg';
import { convertFromHTML, ContentState, EditorState, convertToRaw } from 'draft-js';
import draftToHtml from 'draftjs-to-html';
import 'react-draft-wysiwyg/dist/react-draft-wysiwyg.css';
import { getAllGenderChoices, getPatientRecordById } from '../../service/userService';
import { toast } from 'react-toastify';
import { useSelector } from 'react-redux';
registerLocale("vi", vi);

const ModalRecord = ({ isOpenModal, idRecord, toggle, isCreate, handleDataRecord }) => {
  const user = useSelector((state) => state.auth.user);
  const [genderData, setGenderData] = useState([]);
  const [gender, setGender] = useState('');
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [date_of_birth, setDateOfBirth] = useState(new Date());
  const [address_detail, setAddressDetail] = useState('');
  const [national_id, setNationalId] = useState('');
  const [health_insurance, setHealthInsurance] = useState('');
  const [provinceData, setProvinceData] = useState([]);
  const [province, setProvince] = useState('');
  const [districtData, setDistrictData] = useState([]);
  const [district, setDistrict] = useState('');
  const [wardData, setWardData] = useState([]);
  const [ward, setWard] = useState('');
  const [isChangeImage, setIsChangeImage] = useState(false);
  const [image, setImage] = useState('');

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
      setName('');
      setPhone('');
      setGender('');
      setDateOfBirth(new Date());
      setNationalId('');
      setHealthInsurance('');
      setProvince('');
      setDistrict('');
      setWard('');
      setAddressDetail('');
      fetchDefaultAvatar();
      setIsChangeImage(false)
    }
  }, [isOpenModal]);
  useEffect(() => {
    const fetchPatientRecord = async () => {
      if (idRecord) {
        try {
          const res = await getPatientRecordById(idRecord,user.token);
          if (res?.errCode === 0) {
            let record = res.data;
            if (record) {
              setGender(genderData.find((g) => g.value === record.gender));
              const prov = provinceData.find((p) => p.value === record.province);
              setProvince(prov);

              const districts = await getAllDistrict(prov.value);
              setDistrictData(districts);

              const dist = districts.find(d => d.value === record.district);
              setDistrict(dist);

              const wards = await getAllWard(prov.value, dist.value);
              setWardData(wards);
              setWard(wards.find(w => w.value === record.ward));
              setName(record.name);
              setPhone(record.phone);
              setDateOfBirth(new Date(record.date_of_birth));
              setNationalId(record.national_id);
              setHealthInsurance(record.health_insurance)
              setAddressDetail(record.address_detail);
              setImage(record.image);
            }
          }
        } catch (error) {
          console.error('Lỗi lấy bác sĩ:', error);
        }
      }
    };

    fetchPatientRecord();
  }, [idRecord]);
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
    
    let data = {
      name: name,
      phone: phone,
      gender: gender.value,
      date_of_birth: date_of_birth.toISOString().split("T")[0],
      national_id: national_id,
      health_insurance: health_insurance,
      province: province.value,
      district: district.value,
      ward: ward ? ward.value : '',
      address_detail: address_detail,
    };
    if(isChangeImage) data['image']=image
    if (!isCreate) {
      data['id'] = idRecord
    }
    await handleDataRecord(data);
  };

  return (
    <Modal isOpen={isOpenModal} toggle={toggle} className="modal-record-container" size="lg">
      <ModalHeader toggle={toggle}>Doctor</ModalHeader>
      <ModalBody>
        <form onSubmit={handleSubmit}>
          <div className="modal-doctor-body">
            <div className="avatar-wrapper">
              <img src={image} alt="Avatar" className="avatar" />
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
                <label>Mã BHYT</label>
                <input
                  className="form-control"
                  type="text"
                  inputMode="numeric"
                  pattern="\d{11}"
                  title="Mã đủ 11 số"
                  placeholder='Nhập thông tin'
                  value={health_insurance}
                  onChange={(e) => setHealthInsurance(e.target.value)}
                  required
                />
              </div>
              <div className="form-group col-4">
                <label>Sỗ CCCD</label>
                <input
                  className="form-control"
                  type="text"
                  inputMode="numeric"
                  pattern="\d{12}"
                  title="Mã đủ 12 số"
                  placeholder='Nhập thông tin'
                  value={national_id}
                  onChange={(e) => setNationalId(e.target.value)}
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
                  placeholder='Nhập thông tin'
                  value={address_detail}
                  onChange={(e) => setAddressDetail(e.target.value)}
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

export default ModalRecord;
