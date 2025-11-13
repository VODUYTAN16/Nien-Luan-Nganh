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
  background: var(--bg-color);
}

.card {
  width: 100%;
  max-width: 360px;
  padding: 20px 20px 16px;
  border-radius: 22px;
  background: var(--white);
  box-shadow: var(--shadow-strong, 0 18px 48px rgba(0, 0, 0, 0.08));
  border: var(--border-light, 1px solid rgba(0, 0, 0, 0.02));
}

h1 {
  font-size: 18px;
  font-weight: 500;
  color: var(--text-color);
}

.subtitle {
  margin-top: 4px;
  font-size: 11px;
  color: var(--second-text-color);
}

/* Tabs */
.tabs {
  display: inline-flex;
  margin-top: 12px;
  padding: 3px;
  border-radius: 999px;
  background: var(--sub-bg);
  gap: 3px;
}

.tab {
  padding: 5px 14px;
  border-radius: 999px;
  border: none;
  font-size: 10px;
  cursor: pointer;
  background: transparent;
  color: var(--second-text-color);
  transition: all 0.16s ease;
}

.tab.active {
  background: var(--white);
  color: var(--main-color);
  box-shadow: var(--box-shadow, 0 4px 10px rgba(0, 0, 0, 0.06));
}

/* Form */
form {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label span {
  display: block;
  font-size: 9px;
  color: var(--second-text-color);
  margin-bottom: 2px;
}

input {
  width: 100%;
  padding: 7px 10px;
  border-radius: 12px;
  border: var(--border-light, 1px solid rgba(0, 0, 0, 0.08));
  font-size: 11px;
  background: var(--white);
  color: var(--text-color);
  outline: none;
  transition:
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

input:focus {
  border-color: var(--main-color);
  box-shadow: 0 0 0 2px rgba(95, 191, 143, 0.12);
}

/* Button */
.btn-primary {
  margin-top: 6px;
  width: 100%;
  padding: 8px 0;
  border-radius: 999px;
  border: none;
  background: var(--main-color);
  color: var(--white);
  font-size: 11px;
  cursor: pointer;
  box-shadow: var(--box-shadow, 0 10px 26px rgba(0, 0, 0, 0.16));
  transition: all 0.18s ease;
}

.btn-primary:hover {
  background: var(--green-dark, var(--main-color));
  box-shadow: var(--shadow-strong, var(--box-shadow));
  transform: translateY(-1px);
}

/* Hint */
.hint {
  margin-top: 8px;
  font-size: 9px;
  color: var(--second-text-color);
  text-align: center;
}
</style>
