from pymongo import MongoClient

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["erh_db"]
diagnosis_collection = db['vital_signs']

def delete_diagnosis_by_record_id(record_id_str):
    """Xóa tất cả document có medical_record_id trùng với chuỗi truyền vào"""
    result = diagnosis_collection.delete_many({"medical_record_id": record_id_str})
    if result.deleted_count > 0:
        print(f"🗑️ Đã xóa {result.deleted_count} document có medical_record_id = {record_id_str}")
    else:
        print(f"⚠️ Không tìm thấy document nào có medical_record_id = {record_id_str}")

def print_all_diagnosis():
    """In tất cả dữ liệu hiện có trong collection diagnosis"""
    print("📋 Dữ liệu còn lại trong collection 'diagnosis':")
    for doc in diagnosis_collection.find():
        print(f"🧾 _id: {doc.get('_id')}, medical_record_id: {doc.get('medical_record_id')}")

if __name__ == "__main__":
    # Bước 1: Xóa theo medical_record_id
    delete_diagnosis_by_record_id("681c5112dfc361a52472d10c")

    # Bước 2: Kiểm tra lại dữ liệu còn lại
    print_all_diagnosis()

# Đóng kết nối
client.close()
