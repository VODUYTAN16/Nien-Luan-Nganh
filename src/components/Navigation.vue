<template>
  <div class="d-flex">
    <!-- Nút toggle -->
    <button
      class="btn btn-outline-secondary toggle-btn d-md-none m-3"
      @click="toggleMenu"
    >
      <i class="fas fa-bars"></i>
    </button>

    <!-- Sidebar -->
    <div
      class="d-flex flex-column flex-shrink-0 text-white navigation"
      :class="{ collapsed: !menuVisible }"
    >
      <h5 class="text-dark fw-bold mb-4 px-3">THE BOOKS</h5>

      <ul class="nav nav-pills flex-column mb-auto">
        <li class="nav-item">
          <router-link
            to="/"
            active-class="active"
            class="nav-link d-flex align-items-center text-dark"
          >
            <i class="fa-solid fa-house me-2 p-2"></i> <span>Discover</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link
            to="/category"
            active-class="active"
            class="nav-link d-flex align-items-center text-dark"
          >
            <i class="bx bxs-grid-circle me-2 p-2"></i> <span>Category</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link
            to="/borrowed"
            active-class="active"
            class="nav-link d-flex align-items-center text-dark"
          >
            <i class="fa-regular fa-handshake me-2 p-2"></i>
            <span>Borrowed</span>
          </router-link>
        </li>
        <li class="nav-item" v-if="role === 'admin'">
          <router-link
            to="/books-management"
            active-class="active"
            class="nav-link d-flex align-items-center text-dark"
          >
            <i class="bx bx-book-add me-2 p-2"></i>
            <span>Books Management</span>
          </router-link>
        </li>
        <li class="nav-item" v-if="role === 'admin'">
          <router-link
            to="/account"
            active-class="active"
            class="nav-link d-flex align-items-center text-dark"
          >
            <i class="bx bx-contact-book me-2 p-2"></i>
            <span>Account Management</span>
          </router-link>
        </li>
      </ul>

      <hr />
      <div class="d-flex flex-column gap-2">
        <a href="#" class="custom-nav-link">
          <i class="bi bi-gear-fill"></i> <span>Setting</span>
        </a>
        <a href="#" class="custom-nav-link">
          <i class="bi bi-question-circle-fill"></i> <span>Help</span>
        </a>
        <a @click="_logout" class="custom-nav-link">
          <i class="bi bi-box-arrow-right"></i> <span>Log out</span>
        </a>
        <div class="d-flex justify-content-end">
          <a
            href="#"
            v-if="menuVisible"
            class="custom-nav-link"
            @click="menuVisible = false"
          >
            <i class="bx bx-chevrons-left"></i>
          </a>
          <a
            href="#"
            v-if="!menuVisible"
            class="custom-nav-link"
            @click="menuVisible = true"
          >
            <i class="bx bx-chevrons-right"></i>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const prep = defineProps({ role: {} });

const menuVisible = ref(true); // trạng thái hiển thị menu

const toggleMenu = () => {
  menuVisible.value = !menuVisible.value;
};

const _logout = () => {
  if (!confirm('Do you want to log out?')) return;
  localStorage.removeItem('token');
  location.reload();
};
</script>

<style scoped>
.nav-link:hover {
  background-color: #eaeaea;
  border-radius: 8px;
}
.nav-link.active {
  background-color: transparent; /* Màu nền xanh */
  font-weight: bold;
}
.nav-link.active i {
  background-color: var(--organge);
  border-radius: 10px;
  color: white;
}

i {
  font-size: 20px;
}

.navigation {
  width: 250px;
  transition:
    width 0.3s ease,
    padding 0.3s ease;
  padding: 1rem;
  height: 100vh;
  background-color: var(--white);
  overflow: hidden;
}

.navigation.collapsed {
  width: 80px;
  padding: 1rem 0.5rem;
}

.navigation h5,
.navigation .nav-link span,
.navigation .custom-nav-link span {
  display: inline-block;
  opacity: 1;
  transition: opacity 0.3s ease;
}

.navigation.collapsed h5,
.navigation.collapsed .nav-link span,
.navigation.collapsed .custom-nav-link span {
  opacity: 0;
  width: 0;
  transition:
    opacity 0.2s ease,
    width 0.2s ease;
  overflow: hidden;
  display: inline-block;
}

.custom-nav-link {
  background-color: transparent;
  border: none;
  color: #343a40; /* text-dark */
  transition:
    background-color 0.3s,
    color 0.3s;
  border-radius: 0.375rem;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  text-decoration: none;
}

.custom-nav-link:hover {
  background-color: #e9ecef; /* Màu xám nhạt khi hover */
  color: #0d6efd; /* text-primary */
}

.custom-nav-link i {
  margin-right: 0.5rem;
  transition: color 0.3s;
}

.custom-nav-link:hover i {
  color: #0d6efd; /* icon cũng chuyển sang màu primary */
}
</style>
