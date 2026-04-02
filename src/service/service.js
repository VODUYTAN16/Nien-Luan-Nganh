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
// service.js

// import axios from 'axios';

// Cấu hình axios
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// const api = axios.create({
//   baseURL: API_BASE_URL,
//   timeout: 1200000,
//   headers: {
//     'Content-Type': 'application/json',
//   },
// });

// Thêm interceptor để xử lý lỗi
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

/**
 * Tạo sinh công thức móc len từ ảnh (REST API)
 */
export async function generateCrochetPattern(
  imageFile,
  {
    temperature = 0.8,
    top_p = 0.9,
    max_retries = 3,
    return_invalid = true,
  } = {}
) {
  if (!imageFile) {
    throw new Error('Vui lòng chọn ảnh để tạo công thức');
  }

  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('temperature', temperature.toString());
  formData.append('top_p', top_p.toString());
  formData.append('max_retries', max_retries.toString());
  formData.append('return_invalid', return_invalid.toString());

  try {
    const response = await api.post('/generate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 1200000,
    });

    return response.data;
  } catch (error) {
    console.error('Lỗi khi tạo pattern:', error);

    if (error.response) {
      const status = error.response.status;
      const detail =
        error.response.data?.detail || error.response.data?.message;

      if (status === 400) {
        throw new Error(
          `Lỗi dữ liệu đầu vào: ${detail || 'Vui lòng kiểm tra lại ảnh'}`
        );
      } else if (status === 404) {
        throw new Error(
          `Không tìm thấy endpoint: ${detail || 'Vui lòng kiểm tra lại đường dẫn API'}`
        );
      } else if (status === 500) {
        throw new Error(`Lỗi server: ${detail || 'Vui lòng thử lại sau'}`);
      } else if (status === 503) {
        throw new Error(
          `Service chưa được khởi tạo: ${detail || 'Vui lòng thử lại sau'}`
        );
      } else {
        throw new Error(
          `Lỗi không xác định (${status}): ${detail || 'Vui lòng thử lại sau'}`
        );
      }
    } else if (error.request) {
      throw new Error(
        'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.'
      );
    } else {
      throw new Error(`Lỗi: ${error.message || 'Không thể tạo công thức'}`);
    }
  }
}

/**
 * Tạo sinh công thức với WebSocket real-time
 * @param {File} imageFile - File ảnh
 * @param {Object} params - Tham số
 * @param {Function} onMessage - Callback nhận message từ server
 * @returns {Promise<Object>} Kết quả cuối cùng
 */
export async function generateCrochetPatternStream(
  imageFile,
  { temperature = 0.6, top_p = 0.9, max_retries = 3 } = {},
  onMessage
) {
  return new Promise((resolve, reject) => {
    if (!imageFile) {
      reject(new Error('Vui lòng chọn ảnh để tạo công thức'));
      return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64Image = e.target.result.split(',')[1];

      const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/ws/generate`;
      const ws = new WebSocket(wsUrl);

      let finalResult = null;
      let heartbeatInterval = null;
      let connectionTimeout = null;
      let isResolved = false;

      // Hàm clean up resources
      const cleanup = () => {
        if (heartbeatInterval) {
          clearInterval(heartbeatInterval);
          heartbeatInterval = null;
        }
        if (connectionTimeout) {
          clearTimeout(connectionTimeout);
          connectionTimeout = null;
        }
      };

      // Hàm gửi heartbeat để giữ kết nối
      const sendHeartbeat = () => {
        if (ws.readyState === WebSocket.OPEN && !isResolved) {
          try {
            ws.send(JSON.stringify({ type: 'pong' }));
            console.log('Heartbeat sent');
          } catch (error) {
            console.warn('Failed to send heartbeat:', error);
          }
        }
      };

      // Timeout tổng thể (5 phút) để tránh treo vĩnh viễn
      const totalTimeout = setTimeout(() => {
        if (!isResolved && ws.readyState === WebSocket.OPEN) {
          console.error('Total timeout reached (5 minutes)');
          cleanup();
          ws.close();
          reject(new Error('Quá thời gian chờ (5 phút). Vui lòng thử lại.'));
          isResolved = true;
        }
      }, 300000); // 5 minutes

      ws.onopen = () => {
        console.log('WebSocket connected');

        // Gửi heartbeat mỗi 20 giây để giữ kết nối
        heartbeatInterval = setInterval(sendHeartbeat, 20000);

        // Gửi thông tin khởi tạo
        try {
          ws.send(
            JSON.stringify({
              image: base64Image,
              temperature,
              top_p,
              max_retries,
            })
          );
          console.log('Initial data sent');
        } catch (error) {
          console.error('Failed to send initial data:', error);
          cleanup();
          reject(new Error('Không thể gửi dữ liệu khởi tạo'));
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Received message type:', data.type);

          // Xử lý ping từ server
          if (data.type === 'ping') {
            // Trả lời pong ngay lập tức
            if (ws.readyState === WebSocket.OPEN && !isResolved) {
              ws.send(JSON.stringify({ type: 'pong' }));
              console.log('Pong sent');
            }
            return; // Bỏ qua ping message
          }

          // Gọi callback nếu có
          if (onMessage && !isResolved) {
            onMessage(data);
          }

          // Xử lý các loại message
          switch (data.type) {
            case 'final_result':
              finalResult = data.result;
              isResolved = true;
              cleanup();
              clearTimeout(totalTimeout);
              ws.close();
              resolve(finalResult);
              break;
            case 'error':
              isResolved = true;
              cleanup();
              clearTimeout(totalTimeout);
              ws.close();
              reject(new Error(data.message || 'Lỗi từ server'));
              break;
            case 'status':
              // Status message - tiếp tục chờ
              console.log('Status:', data.status, data.message);
              break;
            case 'pattern_update':
              // Pattern update - tiếp tục chờ
              console.log('Pattern update received for attempt:', data.attempt);
              break;
            case 'evaluation':
              // Evaluation result - tiếp tục chờ
              console.log('Evaluation:', data.gsc, data.sfc);
              break;
          }
        } catch (error) {
          console.error('Error processing message:', error);
          if (!isResolved) {
            cleanup();
            reject(new Error('Lỗi xử lý dữ liệu từ server'));
          }
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (!isResolved) {
          cleanup();
          clearTimeout(totalTimeout);
          reject(new Error('Lỗi kết nối WebSocket. Vui lòng kiểm tra mạng.'));
          isResolved = true;
        }
      };

      ws.onclose = (event) => {
        console.log(
          `WebSocket closed: code=${event.code}, reason=${event.reason || 'No reason'}`
        );
        cleanup();
        clearTimeout(totalTimeout);

        if (!isResolved) {
          // Nếu đóng do lỗi network, thử thông báo lỗi rõ ràng
          if (event.code === 1006) {
            reject(
              new Error(
                'Mất kết nối đến server. Vui lòng kiểm tra mạng và thử lại.'
              )
            );
          } else if (event.code === 1000) {
            // Normal closure, có thể do hoàn thành
            if (!finalResult) {
              reject(new Error('Kết nối đã đóng trước khi nhận kết quả'));
            }
          } else {
            reject(
              new Error(
                `Kết nối đã đóng (${event.code}): ${event.reason || 'Không rõ lý do'}`
              )
            );
          }
          isResolved = true;
        }
      };

      // Optional: Kiểm tra connection health sau 30 giây
      connectionTimeout = setTimeout(() => {
        if (!isResolved && ws.readyState === WebSocket.OPEN) {
          console.log('Connection still alive after 30 seconds');
          // Có thể gửi thêm heartbeat nếu cần
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }
      }, 30000);
    };

    reader.onerror = () => {
      reject(new Error('Không thể đọc file ảnh'));
    };

    reader.readAsDataURL(imageFile);
  });
}
/**
 * Lấy danh sách tất cả pattern (có phân trang)
 * @param {Object} params - Tham số phân trang
 * @param {number} params.limit - Số lượng pattern mỗi trang (mặc định 50)
 * @param {number} params.offset - Vị trí bắt đầu (mặc định 0)
 * @returns {Promise<Object>} Danh sách pattern và thông tin phân trang
 */
export async function getAllPatterns(params = {}) {
  try {
    const response = await api.get('/api/patterns', {
      params: {
        limit: params.limit || 50,
        offset: params.offset || 0,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Lỗi khi lấy danh sách pattern:', error);
    throw handleApiError(error);
  }
}

/**
 * Lấy chi tiết pattern theo tên ảnh
 * @param {string} imageName - Tên file ảnh (ví dụ: "coaster_001.jpg")
 * @returns {Promise<Object>} Chi tiết pattern
 */
export async function getPatternByImageName(imageName) {
  try {
    const response = await api.get(
      `/api/patterns/${encodeURIComponent(imageName)}`
    );
    return response.data;
  } catch (error) {
    console.error(`Lỗi khi lấy pattern ${imageName}:`, error);
    throw handleApiError(error);
  }
}

/**
 * Tìm kiếm pattern theo từ khóa
 * @param {string} keyword - Từ khóa tìm kiếm
 * @param {Object} options - Tùy chọn tìm kiếm
 * @param {number} options.limit - Số lượng kết quả (mặc định 50)
 * @param {number} options.offset - Vị trí bắt đầu (mặc định 0)
 * @returns {Promise<Object>} Kết quả tìm kiếm
 */
export async function searchPatterns(keyword, options = {}) {
  if (!keyword || keyword.trim() === '') {
    throw new Error('Vui lòng nhập từ khóa tìm kiếm');
  }

  try {
    const response = await api.get('/api/search', {
      params: {
        q: keyword.trim(),
        limit: options.limit || 50,
        offset: options.offset || 0,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Lỗi khi tìm kiếm pattern:', error);
    throw handleApiError(error);
  }
}

/**
 * Lấy ảnh của pattern
 * @param {string} imageName - Tên file ảnh
 * @returns {string} URL của ảnh
 */
export function getPatternImageUrl(imageName) {
  if (!imageName) return null;
  return `${API_BASE_URL}/api/images/${encodeURIComponent(imageName)}`;
}

/**
 * Tải ảnh của pattern dưới dạng blob
 * @param {string} imageName - Tên file ảnh
 * @returns {Promise<Blob>} Blob của ảnh
 */
export async function fetchPatternImage(imageName) {
  try {
    const response = await api.get(
      `/api/images/${encodeURIComponent(imageName)}`,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  } catch (error) {
    console.error(`Lỗi khi tải ảnh ${imageName}:`, error);
    throw handleApiError(error);
  }
}

/**
 * Lấy thống kê dataset
 * @returns {Promise<Object>} Thống kê dataset
 */
export async function getDatasetStatistics() {
  try {
    const response = await api.get('/api/statistics');
    return response.data;
  } catch (error) {
    console.error('Lỗi khi lấy thống kê dataset:', error);
    throw handleApiError(error);
  }
}

/**
 * Lấy ngẫu nhiên các pattern
 * @param {number} count - Số lượng pattern muốn lấy (mặc định 5, tối đa 20)
 * @returns {Promise<Object>} Danh sách pattern ngẫu nhiên
 */
export async function getRandomPatterns(count = 5) {
  try {
    const response = await api.get('/api/random', {
      params: { count: Math.min(count, 20) },
    });
    return response.data;
  } catch (error) {
    console.error('Lỗi khi lấy pattern ngẫu nhiên:', error);
    throw handleApiError(error);
  }
}

/**
 * Lấy pattern theo trang với phân trang
 * @param {number} page - Số trang (bắt đầu từ 1)
 * @param {number} pageSize - Số lượng item mỗi trang
 * @returns {Promise<Object>} Pattern theo trang
 */
export async function getPatternsByPage(page = 1, pageSize = 20) {
  const offset = (page - 1) * pageSize;
  const result = await getAllPatterns({ limit: pageSize, offset });

  return {
    patterns: result.patterns,
    total: result.total,
    page: page,
    pageSize: pageSize,
    totalPages: Math.ceil(result.total / pageSize),
    hasNext: result.has_more,
    hasPrev: page > 1,
  };
}

/**
 * Tìm kiếm pattern theo nhiều tiêu chí
 * @param {Object} searchParams - Tham số tìm kiếm
 * @param {string} searchParams.keyword - Từ khóa
 * @param {string} searchParams.patternType - Loại pattern (nếu có)
 * @param {number} searchParams.page - Số trang
 * @param {number} searchParams.pageSize - Số lượng mỗi trang
 * @returns {Promise<Object>} Kết quả tìm kiếm
 */
export async function advancedSearchPatterns(searchParams) {
  const { keyword, page = 1, pageSize = 20 } = searchParams;
  const offset = (page - 1) * pageSize;

  if (!keyword || keyword.trim() === '') {
    return {
      patterns: [],
      total: 0,
      page: 1,
      pageSize: pageSize,
      totalPages: 0,
    };
  }

  const result = await searchPatterns(keyword, { limit: pageSize, offset });

  return {
    patterns: result.patterns,
    total: result.total,
    keyword: result.keyword,
    page: page,
    pageSize: pageSize,
    totalPages: Math.ceil(result.total / pageSize),
    hasNext: result.total > offset + pageSize,
  };
}

/**
 * Lấy tất cả image names (danh sách tên ảnh)
 * @returns {Promise<string[]>} Danh sách tên ảnh
 */
export async function getAllImageNames() {
  try {
    const result = await getAllPatterns({ limit: 1000, offset: 0 });
    return result.patterns.map((p) => p.image_name).filter((name) => name);
  } catch (error) {
    console.error('Lỗi khi lấy danh sách tên ảnh:', error);
    throw handleApiError(error);
  }
}

/**
 * Kiểm tra pattern có tồn tại không
 * @param {string} imageName - Tên ảnh cần kiểm tra
 * @returns {Promise<boolean>} True nếu tồn tại
 */
export async function patternExists(imageName) {
  try {
    await getPatternByImageName(imageName);
    return true;
  } catch (error) {
    if (error.response && error.response.status === 404) {
      return false;
    }
    throw error;
  }
}

/**
 * Export pattern ra file text
 * @param {string} imageName - Tên ảnh
 * @returns {Promise<string>} Nội dung pattern
 */
export async function exportPatternToText(imageName) {
  try {
    const pattern = await getPatternByImageName(imageName);
    if (!pattern || !pattern.pattern) {
      throw new Error('Không tìm thấy pattern');
    }

    // Format pattern để export
    const content = `Pattern: ${pattern.image_name}\n\n${pattern.pattern}\n\nSource: ${pattern.link || 'N/A'}`;
    return content;
  } catch (error) {
    console.error('Lỗi khi export pattern:', error);
    throw handleApiError(error);
  }
}

// Helper function xử lý lỗi API
function handleApiError(error) {
  if (error.response) {
    const status = error.response.status;
    const detail = error.response.data?.detail || error.response.data?.message;

    if (status === 400) {
      return new Error(`Lỗi dữ liệu: ${detail || 'Yêu cầu không hợp lệ'}`);
    } else if (status === 404) {
      return new Error(`Không tìm thấy: ${detail || 'Dữ liệu không tồn tại'}`);
    } else if (status === 500) {
      return new Error(`Lỗi server: ${detail || 'Vui lòng thử lại sau'}`);
    } else if (status === 503) {
      return new Error(
        `Service chưa sẵn sàng: ${detail || 'Vui lòng thử lại sau'}`
      );
    } else {
      return new Error(`Lỗi (${status}): ${detail || 'Vui lòng thử lại sau'}`);
    }
  } else if (error.request) {
    return new Error(
      'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.'
    );
  } else {
    return new Error(`Lỗi: ${error.message || 'Không thể xử lý yêu cầu'}`);
  }
}
