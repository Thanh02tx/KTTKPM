import api from "./axios";
const PHARMACISTSV = 'http://localhost:8007';

const getAllMedicinesActive = (idInput) => {
    return api.get(`${PHARMACISTSV}/api/p/get-all-medicines-active-select`,);
};
const createPrescriptionAndPrescriptionMedicines = (formData,token) => {
    return api.post(`${PHARMACISTSV}/api/p/create-prescription-and-prescription-medicines`,formData,{
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const getPrescriptionByMedical = (id) => {
    return api.get(`${PHARMACISTSV}/api/p/get-prescription-by-medical-id?medical_id=${id}`,);
};
const getActivePaymentMethods = () => {
    return api.get(`${PHARMACISTSV}/api/p/get-active-payment-method`,);
};
const createInvoice = (formData,token) => {
    return api.post(`${PHARMACISTSV}/api/p/create-invoice`,formData,{
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const getImagePrescriptionByMedicalId = (id) => {
    return api.get(`${PHARMACISTSV}/api/p/get-image-prescription-by-medical-id?medical_id=${id}`,);
};

export {
    getAllMedicinesActive,
    createPrescriptionAndPrescriptionMedicines,
    getPrescriptionByMedical,
    getActivePaymentMethods,
    createInvoice,
    getImagePrescriptionByMedicalId
}
