import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
// import '../../asset/scss/DoctorLayout.scss';
import { useSelector } from 'react-redux';
import Nav from '../Nav';
import { menuDoctor } from '../../utils/menuApp';
const DoctorLayout = () => {
    const user = useSelector((state) => state.auth.user);

    return (
        <div>
            <div className="admin-layout d-flex">
                <div className='nav'>
                    <Nav menuStaff={menuDoctor} />
                </div>
                <div className='content'>
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default DoctorLayout;
