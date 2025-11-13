<template>
  <div class="page">
    <div class="hero-blur-overlay"></div>

    <!-- Lớp hiệu ứng lá rơi -->
    <LeafFall class="leaf-layer" />

    <!-- Nội dung chính -->
    <div class="content">
      <header class="page-header">
        <h2>Tìm mẫu móc từ ảnh hoặc mô tả</h2>
        <p>
          Chọn model, tải ảnh hoặc nhập mô tả. Hệ thống sẽ truy vấn CSDL mẫu
          móc.
        </p>
      </header>

      <section class="search-panel">
        <!-- Bên trái: text + upload ảnh -->
        <div class="left">
          <Transition name="fade">
            <div
              v-if="selectedModel === 'model_2' || selectedModel === 'model_3'"
            >
              <label class="label">Mô tả mẫu (text)</label>
              <textarea
                v-model="textQuery"
                class="input"
                rows="3"
                placeholder="Ví dụ: coaster tròn màu be, viền răng cưa, phong cách tối giản..."
              ></textarea>
            </div>
          </Transition>

          <div class="upload-area" @click="triggerFile">
            <div class="upload-icon">📷</div>
            <div class="upload-text">
              <div>Chọn hoặc kéo thả ảnh mẫu của bạn</div>
              <small
                >Hỗ trợ JPG, PNG. Ảnh rõ, đủ sáng giúp model nhận diện tốt
                hơn.</small
              >
            </div>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              @change="onFileChange"
              hidden
            />
          </div>

          <div v-if="previewUrl" class="preview">
            <img :src="previewUrl" alt="preview" />
            <button class="link-btn" @click="clearImage">Xóa ảnh</button>
          </div>
        </div>

        <!-- Bên phải: chọn model -->
        <div class="right">
          <h3>Chọn model</h3>
          <div class="model-list">
            <button
              v-for="m in models"
              :key="m.code"
              :class="['model-btn', { active: selectedModel === m.code }]"
              @click="selectedModel = m.code"
            >
              <div class="model-name">{{ m.name }}</div>
              <div class="model-desc">
                {{ m.description || 'Không có mô tả' }}
              </div>
              <div class="model-tag">
                Top-k: {{ m.top_k }} • dim {{ m.embedding_dim }}
              </div>
            </button>
          </div>
          <button class="btn-run" @click="runSearch" :disabled="loading">
            {{ loading ? 'Đang tìm...' : 'Gợi ý mẫu' }}
          </button>
          <p class="inline-warn" v-if="warnMsg">⚠️ {{ warnMsg }}</p>
          <p class="hint" v-if="selectedModel">
            Gợi ý từ model: <strong>{{ selectedModel }}</strong> • Top-k = 20
            (có thể chỉnh tại Model Lab).
          </p>
        </div>
      </section>

      <div v-if="results" class="results-wrap">
        <div class="results-grid">
          <PatternCard
            v-for="item in results"
            :key="item.id"
            :pattern="item"
            @click="goDetail(item.id)"
          />
        </div>
      </div>

      <section v-else class="empty">
        <p>
          Chưa có kết quả. Nhập mô tả hoặc chọn ảnh, sau đó bấm “Gợi ý mẫu”.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { fetchModels, searchPatterns } from '@/service/service';
import LeafFall from '@/components/LeafFall.vue';
import PatternCard from '@/components/PatternCard.vue';

const router = useRouter();

const models = ref([]);
const selectedModel = ref(null);
const textQuery = ref('');
const imageFile = ref(null);
const fileInput = ref(null);
const previewUrl = ref(null);
const results = ref([]);
const loading = ref(false);
const warnMsg = ref('');

const triggerFile = () => fileInput.value?.click();

function onFileChange(e) {
  const file = e.target.files?.[0] || null;
  imageFile.value = file;
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = file ? URL.createObjectURL(file) : null;
}

function clearImage() {
  imageFile.value = null;
  if (fileInput.value) fileInput.value.value = '';
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = null;
  }
}

function showWarn(msg) {
  warnMsg.value = msg;
  setTimeout(() => (warnMsg.value = ''), 3000);
}

function goDetail(id) {
  if (id) router.push(`/patterns/${id}`);
}

onMounted(async () => {
  try {
    const data = await fetchModels();
    models.value = data || [];
    const def = models.value.find((m) => m.is_default) || models.value[0];
    selectedModel.value = def?.code || null;
  } catch (e) {
    console.error('Lỗi khi tải models:', e);
  }
});

async function runSearch() {
  const model = selectedModel.value;
  const hasText = !!textQuery.value.trim();
  const hasImage = !!imageFile.value;

  if (!model || (!hasText && !hasImage)) {
    showWarn('Vui lòng nhập mô tả hoặc chọn ảnh trước khi ấn "Gợi ý mẫu".');
    return;
  }
  if ((model === 'model_1' || model === 'model_4') && !hasImage) {
    showWarn('Model hiện tại chỉ hỗ trợ tìm theo ảnh. Vui lòng chọn ảnh.');
    return;
  }

  loading.value = true;
  results.value = [];

  try {
    const items = await searchPatterns({
      modelCode: model,
      queryText: hasText ? textQuery.value.trim() : null,
      imageFile: hasImage ? imageFile.value : null,
    });
    results.value = items || [];
  } catch (e) {
    console.error('Lỗi khi search patterns:', e);
    showWarn('Không truy vấn được. Vui lòng thử lại sau.');
  } finally {
    loading.value = false;
  }
}

watch(selectedModel, (newVal) => {
  if (newVal !== 'model_2' && newVal !== 'model_3') {
    textQuery.value = '';
  }
});
</script>

<style scoped>
/* Hiệu ứng fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.hero-blur-overlay {
  position: absolute;
  inset: 0;
  backdrop-filter: blur(6px); /* mức độ mờ */
  background-color: rgba(255, 255, 255, 0.08); /* kính mờ nhẹ */
  z-index: 1;
}
/* Nền blur */
.page {
  position: relative;
  max-width: 1300px;
  margin: 0 auto;
  min-height: calc(100vh - 120px);
  color: var(--text-color);
  overflow: hidden;
}

.page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url('../assets/hinhL.png') center/cover no-repeat;
  filter: blur(8px) brightness(1.1);
  z-index: 0;
  transform: scale(1.05);
}

/* Lớp lá rơi */
.leaf-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 2;
}

/* Nội dung nổi trên nền */
.content {
  position: relative;
  z-index: 3;
  border-radius: 20px;
  padding: 20px 28px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

/* Header */
.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color);
}

.page-header p {
  font-size: 14px;
  color: var(--second-text-color);
  margin-top: 4px;
}

/* Khối tìm kiếm */
.search-panel {
  display: grid;
  grid-template-columns: 1.7fr 1.3fr;
  gap: 26px;
  margin-top: 18px;
  align-items: flex-start;
}

/* Input & Upload */
.label {
  font-size: 13px;
  color: var(--second-text-color);
}
.input {
  width: 100%;
  margin-top: 4px;
  padding: 11px 12px;
  border-radius: 14px;
  border: var(--border-light);
  font-size: 14px;
  resize: vertical;
  background: var(--white);
  color: var(--text-color);
}
.upload-area {
  margin-top: 10px;
  padding: 13px;
  border-radius: 16px;
  border: 1px dashed var(--green-border);
  background: rgba(255, 255, 255, 0.85);
  display: flex;
  gap: 10px;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
}
.upload-area:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-1px);
}
.upload-icon {
  font-size: 22px;
}
.upload-text div {
  font-size: 14px;
  color: var(--text-color);
}
.upload-text small {
  font-size: 11px;
  color: var(--second-text-color);
}
.preview {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  align-items: center;
}
.preview img {
  width: 78px;
  height: 78px;
  border-radius: 14px;
  object-fit: cover;
}
.link-btn {
  border: none;
  background: none;
  font-size: 13px;
  color: var(--main-color);
  cursor: pointer;
}

/* Model */
.right h3 {
  font-size: 16px;
  margin-bottom: 8px;
  color: var(--text-color);
}
.model-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.model-btn {
  padding: 9px 10px;
  border-radius: 14px;
  border: var(--border-light);
  background: var(--white);
  text-align: left;
  cursor: pointer;
  transition: all 0.16s ease;
  font-size: 13px;
  color: var(--text-color);
}
.model-btn.active {
  border-color: var(--main-color);
  box-shadow: var(--box-shadow);
  transform: translateY(-1px);
}
.model-name {
  font-weight: 600;
  font-size: 14px;
}
.model-desc {
  color: var(--second-text-color);
  margin-top: 2px;
}
.model-tag {
  display: inline-block;
  margin-top: 4px;
  padding: 3px 9px;
  border-radius: 999px;
  background: var(--sub-bg);
  font-size: 11px;
  color: var(--main-color);
}

/* Nút chạy */
.btn-run {
  margin-top: 10px;
  width: 100%;
  padding: 10px 0;
  border-radius: 999px;
  border: none;
  background: var(--main-color);
  color: var(--white);
  font-size: 14px;
  cursor: pointer;
  box-shadow: var(--box-shadow);
  transition: all 0.18s ease;
}
.btn-run:disabled {
  opacity: 0.7;
  cursor: default;
}
.btn-run:hover:not(:disabled) {
  background: var(--green-dark);
  box-shadow: var(--shadow-strong);
  transform: translateY(-1px);
}

/* Các phần khác */
.inline-warn {
  margin-top: 6px;
  font-size: 12px;
  color: #b45309;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  padding: 6px 10px;
  border-radius: 10px;
  display: inline-block;
}

.hint {
  margin-top: 6px;
  font-size: 11px;
  color: var(--second-text-color);
}
.results-wrap {
  margin-top: 24px;
}
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}
.empty {
  margin-top: 26px;
  font-size: 14px;
  color: #999;
}
</style>
