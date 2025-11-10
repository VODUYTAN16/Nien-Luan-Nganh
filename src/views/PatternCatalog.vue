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
  font-size: 16px; /* tăng base chữ toàn khu catalog */
}

.catalog-header h2 {
  font-size: 23px; /* 20 -> 23 */
  font-weight: 600;
  margin: 0;
}

.subtitle {
  margin: 2px 0 0;
  font-size: 14px; /* 12 -> 14 */
  color: rgba(0, 0, 0, 0.5);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.empty {
  margin-top: 14px;
  font-size: 14px; /* 12 -> 14 */
  color: rgba(0, 0, 0, 0.45);
  text-align: center;
}

.loading {
  font-size: 15px; /* 13 -> 15 */
  color: #777;
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
  background: #b45b7c;
  color: #fff;
  font-size: 15px; /* 13 -> 15 */
  cursor: pointer;
  transition: background 0.2s ease;
}

.load-more button:hover {
  background: #9b4e6c;
}
</style>
