import React, { useEffect, useState } from 'react';
import '../../asset/scss/Header.scss';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import Imglogo from '../../asset/img/logo.jpg';
import { logout } from '../../redux/slides/authSlide';

const Header = () => {
  const user = useSelector((state) => state.auth.user);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleClickLogo = () => {
    navigate(`/`);
  };

  const handleClickUser = () => {
    navigate(`/patient`);
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    dispatch(logout());
    navigate('/login');
  };

  return (
    <div className="header-container">
      <div className="d-flex">
        {/* <div className="nav-bar">
          <i className="fa-solid fa-bars"></i>
        </div> */}
        <div className="img-logo" onClick={handleClickLogo}>
          <img src={Imglogo} alt="Logo" />
        </div>
      </div>
      <div className="d-flex nav-right">
        <div>
          <i className="fa-solid fa-user icon" onClick={handleClickUser}></i> Xin chào!
        </div>
        <div className="mx-3 icon">
          {user ? (
            <i className="fa-solid fa-right-from-bracket" onClick={handleLogout}></i>
          ) : (
            <i className="fa-solid fa-right-to-bracket"></i>
          )}
        </div>
      </div>
    </div>
  );
};

export default Header;