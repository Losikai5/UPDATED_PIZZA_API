import axios from "axios";

// Backend mounts every router under /api/v2 (see src/__init__.py).
// Set VITE_API_URL at build time for production (e.g. https://api.example.com/api/v2);
// falls back to the local dev server.
const base_url = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v2";

const api = axios.create({
    baseURL: base_url,
    headers: {
        "Content-Type": "application/json"
    }
});

api.interceptors.request.use((config) => {
     const token = localStorage.getItem("access_token"); 
     
     if (token) {
        
        config.headers.Authorization = `Bearer ${token}`;
     }
     
     return config;
}, (error) => {
    return Promise.reject(error);
});

api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        // 1. Get the original request configuration so we can retry it
        const originalRequest = error.config;

        // 2. Check if the server returned a 401 (Unauthorized) 
        // and make sure we haven't already tried to retry this exact request once before
        if (error.response?.status === 401 && !originalRequest._retry) {
            
            // Mark this request so we don't get stuck in an infinite loop if the refresh fails
            originalRequest._retry = true;

            try {
                // 3. Ask the backend for a fresh access token. The refresh endpoint is
                // GET /api/v2/auth/refresh_token and expects the refresh token in the
                // Authorization header (see src/auth/routes.py -> get_refresh_token).
                const refreshToken = localStorage.getItem("refresh_token");

                const response = await axios.get(`${base_url}/auth/refresh_token`, {
                    headers: { Authorization: `Bearer ${refreshToken}` }
                });

                const newAccessToken = response.data.access_token;

                // 4. Save the new working access token back to storage
                localStorage.setItem("access_token", newAccessToken);

                // 5. Update the authorization header of the original, failed request
                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

                // 6. Retry the original request with the brand new token and return it!
                return api(originalRequest);

            } catch (refreshError) {
                // If the refresh token itself is expired, log them out completely
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
                window.location.href = "/login";
                return Promise.reject(refreshError);
            }
        }

        // Always pass the error along if it's not a 401 or if the retry already failed
        return Promise.reject(error);
    }
);
export default api;
