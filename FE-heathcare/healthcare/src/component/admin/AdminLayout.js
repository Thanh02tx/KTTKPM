import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { checkRoleAdmin } from '../../service/userService';
import NotFound from '../NotFound';
import Nav from '../Nav';
import { menuAdmin } from '../../utils/menuApp';
import '../../asset/scss/AdminLayout.scss';
const AdminLayout = () => {
  const user = useSelector((state) => state.auth.user);
  const [isAdmin, setIsAdmin] = useState(null); // null: đang kiểm tra, true: admin, false: không phải admin

  useEffect(() => {
    const verifyAdmin = async () => {
      if (user?.token) {
        try {
          let res = await checkRoleAdmin(user.token);
          if (res?.errCode === 0) {
            setIsAdmin(true);
          } else {
            setIsAdmin(false);
          }
        } catch (error) {
          setIsAdmin(false);
        }
      } else {
        setIsAdmin(false);
      }
    };
    verifyAdmin();
  }, [user]);

  if (isAdmin === null) return <div>Loading...</div>; // hoặc spinner
  if (isAdmin === false) return <NotFound />;

  return (
    <div className="admin-layout d-flex">
      <div className='nav'>
        <Nav menuStaff={menuAdmin}/>
      </div>
      <div className='content'>
        <Outlet />
      </div>
    </div>
  );
};

export default AdminLayout;
