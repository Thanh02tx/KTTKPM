import api from "./axios";
const ERHSERVICE = 'http://localhost:8005';

const createVitalSign = (data,token) => {
    return api.post(`${ERHSERVICE}/api/e/create-vital-sign`,data,{
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getVitalSignByMedical = (idInput) => {
    return api.get(`${ERHSERVICE}/api/e/get-vitalsign-by-medical?id=${idInput}`,);
};
const createDiagnosisAndTestRequests = (data,token) => {
    return api.post(`${ERHSERVICE}/api/e/create-diagnosis-and-test-requests`,data,{
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};

const getDiagnosisByMedical = (idInput) => {
    return api.get(`${ERHSERVICE}/api/e/get-diagnosis-by-medical?id=${idInput}`,);
};

const doctorUpdateDiagnosisAndStatus = (data,token) => {
    return api.put(`${ERHSERVICE}/api/e/doctor-update-diagnosis-and-status`,data,{
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const getImageDiagnosisByMedicalId = (id) => {
    return api.get(`${ERHSERVICE}/api/e/get-image-diagnosi-by-medical-id?medical_id=${id}`);
};

const predictHeart = (data) => {
    return api.post(`${ERHSERVICE}/api/e/predict-heart`,data);
};

export {
    createVitalSign,
    getVitalSignByMedical,
    createDiagnosisAndTestRequests,
    getDiagnosisByMedical,
    doctorUpdateDiagnosisAndStatus,
    getImageDiagnosisByMedicalId,
    predictHeart

}