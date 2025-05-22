from pymongo import MongoClient

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["appointment_db"]  # Đổi tên database nếu cần

# Tham chiếu tới collection 'times'
times_collection = db["times"]

def display_times():
    # Lấy tất cả các document trong collection 'times'
    times = times_collection.find()

    # Hiển thị dữ liệu lên terminal
    print("Danh sách thời gian:")
    print("========================")
    
    for time_doc in times:
        time = time_doc.get("time")
        id = time_doc.get("id")  # Lấy giá trị trường id
        print(f"ID: {id} - Time: {time}")
    
    print("========================")

if __name__ == "__main__":
    display_times()

# Đóng kết nối sau khi thực hiện xong
client.close()
