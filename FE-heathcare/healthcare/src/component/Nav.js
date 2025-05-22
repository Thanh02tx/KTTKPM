import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../asset/scss/nav.scss';
import {useDispatch, useSelector } from 'react-redux';
import { logout } from '../redux/slides/authSlide';
import { useNavigate } from 'react-router-dom';
const Nav = ({ menuStaff }) => {
  const [openMenu, setOpenMenu] = useState(null);
  const user = useSelector((state) => state.auth.user);
  const location = useLocation();
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const toggleMenu = (index) => {
    setOpenMenu(openMenu === index ? null : index);
  };

  const isActiveLink = (link) => location.pathname === link;

  const handleLogOut=()=>{
    dispatch(logout());
    navigate('/login');
  }
  return (
    <div className="admin-nav">
      {menuStaff && menuStaff.map((menu, index) => (
        <div key={index} className={`menu-group ${openMenu === index ? 'open' : ''}`}>
          {menu.menus ? (
            <>
              <div
                className="menu-title"
                onClick={() => toggleMenu(index)}
              >
                <span>{menu.name}</span>
                <i className={`fa ${openMenu === index ? 'fa-chevron-up' : 'fa-chevron-down'}`}></i>
              </div>
              {openMenu === index && (
                <div className="submenu">
                  {menu.menus.map((sub, subIndex) => (
                    <Link
                      key={subIndex}
                      to={sub.link}
                      className={`submenu-item ${isActiveLink(sub.link) ? 'active' : ''}`}
                    >
                      {sub.name}
                    </Link>
                  ))}
                </div>
              )}
            </>
          ) : (
            <Link
              to={menu.link}
              className={`menu-title single ${isActiveLink(menu.link) ? 'active' : ''}`}
            >
              {menu.name}
            </Link>
          )}
        </div>
      ))}
      <div className='menu-group'>
        <button className='menu-title bt-logout' onClick={handleLogOut}>Đăng xuất</button>
      </div>
    </div>
  );
};

export default Nav;
