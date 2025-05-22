import api from "./axios";
const BILLSERVICE = 'http://localhost:8006';

const getActivePaymentMethod = (data,token) => {
    return api.get(`${BILLSERVICE}/api/b/get-active-payment-method`);
};
const createBill = (data,token) => {
    return api.post(`${BILLSERVICE}/api/b/create-bill`,data,{
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};

export {
    getActivePaymentMethod,
    createBill
}