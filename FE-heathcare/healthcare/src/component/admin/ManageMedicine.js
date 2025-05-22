import React, { useEffect, useState } from 'react';
import '../../asset/scss/ManageMedicine.scss';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom'; // ✅ Import useNavigate
const ManageMedicine = () => {
  const user = useSelector((state) => state.auth.user);
  const [doctorData, setDoctorData] = useState([]);

  const navigate = useNavigate(); // ✅ Khởi tạo useNavigate



  return (
    <div className="manage-medicine-container container">
        hello
      </div>
  );
};

export default ManageMedicine;
