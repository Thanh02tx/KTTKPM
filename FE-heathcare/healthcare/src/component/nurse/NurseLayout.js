import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
// import '../../asset/scss/NurseLayout.scss';
import { useSelector } from 'react-redux';
import Nav from '../Nav';
import { menuNurse } from '../../utils/menuApp';
const NurseLayout = () => {
    const user = useSelector((state) => state.auth.user);

    return (
        <div>
            <div className="admin-layout d-flex">
                <div className='nav'>
                    <Nav menuStaff={menuNurse} />
                </div>
                <div className='content'>
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default NurseLayout;
