import api from "./api";

export async function signup(formData) {
    const response = await api.post("/auth/signup", formData);
    return response.data;
}

export async function login(formData) {
    const response = await api.post("/auth/login", formData);
    const { access_token, refresh_token } = response.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    
    return response.data;
}

export async function logout() {
    const response = await api.get("/auth/logout");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    return response.data;
}

export async function resetPassword(email) {
    const response = await api.post("/auth/password_reset", { email });
    return response.data;
}

export async function refreshToken(token) {
    const response = await api.get("/auth/refresh_token", {
        headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
}