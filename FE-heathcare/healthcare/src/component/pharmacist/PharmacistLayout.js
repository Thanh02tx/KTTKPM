import React from 'react';
import { Outlet } from 'react-router-dom';
// import '../../asset/scss/PharmacistLayout.scss';
import { useSelector } from 'react-redux';
import Nav from '../Nav';
import { menuPharmacist } from '../../utils/menuApp';
const PharmacistLayout = () => {
    const user = useSelector((state) => state.auth.user);

    return (
        <div>
            <div className="admin-layout d-flex">
                <div className='nav'>
                    <Nav menuStaff={menuPharmacist} />
                </div>
                <div className='content'>
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default PharmacistLayout;
