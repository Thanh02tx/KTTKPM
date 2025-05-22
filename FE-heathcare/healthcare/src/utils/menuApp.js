export const menuAdmin = [
    {
        name: 'Quản lý Người dùng',
        menus: [
            {
                name: 'Bác sĩ',
                link: '/admin/manage-user/doctor'
            },
            {
                name: 'Y tá',
                link: '/admin/manage-user/nurse'
            },
            {
                name: 'Kĩ thuật viên',
                link: '/admin/manage-user/technician'
            },
            {
                name: 'Dược sĩ',
                link: '/admin/manage-user/pharmacist'
            },
            {
                name: 'Thu Ngân',
                link: '/admin/manage-user/cashier'
            }

        ]
    },
    {
        name: 'Lịch làm việc',
        menus: [
            {
                name: 'Xếp lịch',
                link: '/admin/manage-schedules'
            },
            {
                name: 'Quản lý Phòng',
                link: '/admin/manage-room'
            }
        ]
    },
    {
        name: 'Quản lý Xét nghiệm - Siêu âm',
        link: '/admin/manage-type-test'
    },
    {
        name: 'Quản lý Thuốc',
        link: '/admin/manage-medicine'
    },
    {
        name: 'Lịch hẹn',
        link: '/admin/appointment'
    }
]

export const menuPatient = [
    {
        name: "Quản Lý Hồ sơ",
        link: "/patient/manage-record"
    },
    {
        name: "Lịch hẹn",
        link: "/patient/appointment"
    },
    {
        name: "Đổi mật khẩu",
        link: "/patient/change-account"
    }
]



export const menuNurse = [
    {
        name: "Bệnh nhân",
        link: "/nurse/list-medical"
    },
    {
        name: "Lịch làm việc",
        link: "/nurse/schedule"
    },
    {
        name: "Thông tin",
        link: "/nurse/infor"
    }
]

export const menuDoctor = [
    {
        name: "Bệnh nhân",
        link: "/doctor/list-medical"
    },
    {
        name: "Lịch làm việc",
        link: "/doctor/schedule"
    },
    {
        name: "Thông tin",
        link: "/doctor/infor"
    }
]


export const menuCashier = [
    {
        name: "Bệnh nhân",
        link: "/cashier/list-medical"
    },
    {
        name: "Thông tin",
        link: "/cashier/infor"
    }
]

export const menuTech = [
    {
        name: "Bệnh nhân",
        link: "/tech/list-medical"
    },
    {
        name: "Thông tin",
        link: "/tech/infor"
    }
]
export const menuPharmacist = [
    {
        name: "Bệnh nhân",
        link: "/pharmacist/list-medical"
    },
        {
        name: "Thông tin",
        link: "/pharmacist/infor"
    },
]