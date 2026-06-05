import api from "./api";

export async function get_my_notifications() {
    const response = await api.get("/notifications");
    return response.data;
}

export async function get_unread_notifications() {
    const response = await api.get("/notifications/unread");
    return response.data;
}

export async function mark_all_as_read() {
    const response = await api.patch("/notifications/read-all");
    return response.data;
}

export async function mark_notification_as_read(notification_id) {
    const response = await api.patch(`/notifications/${notification_id}/read`);
    return response.data;
}