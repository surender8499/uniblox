import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  getProducts: () => api.get('/products'),
  getCart: (userId) => api.get('/cart', { params: { user_id: userId } }),
  addToCart: (userId, productId) => api.post('/cart', { user_id: userId, product_id: productId }),
  checkout: (userId, discountCode) => api.post('/checkout', { user_id: userId, discount_code: discountCode }),
  generateDiscount: () => api.post('/admin/discounts/generate'),
  getStats: () => api.get('/admin/stats'),
};