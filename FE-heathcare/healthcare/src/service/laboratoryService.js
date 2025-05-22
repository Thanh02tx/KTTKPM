import api from "./axios";
const LABORATORYSERVICE = 'http://localhost:8003';

const getTypeTypeTest = () => {
    return api.get(`${LABORATORYSERVICE}/api/l/get-typetest-types`);
};

const createTypeTest = (data,token) => {
    return api.post(`${LABORATORYSERVICE}/api/l/create-typetest`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getAllTypeTest = () => {
    return api.get(`${LABORATORYSERVICE}/api/l/get-all-typetest`);
};

const getTypeTestById = (id) => {
    return api.get(`${LABORATORYSERVICE}/api/l/get-typetest-by-id?id=${id}`);
};
const changeActiveTypeTestById = (data,token) => {
    return api.put(`${LABORATORYSERVICE}/api/l/change-active-typetest-by-id`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};


const updateTypeTest = (data,token) => {
    return api.put(`${LABORATORYSERVICE}/api/l/update-typetest`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getTestRequestsByMedicalRecord = (id) => {
    return api.get(`${LABORATORYSERVICE}/api/l/get-test-requests-by-medical-record?id=${id}`);
};
const createTestResult = (data, token) => {
    return api.post(`${LABORATORYSERVICE}/api/l/create-test-result`, data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000 // Thời gian chờ (timeout) tính bằng mili giây, ví dụ 10000ms = 10 giây
    });
};

const getAnnotatedImageTestResultByTestRequest = (id) => {
    return api.get(`${LABORATORYSERVICE}/api/l/get-annotated-image-test-result-by-test-request?id=${id}`);
};
// const getHistoryTestRequestsByMedical = (id) => {
//     return api.get(`${LABORATORYSERVICE}/api/l/get-history-test-requests-by-medical?id=${id}`);
// };


export {
    getTypeTypeTest,
    createTypeTest,
    getAllTypeTest,
    changeActiveTypeTestById,
    getTypeTestById,
    updateTypeTest,
    getTestRequestsByMedicalRecord,
    createTestResult,
    getAnnotatedImageTestResultByTestRequest,
}
