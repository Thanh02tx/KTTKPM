import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
// import '../../asset/scss/CashierLayout.scss';
import { useSelector } from 'react-redux';
import Nav from '../Nav';
import { menuCashier } from '../../utils/menuApp';

const CashierLayout = () => {
    const user = useSelector((state) => state.auth.user);

    return (
        <div>
            <div className="admin-layout d-flex">
                <div className='nav'>
                    <Nav menuStaff={menuCashier} />
                </div>
                <div className='content'>
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default CashierLayout;
