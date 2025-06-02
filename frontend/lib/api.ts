import axios from 'axios';

// Determine the base URL for the API.
// In a Next.js app, environment variables prefixed with NEXT_PUBLIC_ are exposed to the browser.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // You can add other default headers here, like authorization tokens if needed
    // For example, if you store a token in localStorage:
    // 'Authorization': `Bearer ${localStorage.getItem('authToken')}`
  },
});

// You can also add interceptors for request or response handling globally
// For example, to handle errors or refresh tokens:
apiClient.interceptors.response.use(
  (response) => response, // Simply return the response for successful requests
  (error) => {
    // Handle errors globally
    // For example, redirect to login page for 401 errors
    if (error.response && error.response.status === 401) {
      // Handle unauthorized errors, e.g., redirect to login
      // console.error("Unauthorized request, redirecting to login...");
      // window.location.href = '/login'; // Example redirect
    }
    // You can also log errors or transform error messages here
    console.error('API call error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;

// Example usage in a component or page:
// import apiClient from '@/lib/api';
//
// async function fetchData() {
//   try {
//     const response = await apiClient.get('/some-endpoint');
//     console.log(response.data);
//   } catch (error) {
//     console.error('Failed to fetch data:', error);
//   }
// }
