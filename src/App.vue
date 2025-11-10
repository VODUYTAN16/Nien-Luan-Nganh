<template>
  <div class="app-root">
    <header class="app-header">
      <!-- Logo -->
      <div class="logo" @click="goHome">
        <img class="logo-icon" src="@/assets/logo.png" alt="logo" />
        <div class="logo-text">
          <div class="logo-title">CrochetLens</div>
          <div class="logo-sub">Gợi ý mẫu từ ảnh & mô tả</div>
        </div>
      </div>

      <!-- Nav -->
      <nav class="nav-links">
        <RouterLink to="/" exact-active-class="active-link"
          >Trang chủ</RouterLink
        >
        <RouterLink to="/search" active-class="active-link"
          >Tìm theo ảnh / text</RouterLink
        >
        <RouterLink to="/patterns" active-class="active-link"
          >Kho mẫu</RouterLink
        >
        <RouterLink to="/models" active-class="active-link"
          >Model Lab</RouterLink
        >
      </nav>

      <!-- Auth / Actions -->
      <div class="nav-actions">
        <template v-if="isLoggedIn">
          <div class="user-pill">
            <span class="user-dot"></span>
            <span class="user-name">{{ userLabel }}</span>
          </div>
          <button class="btn-outline" @click="logout">Đăng xuất</button>
        </template>

        <template v-else>
          <RouterLink to="/auth" class="btn-outline">Đăng nhập</RouterLink>
          <RouterLink to="/search" class="btn-primary">Bắt đầu</RouterLink>
        </template>
      </div>
    </header>

    <main class="app-main">
      <RouterView />
    </main>

    <footer class="app-footer">
      <span>CrochetLens • Gợi ý mẫu coaster từ ảnh & mô tả</span>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Đọc token từ localStorage (đơn giản cho đồ án)
const accessToken = computed(() => localStorage.getItem('access_token'));
const isLoggedIn = computed(() => !!accessToken.value);

// Hiển thị tên ngắn gọn từ email nếu có
const userLabel = computed(() => {
  const email = localStorage.getItem('user_email');
  if (!email) return 'Đã đăng nhập';
  const name = email.split('@')[0];
  return name.length > 18 ? name.slice(0, 18) + '...' : name;
});

function goHome() {
  router.push('/');
}

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_email');
  router.push('/');
}
</script>

<style scoped>
.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #faf7f5;
  color: #222;
  font-family:
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'SF Pro',
    sans-serif;
  font-size: 16px; /* tăng base cho toàn layout */
}

/* HEADER */

.app-header {
  position: sticky;
  top: 0;
  z-index: 40;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 44px;
  backdrop-filter: blur(18px);
  background: rgba(250, 247, 245, 0.94);
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.logo-icon {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  object-fit: contain;
  background: linear-gradient(135deg, #ffe4ec, #f7f0ff);
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-weight: 600;
  font-size: 19px; /* 17 -> 19 */
  letter-spacing: 0.02em;
}

.logo-sub {
  font-size: 12px; /* 11 -> 12 */
  opacity: 0.7;
}

/* NAV LINKS */

.nav-links {
  display: flex;
  gap: 20px;
  font-size: 15px; /* 14 -> 15 */
}

.nav-links a {
  text-decoration: none;
  color: #444;
  padding: 7px 0;
  position: relative;
  transition: color 0.18s ease;
}

.nav-links a:hover {
  color: #111;
}

.nav-links a.router-link-active::after,
.nav-links a.active-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -4px;
  width: 20px;
  height: 2px;
  border-radius: 999px;
  background: #e8a1b6;
}

/* ACTIONS */

.nav-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-outline,
.btn-primary {
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 13px; /* 12 -> 13 */
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  cursor: pointer;
  background: transparent;
}

.btn-outline {
  color: #555;
}

.btn-outline:hover {
  background: rgba(0, 0, 0, 0.02);
}

.btn-primary {
  background: #e8a1b6;
  color: #fff;
  border: none;
  box-shadow: 0 6px 14px rgba(232, 161, 182, 0.32);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(232, 161, 182, 0.36);
}

/* USER PILL */

.user-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 11px;
  border-radius: 999px;
  background: #fff7fb;
  border: 1px solid rgba(0, 0, 0, 0.04);
  font-size: 12px; /* 11 -> 12 */
  color: #444;
}

.user-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #38c172;
}

.user-name {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* MAIN + FOOTER */

.app-main {
  flex: 1;
  padding: 26px 44px 34px;
  font-size: 1rem; /* bám theo base 16px */
}

.app-footer {
  padding: 16px 44px 22px;
  font-size: 12px; /* 11 -> 12 */
  color: rgba(0, 0, 0, 0.42);
}
</style>
