import api from "./axios";
const USERSERVICEURL = 'http://localhost:8001';

const getAllGenderChoices = () => {
    return api.get(`${USERSERVICEURL}/api/u/get-gender-choices`);
}

const postLogin = (data) => {
    return api.post(`${USERSERVICEURL}/api/u/login`, data, {
        headers: {
            'Content-Type': 'application/json',
        }
    });
}
const checkRoleAdmin = (token) => {
    return api.get(`${USERSERVICEURL}/api/u/check-role-admin`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const createDoctor = (formData,token) => {
    return api.post(`${USERSERVICEURL}/api/u/create-doctor`,formData, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const getAllDoctorAdmin = () => {
    return api.get(`${USERSERVICEURL}/api/u/get-all-doctor-admin`);
};
const changeActiveUser = (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/change-active-user`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const getDoctor = (id) => {
    return api.get(`${USERSERVICEURL}/api/u/get-doctor?id=${id}`);
};
const updateDoctor = (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-doctor`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const createNurse = (data,token) => {
    return api.post(`${USERSERVICEURL}/api/u/create-nurse`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const getAllNurseAdmin = () => {
    return api.get(`${USERSERVICEURL}/api/u/get-all-nurse-admin`);
};

const getNurse = (id) => {
    return api.get(`${USERSERVICEURL}/api/u/get-nurse?id=${id}`);
};
const updateNurse = (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-nurse`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};

const createTechnician = (data,token) => {
    return api.post(`${USERSERVICEURL}/api/u/create-technician`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const getAllTechnicianAdmin = () => {
    return api.get(`${USERSERVICEURL}/api/u/get-all-technician-admin`);
};

const getTechnician = (id) => {
    return api.get(`${USERSERVICEURL}/api/u/get-technician?id=${id}`);
};
const updateTechnician = (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-technician`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const createPharmacist = (data,token) => {
    return api.post(`${USERSERVICEURL}/api/u/create-pharmacist`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const getAllPharmacistAdmin = () => {
    return api.get(`${USERSERVICEURL}/api/u/get-all-pharmacist-admin`);
};

const getPharmacist = (id) => {
    return api.get(`${USERSERVICEURL}/api/u/get-pharmacist?id=${id}`);
};
const updatePharmacist = (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-pharmacist`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};



const createCashier = (data,token) => {
    return api.post(`${USERSERVICEURL}/api/u/create-cashier`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },timeout: 30000
    });
};
const getAllCashierAdmin = () => {
    return api.get(`${USERSERVICEURL}/api/u/get-all-cashier-admin`);
};

const getCashier = (id) => {
    return api.get(`${USERSERVICEURL}/api/u/get-cashier?id=${id}`);
};
const updateCashier = (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-cashier`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};

const getSelectAllDoctor = () => {
    return api.get(`${USERSERVICEURL}/api/u/get-select-all-doctor`);
};
const getSelectAllNurse = () => {
    return api.get(`${USERSERVICEURL}/api/u/get-select-all-nurse`);
};

const getAllDoctorHome = () => {
    return api.get(`${USERSERVICEURL}/api/u/get-all-doctor-home`);
};

const getDoctorByUserId = (id) => {
    return api.get(`${USERSERVICEURL}/api/u/get-doctor-by-user-id?id=${id}`);
};

const createPatientRecord = (data,token) => {
    return api.post(`${USERSERVICEURL}/api/u/create-patient-record`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};

const getAllPatientRecordByUser= (token) => {
    return api.get(`${USERSERVICEURL}/api/u/get-all-patient-records-by-user`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getPatientRecordById= (id,token) => {
    return api.get(`${USERSERVICEURL}/api/u/get-patient-record-by-id?id=${id}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const updatePatientRecord= (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-patient-record`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        timeout: 30000
    });
};
const getCashierByToken= (token) => {
    return api.get(`${USERSERVICEURL}/api/u/get-cashier-by-token`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getTechnicianByToken= (token) => {
    return api.get(`${USERSERVICEURL}/api/u/get-technician-by-token`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getDoctorByToken= (token) => {
    return api.get(`${USERSERVICEURL}/api/u/get-doctor-by-token`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getPharmacistByToken= (token) => {
    return api.get(`${USERSERVICEURL}/api/u/get-pharmacist-by-token`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getNurseByToken= (token) => {
    return api.get(`${USERSERVICEURL}/api/u/get-nurse-by-token`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const updateNurseToken= (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-nurse-token`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        time:30000
    });
};

const updatePharmacistToken= (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-pharmacist-token`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const updateTechnicianToken= (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-technician-token`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const updateCashierToken= (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-cashier-token`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const updateDoctorToken= (data,token) => {
    return api.put(`${USERSERVICEURL}/api/u/update-doctor-token`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};

export {
    getAllGenderChoices,
    postLogin,
    checkRoleAdmin,
    createDoctor,
    getAllDoctorAdmin,
    changeActiveUser,
    getDoctor,
    updateDoctor,
    createNurse,
    getAllNurseAdmin,
    getNurse,
    updateNurse,
    createTechnician,
    getAllTechnicianAdmin,
    getTechnician,
    updateTechnician,
    createPharmacist,
    getAllPharmacistAdmin,
    getPharmacist,
    updatePharmacist,
    createCashier,
    getAllCashierAdmin,
    getCashier,
    updateCashier,
    getSelectAllDoctor,
    getSelectAllNurse,
    getAllDoctorHome,
    getDoctorByUserId,
    createPatientRecord,
    getAllPatientRecordByUser,
    getPatientRecordById,
    updatePatientRecord,
    getCashierByToken,
    getTechnicianByToken,
    getDoctorByToken,
    getPharmacistByToken,
    getNurseByToken,
    updateNurseToken,
    updatePharmacistToken,
    updateTechnicianToken,
    updateCashierToken,
    updateDoctorToken
}