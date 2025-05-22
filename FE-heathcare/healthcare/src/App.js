import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './component/patient/Mainlayout';
import Home from './component/patient/Home';
import Login from '../src/component/patient/login';
import AdminLayout from './component/admin/AdminLayout';
import ManageNurse from './component/admin/ManageNurse';
import ManageDoctor from './component/admin/ManageDoctor';
import ManageTechnician from './component/admin/ManageTechcinian';
import ManagePharmacist from './component/admin/ManagePharmacist';
import ManageSchedule from './component/admin/ManageSchedule';
import ManageCashier from './component/admin/ManageCashier';
import ManageRoom from './component/admin/ManageRoom';
import DetailDoctor from './component/patient/DetailDoctor';
import PatientLayout from './component/patient/PatientLayout';
import ScheduleDoctor from './component/patient/ScheduleDoctor';
import ManageRecord from './component/patient/ManageRecord';
import ManageAppointment from './component/patient/ManageAppointment';
import ManageTypeTest from './component/admin/ManageTypeTest';
import ManageMedicine from './component/admin/ManageMedicine';
import NurseLayout from './component/nurse/NurseLayout';
import NurseMedicalList from './component/nurse/NurseMedicalList';
import NurseInfor from './component/nurse/NurseInfor';
import DoctorLayout from './component/doctor/DoctorLayout';
import DoctorMedicalList from './component/doctor/DoctorMedicalList';
import DoctorSchedule from './component/doctor/DoctorSchedule';
import DoctorInfor from './component/doctor/DoctorInfor';
import NurseSchedule from './component/nurse/NurseSchedule';
import CashierLayout from './component/cashier/CashierLayout';
import CashierInfor from './component/cashier/CashierInfor';
import MedicalList from './component/cashier/MedicalList';
import TechLayout from './component/technician/TechLayout';
import TechMedicalList from './component/technician/TechMedicalList';
import TechnicianInfor from './component/technician/TechnicianInfor';
import PharmacistLayout from './component/pharmacist/PharmacistLayout';
import PharmacistMedicalList from './component/pharmacist/PharmacistMedicalList';
import PharmacistInfor from './component/pharmacist/PharmacistInfor';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route path="/" element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="/home" element={<Home />} />
          <Route path="/detail-doctor/:id" element={<DetailDoctor />} />
          <Route path="schedule/:id" element={<ScheduleDoctor />} />
        </Route>


        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<ManageNurse />} />
          <Route path="manage-user/doctor" element={<ManageDoctor />} />
          <Route path="manage-user/nurse" element={<ManageNurse />} />
          <Route path="manage-user/technician" element={<ManageTechnician />} />
          <Route path="manage-user/pharmacist" element={<ManagePharmacist />} />
          <Route path="manage-user/cashier" element={<ManageCashier />} />
          <Route path="manage-schedules" element={<ManageSchedule />} />
          <Route path="manage-room" element={<ManageRoom />} />
          <Route path="manage-type-test" element={<ManageTypeTest />} />
          <Route path="manage-medicine" element={<ManageMedicine />} />
        </Route>
        <Route path="/patient" element={<PatientLayout />}>
          <Route index element={<ManageRecord />} />
          <Route path="manage-record" element={<ManageRecord />} />
          <Route path="appointment" element={<ManageAppointment />} />
        </Route>
        <Route path="/nurse" element={<NurseLayout />}>
          <Route index element={<NurseMedicalList />} />
          <Route path="list-medical" element={<NurseMedicalList />} />
          <Route path="schedule" element={<NurseSchedule />} />
          <Route path="infor" element={<NurseInfor />} />
        </Route>
        <Route path="/doctor" element={<DoctorLayout />}>
          <Route index element={<DoctorMedicalList />} />
          <Route path="list-medical" element={<DoctorMedicalList />} />
          <Route path="schedule" element={<DoctorSchedule />} />
          <Route path="infor" element={<DoctorInfor />} />
        </Route>
        <Route path="/cashier" element={<CashierLayout />}>
          <Route index element={<MedicalList />} />
          <Route path="list-medical" element={<MedicalList />} />
          <Route path="infor" element={<CashierInfor />} />
        </Route>
        <Route path="/tech" element={<TechLayout />}>
          <Route index element={<TechMedicalList />} />
          <Route path="list-medical" element={<TechMedicalList />} />
          <Route path="infor" element={<TechnicianInfor />} />

        </Route>
        <Route path="/pharmacist" element={<PharmacistLayout />}>
          <Route index element={<PharmacistMedicalList />} />
          <Route path="list-medical" element={<PharmacistMedicalList />} />
          <Route path="infor" element={<PharmacistInfor />} />
        </Route>
      </Routes>
      <ToastContainer
        position='bottom-right'
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </Router>
  );
}

export default App;
