<template>
  <div class="pattern-card" @click="$emit('click')">
    <img
      class="thumb"
      :src="imageSrc"
      :alt="pattern.image_name || pattern.name"
    />
    <div class="info">
      <div class="name">Sản phẩm mã - {{ truncatedName }}</div>
      <div class="meta">
        <span class="badge">coaster/granny</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { getPatternImageUrl } from '@/service/service';

const props = defineProps({
  pattern: {
    type: Object,
    required: true,
  },
});

defineEmits(['click']);

const imageSrc = computed(() => {
  // Ưu tiên dùng image_name để lấy ảnh từ API
  if (props.pattern.image_name) {
    return getPatternImageUrl(props.pattern.image_name);
  }
  // Fallback cho các field cũ
  return props.pattern.top_image_url || props.pattern.image || '';
});

// Tên hiển thị (lấy từ image_name hoặc pattern)
const truncatedName = computed(() => {
  let text = props.pattern.image_name || props.pattern.name || 'Mẫu không tên';

  // Bỏ đuôi .jpg, .png, .jpeg nếu có
  text = text.replace(/\.(jpg|jpeg|png|gif|webp)$/i, '');

  const maxLen = 70;
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text;
});
</script>

<style scoped>
.pattern-card {
  background: var(--white);
  border-radius: 18px;
  padding: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: all 0.16s ease;
  color: var(--text-color);
}

.pattern-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.06);
}

.thumb {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 14px;
  object-fit: cover;
  background: var(--sub-bg);
}

.info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-color);
  line-height: 1.3;
}

.meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.badge {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--sub-bg);
  color: var(--white);
}

.badge.soft {
  background: var(--bg-color);
  color: var(--second-text-color);
}
</style>
