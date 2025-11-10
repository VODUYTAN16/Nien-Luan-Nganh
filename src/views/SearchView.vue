<template>
  <div class="page">
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
          <label class="label">Mô tả mẫu (text)</label>
          <textarea
            v-model="textQuery"
            class="input"
            rows="3"
            placeholder="Ví dụ: coaster tròn màu be, viền răng cưa, phong cách tối giản..."
          ></textarea>

          <div class="upload-area" @click="triggerFile">
            <div class="upload-icon">📷</div>
            <div class="upload-text">
              <div>Chọn hoặc kéo thả ảnh mẫu của bạn</div>
              <small>
                Hỗ trợ JPG, PNG. Ảnh rõ, đủ sáng giúp model nhận diện tốt hơn.
              </small>
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
          <p class="hint" v-if="selectedModel">
            Gợi ý từ model: <strong>{{ selectedModel }}</strong>
            • Top-k = 20 (có thể chỉnh tại Model Lab).
          </p>
        </div>
      </section>

      <!-- Kết quả -->
      <div v-if="results.length" class="grid">
        <div
          v-for="item in results"
          :key="item.id"
          class="pattern-card"
          @click="goDetail(item.id)"
        >
          <img
            :src="withBase(item.top_image_url)"
            :alt="item.name || item.base_name"
          />
          <div class="name">
            {{ item.name || item.base_name }}
          </div>
        </div>
      </div>

      <!-- Trạng thái rỗng -->
      <section v-else class="empty">
        <p>
          Chưa có kết quả. Nhập mô tả hoặc chọn ảnh, sau đó bấm “Gợi ý mẫu”.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { fetchModels, searchPatterns, withBase } from '@/service/service';
import LeafFall from '@/components/LeafFall.vue';

const router = useRouter();

const models = ref([]);
const selectedModel = ref(null);

const textQuery = ref('');
const imageFile = ref(null);
const fileInput = ref(null);
const previewUrl = ref(null);

const results = ref([]);
const loading = ref(false);

// chọn file
const triggerFile = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

function onFileChange(e) {
  const file = e.target.files?.[0];
  imageFile.value = file || null;

  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }

  if (file) {
    previewUrl.value = URL.createObjectURL(file);
  } else {
    previewUrl.value = null;
  }
}

const clearImage = () => {
  imageFile.value = null;
  if (fileInput.value) fileInput.value.value = '';
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = null;
  }
};

// điều hướng sang detail
const goDetail = (id) => {
  if (!id) return;
  router.push(`/patterns/${id}`);
};

// gọi API model khi mount
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

// chạy search
async function runSearch() {
  if (!selectedModel.value) return;

  loading.value = true;
  results.value = [];

  try {
    const res = await searchPatterns({
      modelCode: selectedModel.value,
      queryText: textQuery.value || null,
      imageFile: imageFile.value || null,
    });
    results.value = res || [];
  } catch (e) {
    console.error('Lỗi khi search patterns:', e);
    results.value = [];
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.page {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 120px);
  font-size: 16px; /* base to hơn cho toàn page */
}

/* lớp lá rơi nằm dưới, không chặn thao tác */
.leaf-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

/* nội dung nằm trên hiệu ứng */
.content {
  position: relative;
  z-index: 2;
}

/* header */
.page-header h2 {
  font-size: 24px; /* 22 -> 24 */
  font-weight: 500;
}
.page-header p {
  font-size: 14px; /* 13 -> 14 */
  color: #666;
  margin-top: 4px;
}

/* khối tìm kiếm */
.search-panel {
  display: grid;
  grid-template-columns: 1.7fr 1.3fr;
  gap: 26px;
  margin-top: 18px;
  align-items: flex-start;
}
.label {
  font-size: 13px; /* 11 -> 13 */
  color: #777;
}
.input {
  width: 100%;
  margin-top: 4px;
  padding: 11px 12px;
  border-radius: 14px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 14px; /* 12 -> 14 */
  resize: vertical;
  background: #fff;
}

/* upload ảnh */
.upload-area {
  margin-top: 10px;
  padding: 13px;
  border-radius: 16px;
  border: 1px dashed rgba(0, 0, 0, 0.14);
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  gap: 10px;
  align-items: center;
  cursor: pointer;
}
.upload-icon {
  font-size: 22px; /* 20 -> 22 */
}
.upload-text div {
  font-size: 14px; /* 12 -> 14 */
  color: #444;
}
.upload-text small {
  font-size: 11px; /* 10 -> 11 */
  color: #888;
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
  font-size: 13px; /* 11 -> 13 */
  color: #c66b8e;
  cursor: pointer;
}

/* chọn model */
.right h3 {
  font-size: 16px; /* 14 -> 16 */
  margin-bottom: 8px;
}
.model-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.model-btn {
  padding: 9px 10px;
  border-radius: 14px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  background: #fff;
  text-align: left;
  cursor: pointer;
  transition: all 0.16s ease;
  font-size: 13px; /* 11 -> 13 */
}
.model-btn.active {
  border-color: #e8a1b6;
  box-shadow: 0 6px 18px rgba(232, 161, 182, 0.26);
  transform: translateY(-1px);
}
.model-name {
  font-weight: 600;
  font-size: 14px; /* 12 -> 14 */
}
.model-desc {
  color: #777;
  margin-top: 2px;
}
.model-tag {
  display: inline-block;
  margin-top: 4px;
  padding: 3px 9px;
  border-radius: 999px;
  background: #fff4f7;
  font-size: 11px; /* 9 -> 11 */
  color: #c66b8e;
}

/* nút chạy */
.btn-run {
  margin-top: 10px;
  width: 100%;
  padding: 10px 0;
  border-radius: 999px;
  border: none;
  background: #e8a1b6;
  color: #fff;
  font-size: 14px; /* 12 -> 14 */
  cursor: pointer;
  box-shadow: 0 8px 22px rgba(232, 161, 182, 0.34);
}
.btn-run:disabled {
  opacity: 0.7;
  cursor: default;
}
.hint {
  margin-top: 6px;
  font-size: 11px; /* 9 -> 11 */
  color: #888;
}

/* kết quả */
.grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 14px;
}
.pattern-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 7px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.14s ease;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.pattern-card img {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  object-fit: cover;
  background: #f5e9ef;
}
.pattern-card .name {
  font-size: 13px; /* 11 -> 13 */
  color: #444;
}
.pattern-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.06);
}

/* trạng thái rỗng */
.empty {
  margin-top: 26px;
  font-size: 14px; /* 12 -> 14 */
  color: #999;
}
</style>
