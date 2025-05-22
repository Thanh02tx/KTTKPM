import React, { useEffect, useState } from 'react';
import '../../asset/scss/CashierInfor.scss';
import DatePicker, { registerLocale } from "react-datepicker";
import vi from "date-fns/locale/vi";
import "react-datepicker/dist/react-datepicker.css";
import { useSelector } from 'react-redux';
import { getCashierByToken,updateCashierToken} from '../../service/userService';
import { getWardDistricProvince, getAllProvince, getAllDistrict, getAllWard } from '../../service/address';
import moment from 'moment';
import Select from 'react-select';
import { Editor } from 'react-draft-wysiwyg';
import { convertFromHTML, ContentState, EditorState, convertToRaw } from 'draft-js';
import draftToHtml from 'draftjs-to-html';
import 'react-draft-wysiwyg/dist/react-draft-wysiwyg.css';
import { toast } from 'react-toastify';
import { Triangle } from 'react-loader-spinner';
import { intlFormatDistance } from 'date-fns';
const CashierInfor = () => {
    const user = useSelector((state) => state.auth.user);
    const [inforData, setInforData] = useState({})
    const [isChange, setIsChange] = useState(false)
    const [name, setName] = useState("")
    const [date_of_birth, setDateOfBirth] = useState("")
    const [phone, setPhone] = useState("")
    const [gender, setGender] = useState("")
    const [address_detail, setAddressDetail] = useState("")
    const [bio_html, setBioHtml] = useState(EditorState.createEmpty());
    const [listProvince, setListProvince] = useState([])
    const [listDistrict, setListDistrict] = useState([])
    const [listWard, setListWard] = useState([])
    const [ward, setWard] = useState("")
    const [district, setDistrict] = useState("")
    const [province, setProvince] = useState("")
    const [image, setImage] = useState("")
    const [loading, setLoading] = useState(false);
    useEffect(() => {

        loadData()
    }, [])
    const loadData = async () => {
        if (user?.token) {
            let res = await getCashierByToken(user.token)
            if (res?.errCode === 0) {
                let fullInfor = res.data
                if (fullInfor) {
                    let address = getWardDistricProvince(fullInfor.ward, fullInfor.district, fullInfor.province)
                    console.log('add',address)
                    if (address) {
                        fullInfor = {
                            ...fullInfor,
                            address
                        }
                    }
                    setInforData(fullInfor)
                }
            }
        }
        setListProvince(getAllProvince())
        
    }
    const handleProvinceChange = (selectedOption) => {
        setProvince(selectedOption);
        setListDistrict(getAllDistrict(selectedOption.value))
        setDistrict("")
        setListWard([])
        setWard("")
    };
    const handleDistrictChange = (selectedOption) => {
        setDistrict(selectedOption);
        setListWard(getAllWard(province.value, selectedOption.value))
        setWard("")
    };

    const handleChangeInfor = () => {
        if (!isChange) {
            setName(inforData.name)
            setPhone(inforData.phone)
            setDateOfBirth(inforData.date_of_birth)
            let pro = listProvince.find(item => item.value === inforData.province)
            setProvince(pro)
            let listDis = getAllDistrict(pro.value)
            console.log('ea',listDis)
            let dis = listDis.find(item => item.value === inforData.district)
            setListDistrict(listDis)
            setDistrict(dis)
            let listWard = getAllWard(pro.value, dis.value)
            let ward = listWard.find(item => item.value === inforData.ward)
            setListWard(listWard)
            setWard(ward)
            setAddressDetail(inforData.address_detail)
            setBioHtml(EditorState.createWithContent(
                ContentState.createFromBlockArray(convertFromHTML(inforData.bio_html))
            ));
        }
        setIsChange(!isChange)
    }
    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setImage(reader.result); // This will be the base64 string of the selected file
            };
            reader.readAsDataURL(file); // Converts the file to base64
        }
    };
    const handleUpdateInfor = async (e) => {
        e.preventDefault();
        const bioHtml = draftToHtml(convertToRaw(bio_html.getCurrentContent()));
        let data ={
            name,
            date_of_birth,
            phone,
            province:province.value,
            district:district.value,
            ward:ward.value,
            address_detail,
            bio_html:bioHtml
        }
        console.log('ew',data)
        setLoading(true)
        let res = await updateCashierToken(data, user.token)
        if (res?.errCode === 0) {
            setLoading(false)
            toast.success("Cập nhập thành công!")
            await loadData()
            setIsChange(false)
            setProvince("")
            setDistrict("")
            setWard("")
        }
        else {
            toast.error("Lỗi!")
        }
        setLoading(false)
    }
    const handleUpdateImage = async () => {
        let data = { image }
        setLoading(true)
        let res = await updateCashierToken(data, user.token)
        if (res?.errCode === 0) {
            setLoading(false)
            toast.success("Cập nhập thành công!")
            await loadData()
            setImage("")
        }
        else {
            toast.error("Lỗi!")
        }
        setLoading(false)
    }
    return (
        <div className='cashier-infor-container my-4 mx-5'>
            <div className='n-i-nav'>
                <span>Thông tin</span>
                <button onClick={handleChangeInfor}>{!isChange ? 'Chỉnh sửa' : 'Huỷ'}</button>
            </div>
            <div className='nurse-infor-content d-flex'>
                <div className='left'>
                    <div className='image-box'>
                        <img src={image ? image : inforData?.image ? inforData.image : ""} />
                        <label>
                            <i className="fa-solid fa-pen-to-square"></i>
                            <input type='file' accept="image/*" onChange={handleImageChange} hidden />
                        </label>
                    </div>
                    {image &&
                        <div className='d-flex mt-3 btn-image'>
                            <button onClick={() => setImage("")}>Huỷ</button>
                            <button onClick={handleUpdateImage}>Lưu</button>
                        </div>
                    }
                </div>
                {!isChange ?
                    <div className='right row'>
                        <div className='form-group col-4 item'>
                            <label className='mb-2'>Họ và tên:</label>
                            <p>
                                {inforData?.name || "N/A"}
                            </p>
                        </div>
                        <div className='form-group col-4'>
                            <label className='mb-2'>Ngày sinh:</label>
                            <p>
                                {inforData?.date_of_birth ? moment(inforData.date_of_birth).format('DD-MM-YYYY') : "N/A"}
                            </p>
                        </div>
                        <div className='form-group col-4'>
                            <label className='mb-2'>Số điện thoại:</label>
                            <p>
                                {inforData?.phone || "N/A"}
                            </p>
                        </div>
                        <div className='form-group col-4'>
                            <label className='mb-2'>Tỉnh thành:</label>
                            <p>
                                {inforData?.address?.province || "N/A"}
                            </p>
                        </div>
                        <div className='form-group col-4'>
                            <label className='mb-2'>Quận huyện:</label>
                            <p>
                                {inforData?.address?.district || "N/A"}
                            </p>
                        </div>
                        <div className='form-group col-4'>
                            <label className='mb-2'>Xã phường:</label>
                            <p>
                                {inforData?.address?.ward || "N/A"}
                            </p>
                        </div>
                        <div className='form-group'>
                            <label className='mb-2'>Địa chỉ chi tiết:</label>
                            <p>
                                {inforData?.address_detail || "N/A"}
                            </p>
                        </div>
                        <div className='form-group'>
                            <label className='mb-2'>Bio:</label>
                            <div dangerouslySetInnerHTML={{ __html: inforData?.bio_html || '' }} />
                        </div>
                    </div>
                    :
                    <form className='right row'>
                        <div className='form-group col-4 item'>
                            <label className='mb-2'><span className='text-danger'>* </span>Họ và tên:</label>
                            <input
                                className='form-control'
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        </div>
                        <div className='form-group col-4 item'>
                            <label className='mb-2'><span className='text-danger'>* </span>Ngày sinh:</label>
                            <DatePicker
                                className="form-control"
                                selected={date_of_birth}
                                onChange={(date) => setDateOfBirth(date)}
                                locale="vi"
                                dateFormat="dd/MM/yyyy"
                                maxDate={new Date()}
                            />
                        </div>
                        <div className='form-group col-4 item'>
                            <label className='mb-2'><span className='text-danger'>* </span>Số điện thoại:</label>
                            <input
                                className='form-control'
                                value={phone}
                                onChange={(e) => setPhone(e.target.value)}
                                required
                            />
                        </div>
                        <div className='form-group col-4 item'>
                            <label className='mb-2'><span className='text-danger'>* </span>Tỉnh thành:</label>
                            <Select
                                className='mt-2'
                                options={listProvince}
                                placeholder="Chọn Tỉnh thành"
                                value={province}
                                onChange={handleProvinceChange}
                                required
                            />
                        </div>
                        <div className='form-group col-4 item'>
                            <label className='mb-2'><span className='text-danger'>* </span>Quận huyện:</label>
                            <Select
                                className='mt-2'
                                options={listDistrict}
                                placeholder="Chọn Quận huyện"
                                value={district}
                                onChange={handleDistrictChange}
                                required
                            />
                        </div>
                        <div className='form-group col-4 item'>
                            <label className='mb-2'><span className='text-danger'>* </span>Xã phường:</label>
                            <Select
                                className='mt-2'
                                options={listWard}
                                placeholder="Chọn Xã phường"
                                value={ward}
                                onChange={(selectedOption) => setWard(selectedOption)}
                                required
                            />
                        </div>
                        <div className='form-group item'>
                            <label className='mb-2'><span className='text-danger'>* </span>Địa chỉ chi tiết:</label>
                            <input
                                className='form-control'
                                value={address_detail}
                                onChange={(e) => setAddressDetail(e.target.value)}
                                required
                            />
                        </div>
                        <div className='form-group item'>
                            <label className='mb-2'><span className='text-danger'>* </span>Bio:</label>
                            <Editor
                                editorState={bio_html}
                                onEditorStateChange={setBioHtml}
                                placeholder="Nhập tiểu sử"
                            />
                        </div>
                        <div className='mt-3'>
                            <button className='btn btn-secondary px-4' onClick={handleUpdateInfor}>Lưu</button>
                        </div>
                    </form>
                }
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
        </div>
    );
};

export default CashierInfor;
