import data from '../asset/data/dvhc.json';

export const getAllProvince = () => {
    return data.map((item) => {
        return {
            value: item.Code,
            label: item.FullName
        };
    })
}
export const getWardDistricProvince = (wardId, districtId, provinceId) => {
    let provinceName = '';
    let districtName = '';
    let wardName = '';
    let selectedPro = data.find(item => item.Code === provinceId);
    
    if (selectedPro) {
        provinceName = selectedPro.FullName;
        let selectedDis = selectedPro.District.find(item => item.Code === districtId)
        if(selectedDis) {
            districtName = selectedDis.FullName;
            let selectedWard = selectedDis.Ward.find(item => item.Code ===wardId ) 
            if(selectedWard){
                wardName = selectedWard.FullName  
            }
        }
    }

    return {
        province:provinceName,
        district:districtName,
        ward:wardName
    }
}
export const getAllDistrict = (provinceId) => {
    let dt = data.find(item => item.Code === provinceId);
    if (dt.District) {
        return dt.District.map((it) => {
            return {
                value: it.Code,
                label: it.FullName
            }
        })
    }
    return [];
}
export const getAllWard = (provinceId, districId) => {
    let province = data.find(item => item.Code === provinceId);
    if (province.District) {
        let districts = province.District
        let district = districts.find(item => item.Code === districId);
        if (district.Ward) {
            let wards = district.Ward
            return wards.map((it) => {
                return {
                    value: it.Code,
                    label: it.FullName
                }
            })
        }
    }
    return [];
}

