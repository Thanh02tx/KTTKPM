import api from "./axios";
const APPOINTMENT_SERVICE = 'http://localhost:8002';

const createRoom = (data,token) => {
    return api.post(`${APPOINTMENT_SERVICE}/api/a/create-room`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};


const getRooms = () => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-rooms`);
};

const changeActiveRoom = (data,token) => {
    return api.put(`${APPOINTMENT_SERVICE}/api/a/change-active-room`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getRoomById = (id) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-room-by-id?id=${id}`);
};

const updateRoom = (data,token) => {
    return api.put(`${APPOINTMENT_SERVICE}/api/a/update-room`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const createSchedulesAndTimeSlots = (data,token) => {
    return api.post(`${APPOINTMENT_SERVICE}/api/a/create-schedules-and-timeslots`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getSchedulesWeek = (startDate) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-schedules-week?startDate=${startDate}`);
};
const getTimeslotsByDateAndDoctor = (date,doctorId) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-timeslots-by-date-doctorid?date=${date}&doctor_id=${doctorId}`);
};
const getScheduleDoctorByTimeslotId = (id) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-schedule-doctor-by-timeslotid?timeslot_id=${id}`);
};
const checkDuplicateAppointment = (data) => {
    return api.post(`${APPOINTMENT_SERVICE}/api/a/check-duplicate-appointment`,data);
};
const createAppointmentWithMedicalRecord = (data,token) => {
    return api.post(`${APPOINTMENT_SERVICE}/api/a/create-appointment-with-medical-record`,data, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        time:15000
    });
};
const getMedicalByNurseAndDate = (date,token) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-appointment-medical-by-nurse-and-date?date=${date}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getMedicalByDoctorAndDate = (date,token) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-appointment-medical-by-doctor-and-date?date=${date}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};
const getMedicalCashier = (date) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-cashier-appointment-medical-by-date?date=${date}`);
};

const getMedicalById = (id) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-medical-by-id?id=${id}`);
};
const getApptMedicalTestRequestPaidByDate = (date) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-appointment-medical-testrequest-paid-by-date?date=${date}`);
};
const getMedicalByPharmacistAndDate = (date,token) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-appointment-medical-by-pharmacist-and-date?date=${date}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
};

const getHistoryAppointmentByPatient = (id) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-history-appointment-by-patient?patient_id=${id}`);
};
const getDoctorWeeklySchedule = (date,token) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-doctor-weekly-schedule?start_date=${date}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        time:30000
    });
};
const getNurseWeeklySchedule = (date,token) => {
    return api.get(`${APPOINTMENT_SERVICE}/api/a/get-nurse-weekly-schedule?start_date=${date}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        time:30000
    });
};

export {
    createRoom,
    getRooms,
    changeActiveRoom,
    getRoomById,
    updateRoom,
    createSchedulesAndTimeSlots,
    getSchedulesWeek,
    getTimeslotsByDateAndDoctor,
    getScheduleDoctorByTimeslotId,
    checkDuplicateAppointment,
    createAppointmentWithMedicalRecord,
    getMedicalByNurseAndDate,
    getMedicalByDoctorAndDate,
    getMedicalCashier,
    getMedicalById,
    getApptMedicalTestRequestPaidByDate,
    getMedicalByPharmacistAndDate,
    getHistoryAppointmentByPatient,
    getDoctorWeeklySchedule,
    getNurseWeeklySchedule
}