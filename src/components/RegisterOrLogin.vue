<template>
  <div
    class="auth-container row g-5 d-flex justify-content-center align-items-center"
  >
    <LeafFall></LeafFall>
    <div class="col m-5" style="max-width: 700px">
      <img src="../assets/Education-bro.svg" alt="" />
    </div>
    <div class="card p-4 shadow col mb-5">
      <div class="d-flex justify-content-center mb-3">
        <h4 v-if="isLogin"><strong>SIGN IN</strong></h4>
        <h4 v-else><strong>SIGN UP</strong></h4>
      </div>

      <form @submit.prevent="isLogin ? submitLogin() : submitRegister()">
        <!-- Loại tài khoản -->
        <div class="mb-3" v-if="isLogin">
          <label class="form-label">Type Of Account</label>
          <select v-model="userType" class="form-select">
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <!-- Form đăng nhập -->
        <template v-if="isLogin">
          <div class="mb-3">
            <label class="form-label">Phone Number</label>
            <input
              v-model.trim="loginForm.dienthoai"
              type="text"
              class="form-control"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Password</label>
            <input
              v-model="loginForm.matkhau"
              type="password"
              class="form-control"
              required
            />
          </div>
        </template>

        <!-- Form đăng ký -->
        <template v-else>
          <div class="row">
            <div class="col">
              <div class="mb-3">
                <label class="form-label">Middle Name</label>
                <input
                  v-model.trim="registerForm.holot"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">First Name</label>
                <input
                  v-model.trim="registerForm.ten"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Date of Birth</label>
                <input
                  v-model="registerForm.ngaysinh"
                  type="date"
                  class="form-control"
                  required
                />
              </div>
              <div class="mb-3">
                <label class="form-label">Gender</label>
                <select
                  v-model="registerForm.phai"
                  class="form-select"
                  required
                >
                  <option value="">-- Select Gender --</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </select>
              </div>
            </div>

            <div class="col">
              <div class="mb-3">
                <label class="form-label">Address</label>
                <input
                  v-model.trim="registerForm.diachi"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Phone Number</label>
                <input
                  v-model.trim="registerForm.dienthoai"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Password</label>
                <input
                  v-model="registerForm.matkhau"
                  type="password"
                  class="form-control"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Confirm Password</label>
                <input
                  v-model="registerForm.xacnhanmatkhau"
                  type="password"
                  class="form-control"
                  required
                />
              </div>
            </div>
          </div>
        </template>

        <div class="form-check mb-3" v-if="!isLogin">
          <input type="checkbox" class="form-check-input" id="terms" required />
          <label class="form-check-label" for="terms">
            I agree to the
            <a href="#" class="text-decoration-none">terms of service</a> and
            <a href="#" class="text-decoration-none">privacy policy</a>.
          </label>
        </div>

        <button
          type="submit"
          class="btn btn-primary w-100 btn-gradient"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm"></span>
          <span v-else>{{ isLogin ? 'Sign In' : 'Sign Up' }}</span>
        </button>
        <p class="text-center">
          {{ isLogin ? "Don't have an account?" : 'Already have an account?' }}
          <a href="#" class="text-decoration-none" @click="toggleForm">
            {{ isLogin ? 'Sign Up' : 'Sign In' }}
          </a>
        </p>

        <!-- Thông báo -->
        <div
          v-if="message"
          :class="[
            'mt-3',
            'alert',
            messageType === 'success' ? 'alert-success' : 'alert-danger',
          ]"
        >
          {{ message }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import LeafFall from './LeafFall.vue';
import { ref } from 'vue';
import api from '../axios';
import { _register } from '../service/service';

const isLogin = ref(true);
const userType = ref('user');
const loading = ref(false);
const message = ref('');
const messageType = ref('');

const loginForm = ref({
  dienthoai: '',
  matkhau: '',
});

const registerForm = ref({
  madocgia: '',
  holot: '',
  ten: '',
  ngaysinh: '',
  phai: '',
  diachi: '',
  dienthoai: '',
  matkhau: '',
  xacnhanmatkhau: '',
});

const clearForm = () => {
  loginForm.value = {
    dienthoai: '',
    matkhau: '',
  };
  registerForm.value = {
    madocgia: '',
    holot: '',
    ten: '',
    ngaysinh: '',
    phai: '',
    diachi: '',
    dienthoai: '',
    matkhau: '',
    xacnhanmatkhau: '',
  };
};

const submitLogin = async () => {
  loading.value = true;
  message.value = '';

  try {
    const endpoint =
      userType.value === 'user' ? '/api/auth/login' : '/api/auth/login-admin';

    const res = await api.post(endpoint, loginForm.value);
    if (res.data.status == 401) {
      alert(res.data.message);
    }
    console.log(res);
    localStorage.setItem('token', res.data.token);
    messageType.value = 'success';
    message.value = 'Đăng nhập thành công';

    // Chuyển hướng nếu muốn
    window.location.href = '/';
  } catch (err) {
    messageType.value = 'error';
    message.value = 'Đăng nhập thất bại. Kiểm tra lại thông tin.';
  } finally {
    loading.value = false;
  }
};

const submitRegister = async () => {
  loading.value = true;
  message.value = '';
  try {
    if (registerForm.value.matkhau !== registerForm.value.xacnhanmatkhau) {
      alert('Passwords do not match.');
      return;
    }

    const res = await _register(registerForm.value, 'user');
    console.log(res);
    if (res.status != 200) {
      alert(res.message);
      messageType.value = 'error';
      message.value = res.message;
    } else {
      messageType.value = 'success';
      message.value = 'Registration successful! Please log in.';
      isLogin.value = true;
    }
  } catch (err) {
    messageType.value = 'error';
    message.value = 'Registration failed. Please check your information.';
  } finally {
    loading.value = false;
  }
};

const toggleForm = () => {
  isLogin.value = !isLogin.value;
  clearForm();
};
</script>

<style scoped>
.btn-gradient {
  background: linear-gradient(135deg, #4f46e5, #ec4899);
  color: white;
  border: none;
  border-radius: 2rem;
  transition: all 0.3s ease;
}

.btn-gradient:hover {
  transform: scale(1.05);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.2);
}
.auth-container {
  margin: auto;
  overflow: hidden;
  height: 100vh;
  background-color: #fff2cc !important;
}
.card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border: 1px solid #fff;
  border-radius: 10px;
  max-width: 500px;
  max-height: fit-content;
  z-index: 100;
}
</style>
