import api from "./api";

// Customer & Admin
export async function get_orders() {
    const response = await api.get("/orders");
    return response.data;
}

export async function create_order(orderData) {
    const response = await api.post("/orders", orderData);
    return response.data;
}

export async function get_my_orders() {
    const response = await api.get("/orders/me");
    return response.data;
}

export async function update_order(order_id, orderData) {
    const response = await api.put(`/orders/${order_id}`, orderData);
    return response.data;
}

export async function delete_order(order_id) {
    const response = await api.delete(`/orders/${order_id}`);
    return response.data;
}

export async function get_order_by_id(order_id) {
    const response = await api.get(`/orders/${order_id}`);
    return response.data;
}

export async function get_orders_by_user(user_id) {
    const response = await api.get(`/orders/user/${user_id}`);
    return response.data;
}

export async function cancel_order(order_id) {
    const response = await api.post(`/orders/${order_id}/cancel`);
    return response.data;
}

// Admin/Staff only
export async function accept_order(order_id) {
    const response = await api.put(`/orders/${order_id}/accept`);
    return response.data;
}

export async function mark_delivered(order_id) {
    const response = await api.put(`/orders/${order_id}/delivered`);
    return response.data;
}

export async function update_order_status(order_id, order_status) {
    const response = await api.patch(`/orders/${order_id}/status`, { order_status });
    return response.data;
}