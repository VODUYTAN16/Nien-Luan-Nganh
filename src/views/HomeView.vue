<template>
  <div class="hero-wrapper">
    <!-- Lớp hiệu ứng lá -->
    <LeafFall class="leaf-layer" />

    <!-- Nội dung hero -->
    <section class="hero">
      <div class="hero-left">
        <h1>Biến ý tưởng len thành mẫu móc cụ thể.</h1>
        <p>
          Tải lên một bức ảnh, hay gõ vài dòng mô tả. Hệ thống sẽ gợi ý mẫu móc
          len, chart, màu sắc và độ khó phù hợp, dựa trên CSDL mẫu của bạn.
        </p>
        <div class="hero-actions">
          <RouterLink to="/search" class="btn-primary-large">
            Bắt đầu từ ảnh / text
          </RouterLink>
          <RouterLink to="/patterns" class="ghost-link">
            Xem kho mẫu hiện có →
          </RouterLink>
        </div>
        <div class="hero-meta">
          <span>✓ Tìm kiếm theo ảnh</span>
          <span>✓ Tối ưu cho coaster, túi, plushies</span>
          <span>✓ Tinh chỉnh model trực tiếp</span>
        </div>
      </div>

      <div class="hero-right">
        <div class="hero-card">
          <div class="hero-label">Demo gợi ý</div>

          <!-- Ảnh đầu vào -->
          <div class="input-preview">
            <img :src="inputImg" alt="input demo" />
            <p class="input-caption">"Hoa năm cánh"</p>
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

          <div class="hero-note">Top 6 kết quả tương tự từ CLIP-Image.</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import LeafFall from '@/components/LeafFall.vue';

const similarImgs = ['0385', '0383', '0379', '0325', '0309', '0076'];

// dùng đường dẫn tương đối từ file component (ổn định cho Vite)
const inputImg = new URL('../assets/top/0384.jpg', import.meta.url).href;
const getThumbUrl = (name) =>
  new URL(`../assets/top/${name}.jpg`, import.meta.url).href;
</script>

<style scoped>
.hero-wrapper {
  position: relative;
  overflow: hidden;
  min-height: 75vh;
}

/* hiệu ứng lá rơi phủ toàn vùng hero */
.leaf-layer {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

/* nội dung hero */
.hero {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(260px, 1fr);
  gap: 40px;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 0;
}

.hero-left h1 {
  font-size: 34px;
  line-height: 1.18;
  font-weight: 600;
}

.hero-left p {
  margin-top: 12px;
  font-size: 14px;
  color: #555;
  max-width: 460px;
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
  background: #e8a1b6;
  color: #fff;
  font-size: 13px;
  text-decoration: none;
  box-shadow: 0 8px 24px rgba(232, 161, 182, 0.32);
}

.ghost-link {
  font-size: 12px;
  text-decoration: none;
  color: #666;
}

.hero-meta {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 11px;
  color: #777;
}

/* card bên phải */
.hero-right {
  display: flex;
  justify-content: flex-end;
}

.hero-card {
  width: 100%;
  max-width: 360px; /* to hơn một chút */
  padding: 16px 16px 12px;
  background: #ffffff;
  border-radius: 22px;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.02);
}

.hero-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #999;
  margin-bottom: 6px;
}

/* ảnh input demo to hơn một chút */
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
  color: #444;
}

/* lưới ảnh kết quả: thumbnail to hơn */
.hero-thumbs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  margin-top: 6px;
}

.thumb {
  padding-top: 75%; /* tăng chiều cao */
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  background-color: #f5f5f5;
}

.hero-note {
  margin-top: 8px;
  font-size: 10px;
  color: #888;
  text-align: center;
}
</style>
