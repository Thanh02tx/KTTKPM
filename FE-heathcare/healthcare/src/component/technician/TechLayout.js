import React from 'react';
import { Outlet } from 'react-router-dom';
// import '../../asset/scss/TechLayout.scss';
import { useSelector } from 'react-redux';
import Nav from '../Nav';
import { menuTech } from '../../utils/menuApp';
const TechLayout = () => {
    const user = useSelector((state) => state.auth.user);

    return (
        <div>
            <div className="admin-layout d-flex">
                <div className='nav'>
                    <Nav menuStaff={menuTech} />
                </div>
                <div className='content'>
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default TechLayout;
