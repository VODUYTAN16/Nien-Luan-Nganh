<template>
  <div class="wrap">
    <div class="card">
      <h1>CrochetLens Studio</h1>
      <p class="subtitle">
        Đăng nhập để quản lý kho mẫu, cấu hình model và theo dõi log truy vấn.
      </p>

      <div class="tabs">
        <button
          :class="['tab', { active: mode === 'login' }]"
          @click="mode = 'login'"
        >
          Đăng nhập
        </button>
        <button
          :class="['tab', { active: mode === 'register' }]"
          @click="mode = 'register'"
        >
          Tạo tài khoản
        </button>
      </div>

      <form @submit.prevent="submit">
        <label>
          <span>Email</span>
          <input
            v-model="email"
            type="email"
            required
            placeholder="you@example.com"
          />
        </label>

        <label>
          <span>Mật khẩu</span>
          <input
            v-model="password"
            type="password"
            required
            minlength="6"
            placeholder="Tối thiểu 6 ký tự"
          />
        </label>

        <label v-if="mode === 'register'">
          <span>Tên hiển thị</span>
          <input v-model="name" type="text" placeholder="Studio / tên bạn" />
        </label>

        <button type="submit" class="btn-primary">
          {{ mode === 'login' ? 'Đăng nhập' : 'Đăng ký' }}
        </button>
      </form>

      <p class="hint">
        Với người dùng nội bộ, có thể bỏ qua bước này hoặc dùng SSO sau.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { login, register } from '../service/service';

const mode = ref('login');
const email = ref('');
const password = ref('');
const name = ref('');
const error = ref('');

async function submit() {
  error.value = '';
  try {
    if (mode.value === 'login') {
      await login({ email: email.value, password: password.value });
      // TODO: điều hướng vào trang admin hoặc home
    } else {
      await register({
        email: email.value,
        password: password.value,
        display_name: name.value,
      });
      mode.value = 'login';
    }
  } catch (e) {
    console.error(e);
    error.value = e.response?.data?.detail || 'Có lỗi xảy ra';
  }
}
</script>

<style scoped>
.wrap {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.card {
  width: 100%;
  max-width: 360px;
  padding: 20px 20px 16px;
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.02);
}
h1 {
  font-size: 18px;
  font-weight: 500;
}
.subtitle {
  margin-top: 4px;
  font-size: 11px;
  color: #666;
}
.tabs {
  display: inline-flex;
  margin-top: 12px;
  padding: 3px;
  border-radius: 999px;
  background: #f7f4f2;
  gap: 3px;
}
.tab {
  padding: 5px 14px;
  border-radius: 999px;
  border: none;
  font-size: 10px;
  cursor: pointer;
  background: transparent;
  color: #777;
}
.tab.active {
  background: #fff;
  color: #c66b8e;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
}
form {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
label span {
  display: block;
  font-size: 9px;
  color: #888;
  margin-bottom: 2px;
}
input {
  width: 100%;
  padding: 7px 10px;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 11px;
  background: #fff;
}
.btn-primary {
  margin-top: 6px;
  width: 100%;
  padding: 8px 0;
  border-radius: 999px;
  border: none;
  background: #e8a1b6;
  color: #fff;
  font-size: 11px;
  cursor: pointer;
  box-shadow: 0 10px 26px rgba(232, 161, 182, 0.34);
}
.hint {
  margin-top: 8px;
  font-size: 9px;
  color: #aaa;
  text-align: center;
}
</style>
