<template>
  <div class="app-root">
    <!-- HEADER -->
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
        <RouterLink to="/" exact-active-class="active-link">
          Trang chủ
        </RouterLink>
        <RouterLink to="/search" active-class="active-link">
          Tìm theo ảnh / text
        </RouterLink>
        <RouterLink to="/patterns" active-class="active-link">
          Kho mẫu
        </RouterLink>
        <RouterLink to="/models" active-class="active-link">
          Không gian embedding
        </RouterLink>
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
          <!-- <RouterLink to="/auth" class="btn-outline">Đăng nhập</RouterLink> -->
          <RouterLink to="/search" class="btn-primary">Bắt đầu</RouterLink>
        </template>
      </div>
    </header>

    <!-- MAIN -->
    <main class="app-main">
      <RouterView v-slot="{ Component, route }">
        <!-- Cache các view có meta.keepAlive (ví dụ SearchView) -->
        <KeepAlive>
          <component v-if="route.meta.keepAlive" :is="Component" />
        </KeepAlive>

        <!-- Các view khác render bình thường -->
        <component v-if="!route.meta.keepAlive" :is="Component" />
      </RouterView>
    </main>

    <!-- FOOTER -->
    <footer class="app-footer">
      <span>CrochetLens • Gợi ý mẫu coaster từ ảnh & mô tả</span>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter, RouterView, RouterLink } from 'vue-router';

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
  background: var(--bg-color);
  color: var(--text-color);
  font-family:
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    'SF Pro',
    sans-serif;
  font-size: 16px;
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
  background: var(--bg-color);
  border-bottom: var(--border-light);
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
  border: var(--border-light);
  object-fit: contain;
  background: var(--green-gradient);
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-weight: 600;
  font-size: 19px;
  letter-spacing: 0.02em;
  color: var(--text-color);
}

.logo-sub {
  font-size: 12px;
  opacity: 0.7;
  color: var(--text-sub);
}

/* NAV LINKS */
.nav-links {
  display: flex;
  gap: 20px;
  font-size: 15px;
}

.nav-links a {
  text-decoration: none;
  color: var(--text-color);
  padding: 7px 0;
  position: relative;
  transition: color 0.18s ease;
}

.nav-links a:hover {
  color: var(--text-sub);
}

.nav-links a.router-link-active::after,
.nav-links a.active-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -4px;
  width: 22px;
  height: 2px;
  border-radius: 999px;
  background: var(--main-color);
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
  font-size: 13px;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: var(--border-light);
  cursor: pointer;
  background: transparent;
  transition: all 0.18s ease;
}

.btn-outline {
  color: var(--text-sub);
}

.btn-outline:hover {
  background: rgba(95, 191, 143, 0.06);
  border-color: var(--green-border);
}

.btn-primary {
  background: var(--main-color);
  color: var(--white);
  border: none;
  box-shadow: var(--shadow-soft);
}

.btn-primary:hover {
  background: var(--green-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-strong);
}

/* USER PILL */
.user-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 11px;
  border-radius: 999px;
  background: var(--sub-bg);
  border: var(--border-light);
  font-size: 12px;
  color: var(--text-color);
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
  font-size: 1rem;
}

.app-footer {
  padding: 16px 44px 22px;
  font-size: 12px;
  color: rgba(27, 46, 36, 0.45);
}
</style>
