from pymongo import MongoClient

try:
    # Kết nối tới MongoDB
    client = MongoClient("mongodb://localhost:27017/")

    # Chọn database và collection
    db = client["laboratory_db"]
    diagnosis_collection = db["testresults"]

    # Xóa toàn bộ collection
    diagnosis_collection.drop()

    print("Đã xóa collection 'diagnosis' thành công.")

except Exception as e:
    print(f"Lỗi khi xóa collection: {e}")

finally:
    # Đóng kết nối
    client.close()
