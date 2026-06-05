import api from "./api";

// ✅ FIX 1: added export to all functions

export async function get_menu() {
    const response = await api.get("/menu");
    return response.data;
}

// ✅ FIX 2 & 3: item_id is a parameter, use template literal `${item_id}`
export async function get_menu_item(item_id) {
    const response = await api.get(`/menu/${item_id}`);
    return response.data;
}

export async function create_menu_item(formData) {
    const response = await api.post("/menu", formData);
    return response.data;
}

// ✅ FIX 3: item_id passed as parameter
export async function update_menu_item(item_id, formData) {
    const response = await api.patch(`/menu/${item_id}`, formData);
    return response.data;
}

// ✅ FIX 3: item_id passed as parameter
export async function delete_menu_item(item_id) {
    const response = await api.delete(`/menu/${item_id}`);
    return response.data;
}

// ✅ FIX 3 & 4: item_id as parameter, PATCH not GET
export async function toggle_availability(item_id) {
    const response = await api.patch(`/menu/${item_id}/toggle-availability`);
    return response.data;
}