<script setup>
import Navigation from '../components/Navigation.vue';
import RegisterOrLogin from '../components/RegisterOrLogin.vue';
import { ref } from 'vue';
import { onMounted } from 'vue';
import { _fetch_current_account } from '@/service/service';

const role = ref('');
const isAuthenticated = ref(false);
onMounted(async () => {
  try {
    const token = localStorage.getItem('token');
    if (token) {
      const res = await _fetch_current_account();
      console.log(res);
      role.value = res.role;
      console.log(res);
      isAuthenticated.value = true;
    }
  } catch (error) {
    console.log(error);
    console.warn('Token hết hạn hoặc không hợp lệ:', error.response?.status);
    isAuthenticated.value = false;
  }
});
</script>

<template>
  <main style="overflow-x: hidden">
    <div v-if="isAuthenticated">
      <div style="position: relative" class="d-flex">
        <div class="p-0 m-0"><Navigation :role="role"></Navigation></div>
        <div
          class="p-0 m-0"
          style="
            overflow-y: scroll !important;
            max-height: 100vh;
            width: 100%;
            max-width: 100vw;
          "
        >
          <!-- <div class="box"></div> -->

          <router-view></router-view>
        </div>
      </div>
    </div>
    <div v-else>
      <RegisterOrLogin></RegisterOrLogin>
    </div>
  </main>
</template>

<style scoped>
.row {
  background-color: var(--white);
}

main {
  position: relative;
}

.box {
  z-index: -10;
  position: absolute;
  top: 0;
  width: 100%;
  height: 95vh;
  border-end-start-radius: 50px;
  background-color: var(--sub-bg);
  transform: translateY(-100%);
  animation: slideDown 0.8s ease-out forwards;
}

@keyframes slideDown {
  to {
    transform: translateY(0);
  }
}
</style>
