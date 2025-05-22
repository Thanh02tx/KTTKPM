from pymongo import MongoClient

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["appointment_db"]  # Tên database

# Tham chiếu tới collection 'appointments'
appointments_collection = db['appointments']

def update_payment_status_to_false():
    # Cập nhật tất cả các bản ghi, set payment_status = False
    result = appointments_collection.update_many(
        {},  # Điều kiện rỗng: áp dụng cho tất cả bản ghi
        {"$set": {"payment_status": False}}
    )
    print(f"✅ Đã cập nhật {result.modified_count} bản ghi: 'payment_status' = False")

if __name__ == "__main__":
    update_payment_status_to_false()

# Đóng kết nối
client.close()
