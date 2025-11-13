// src/service.js
import api from '../axios';

// ===== Base URL helper (optional when using `api`) =====
export const API_BASE =
  (typeof import.meta !== 'undefined' &&
    import.meta.env &&
    import.meta.env.VITE_API_BASE) ||
  'http://localhost:8000';

export function withBase(url) {
  if (!url) return url;
  if (/^https?:\/\//i.test(url)) return url;
  return API_BASE + url;
}

/* =========================
 * Auth
 * ========================= */
export async function register(payload) {
  const res = await api.post('/auth/register', payload);
  return res.data;
}

export async function login(payload) {
  const res = await api.post('/auth/login', payload);
  const token = res.data?.access_token;
  if (token) {
    localStorage.setItem('access_token', token);
  }
  return res.data;
}

/* =========================
 * Patterns
 * ========================= */
export async function fetchPatterns(params = {}) {
  const res = await api.get('/patterns', { params });
  return res.data; // array
}

export async function fetchPatternDetail(id) {
  const res = await api.get(`/patterns/${id}`);
  return res.data; // object
}

/* =========================
 * Models (Model Lab)
 * ========================= */
export async function fetchModels() {
  const res = await api.get('/models');
  return res.data;
}

export async function setDefaultModel(code) {
  const res = await api.post(`/models/${code}/default`);
  return res.data;
}

// (Optional) Lấy dữ liệu embed để vẽ 3D scatter
export async function fetchEmbedViz(modelCode) {
  const res = await api.get('/models/embed_viz', {
    params: { model_code: modelCode },
  });
  return res.data;
}

/* =========================
 * Search (ảnh + text / chỉ ảnh / chỉ text)
 * Backend hỗ trợ 3 endpoint:
 *  - POST /search/image  (FormData: model_code, image)
 *  - POST /search/text   (JSON:     model_code, text)
 *  - POST /search/fuse   (FormData: model_code, image, text)
 * Nếu server bạn gom vào /search duy nhất, chỉ cần đổi `endpoint` các nhánh về '/search'
 * ========================= */

/**
 * @param {{ modelCode: string, queryText: string|null, imageFile: File|null }} params
 * @returns {Promise<any[]>} danh sách pattern (BE trả dữ liệu gì thì trả nguyên res.data)
 */
export async function searchPatterns({ modelCode, queryText, imageFile }) {
  const hasText = !!(queryText && String(queryText).trim());
  const hasImage = !!imageFile;

  let endpoint = '/search';
  let res;

  if (hasImage && hasText) {
    // Ảnh + Text
    endpoint = '/search/fuse';
    const fd = new FormData();
    fd.append('model_code', modelCode);
    fd.append('text', String(queryText).trim());
    fd.append('image', imageFile);
    res = await api.post(endpoint, fd, {
      // KHÔNG set 'Content-Type' — axios sẽ tự set multipart boundary
    });
  } else if (hasImage) {
    // Chỉ ảnh
    endpoint = '/search/image';
    const fd = new FormData();
    fd.append('model_code', modelCode);
    fd.append('image', imageFile);
    res = await api.post(endpoint, fd);
  } else {
    // Chỉ text
    endpoint = '/search/text';
    res = await api.post(endpoint, {
      model_code: modelCode,
      text: String(queryText).trim(),
    });
  }

  return res.data;
}
