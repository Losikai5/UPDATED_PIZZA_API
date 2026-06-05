import api from "./api";

export async function get_my_addresses() {
    const response = await api.get("/addresses");
    return response.data;
}

export async function create_address(addressData) {
    const response = await api.post("/addresses", addressData);
    return response.data;
}

export async function get_address(address_id) {
    const response = await api.get(`/addresses/${address_id}`);
    return response.data;
}

export async function update_address(address_id, addressData) {
    const response = await api.put(`/addresses/${address_id}`, addressData);
    return response.data;
}

export async function delete_address(address_id) {
    const response = await api.delete(`/addresses/${address_id}`);
    return response.data;
}

export async function set_default_address(address_id) {
    const response = await api.patch(`/addresses/${address_id}/default`);
    return response.data;
}