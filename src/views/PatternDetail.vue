<template>
  <div class="page" v-if="pattern">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <RouterLink to="/patterns">Kho mẫu</RouterLink>
      <span>/</span>
      <span>{{ pattern.name }}</span>
    </div>

    <!-- Layout chính -->
    <section class="layout">
      <!-- Cột trái: ảnh top -->
      <div class="left">
        <div class="image-wrap">
          <img :src="withBase(pattern.top_image_url)" :alt="pattern.name" />
          <p class="caption">Ảnh sản phẩm móc len</p>
        </div>
      </div>

      <!-- Cột phải: thông tin chi tiết -->
      <div class="right">
        <h1>Sản phẩm mã - {{ pattern.name }}</h1>

        <div class="meta">
          <span v-if="pattern.type" class="pill">{{ pattern.type }}</span>
          <span v-if="pattern.difficulty" class="pill ghost">
            {{ pattern.difficulty }}
          </span>
          <span v-for="tag in tagList" :key="tag" class="tag">
            #{{ tag }}
          </span>
        </div>

        <p class="desc">
          {{
            pattern.description || 'Mẫu đang chờ được cập nhật mô tả chi tiết.'
          }}
        </p>

        <!-- Ảnh bot nhỏ dưới mô tả + click để phóng to -->
        <div v-if="pattern.bot_image_url" class="bot-image-box">
          <img
            :src="withBase(pattern.bot_image_url)"
            alt="Bot image"
            class="bot-image"
            @click="showModal = true"
          />
          <p class="caption-bot">Ảnh công thức — click để xem lớn</p>
        </div>

        <!-- Nguyên liệu (nếu có) -->
        <div class="block" v-if="pattern.materials || pattern.hook">
          <h3>Nguyên liệu gợi ý</h3>
          <ul>
            <li v-if="pattern.yarn">Len: {{ pattern.yarn }}</li>
            <li v-if="pattern.hook">Kim móc: {{ pattern.hook }}</li>
            <li v-if="pattern.materials">{{ pattern.materials }}</li>
          </ul>
        </div>

        <!-- Link hướng dẫn gốc -->
        <div class="block" v-if="pattern.link">
          <h3>Hướng dẫn chi tiết</h3>
          <a
            class="external"
            :href="pattern.link"
            target="_blank"
            rel="noopener noreferrer"
          >
            Mở pattern / chart gốc →
          </a>
        </div>
      </div>
    </section>

    <!-- Mẫu tương tự: dùng PatternCard, tối đa 10 mẫu, 2 hàng -->
    <section class="related" v-if="related.length">
      <div class="related-header">
        <h3>Mẫu tương tự</h3>
      </div>
      <div class="grid">
        <PatternCard
          v-for="p in related"
          :key="p.id"
          :pattern="p"
          @click="openPattern(p.id)"
        />
      </div>
    </section>

    <!-- Modal phóng to ảnh bot -->
    <transition name="zoom-fade">
      <div
        v-if="showModal"
        class="modal-overlay"
        @click.self="showModal = false"
      >
        <div class="modal-content">
          <button class="close-btn" @click="showModal = false">×</button>
          <img
            :src="withBase(pattern.bot_image_url)"
            alt="Bot image enlarged"
            class="modal-img"
          />
        </div>
      </div>
    </transition>
  </div>

  <div v-else class="page loading">Đang tải mẫu...</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchPatternDetail, fetchPatterns } from '@/service/service';
import PatternCard from '@/components/PatternCard.vue';

const API_BASE = 'http://localhost:8000';
const withBase = (url) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return API_BASE + url;
};

const route = useRoute();
const router = useRouter();

const pattern = ref(null);
const related = ref([]);
const showModal = ref(false);

const tagList = computed(() => {
  if (!pattern.value?.tags) return [];
  if (Array.isArray(pattern.value.tags)) return pattern.value.tags;
  return pattern.value.tags
    .split(/[,\s]+/)
    .map((s) => s.trim())
    .filter(Boolean);
});

const loadPattern = async (id) => {
  if (!id) return;
  try {
    const data = await fetchPatternDetail(id);
    pattern.value = data;

    const all = await fetchPatterns({ type: data.type });
    related.value = all.filter((p) => p.id !== data.id).slice(0, 10);

    showModal.value = false;
  } catch (e) {
    console.error(e);
  }
};

const openPattern = async (id) => {
  if (!id || id === pattern.value?.id) return;
  await router.push(`/patterns/${id}`);
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

onMounted(() => {
  loadPattern(route.params.id);
});

watch(
  () => route.params.id,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      loadPattern(newId);
    }
  }
);
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  font-size: 16px; /* tăng base chữ toàn trang */
}

.loading {
  font-size: 14px; /* 12 -> 14 */
  color: #777;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 12px; /* 10 -> 12 */
  color: #999;
  margin-bottom: 12px;
}
.breadcrumb a {
  text-decoration: none;
  color: #c66b8e;
}

/* Layout chính */
.layout {
  display: grid;
  grid-template-columns: minmax(260px, 380px) minmax(0, 1fr);
  gap: 28px;
}

/* Ảnh top */
.image-wrap {
  width: 100%;
  position: relative;
  border-radius: 22px;
  overflow: hidden;
  background: #f5ece7;
}
.image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.caption {
  position: absolute;
  bottom: 8px;
  left: 10px;
  right: 10px;
  font-size: 12px; /* 10 -> 12 */
  color: #fff;
  background: rgba(0, 0, 0, 0.45);
  padding: 4px 8px;
  border-radius: 8px;
  text-align: center;
}

/* Thông tin bên phải */
.right h1 {
  font-size: 26px; /* 22 -> 26 */
  font-weight: 500;
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}
.pill {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px; /* 9 -> 11 */
  background: #e8a1b6;
  color: #fff;
}
.pill.ghost {
  background: #fff4f7;
  color: #c66b8e;
}
.tag {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px; /* 9 -> 11 */
  background: #f7f4f2;
  color: #666;
}
.desc {
  margin-top: 12px;
  font-size: 15px; /* 12 -> 15 */
  color: #555;
  line-height: 1.5;
}

/* Ảnh bot nhỏ hơn + hover + caption riêng */
.bot-image-box {
  margin-top: 14px;
  text-align: center;
}
.bot-image {
  max-width: 75%;
  border-radius: 16px;
  background: #fffaf8;
  object-fit: contain;
  cursor: zoom-in;
  transition: all 0.2s ease;
}
.bot-image:hover {
  transform: scale(1.03);
}
.caption-bot {
  margin-top: 6px;
  font-size: 12px; /* 10 -> 12 */
  color: #777;
}

/* Block nội dung phụ */
.block {
  margin-top: 18px;
}
.block h3 {
  font-size: 13px; /* 11 -> 13 */
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: #999;
  margin-bottom: 6px;
}
.block ul {
  padding-left: 18px;
  font-size: 13px; /* 11 -> 13 */
  color: #555;
  line-height: 1.5;
}
.external {
  font-size: 13px; /* 11 -> 13 */
  color: #c66b8e;
  text-decoration: none;
}

/* Mẫu tương tự: 2 hàng, tối đa 10 card */
.related {
  margin-top: 32px;
}
.related-header h3 {
  font-size: 17px; /* 14 -> 17 */
}
.grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}
.grid :deep(.pattern-card),
.grid :deep(.card) {
  width: 100%;
}

/* Modal phóng to ảnh bot */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
  padding: 24px;
}
.modal-content {
  position: relative;
  max-width: 95vw;
  max-height: 90vh;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  animation: zoomIn 0.25s ease;
}
.modal-img {
  display: block;
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: 90vh;
  margin: 0 auto;
  object-fit: contain;
}
.close-btn {
  position: absolute;
  top: 8px;
  right: 12px;
  background: transparent;
  border: none;
  font-size: 28px; /* 26 -> 28 */
  color: #777;
  cursor: pointer;
}
.close-btn:hover {
  color: #c66b8e;
}

/* Hiệu ứng modal */
@keyframes zoomIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
.zoom-fade-enter-active,
.zoom-fade-leave-active {
  transition: opacity 0.25s;
}
.zoom-fade-enter-from,
.zoom-fade-leave-to {
  opacity: 0;
}
</style>
