import api from "./api";

export async function get_cart() {
    const response = await api.get("/cart");
    return response.data;
}

export async function add_item(itemData) {
    const response = await api.post("/cart/items", itemData);
    return response.data;
}

export async function update_item(item_id, quantity) {
    const response = await api.patch(`/cart/items/${item_id}`, { quantity });
    return response.data;
}

export async function remove_item(item_id) {
    const response = await api.delete(`/cart/items/${item_id}`);
    return response.data;
}

export async function clear_cart() {
    const response = await api.delete("/cart");
    return response.data;
}