<template>
  <div class="page">
    <header class="page-header">
      <h2>Model Lab</h2>
      <p>
        Chọn model gợi ý đang sử dụng, xem mô tả và thử nhanh với input mẫu.
        Phần này dành cho bạn tinh chỉnh hệ thống, không làm rối người dùng
        cuối.
      </p>
    </header>

    <!-- Danh sách model -->
    <section class="models">
      <div
        v-for="m in models"
        :key="m.code"
        :class="['model-card', { active: m.code === selectedCode }]"
        @click="selectModel(m.code)"
      >
        <div class="title-row">
          <h3>{{ m.name }}</h3>
          <span class="badge" v-if="m.code === defaultCode">Default</span>
        </div>
        <p class="desc">{{ m.description || 'Không có mô tả' }}</p>
        <ul class="meta">
          <li>Embedding: {{ m.embedding_dim }}</li>
          <li>Top-k: {{ m.top_k }}</li>
          <li>Code: {{ m.code }}</li>
        </ul>
      </div>
    </section>

    <!-- Playground -->
    <section class="playground" v-if="current">
      <h3>Thử nhanh với "{{ current.name }}"</h3>

      <!-- Ô nhập text chỉ hiện khi là model 2 hoặc 3 -->
      <div v-if="current.code === 'model_2' || current.code === 'model_3'">
        <textarea
          v-model="sampleText"
          class="input"
          rows="3"
          placeholder="Ví dụ: 'coaster hoa nhiều lớp, màu pastel, phong cách Nhật'"
        ></textarea>
      </div>

      <div class="actions">
        <button class="btn-run" @click="runTest">Chạy thử</button>
        <button
          class="btn-outline"
          v-if="selectedCode !== defaultCode"
          @click="makeDefault"
        >
          Đặt làm default
        </button>
      </div>

      <div class="results" v-if="testResults.length">
        <div class="results-header">
          <span>Kết quả giả lập</span>
        </div>
        <ul class="list">
          <li v-for="r in testResults" :key="r.id">
            <span class="name">{{ r.name }}</span>
            <span class="score">score {{ r.score }}</span>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { fetchModels, setDefaultModel } from '@/service/service';

const models = ref([]);
const selectedCode = ref(null);
const defaultCode = ref(null);
const sampleText = ref('');
const testResults = ref([]);

const current = computed(
  () => models.value.find((m) => m.code === selectedCode.value) || null
);

onMounted(async () => {
  try {
    const data = await fetchModels();
    models.value = data;
    const def = data.find((m) => m.is_default) || data[0];
    if (def) {
      selectedCode.value = def.code;
      defaultCode.value = def.code;
    }
  } catch (e) {
    console.error('Lỗi khi tải models:', e);
  }
});

function selectModel(code) {
  selectedCode.value = code;
  testResults.value = [];
}

async function makeDefault() {
  if (!selectedCode.value) return;
  await setDefaultModel(selectedCode.value);
  defaultCode.value = selectedCode.value;
  models.value = models.value.map((m) => ({
    ...m,
    is_default: m.code === selectedCode.value,
  }));
}

function runTest() {
  // tạm mock, khi có search_engine thì sẽ call API thật
  if (
    !sampleText.value &&
    (current.value.code === 'model_2' || current.value.code === 'model_3')
  ) {
    testResults.value = [];
    return;
  }
  testResults.value = [
    { id: 1, name: 'Gợi ý 1 (demo)', score: 0.95 },
    { id: 2, name: 'Gợi ý 2 (demo)', score: 0.9 },
  ];
}
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  color: var(--text-color);
}

/* Header */
.page-header h2 {
  font-size: 20px;
  font-weight: 500;
  color: var(--text-color);
}

.page-header p {
  font-size: 12px;
  color: var(--second-text-color);
  margin-top: 4px;
}

/* Danh sách model */
.models {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.model-card {
  padding: 10px;
  border-radius: 18px;
  background: var(--white);
  border: var(--border-light);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  font-size: 11px;
  transition: all 0.16s ease;
  color: var(--text-color);
}

.model-card.active {
  border-color: var(--main-color);
  box-shadow: var(--box-shadow);
  transform: translateY(-2px);
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-row h3 {
  font-size: 13px;
  font-weight: 500;
}

.badge {
  font-size: 8px;
  padding: 2px 6px;
  border-radius: 999px;
  background: var(--sub-bg);
  color: var(--main-color);
}

/* Mô tả & meta */
.desc {
  margin-top: 4px;
  color: var(--second-text-color);
}

.meta {
  margin-top: 6px;
  padding-left: 14px;
  color: var(--second-text-color);
}

/* Playground */
.playground {
  margin-top: 22px;
}

.playground h3 {
  font-size: 13px;
  color: var(--text-color);
}

.input {
  width: 100%;
  margin-top: 6px;
  padding: 8px 10px;
  border-radius: 14px;
  border: var(--border-light);
  font-size: 11px;
  background: var(--white);
  resize: vertical;
  color: var(--text-color);
}

/* Actions */
.actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.btn-run {
  padding: 7px 16px;
  border-radius: 999px;
  border: none;
  background: var(--main-color);
  color: var(--white);
  font-size: 11px;
  cursor: pointer;
  box-shadow: var(--box-shadow);
  transition: all 0.16s ease;
}

.btn-run:hover {
  background: var(--green-dark, var(--main-color));
  box-shadow: var(--shadow-strong, var(--box-shadow));
  transform: translateY(-1px);
}

.btn-outline {
  padding: 7px 14px;
  border-radius: 999px;
  border: var(--border-light);
  background: var(--white);
  font-size: 10px;
  color: var(--second-text-color);
  cursor: pointer;
  transition: all 0.16s ease;
}

.btn-outline:hover {
  background: var(--sub-bg);
}

/* Kết quả giả lập */
.results {
  margin-top: 14px;
  font-size: 10px;
  color: var(--second-text-color);
}

.results-header {
  margin-bottom: 4px;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list li {
  display: flex;
  justify-content: space-between;
  padding: 6px 9px;
  border-radius: 12px;
  background: var(--white);
  border: 1px solid rgba(0, 0, 0, 0.02);
  margin-bottom: 4px;
}

.name {
  font-size: 10px;
  color: var(--text-color);
}

.score {
  font-size: 9px;
  color: var(--second-text-color);
}
</style>
