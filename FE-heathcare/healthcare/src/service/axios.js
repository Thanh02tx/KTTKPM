// // src/services/axios.js

// import axios from 'axios';

// const api = axios.create({
//   baseURL: '', 
//   timeout: 10000,
//   headers: {
//     'Content-Type': 'application/json',
//   },
// });
                                                
// api.interceptors.request.use(
//   (config) => {
//     const token = localStorage.getItem('token');
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`;
//     }
//     return config;
//   },
//   (error) => Promise.reject(error)
// );

// // ✅ Interceptor cho response
// api.interceptors.response.use(
//   (response) => response.data,
//   (error) => {
//     // Gọn gàng hơn: không in ra lỗi Axios xấu xí
//     if (error.response) {
//       // Trả lỗi rõ ràng để xử lý ở component
//       return Promise.reject(error.response.data);
//     }

//     // Lỗi ngoài tầm (mất mạng, timeout, ...)
//     return Promise.reject({ message: "Lỗi kết nối đến server" });
//   }
// );

// export default api;
// src/services/axios.js
// import axios from 'axios';

// const api = axios.create({
//   baseURL: '', 
//   timeout: 10000,
//   headers: {
//     // Xóa 'Content-Type' để nó tự động điều chỉnh khi gửi FormData
//     // 'Content-Type': 'application/json',
//   },
// });

// api.interceptors.request.use(
//   (config) => {
//     const token = localStorage.getItem('token');
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`;
//     }

//     // Nếu có FormData, axios sẽ tự động thêm Content-Type là 'multipart/form-data'
//     if (config.data instanceof FormData) {
//       delete config.headers['Content-Type'];
//     }
    
//     return config;
//   },
//   (error) => Promise.reject(error)
// );

// // ✅ Interceptor cho response
// api.interceptors.response.use(
//   (response) => response.data,
//   (error) => {
//     // Gọn gàng hơn: không in ra lỗi Axios xấu xí
//     if (error.response) {
//       // Trả lỗi rõ ràng để xử lý ở component
//       return Promise.reject(error.response.data);
//     }

//     // Lỗi ngoài tầm (mất mạng, timeout, ...)
//     return Promise.reject({ message: "Lỗi kết nối đến server" });
//   }
// );

// export default api;
import axios from 'axios';

const baseConfig = {
  baseURL: '',
  timeout: 10000,
};

// --- API mặc định: trả về response.data ---
const api = axios.create(baseConfig);
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  if (config.data instanceof FormData) delete config.headers['Content-Type'];
  return config;
});
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) return Promise.reject(error.response.data);
    return Promise.reject({ message: 'Lỗi kết nối đến server' });
  }
);

// --- API giữ nguyên toàn bộ response (dành cho blob, headers, status...) ---
const apiRaw = axios.create(baseConfig);
apiRaw.interceptors.request.use(api.interceptors.request.handlers[0].fulfilled);
apiRaw.interceptors.response.use(
  (response) => response, // giữ nguyên toàn bộ response
  (error) => {
    if (error.response) return Promise.reject(error.response);
    return Promise.reject({ message: 'Lỗi kết nối đến server' });
  }
);

// ✅ Export mặc định là api (giữ nguyên import cũ), export thêm apiRaw
export default api;
export { apiRaw };

