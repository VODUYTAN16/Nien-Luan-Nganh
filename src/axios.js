// src/axios.js
import axios from 'axios';
import router from './router';

const api = axios.create({
  baseURL: 'http://localhost:3000',
  headers: {
    'Content-Type': 'application/json',
    // Thêm các headers khác nếu cần
  },
  withCredentials: true,
});

// Gắn token vào tất cả request nếu có
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  console.log(token);

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Xử lý khi có lỗi từ server
// api.interceptors.response.use(
//   (response) => response,
//   (error) => {
//     if (error.response?.status === 403 || error.response?.status === 401) {
//       console.warn('Token hết hạn hoặc không hợp lệ');

//       // Xoá token cũ (nếu cần)
//       localStorage.removeItem('token');

//       // Chuyển hướng đến trang đăng nhập
//       router.push('/login');
//     }

//     return Promise.reject(error);
//   }
// );

export default api;
