<template>
  <div class="page">
    <div class="hero-blur-overlay"></div>
    <LeafFall class="leaf-layer" />

    <div class="content container">
      <header class="page-header text-center">
        <h1 class="title display-4 fw-bold mb-2">
          🧶TẠO SINH CÔNG THỨC MÓC LEN
        </h1>
        <p class="subtitle">Tạo công thức móc len từ hình ảnh với AI</p>
      </header>

      <div class="row g-4 justify-content-center">
        <div class="col-lg-5 col-xl-4">
          <div class="card shadow-lg border-0">
            <div class="card-header bg-white">
              <h5 class="mb-0 fw-semibold text-center">📸 Tải lên hình ảnh</h5>
            </div>
            <div class="card-body d-flex flex-column">
              <div
                class="upload-area flex-grow-1 d-flex align-items-center justify-content-center border border-2 border-dashed rounded-3 p-4"
                :class="{ 'has-image': previewUrl, dragover: isDragOver }"
                @dragover.prevent="isDragOver = true"
                @dragleave.prevent="isDragOver = false"
                @drop.prevent="handleDrop"
                @click="triggerFile"
              >
                <input
                  :disabled="loading"
                  ref="fileInput"
                  type="file"
                  accept="image/jpeg,image/png,image/jpg,image/bmp,image/tiff,image/webp"
                  style="display: none"
                  @change="onFileChange"
                />

                <div v-if="!previewUrl" class="text-center">
                  <div class="upload-icon mb-3">📸</div>
                  <h6 class="text-muted">Nhấp hoặc kéo thả ảnh vào đây</h6>
                  <small class="text-secondary">
                    Hỗ trợ: JPG, PNG, BMP, TIFF, WEBP (≤ 10MB)
                  </small>
                </div>

                <div
                  v-else
                  class="preview-container position-relative w-100 h-100"
                >
                  <img
                    :src="previewUrl"
                    alt="Preview"
                    class="preview-image img-fluid rounded"
                  />
                  <button
                    :disabled="loading"
                    class="btn btn-danger btn-sm position-absolute top-0 end-0 m-2 rounded-circle"
                    @click.stop="clearImage"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>

            <div class="card-footer bg-white">
              <button
                class="generate-btn btn w-100 py-3 fs-5 fw-bold"
                :disabled="!imageFile || loading"
                @click="generatePatternStream"
              >
                <span v-if="!loading">Tạo công thức</span>
                <span
                  v-else
                  class="d-flex align-items-center justify-content-center gap-2"
                >
                  <span
                    class="spinner-border spinner-border-sm"
                    role="status"
                  ></span>
                  Đang tạo...
                </span>
              </button>

              <div
                v-if="warnMsg"
                class="alert alert-warning mt-3 py-2 small text-center"
              >
                ⚠️ {{ warnMsg }}
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-7 col-xl-8">
          <div class="card h-100 shadow-lg border-0">
            <div class="card-header bg-white">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0 fw-semibold">📋 Công thức tạo sinh</h5>
                <!-- Thêm select số lần retries -->
                <div class="d-flex align-items-center gap-2">
                  <label class="text-muted small mb-0">Số lần thử:</label>
                  <select
                    v-model="config.max_retries"
                    class="form-select form-select-sm"
                    style="width: auto"
                    :disabled="loading"
                  >
                    <option :value="1">1 lần</option>
                    <option :value="2">2 lần</option>
                    <option :value="3">3 lần</option>
                    <option :value="4">4 lần</option>
                    <option :value="5">5 lần</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="card-body d-flex flex-column">
              <!-- Current Pattern Display (Real-time) -->
              <div v-if="currentPattern" class="current-pattern mb-4">
                <div
                  class="d-flex justify-content-between align-items-center mb-2"
                >
                  <h6 class="mb-0 fw-bold">
                    🔄 Công thức hiện tại
                    <span v-if="currentAttempt" class="badge bg-secondary ms-2">
                      Lần thử {{ currentAttempt }}
                    </span>
                  </h6>
                  <div class="d-flex gap-2">
                    <!-- <span v-if="currentTemp" class="badge bg-info">
                      🌡️ Temp: {{ currentTemp.toFixed(2) }}
                    </span> -->
                    <span
                      v-if="currentProcessingTime"
                      class="badge bg-secondary"
                    >
                      ⏱️ {{ currentProcessingTime.toFixed(2) }}s
                    </span>
                  </div>
                </div>
                <div class="pattern-display border rounded bg-light p-3">
                  <pre class="pattern-text mb-0">{{
                    formatPattern(currentPattern)
                  }}</pre>
                </div>

                <!-- Current Evaluation -->
                <div v-if="currentEvaluation" class="evaluation-info mt-2">
                  <div class="d-flex gap-3">
                    <span
                      class="badge"
                      :class="
                        currentEvaluation.gsc === 1
                          ? 'bg-success'
                          : 'bg-warning'
                      "
                    >
                      GSC: {{ currentEvaluation.gsc?.toFixed(2) || 'N/A' }}
                    </span>
                    <span
                      class="badge"
                      :class="
                        currentEvaluation.sfc >= 1 ? 'bg-success' : 'bg-warning'
                      "
                    >
                      SFC: {{ currentEvaluation.sfc?.toFixed(4) || 'N/A' }}
                    </span>
                  </div>
                  <div
                    v-if="currentEvaluation.errors?.length"
                    class="mt-2 small text-warning"
                  >
                    ⚠️ {{ currentEvaluation.errors[0]?.message }}
                  </div>
                </div>
              </div>

              <!-- Placeholder khi đang loading và chưa có pattern -->
              <div
                v-else-if="loading && !currentPattern"
                class="current-pattern mb-4"
              >
                <div
                  class="d-flex justify-content-between align-items-center mb-2"
                >
                  <h6 class="mb-0 fw-bold">
                    🔄 Công thức hiện tại
                    <span class="placeholder-glow ms-2">
                      <span class="placeholder col-3"></span>
                    </span>
                  </h6>
                  <div class="placeholder-glow">
                    <span class="placeholder col-2"></span>
                  </div>
                </div>
                <div class="pattern-display border rounded bg-light p-3">
                  <div class="placeholder-glow">
                    <p class="placeholder col-12"></p>
                    <p class="placeholder col-10"></p>
                    <p class="placeholder col-8"></p>
                    <p class="placeholder col-11"></p>
                    <p class="placeholder col-9"></p>
                  </div>
                </div>
              </div>

              <!-- Hướng dẫn khi chưa tạo pattern -->
              <div
                v-else-if="
                  !currentPattern && !loading && attemptsHistory.length === 0
                "
                class="text-center text-muted py-5"
              >
                <i class="bi bi-lightbulb fs-1"></i>
                <p class="mt-3 mb-0">
                  📌 Hướng dẫn: Tải ảnh lên và ấn vào nút "Tạo công thức" để bắt
                  đầu
                </p>
                <small class="text-secondary">
                  Hệ thống sẽ tự động tạo và đánh giá công thức móc len từ ảnh
                  của bạn
                </small>
              </div>

              <!-- All Attempts History -->
              <div class="history-section">
                <h6 class="fw-bold mb-2">📜 Lịch sử các lần thử</h6>

                <!-- Hiển thị placeholder khi đang loading và chưa có lịch sử -->
                <div
                  v-if="loading && attemptsHistory.length === 0"
                  class="history-list"
                >
                  <div
                    class="history-item border rounded p-2 mb-2 placeholder-glow"
                  >
                    <div
                      class="d-flex justify-content-between align-items-center"
                    >
                      <div>
                        <strong class="placeholder col-3"></strong>
                        <span class="ms-2 placeholder col-2"></span>
                      </div>
                      <div class="placeholder col-2"></div>
                    </div>
                    <div class="mt-1">
                      <span class="placeholder col-4"></span>
                    </div>
                  </div>
                </div>

                <!-- Hiển thị lịch sử thực tế -->
                <div
                  v-else-if="attemptsHistory.length > 0"
                  class="history-list"
                >
                  <div
                    v-for="(attempt, idx) in attemptsHistory"
                    :key="idx"
                    class="history-item border rounded p-2 mb-2"
                    :class="{ 'border-success': attempt.is_valid }"
                    @click="viewAttemptHistory(attempt)"
                  >
                    <div
                      class="d-flex justify-content-between align-items-center"
                    >
                      <div>
                        <strong>Lần {{ attempt.attempt }}</strong>
                        <span class="ms-2">
                          <!-- <span class="badge bg-secondary"
                            >Temp: {{ attempt.temperature?.toFixed(2) }}</span
                          > -->
                        </span>
                        <span v-if="attempt.generation_time" class="ms-1">
                          <span class="badge bg-secondary"
                            >⏱️ {{ attempt.generation_time.toFixed(2) }}s</span
                          >
                        </span>
                      </div>
                      <div>
                        <span v-if="attempt.is_valid" class="badge bg-success"
                          >Hợp lệ</span
                        >
                        <span v-else class="badge bg-warning">Chưa hợp lệ</span>
                      </div>
                    </div>
                    <div class="small text-muted mt-1">
                      GSC: {{ attempt.gsc?.toFixed(2) || 'N/A' }} | SFC:
                      {{ attempt.sfc?.toFixed(4) || 'N/A' }}
                    </div>
                  </div>
                </div>

                <!-- Hiển thị khi chưa có lịch sử và không loading -->
                <div v-else class="text-center text-muted py-3">
                  <small>Chưa có lịch sử thử nghiệm</small>
                </div>
              </div>

              <!-- Final Result Display -->
              <!-- <div v-if="finalResult" class="final-result mt-4">
                <div
                  class="alert"
                  :class="
                    finalResult.is_valid ? 'alert-success' : 'alert-warning'
                  "
                >
                  <strong>
                    {{
                      finalResult.is_valid
                        ? '✅ Công thức hợp lệ!'
                        : '⚠️ Công thức cuối cùng'
                    }}
                  </strong>
                  <div
                    v-if="!finalResult.is_valid && finalResult.selection_reason"
                    class="mt-1 small"
                  >
                    Lý do chọn: {{ finalResult.selection_reason }}
                  </div>
                </div>
              </div> -->
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="toast-notification-container">
      <div
        v-for="(msg, idx) in statusMessages"
        :key="idx"
        class="toast-notification"
        :class="{
          'toast-info': msg.type === 'info',
          'toast-warning': msg.type === 'warning',
          'toast-success': msg.type === 'success',
          'toast-error': msg.type === 'error',
        }"
        role="alert"
      >
        <div class="toast-icon">
          <i
            :class="{
              'bi-info-circle-fill': msg.type === 'info',
              'bi-exclamation-triangle-fill': msg.type === 'warning',
              'bi-check-circle-fill': msg.type === 'success',
              'bi-x-circle-fill': msg.type === 'error',
            }"
          ></i>
        </div>
        <div class="toast-content">
          <div class="toast-message">{{ msg.message }}</div>
        </div>
        <button class="toast-close" @click="removeStatusMessage(idx)">×</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, watch } from 'vue';
import { generateCrochetPatternStream } from '@/service/service';
import LeafFall from '@/components/LeafFall.vue';

// State
const imageFile = ref(null);
const fileInput = ref(null);
const previewUrl = ref(null);
const loading = ref(false);
const warnMsg = ref('');
const isDragOver = ref(false);
const isViewingHistory = ref(false);
const currentRealTimePattern = ref(null);
const currentRealTimeAttempt = ref(null);
const currentRealTimeTemp = ref(null);
const currentRealTimeProcessingTime = ref(null);
const currentRealTimeEvaluation = ref(null);

// WebSocket real-time state
const statusMessages = ref([]);
const currentPattern = ref('');
const currentAttempt = ref(null);
const currentTemp = ref(null);
const currentProcessingTime = ref(null);
const currentEvaluation = ref(null);
const attemptsHistory = ref([]);
const finalResult = ref(null);

// Cấu hình
const config = ref({
  temperature: 0.8,
  top_p: 0.9,
  max_retries: 3,
});

// Remove status message
const removeStatusMessage = (index) => {
  statusMessages.value.splice(index, 1);
};

// Clear all real-time data
const clearRealtimeData = () => {
  statusMessages.value = [];
  currentPattern.value = '';
  currentAttempt.value = null;
  currentTemp.value = null;
  currentProcessingTime.value = null;
  currentEvaluation.value = null;
  attemptsHistory.value = [];
  finalResult.value = null;
  isViewingHistory.value = false;
  currentRealTimePattern.value = null;
  currentRealTimeAttempt.value = null;
  currentRealTimeTemp.value = null;
  currentRealTimeProcessingTime.value = null;
  currentRealTimeEvaluation.value = null;
};

// Back to current pattern from history
const backToCurrentPattern = () => {
  if (currentRealTimePattern.value) {
    currentPattern.value = currentRealTimePattern.value;
    currentAttempt.value = currentRealTimeAttempt.value;
    currentTemp.value = currentRealTimeTemp.value;
    currentProcessingTime.value = currentRealTimeProcessingTime.value;
    currentEvaluation.value = currentRealTimeEvaluation.value;
  }
  isViewingHistory.value = false;
  addStatusMessage('Quay lại công thức hiện tại', 'info');
};

// Add status message with duplicate check
const addStatusMessage = (message, type = 'info') => {
  const isDuplicate = statusMessages.value.some(
    (msg) => msg.message === message && msg.type === type
  );

  if (!isDuplicate) {
    statusMessages.value.push({ message, type, timestamp: new Date() });
    setTimeout(() => {
      const index = statusMessages.value.findIndex(
        (m) => m.message === message
      );
      if (index !== -1) statusMessages.value.splice(index, 1);
    }, 6000);
  }
};

// Clear specific type of messages
const clearMessagesByType = (type) => {
  statusMessages.value = statusMessages.value.filter(
    (msg) => msg.type !== type
  );
};

// Handle WebSocket messages
const handleWebSocketMessage = (data) => {
  console.log('WebSocket message:', data); // Debug log

  switch (data.type) {
    case 'status':
      if (data.status === 'generating') {
        clearMessagesByType('info');
      }
      addStatusMessage(
        data.message,
        data.status === 'success'
          ? 'success'
          : data.status === 'error'
            ? 'error'
            : 'info'
      );
      break;

    case 'pattern_update':
      // Lưu real-time pattern
      currentRealTimePattern.value = data.pattern;
      currentRealTimeAttempt.value = data.attempt;
      currentRealTimeTemp.value = data.temperature;

      if (data.generation_time) {
        currentRealTimeProcessingTime.value = data.generation_time;
      } else if (data.processing_time) {
        currentRealTimeProcessingTime.value = data.processing_time;
      }

      if (!isViewingHistory.value) {
        currentPattern.value = data.pattern;
        currentAttempt.value = data.attempt;
        currentTemp.value = data.temperature;
        if (data.generation_time || data.processing_time) {
          currentProcessingTime.value =
            data.generation_time || data.processing_time;
        }
      }

      if (data.is_final) {
        finalResult.value = data;
        // Nếu là final result, cập nhật evaluation từ data
        if (data.gsc !== undefined && data.sfc !== undefined) {
          currentEvaluation.value = {
            gsc: data.gsc,
            sfc: data.sfc,
            errors: data.errors || [],
          };
          // Cập nhật real-time evaluation
          currentRealTimeEvaluation.value = {
            gsc: data.gsc,
            sfc: data.sfc,
            errors: data.errors || [],
          };
        }
      }
      break;

    case 'evaluation':
      // Lưu real-time evaluation
      currentRealTimeEvaluation.value = {
        gsc: data.gsc,
        sfc: data.sfc,
        errors: data.errors,
      };

      if (!isViewingHistory.value) {
        currentEvaluation.value = {
          gsc: data.gsc,
          sfc: data.sfc,
          errors: data.errors,
        };
      }

      // Kiểm tra xem đã có lịch sử cho attempt này chưa
      const existingAttempt = attemptsHistory.value.find(
        (a) => a.attempt === data.attempt
      );

      if (!existingAttempt) {
        attemptsHistory.value.unshift({
          attempt: data.attempt,
          pattern: currentRealTimePattern.value,
          temperature: currentRealTimeTemp.value,
          generation_time:
            data.generation_time || currentRealTimeProcessingTime.value,
          validation_time: data.validation_time,
          total_time: data.total_time,
          gsc: data.gsc,
          sfc: data.sfc,
          is_valid: data.is_valid,
          errors: data.errors,
        });
      } else {
        // Cập nhật thông tin cho attempt đã tồn tại
        existingAttempt.gsc = data.gsc;
        existingAttempt.sfc = data.sfc;
        existingAttempt.is_valid = data.is_valid;
        existingAttempt.errors = data.errors;
      }

      if (!data.is_valid) {
        const invalidMessage = `Công thức lần ${data.attempt} chưa hợp lệ (GSC=${data.gsc?.toFixed(2)}, SFC=${data.sfc?.toFixed(4)}). Đang thử lại...`;
        addStatusMessage(invalidMessage, 'warning');
      } else {
        const successMessage = `✅ Tìm thấy công thức hợp lệ sau ${data.attempt} lần thử!`;
        addStatusMessage(successMessage, 'success');
      }
      break;

    case 'error':
      addStatusMessage(`❌ Lỗi: ${data.message}`, 'error');
      break;

    case 'final_result':
      console.log('Final result received:', data.result); // Debug log

      finalResult.value = data.result;
      loading.value = false;

      // Cập nhật current pattern và evaluation từ kết quả cuối cùng
      if (data.result && data.result.generated_pattern) {
        currentPattern.value = data.result.generated_pattern;
        currentAttempt.value =
          data.result.selected_attempt || data.result.attempts;
        currentTemp.value =
          data.result.temperatures_used?.[
            data.result.temperatures_used.length - 1
          ] || null;
        currentProcessingTime.value = data.result.processing_time;

        // Cập nhật evaluation cho kết quả cuối cùng
        currentEvaluation.value = {
          gsc: data.result.gsc,
          sfc: data.result.sfc,
          errors: data.result.errors || [],
        };

        // Cập nhật real-time evaluation
        currentRealTimeEvaluation.value = {
          gsc: data.result.gsc,
          sfc: data.result.sfc,
          errors: data.result.errors || [],
        };

        // Nếu có lịch sử, cập nhật thông tin cho attempt cuối cùng
        if (attemptsHistory.value.length > 0 && data.result.selected_attempt) {
          const lastAttempt = attemptsHistory.value.find(
            (a) => a.attempt === data.result.selected_attempt
          );
          if (lastAttempt) {
            lastAttempt.gsc = data.result.gsc;
            lastAttempt.sfc = data.result.sfc;
            lastAttempt.is_valid = data.result.is_valid;
            lastAttempt.errors = data.result.errors;
          }
        }
      }

      // Xóa tất cả thông báo cũ và chỉ giữ thông báo hoàn thành
      statusMessages.value = [];

      if (data.result && data.result.is_valid) {
        addStatusMessage(
          '✅ Hoàn thành quá trình tạo công thức! Công thức đã hợp lệ.',
          'success'
        );
      } else if (data.result && data.result.generated_pattern) {
        addStatusMessage(
          `✅ Hoàn thành quá trình tạo công thức! Đã chọn công thức tốt nhất: ${data.result.selection_reason || ''}`,
          'info'
        );
      } else {
        addStatusMessage('✅ Hoàn thành quá trình tạo công thức!', 'success');
      }
      break;
  }
};

// Watch for changes in finalResult to update display
watch(finalResult, (newVal) => {
  if (newVal && newVal.generated_pattern) {
    console.log('Final result updated:', newVal);
    // Đảm bảo currentEvaluation được cập nhật
    if (
      !currentEvaluation.value ||
      currentEvaluation.value.gsc !== newVal.gsc
    ) {
      currentEvaluation.value = {
        gsc: newVal.gsc,
        sfc: newVal.sfc,
        errors: newVal.errors || [],
      };
    }
  }
});

// Generate pattern with WebSocket streaming
const generatePatternStream = async () => {
  if (!imageFile.value) {
    showWarn('Vui lòng chọn ảnh trước khi tạo công thức');
    return;
  }

  loading.value = true;
  clearRealtimeData();

  addStatusMessage('🚀 Bắt đầu tạo công thức móc len...', 'info');

  try {
    await generateCrochetPatternStream(
      imageFile.value,
      {
        temperature: config.value.temperature,
        top_p: config.value.top_p,
        max_retries: config.value.max_retries,
      },
      handleWebSocketMessage
    );
  } catch (error) {
    console.error('Lỗi generate pattern:', error);
    addStatusMessage(`❌ ${error.message || 'Có lỗi xảy ra'}`, 'error');
    loading.value = false;
  }
};

// View attempt history
const viewAttemptHistory = (attempt) => {
  isViewingHistory.value = true;
  currentPattern.value = attempt.pattern;
  currentAttempt.value = attempt.attempt;
  currentTemp.value = attempt.temperature;
  currentProcessingTime.value = attempt.generation_time;
  currentEvaluation.value = {
    gsc: attempt.gsc,
    sfc: attempt.sfc,
    errors: attempt.errors,
  };
  addStatusMessage(`Đang xem lại công thức lần thử ${attempt.attempt}`, 'info');
};

// Format pattern text
const formatPattern = (text) => {
  if (!text) return '';
  return text.replace(/(r\d+:|round\s+\d+:)/gi, '\n$1').trim();
};

// Trigger file selection
const triggerFile = () => fileInput.value?.click();

// Handle file change
const onFileChange = (e) => {
  const file = e.target.files?.[0] || null;
  if (file) {
    if (file.size > 10 * 1024 * 1024) {
      showWarn('File ảnh quá lớn. Vui lòng chọn ảnh dưới 10MB');
      clearImage();
      return;
    }
    imageFile.value = file;
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = URL.createObjectURL(file);
  }
};

// Handle drop
const handleDrop = (e) => {
  isDragOver.value = false;
  const file = e.dataTransfer.files?.[0];
  if (file && file.type.startsWith('image/')) {
    if (file.size > 10 * 1024 * 1024) {
      showWarn('File ảnh quá lớn. Vui lòng chọn ảnh dưới 10MB');
      return;
    }
    imageFile.value = file;
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = URL.createObjectURL(file);
  } else {
    showWarn('Vui lòng kéo thả file ảnh hợp lệ');
  }
};

// Clear image
const clearImage = () => {
  imageFile.value = null;
  if (fileInput.value) fileInput.value.value = '';
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = null;
  }
  clearRealtimeData();
};

// Show warning message
const showWarn = (msg) => {
  warnMsg.value = msg;
  setTimeout(() => (warnMsg.value = ''), 3000);
};

// Cleanup on unmount
onUnmounted(() => {
  // Cleanup any pending WebSocket connections if needed
});
</script>

<style scoped>
.toast-notification-container {
  position: fixed;
  right: 1%;
  top: 30%;
  transform: translateY(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 380px;
  min-width: 30px;
  pointer-events: none;
}

.toast-notification {
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  /* background: var(--white); */
  box-shadow: var(--shadow-soft);
  animation: slideIn 0.3s ease-out;
  transition: all 0.3s ease;
  width: 240px;
  backdrop-filter: blur(10px);
  border: var(--border-light);
}

.toast-notification:hover {
  transform: translateX(-4px);
  box-shadow: var(--shadow-strong);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  color: var(--green-dark);
}

.toast-content {
  flex: 1;
}

.toast-message {
  font-size: 0.9rem;
  line-height: 1.4;
  color: var(--text-color);
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--text-sub);
  transition: color 0.2s;
}

.toast-close:hover {
  color: var(--green-dark);
}

/* Toast types (chỉ dùng tone xanh) */
.toast-info {
  border-left: 5px solid #0ea5e9;
}
.toast-success {
  border-left: 5px solid #22c55e;
}
.toast-warning {
  border-left: 5px solid #f59e0b;
}
.toast-error {
  border-left: 5px solid #ef4444;
}

.toast-info .toast-icon,
.toast-success .toast-icon,
.toast-warning .toast-icon,
.toast-error .toast-icon {
  color: var(--green-dark);
}

/* Placeholder */
.placeholder-glow .placeholder {
  background-color: var(--green-light);
  animation: placeholder-glow 2s ease-in-out infinite;
}

@keyframes placeholder-glow {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    opacity: 0.6;
  }
}

/* Select */
.form-select-sm {
  font-size: 0.875rem;
  padding: 0.25rem 2rem 0.25rem 0.75rem;
  cursor: pointer;
  border: var(--border-light);
}

.form-select-sm:focus {
  border-color: var(--green-main);
  box-shadow: 0 0 0 0.2rem rgba(95, 191, 143, 0.25);
}

/* Pattern */
.pattern-display {
  max-height: 400px;
  overflow-y: auto;
}

.pattern-text {
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  line-height: 1.6;
  color: var(--text-color);
}

/* Current Pattern */
.current-pattern {
  border: var(--border);
  border-radius: 12px;
  padding: 1rem;
  background: var(--white);
  transition: all 0.3s ease;
}

/* History */
.history-section {
  border-top: var(--border-light);
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  cursor: pointer;
  transition: all 0.2s ease;
}

.history-item:hover {
  background: var(--green-light);
  transform: translateX(5px);
  box-shadow: var(--shadow-soft);
}

.history-item.border-success {
  background: var(--green-light);
  border-left: 4px solid var(--green-main);
}

/* Button */
.generate-btn {
  background: var(--green-main);
  color: var(--white);
  border: none;
  padding: 1rem;
  font-size: 1.2rem;
  font-weight: bold;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  /* box-shadow: var(--shadow-soft); */
}

.generate-btn:hover:not(:disabled) {
  background: var(--green-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-strong);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
  }
  .title {
    font-size: 1.5rem;
  }
  .subtitle {
    font-size: 1rem;
  }
  .pattern-display {
    max-height: 300px;
  }

  .toast-notification-container {
    right: 5%;
    left: 5%;
  }
}

/* Page */
.page {
  position: relative;
  background: var(--green-light);
}

.leaf-layer {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.content {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 0.6rem;
  padding-bottom: 2rem;
}

.page-header {
  text-align: center;
}

.title {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1rem;
  color: var(--text-sub);
}

/* Upload */
.upload-area {
  border: 2px dashed var(--green-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--white);
}

.upload-area:hover {
  border-color: var(--green-main);
  background: var(--green-light);
}

.upload-area.dragover {
  border-color: var(--green-dark);
  background: var(--green-light);
}

.upload-area.has-image {
  padding: 0;
}

.upload-icon {
  font-size: 4rem;
  color: var(--green-main);
}

.preview-container {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  object-fit: contain;
}
</style>
