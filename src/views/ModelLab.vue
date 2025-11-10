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

    <section class="models">
      <div
        v-for="m in models"
        :key="m.id"
        :class="['model-card', { active: m.id === selectedId }]"
        @click="selectModel(m.id)"
      >
        <div class="title-row">
          <h3>{{ m.name }}</h3>
          <span class="badge" v-if="m.id === defaultId">Default</span>
        </div>
        <p class="desc">{{ m.desc }}</p>
        <ul class="meta">
          <li>Embedding: {{ m.embedding }}</li>
          <li>Top-k: {{ m.topk }}</li>
          <li>Data domain: {{ m.domain }}</li>
        </ul>
      </div>
    </section>

    <section class="playground" v-if="current">
      <h3>Thử nhanh với "{{ current.name }}"</h3>
      <textarea
        v-model="sampleText"
        class="input"
        rows="3"
        placeholder="Ví dụ: 'coaster hoa nhiều lớp, màu pastel, phong cách Nhật'"
      ></textarea>
      <div class="actions">
        <button class="btn-run" @click="runTest">Chạy thử</button>
        <button
          class="btn-outline"
          v-if="selectedId !== defaultId"
          @click="setDefault"
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
import { fetchModels, setDefaultModel } from '../service/service';

const models = ref([]);
const selectedId = ref(null);
const defaultId = ref(null);
const sampleText = ref('');
const testResults = ref([]);

const current = computed(
  () => models.value.find((m) => m.code === selectedId.value) || null
);

onMounted(async () => {
  const data = await fetchModels();
  models.value = data;
  const def = data.find((m) => m.is_default) || data[0];
  if (def) {
    selectedId.value = def.code;
    defaultId.value = def.code;
  }
});

function selectModel(code) {
  selectedId.value = code;
  testResults.value = [];
}

async function makeDefault() {
  if (!selectedId.value) return;
  await setDefaultModel(selectedId.value);
  defaultId.value = selectedId.value;
  models.value = models.value.map((m) => ({
    ...m,
    is_default: m.code === selectedId.value,
  }));
}

function runTest() {
  // tạm mock, phần này khi có search_engine thật thì call /search với sampleText + modelCode
  if (!sampleText.value) {
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
}
.page-header h2 {
  font-size: 20px;
}
.page-header p {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
.models {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
  margin-top: 14px;
}
.model-card {
  padding: 10px;
  border-radius: 18px;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  font-size: 11px;
  transition: all 0.16s ease;
}
.model-card.active {
  border-color: #e8a1b6;
  box-shadow: 0 10px 26px rgba(232, 161, 182, 0.26);
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
  background: #fff4f7;
  color: #c66b8e;
}
.desc {
  margin-top: 4px;
  color: #666;
}
.meta {
  margin-top: 6px;
  padding-left: 14px;
  color: #888;
}
.playground {
  margin-top: 22px;
}
.playground h3 {
  font-size: 13px;
}
.input {
  width: 100%;
  margin-top: 6px;
  padding: 8px 10px;
  border-radius: 14px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 11px;
  background: #fff;
  resize: vertical;
}
.actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}
.btn-run {
  padding: 7px 16px;
  border-radius: 999px;
  border: none;
  background: #e8a1b6;
  color: #fff;
  font-size: 11px;
  cursor: true;
  box-shadow: 0 8px 22px rgba(232, 161, 182, 0.34);
}
.btn-outline {
  padding: 7px 14px;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  background: #fff;
  font-size: 10px;
  color: #555;
  cursor: pointer;
}
.results {
  margin-top: 14px;
  font-size: 10px;
}
.results-header {
  color: #888;
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
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.02);
  margin-bottom: 4px;
}
.name {
  font-size: 10px;
  color: #444;
}
.score {
  font-size: 9px;
  color: #999;
}
</style>
