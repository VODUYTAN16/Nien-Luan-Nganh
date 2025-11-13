<template>
  <div class="catalog-root">
    <div class="catalog-header">
      <h2>Kho mẫu coaster</h2>
      <p class="subtitle">{{ total }} mẫu đang có trong hệ thống CrochetLens</p>
    </div>

    <!-- Đang tải -->
    <div v-if="loading" class="loading">Đang tải danh sách mẫu...</div>

    <!-- Danh sách mẫu -->
    <div v-else-if="visiblePatterns.length" class="grid">
      <PatternCard
        v-for="item in visiblePatterns"
        :key="item.id"
        :pattern="item"
        @click="goDetail(item.id)"
      />
    </div>

    <!-- Không có dữ liệu -->
    <p v-else class="empty">
      Không có mẫu nào trong CSDL. Kiểm tra lại static/top hoặc
      populate_patterns.py.
    </p>

    <!-- Nút Xem thêm -->
    <div v-if="!loading && visibleCount < total" class="load-more">
      <button @click="loadMore">Xem thêm</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { fetchPatterns } from '@/service/service';
import PatternCard from '@/components/PatternCard.vue';

const router = useRouter();

const patterns = ref([]);
const visibleCount = ref(20);
const loading = ref(true);

const total = computed(() => patterns.value.length);
const visiblePatterns = computed(() =>
  patterns.value.slice(0, visibleCount.value)
);

const loadMore = () => {
  visibleCount.value += 20;
};

const goDetail = (id) => {
  router.push(`/patterns/${id}`);
};

onMounted(async () => {
  try {
    const data = await fetchPatterns();
    console.log(data);
    patterns.value = data || [];
  } catch (e) {
    console.error('Lỗi khi tải patterns:', e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.catalog-root {
  display: flex;
  flex-direction: column;
  gap: 18px;
  font-size: 16px;
  color: var(--text-color);
}

.catalog-header h2 {
  font-size: 23px;
  font-weight: 600;
  margin: 0;
  color: var(--text-color);
}

.subtitle {
  margin: 2px 0 0;
  font-size: 14px;
  color: var(--second-text-color);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.empty {
  margin-top: 14px;
  font-size: 14px;
  color: var(--second-text-color);
  text-align: center;
}

.loading {
  font-size: 15px;
  color: var(--second-text-color);
  text-align: center;
}

.load-more {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.load-more button {
  padding: 10px 18px;
  border-radius: 12px;
  border: none;
  background: var(--main-color);
  color: var(--white);
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--box-shadow);
}

.load-more button:hover {
  background: var(--green-dark, var(--main-color));
  box-shadow: var(--shadow-strong, var(--box-shadow));
  transform: translateY(-1px);
}
</style>
