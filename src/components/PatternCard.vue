<template>
  <div class="pattern-card" @click="$emit('click')">
    <img
      class="thumb"
      :src="imageSrc"
      :alt="pattern.name || pattern.base_name"
    />
    <div class="info">
      <div class="name">
        {{ truncatedDescription }}
      </div>
      <div class="meta">
        <span class="badge">{{ pattern.type || 'coaster' }}</span>
        <span v-if="pattern.difficulty" class="badge soft">
          {{ pattern.difficulty }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { withBase } from '@/service/service';

const props = defineProps({
  pattern: {
    type: Object,
    required: true,
  },
});

defineEmits(['click']);

const imageSrc = computed(() =>
  withBase(props.pattern.top_image_url || props.pattern.image)
);

// caption rút gọn
const truncatedDescription = computed(() => {
  const text =
    (props.pattern.description && props.pattern.description.trim()) ||
    props.pattern.name ||
    props.pattern.base_name ||
    '';

  const maxLen = 70; // chỉnh nếu cần ngắn hơn
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
  color: var(--main-color);
}

.badge.soft {
  background: var(--bg-color);
  color: var(--second-text-color);
}
</style>
