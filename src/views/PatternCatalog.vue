<template>
  <div class="catalog-root">
    <div class="catalog-header">
      <h2>Kho mẫu coaster</h2>
      <p class="subtitle">{{ total }} mẫu đang có trong hệ thống</p>
    </div>

    <!-- Thanh tìm kiếm -->
    <!-- <div class="search-bar">
      <input
        v-model="searchKeyword"
        type="text"
        placeholder="🔍 Tìm kiếm theo tên ảnh hoặc công thức..."
        class="search-input"
        @keyup.enter="handleSearch"
      />
      <button @click="handleSearch" class="search-btn">Tìm kiếm</button>
      <button v-if="searchKeyword" @click="clearSearch" class="clear-btn">
        Xóa
      </button>
    </div> -->

    <!-- Đang tải -->
    <div v-if="loading" class="loading">Đang tải danh sách mẫu...</div>

    <!-- Danh sách mẫu -->
    <div v-else-if="visiblePatterns.length" class="grid">
      <PatternCard
        v-for="item in visiblePatterns"
        :key="item.image_name"
        :pattern="item"
        @click="goDetail(item.image_name)"
      />
    </div>

    <!-- Không có dữ liệu -->
    <p v-else class="empty">
      {{
        searchKeyword
          ? 'Không tìm thấy mẫu nào phù hợp với từ khóa "' + searchKeyword + '"'
          : 'Không có mẫu nào trong CSDL.'
      }}
    </p>

    <!-- Nút Xem thêm -->
    <div
      v-if="!loading && !isSearching && visibleCount < total"
      class="load-more"
    >
      <button @click="loadMore">Xem thêm</button>
    </div>

    <!-- Nút load more khi tìm kiếm có phân trang -->
    <div v-if="!loading && isSearching && searchHasMore" class="load-more">
      <button @click="loadMoreSearch">Tải thêm kết quả</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import {
  getAllPatterns,
  searchPatterns,
  getDatasetStatistics,
} from '@/service/service';
import PatternCard from '@/components/PatternCard.vue';

const router = useRouter();

// State
const patterns = ref([]);
const visibleCount = ref(20);
const loading = ref(true);
const searchKeyword = ref('');
const isSearching = ref(false);
const searchResults = ref([]);
const searchTotal = ref(0);
const searchOffset = ref(0);
const searchLimit = ref(20);
const stats = ref(null);

// Computed
const total = computed(() => {
  if (isSearching.value) {
    return searchTotal.value;
  }
  return patterns.value.length;
});

const visiblePatterns = computed(() => {
  if (isSearching.value) {
    return searchResults.value;
  }
  return patterns.value.slice(0, visibleCount.value);
});

const searchHasMore = computed(() => {
  return searchResults.value.length < searchTotal.value;
});

// Methods
const loadMore = () => {
  visibleCount.value += 20;
};

const loadMoreSearch = async () => {
  if (!searchKeyword.value.trim()) return;

  searchOffset.value += searchLimit.value;
  loading.value = true;

  try {
    const result = await searchPatterns(searchKeyword.value, {
      limit: searchLimit.value,
      offset: searchOffset.value,
    });

    searchResults.value.push(...result.patterns);
    searchTotal.value = result.total;
  } catch (error) {
    console.error('Lỗi khi tải thêm kết quả tìm kiếm:', error);
  } finally {
    loading.value = false;
  }
};

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    clearSearch();
    return;
  }

  loading.value = true;
  isSearching.value = true;
  searchOffset.value = 0;

  try {
    const result = await searchPatterns(searchKeyword.value, {
      limit: searchLimit.value,
      offset: 0,
    });

    searchResults.value = result.patterns || [];
    searchTotal.value = result.total || 0;
  } catch (error) {
    console.error('Lỗi khi tìm kiếm:', error);
    searchResults.value = [];
    searchTotal.value = 0;
  } finally {
    loading.value = false;
  }
};

const clearSearch = () => {
  searchKeyword.value = '';
  isSearching.value = false;
  searchResults.value = [];
  searchTotal.value = 0;
  searchOffset.value = 0;
  visibleCount.value = 20;
  loadPatterns();
};

const loadPatterns = async () => {
  loading.value = true;
  try {
    const result = await getAllPatterns({ limit: 200, offset: 0 });
    patterns.value = result.patterns || [];
  } catch (error) {
    console.error('Lỗi khi tải patterns:', error);
    patterns.value = [];
  } finally {
    loading.value = false;
  }
};

const loadStatistics = async () => {
  try {
    const data = await getDatasetStatistics();
    stats.value = data;
  } catch (error) {
    console.error('Lỗi khi tải thống kê:', error);
  }
};

const goDetail = (imageName) => {
  if (imageName) {
    router.push(`/patterns/${encodeURIComponent(imageName)}`);
  }
};

// Watch
watch(searchKeyword, (newVal) => {
  if (!newVal?.trim()) {
    clearSearch();
  }
});

// Lifecycle
onMounted(async () => {
  await Promise.all([loadPatterns(), loadStatistics()]);
});
</script>

<style scoped>
.catalog-root {
  display: flex;
  flex-direction: column;
  gap: 18px;
  font-size: 16px;
  color: var(--text-color);
  padding: 27px 182px;
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

/* Search bar styles */
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
  background: var(--white);
  color: var(--text-color);
}

.search-input:focus {
  border-color: var(--main-color);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.search-btn,
.clear-btn {
  padding: 10px 20px;
  border-radius: 12px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-btn {
  background: var(--main-color);
  color: var(--white);
}

.search-btn:hover {
  background: var(--green-dark, var(--main-color));
  transform: translateY(-1px);
}

.clear-btn {
  background: #ef4444;
  color: white;
}

.clear-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

/* Stats bar */
.stats-bar {
  display: flex;
  gap: 20px;
  padding: 10px 15px;
  background: var(--bg-secondary, #f3f4f6);
  border-radius: 12px;
  font-size: 13px;
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
  padding: 40px;
}

.loading {
  font-size: 15px;
  color: var(--second-text-color);
  text-align: center;
  padding: 40px;
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

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .stats-bar {
    background: #1f2937;
  }

  .search-input {
    background: #1f2937;
    border-color: #374151;
    color: #f3f4f6;
  }

  .search-input:focus {
    border-color: var(--main-color);
  }
}
</style>
