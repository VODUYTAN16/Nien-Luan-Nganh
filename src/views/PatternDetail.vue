<template>
  <div class="page" v-if="pattern">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <RouterLink to="/patterns">Kho mẫu</RouterLink>
      <span>/</span>
      <span>{{ pattern.image_name || pattern.name }}</span>
    </div>

    <!-- Layout chính -->
    <section class="layout">
      <!-- Cột trái: ảnh -->
      <div class="left">
        <div class="image-wrap">
          <img :src="imageUrl" :alt="pattern.image_name" />
          <p class="caption">Ảnh sản phẩm móc len</p>
        </div>
      </div>

      <!-- Cột phải: thông tin chi tiết -->
      <div class="right">
        <h1>
          Sản phẩm mã -
          {{ pattern.image_name?.replace(/\.(jpg|jpeg|png)$/i, '') }}
        </h1>

        <div class="meta">
          <span class="pill">coaster/granny</span>
        </div>

        <!-- Công thức pattern (đã được chuyển thành chữ thường) -->
        <div class="pattern-content">
          <h3>📝 Công thức</h3>
          <div class="pattern-text">{{ formattedPattern }}</div>
        </div>

        <!-- Nút copy pattern -->
        <div class="copy-btn-container" v-if="pattern.pattern">
          <button @click="copyPattern" class="copy-btn">
            📋 Sao chép công thức
          </button>
        </div>

        <!-- Nguồn (Link) -->
        <div class="block" v-if="pattern.Link || pattern.link">
          <h3>🔗 Nguồn tham khảo</h3>
          <a
            class="external"
            :href="pattern.Link || pattern.link"
            target="_blank"
            rel="noopener noreferrer"
          >
            Mở link gốc →
          </a>
        </div>
      </div>
    </section>

    <!-- Mẫu tương tự -->
    <section class="related" v-if="related.length">
      <div class="related-header">
        <h3>Mẫu tương tự</h3>
      </div>
      <div class="grid">
        <PatternCard
          v-for="p in related"
          :key="p.image_name"
          :pattern="p"
          @click="openPattern(p.image_name)"
        />
      </div>
    </section>
  </div>

  <div v-else class="page loading">Đang tải mẫu...</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  getPatternByImageName,
  getAllPatterns,
  getPatternImageUrl,
} from '@/service/service';
import PatternCard from '@/components/PatternCard.vue';

const route = useRoute();
const router = useRouter();

const pattern = ref(null);
const related = ref([]);

// Computed: Pattern đã được xử lý (chữ thường)
const formattedPattern = computed(() => {
  if (!pattern.value?.pattern) return 'Chưa có công thức';

  let text = pattern.value.pattern;

  // Chuyển toàn bộ về chữ thường
  text = text.toLowerCase();

  // Optional: Giữ nguyên chữ hoa cho từ đầu tiên của mỗi câu
  // text = text.replace(/(^\s*|[.!?]\s+)([a-z])/g, (match, separator, letter) => {
  //   return separator + letter.toUpperCase();
  // });

  return text;
});

// Lấy URL ảnh
const imageUrl = computed(() => {
  if (!pattern.value?.image_name) return '';
  return getPatternImageUrl(pattern.value.image_name);
});

// Copy pattern vào clipboard
const copyPattern = async () => {
  if (!pattern.value?.pattern) return;

  try {
    await navigator.clipboard.writeText(formattedPattern.value);
    alert('✅ Đã sao chép công thức vào clipboard!');
  } catch (err) {
    console.error('Lỗi khi copy:', err);
    alert('❌ Không thể sao chép. Vui lòng thử lại.');
  }
};

// Tải chi tiết pattern
const loadPattern = async (imageName) => {
  if (!imageName) return;
  try {
    const data = await getPatternByImageName(imageName);
    pattern.value = data;

    // Tải mẫu tương tự
    await loadRelatedPatterns(imageName);
  } catch (e) {
    console.error('Lỗi khi tải pattern:', e);
    pattern.value = null;
  }
};

// Tải mẫu tương tự
const loadRelatedPatterns = async (currentImageName) => {
  try {
    const allPatterns = await getAllPatterns({ limit: 20, offset: 0 });
    let otherPatterns = (allPatterns.patterns || []).filter(
      (p) => p.image_name !== currentImageName
    );

    // Trộn ngẫu nhiên và lấy 10 mẫu
    for (let i = otherPatterns.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [otherPatterns[i], otherPatterns[j]] = [
        otherPatterns[j],
        otherPatterns[i],
      ];
    }

    related.value = otherPatterns.slice(0, 10);
  } catch (e) {
    console.error('Lỗi khi tải mẫu tương tự:', e);
    related.value = [];
  }
};

// Mở pattern khác
const openPattern = async (imageName) => {
  if (!imageName || imageName === pattern.value?.image_name) return;
  await router.push(`/patterns/${encodeURIComponent(imageName)}`);
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// Lifecycle
onMounted(() => {
  const imageName = route.params.id;
  if (imageName) {
    loadPattern(imageName);
  }
});

// Watch cho route change
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
.copy-btn-container {
  margin: 12px 0;
}

.copy-btn {
  padding: 8px 16px;
  background: var(--main-color);
  color: var(--white);
  border: none;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  background: var(--green-dark, var(--main-color));
  transform: translateY(-1px);
}

.pattern-text {
  font-size: 13px;
  line-height: 1.6;
  color: var(--second-text-color);
  white-space: pre-wrap;
  word-break: break-word;
  font-family: monospace;
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
  background: var(--bg-color);
  border-radius: 8px;
}

.guide-img img {
  margin-top: 10px;
  width: 100%;
  height: auto;
  border-radius: 8px;
  display: block;
}

.page {
  max-width: 1100px;
  margin: 0 auto;
  font-size: 16px;
  color: var(--text-color);
}

.loading {
  font-size: 14px;
  color: var(--second-text-color);
  text-align: center;
  padding: 40px;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 12px;
  color: var(--second-text-color);
  margin-bottom: 12px;
  margin-top: 20px;
}

.breadcrumb a {
  text-decoration: none;
  color: var(--main-color);
}

/* Layout chính */
.layout {
  display: grid;
  grid-template-columns: minmax(260px, 380px) minmax(0, 1fr);
  gap: 28px;
}

/* Ảnh */
.image-wrap {
  width: 100%;
  position: relative;
  border-radius: 22px;
  overflow: hidden;
  background: var(--sub-bg);
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
  font-size: 12px;
  color: #fff;
  background: rgba(0, 0, 0, 0.45);
  padding: 4px 8px;
  border-radius: 8px;
  text-align: center;
}

/* Thông tin bên phải */
.right h1 {
  font-size: 26px;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 16px;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
  margin-bottom: 20px;
}

.pill {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px;
  background: var(--main-color);
  color: var(--white);
}

.pill.ghost {
  background: var(--sub-bg);
  color: var(--main-color);
}

/* Pattern content */
.pattern-content {
  margin: 20px 0;
  background: var(--bg-color);
  border-radius: 16px;
  padding: 16px;
}

.pattern-content h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-color);
}

.pattern-text {
  font-size: 13px;
  line-height: 1.6;
  color: var(--second-text-color);
  white-space: pre-wrap;
  word-break: break-word;
  font-family: monospace;
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
  background: var(--white);
  border-radius: 8px;
}

/* Block nội dung phụ */
.block {
  margin-top: 18px;
}

.block h3 {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--second-text-color);
  margin-bottom: 6px;
}

.block ul {
  padding-left: 18px;
  font-size: 13px;
  color: var(--second-text-color);
  line-height: 1.5;
}

.external {
  font-size: 13px;
  color: var(--main-color);
  text-decoration: none;
}

.external:hover {
  text-decoration: underline;
}

/* Mẫu tương tự */
.related {
  margin-top: 32px;
  margin-bottom: 35px;
}

.related-header h3 {
  font-size: 17px;
  color: var(--text-color);
}

.grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.grid :deep(.pattern-card) {
  width: 100%;
}

/* Responsive */
@media (max-width: 768px) {
  .layout {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
