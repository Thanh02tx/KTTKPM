from pymongo import MongoClient
from bson import ObjectId  # Đảm bảo sử dụng ObjectId từ bson

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["appointment_db"]  # Đổi tên database nếu cần

# Tham chiếu tới collection 'rooms'
rooms_collection = db['appointments']

def clear_old_rooms():
    # Xóa collection 'rooms' nếu đã tồn tại
    if rooms_collection:
        rooms_collection.drop()  # Xóa collection
        print("✅ Đã xóa collection 'rooms' cũ!")

if __name__ == "__main__":
    clear_old_rooms()  # Xóa dữ liệu cũ trong collection 'rooms'

# Đóng kết nối sau khi thực hiện xong
client.close()

# from pymongo import MongoClient

# # Kết nối MongoDB
# client = MongoClient("mongodb://localhost:27017/")
# db = client["appointment_db"]
# appointments_collection = db['appointments']

# # Cập nhật tất cả document để thêm trường 'payment_status' nếu chưa có
# result = appointments_collection.update_many(
#     {"payment_status": {"$exists": False}},  # Chỉ cập nhật nếu chưa có trường này
#     {"$set": {"payment_status": False}}
# )

# print(f"✅ Đã cập nhật {result.modified_count} bản ghi.")

# client.close()
