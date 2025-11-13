<template>
  <div class="page">
    <header class="page-header">
      <h2>Embedding Playground</h2>
      <p>
        Khám phá không gian embedding của từng model: mỗi điểm là một mẫu
        pattern.
      </p>
    </header>

    <div class="controls">
      <label>Chọn model:</label>
      <select v-model="selectedModel" @change="fetchData">
        <option v-for="m in models" :key="m.code" :value="m.code">
          {{ m.name }}
        </option>
      </select>

      <label>Lọc theo tag:</label>
      <select v-model="selectedTag">
        <option value="">Tất cả</option>
        <option v-for="t in tags" :key="t" :value="t">
          {{ t }}
        </option>
      </select>
    </div>

    <div class="chart-container" ref="chartRef"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue';
import * as echarts from 'echarts';
import 'echarts-gl';
import { fetchModels, withBase } from '@/service/service';
import axios from 'axios';

const models = ref([]);
const selectedModel = ref(null);

const selectedTag = ref('');
const tags = ref([]);

const rawPoints = ref([]);

const chartRef = ref(null);
let chart = null;

// lọc theo tag
const filteredPoints = computed(() => {
  if (!Array.isArray(rawPoints.value)) return [];
  if (!selectedTag.value) return rawPoints.value;
  return rawPoints.value.filter((p) => p.tag === selectedTag.value);
});

onMounted(async () => {
  try {
    const data = await fetchModels();
    models.value = data || [];
    selectedModel.value = models.value[0]?.code || null;
    if (selectedModel.value) {
      await fetchData();
    }
  } catch (e) {
    console.error('Lỗi khi load models:', e);
  }
});

async function fetchData() {
  if (!selectedModel.value) return;

  try {
    const url = withBase(`/models/embed_viz?model_code=${selectedModel.value}`);
    const { data } = await axios.get(url);

    let arr = [];
    if (Array.isArray(data)) {
      arr = data;
    } else if (data && Array.isArray(data.items)) {
      arr = data.items;
    } else {
      console.warn('embed_viz response không phải array:', data);
    }

    // chỉ nhận điểm hợp lệ
    arr = arr.filter(
      (p) =>
        p &&
        Number.isFinite(p.x) &&
        Number.isFinite(p.y) &&
        (p.z === undefined || Number.isFinite(p.z))
    );

    rawPoints.value = arr;
    tags.value = [...new Set(arr.map((p) => p.tag).filter(Boolean))];

    await nextTick();
    renderChart();
  } catch (err) {
    console.error('Lỗi fetch embed_viz:', err);
    rawPoints.value = [];
    tags.value = [];
    await nextTick();
    renderChart();
  }
}

function renderChart() {
  if (!chartRef.value) return;

  if (chart) chart.dispose();
  chart = echarts.init(chartRef.value);

  const pts = filteredPoints.value;

  // mỗi điểm: [x, y, z, base_name, top_image_url]
  const scatterData = pts.map((p) => [
    p.x,
    p.y,
    p.z ?? 0,
    p.base_name,
    p.top_image_url,
  ]);

  const option = {
    backgroundColor: '#f5f5f8',

    // Tooltip built-in hiển thị ảnh
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.98)',
      borderWidth: 0,
      extraCssText:
        'box-shadow:0 4px 12px rgba(0,0,0,0.16);border-radius:10px;padding:4px;',
      formatter: (params) => {
        const v = params.value;
        if (!v || v.length < 5) return '';
        const baseName = v[3];
        const imgUrl = withBase(v[4]);
        return `
          <div style="text-align:center;">
            <img src="${imgUrl}"
                 style="width:80px;height:80px;border-radius:8px;object-fit:cover;display:block;margin-bottom:4px;" />
            <div style="font-size:11px;color:#333;">${baseName}</div>
          </div>
        `;
      },
    },

    grid3D: {
      boxWidth: 160,
      boxHeight: 120,
      boxDepth: 160,
      environment: '#ffffff',
      axisLine: { lineStyle: { color: '#d0d0d0' } },
      axisPointer: { lineStyle: { color: '#aaa' } },
      viewControl: {
        projection: 'perspective',
        autoRotate: true,
        autoRotateSpeed: 8,
        minDistance: 80,
        maxDistance: 400,
      },
    },

    xAxis3D: {
      type: 'value',
      name: 'PC1',
      nameTextStyle: { color: '#999', fontSize: 10 },
      axisLabel: { show: false },
      axisLine: { lineStyle: { color: '#e0e0e0' } },
      splitLine: { show: false },
    },
    yAxis3D: {
      type: 'value',
      name: 'PC2',
      nameTextStyle: { color: '#999', fontSize: 10 },
      axisLabel: { show: false },
      axisLine: { lineStyle: { color: '#e0e0e0' } },
      splitLine: { show: false },
    },
    zAxis3D: {
      type: 'value',
      name: 'PC3',
      nameTextStyle: { color: '#999', fontSize: 10 },
      axisLabel: { show: false },
      axisLine: { lineStyle: { color: '#e0e0e0' } },
      splitLine: { show: false },
    },

    series: [
      {
        type: 'scatter3D',
        data: scatterData,
        symbolSize: 6,
        itemStyle: {
          color: '#62b5a6',
          opacity: 0.9,
        },
        // tắt label text hoàn toàn (tránh hiện "/static/top/xxx.jpg")
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: false,
          },
          itemStyle: {
            color: '#ff9f7f',
            opacity: 1,
            borderWidth: 1,
            borderColor: '#ffffff',
          },
        },
      },
    ],
  };

  chart.setOption(option);
}

// re-render khi đổi tag
watch(selectedTag, () => {
  if (chart) renderChart();
});
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  color: var(--text-color);
}

.page-header h2 {
  font-size: 20px;
  font-weight: 500;
}

.page-header p {
  font-size: 12px;
  color: var(--second-text-color);
  margin-top: 4px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 12px;
  font-size: 12px;
}

.controls select {
  padding: 4px 8px;
  border-radius: 10px;
  border: var(--border-light);
  font-size: 12px;
}

.chart-container {
  width: 100%;
  height: 600px;
  margin-top: 20px;
  background: #f5f5f8;
  border-radius: 16px;
  box-shadow: var(--box-shadow);
}
</style>
