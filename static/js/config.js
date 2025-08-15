// IMPORTANT: replace the placeholder with your Render backend URL (no trailing slash)
const API_ROOT = "https://hospital-backend-r1uz.onrender.com";

// helper to get Authorization header
function authHeader() {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': 'Bearer ' + token } : {};
}
