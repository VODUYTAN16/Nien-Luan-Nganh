<template>
  <div class="hero-wrapper">
    <!-- Lớp mờ phủ lên ảnh nền -->

    <!-- Lớp hiệu ứng lá -->
    <LeafFall class="leaf-layer" />

    <!-- Nội dung hero -->
    <section class="hero">
      <div class="hero-left">
        <h1>Tạo sinh công thức móc len từ hình ảnh.</h1>
        <p>Tải lên một bức ảnh. Hệ thống sẽ gợi ý mẫu móc len.</p>
        <div class="hero-actions">
          <RouterLink to="/search" class="btn-primary-large">
            Bắt đầu tạo sinh
          </RouterLink>
          <RouterLink to="/patterns" class="ghost-link">
            Xem kho mẫu hiện có →
          </RouterLink>
        </div>
        <div class="hero-meta">
          <span>✓ Tạo sinh theo ảnh</span>
          <span>✓ Tối ưu cho coaster, granny</span>
        </div>
      </div>

      <div class="hero-right">
        <div class="hero-card">
          <div class="hero-label">Hình ảnh mẫu móc minh họa</div>

          <!-- Ảnh đầu vào -->
          <div class="input-preview">
            <img :src="inputImg" alt="input demo" />
            <p class="input-caption">"Những mẫu granny phổ biến"</p>
          </div>

          <!-- Kết quả tương tự -->
          <div class="hero-thumbs">
            <div
              v-for="img in similarImgs"
              :key="img"
              class="thumb"
              :style="{ backgroundImage: `url(${getThumbUrl(img)})` }"
            ></div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import LeafFall from '@/components/LeafFall.vue';

const similarImgs = ['2_R5', '57', '35', '39', '48', '56'];
const inputImg = new URL('../assets/top/25.png', import.meta.url).href;

const getThumbUrl = (name) =>
  new URL(`../assets/top/${name}.png`, import.meta.url).href;
</script>

<style scoped>
/* --- ẢNH NỀN & HIỆU ỨNG MỜ --- */
.hero-wrapper {
  position: relative;
  overflow: hidden;
  min-height: 75vh;
  background: var(--green-light);
}

/* lớp mờ phủ lên nền */
.hero-blur-overlay {
  position: absolute;
  inset: 0;
  backdrop-filter: blur(6px); /* mức độ mờ */
  background-color: rgba(100, 100, 100, 0.08); /* kính mờ nhẹ */
  z-index: 1;
}

/* hiệu ứng lá rơi phủ toàn vùng hero */
.leaf-layer {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
}

/* --- BỐ CỤC CHÍNH HERO --- */
.hero {
  position: relative;
  z-index: 3; /* cao hơn lớp mờ và lá */
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(260px, 1fr);
  gap: 40px;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  color: var(--text-color);
}

/* --- NỘI DUNG BÊN TRÁI --- */
.hero-left h1 {
  font-size: 34px;
  line-height: 1.18;
  font-weight: 600;
  color: var(--text-color);
}

.hero-left p {
  margin-top: 12px;
  font-size: 18px;
  color: var(--second-text-color);
  max-width: 600px;
}

.hero-actions {
  margin-top: 18px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.btn-primary-large {
  padding: 10px 22px;
  border-radius: 999px;
  background: var(--main-color);
  color: var(--white);
  font-size: 14px;
  text-decoration: none;
  box-shadow: var(--box-shadow);
  transition: all 0.18s ease;
}

.btn-primary-large:hover {
  background: var(--green-dark, var(--main-color));
  box-shadow: var(--shadow-strong, var(--box-shadow));
  transform: translateY(-1px);
}

.ghost-link {
  font-size: 13px;
  text-decoration: none;
  color: var(--second-text-color);
  transition: color 0.18s ease;
}

.ghost-link:hover {
  color: var(--main-color);
}

.hero-meta {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 14px;
  color: var(--second-text-color);
}

/* --- CARD BÊN PHẢI --- */
.hero-right {
  display: flex;
  justify-content: flex-end;
}

.hero-card {
  width: 100%;
  max-width: 360px;
  padding: 16px 16px 12px;
  background: var(--white);
  border-radius: 22px;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.06);
  border: var(--border-light);
}

.hero-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--second-text-color);
  margin-bottom: 6px;
}

.input-preview {
  width: 85%;
  margin: 4px auto 8px;
  text-align: center;
}

.input-preview img {
  width: 100%;
  border-radius: 10px;
  object-fit: cover;
}

.input-caption {
  margin-top: 4px;
  font-size: 11px;
  color: var(--second-text-color);
}

.hero-thumbs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  margin-top: 6px;
}

.thumb {
  padding-top: 75%;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  background-color: var(--sub-bg);
}

.hero-note {
  margin-top: 8px;
  font-size: 10px;
  color: var(--second-text-color);
  text-align: center;
}
</style>
