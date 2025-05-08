from pymongo import MongoClient
from bson import ObjectId  # Đảm bảo sử dụng ObjectId từ bson

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["appointment_db"]  # Đổi tên database nếu cần

# Tham chiếu tới collection 'times'
times_collection = db["times"]

def clear_old_data():
    # Xóa collection 'times' nếu đã tồn tại
    if times_collection:
        times_collection.drop()  # Xóa collection
        print("✅ Đã xóa collection 'times' cũ!")

def init_times():
    time_ranges = [
        "07:00 - 08:00",
        "08:00 - 09:00",
        "09:00 - 10:00",
        "10:00 - 11:00",
        "13:00 - 14:00",
        "14:00 - 15:00",
        "15:00 - 16:00",
    ]

    for t in time_ranges:
        # Kiểm tra xem thời gian đã tồn tại trong collection chưa
        if times_collection.count_documents({"time": t}) == 0:
            # Nếu chưa tồn tại thì thêm mới với trường 'id' là ObjectId
            new_id = ObjectId()  # Tạo ObjectId duy nhất
            times_collection.insert_one({"id": new_id, "time": t})
            print(f"✅ Đã tạo: {new_id} - Time: {t}")
        else:
            print(f"⚠️ Đã tồn tại: {t}")

if __name__ == "__main__":
    clear_old_data()  # Xóa dữ liệu cũ trước khi thêm mới
    init_times()  # Thêm dữ liệu mới vào collection

# Đóng kết nối sau khi thực hiện xong
client.close()
