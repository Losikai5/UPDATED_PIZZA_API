import api from "./api";

// NOTE: the backend mounts the reviews router at /api/v2/review (singular) —
// see src/__init__.py. Keep these paths singular to match it.

export async function get_reviews() {
    const response = await api.get("/review");
    return response.data;
}

export async function create_review(order_id, reviewData) {
    const response = await api.post(`/review/${order_id}`, reviewData);
    return response.data;
}

export async function get_review_by_id(review_id) {
    const response = await api.get(`/review/${review_id}`);
    return response.data;
}

export async function delete_review(review_id) {
    const response = await api.delete(`/review/${review_id}`);
    return response.data;
}

export async function get_reviews_by_user(user_id) {
    const response = await api.get(`/review/user/${user_id}`);
    return response.data;
}