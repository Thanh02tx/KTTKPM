import React, { useEffect, useState } from 'react';
import '../../asset/scss/login.scss';
import { useDispatch, useSelector } from 'react-redux';
import { login } from '../../redux/slides/authSlide';
import { postLogin } from '../../service/userService';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const user = useSelector((state) => state.auth.user);
  const isLoggedIn = useSelector((state) => state.auth.isLoggedIn);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isShowPassword, setIsShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleShowHidePassword = () => setIsShowPassword(!isShowPassword);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMessage("Email và mật khẩu không được để trống.");
      return;
    }

    try {
      const res = await postLogin({
        email,
        password,
      });

      if (res?.errCode === 0) {
        dispatch(login(res.data));
        // Có thể lưu vào localStorage nếu muốn giữ đăng nhập lâu dài
        // localStorage.setItem("user", JSON.stringify(res.data));
      } else {
        setErrorMessage(res?.message || 'Đăng nhập thất bại.');
      }
    } catch (error) {
      console.error('Login failed', error);
      setErrorMessage('Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.');
    }
  };

  // ⚠️ Điều hướng nếu đã đăng nhập mà vào lại trang login
  // ✅ Điều hướng sau khi đăng nhập thành công
  useEffect(() => {
    if (!isLoggedIn || !user?.role) return;
  
    if (user.role === 'admin') {
      navigate('/admin/manage-user/doctor');
      return;
    }
  
    if (user.role === 'nurse') {
      navigate('/nurse/list-medical');
      return;
    }
  
    if (user.role === 'doctor') {
      navigate('/doctor/list-medical');
      return;
    }
    if (user.role === 'cashier') {
      navigate('/cashier/list-medical');
      return;
    }
    if (user.role === 'technician') {
      navigate('/tech/list-medical');
      return;
    }
    if (user.role === 'pharmacist') {
      navigate('/pharmacist/list-medical');
      return;
    }
        if (user.role === 'patient') {
      navigate('/home');
      return;
    }
    // Nếu không khớp role nào ở trên
    navigate('/');
  }, [isLoggedIn, user, navigate]);
  
  return (
    <div className="login-container full-screen">
      <div className='content'>
        <h1 className='text-center my-3'>LOGIN</h1>
        <form onSubmit={handleLogin}>
          <div className='form-group mb-1'>
            <label>Email Đăng nhập</label>
            <input
              type='email'
              required
              className='form-control'
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className='form-group mb-1'>
            <label>Mật khẩu</label>
            <div className='s-password'>
              <input
                type={isShowPassword ? "text" : 'password'}
                required
                className='form-control'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <span onClick={handleShowHidePassword}>
                <i className={isShowPassword ? "fas fa-eye" : "fas fa-eye-slash"}></i>
              </span>
            </div>
          </div>
          {errorMessage && <div className="text-danger mb-2">{errorMessage}</div>}
          <button type='submit' className='bt-login'>Login</button>
          <div className='d-flex justify-content-between align-items-center mt-2'>
            <span>Đăng nhập</span>
            <span>Quên mật khẩu ?</span>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
