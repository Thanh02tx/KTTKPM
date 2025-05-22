import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import '../../asset/scss/PatientLayout.scss';
import { useSelector } from 'react-redux';
import Nav from '../Nav';
import { menuPatient } from '../../utils/menuApp';
import Header from './Header';
const PatientLayout = () => {
    const user = useSelector((state) => state.auth.user);

    return (
        <div>
            <div className="patient-layout d-flex">
                <div className='nav'>
                    <Nav menuStaff={menuPatient} />
                </div>
                <div className='content'>
                    <Header />
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default PatientLayout;
