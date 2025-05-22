import React, { useEffect, useState } from 'react';
import '../../asset/scss/home.scss';
import { useSelector } from 'react-redux';
import { getAllDoctorHome } from '../../service/userService';
import { useNavigate } from 'react-router-dom'; // ✅ Import useNavigate
import Header from './Header';
const Home = () => {
  const user = useSelector((state) => state.auth.user);
  const [doctorData, setDoctorData] = useState([]);

  const navigate = useNavigate(); // ✅ Khởi tạo useNavigate

  useEffect(() => {
    const loadDataDoctor = async () => {
      let res = await getAllDoctorHome();
      if (res?.errCode === 0) {
        setDoctorData(res.data);
      }
      
    };
    loadDataDoctor();
  }, []);
  // ✅ Hàm chuyển hướng tới trang chi tiết bác sĩ
  const handleClickDoctor = (id) => {
    navigate(`/detail-doctor/${id}`); // Chuyển tới route chi tiết với id
  };

  return (
    <div className="home-container">
      <Header />
      <div className='img-content'>
        
      </div>
      <div className="content container">
        {doctorData?.length > 0 ? (
          doctorData.map((item, index) => (
            <div
              key={`dt-home-${index}`}
              className="doctor-card"
              onClick={() => handleClickDoctor(item.user_id)} // Sử dụng user_id làm id cho route
            >
              <div className="image-wrapper">
                <img
                  src={item.image}
                  alt="doctor"
                  className="doctor-img"
                />
              </div>
              <div className="text-center mt-2">
                {`${item.degree} - ${item.name}`}
              </div>
            </div>
          ))
        ) : (
          <p className="text-center">Không có bác sĩ nào.</p>
        )}
      </div>
    </div>
  );
};

export default Home;
