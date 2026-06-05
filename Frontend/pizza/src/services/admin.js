import api from "./api";

export async function get_dashboard_stats() {
    const response = await api.get("/admin/dashboard");
    return response.data;
}

export async function get_users() {
    const response = await api.get("/admin/users");
    return response.data;
}

export async function get_user(user_id) {
    const response = await api.get(`/admin/users/${user_id}`);
    return response.data;
}

export async function update_user_role(user_id, role) {
    const response = await api.patch(`/admin/users/${user_id}/role`, { role });
    return response.data;
}

export async function update_user_verification(user_id, is_verified) {
    const response = await api.patch(`/admin/users/${user_id}/verify`, { is_verified });
    return response.data;
}