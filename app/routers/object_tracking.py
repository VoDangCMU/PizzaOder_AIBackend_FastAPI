# import cv2
# import numpy as np
# import base64
# import torch
# import asyncio
# from fastapi import FastAPI, WebSocket
# from deep_sort_realtime.deepsort_tracker import DeepSort
# from yolov9.models.common import DetectMultiBackend

# # Cấu hình giá trị
# video_path = "data_ext/highway.mp4"
# conf_threshold = 0.5
# tracking_class = 2  # Lớp đối tượng muốn theo dõi (ví dụ "person")

# # Khởi tạo DeepSort
# tracker = DeepSort(max_age=5)

# # Khởi tạo YOLOv9
# device = "cuda" if torch.cuda.is_available() else "cpu"  # Chọn device (GPU hoặc CPU)

# # Tải mô hình YOLOv9
# model = DetectMultiBackend(weights="weights/yolov9-c.pt", device=device, fuse=True)
# model.eval()

# # Đọc tên lớp từ file classes.names
# with open("data_ext/classes.names") as f:
#     class_names = f.read().strip().split('\n')

# # Tạo màu ngẫu nhiên cho mỗi lớp
# colors = np.random.randint(0, 255, size=(len(class_names), 3))

# # Khởi tạo FastAPI app
# app = FastAPI()

# # Hàm xử lý mỗi frame
# def detect_objects(frame):
#     results = model(frame)
#     detect = []
    
#     for detect_object in results.pred[0]:
#         label, confidence, bbox = detect_object[5], detect_object[4], detect_object[:4]
#         x1, y1, x2, y2 = map(int, bbox)
#         class_id = int(label)

#         if tracking_class is not None:
#             if class_id != tracking_class or confidence < conf_threshold:
#                 continue

#         detect.append([[x1, y1, x2 - x1, y2 - y1], confidence, class_id])

#     tracks = tracker.update_tracks(detect, frame=frame)

#     # Vẽ hộp và ID lên frame
#     for track in tracks:
#         if track.is_confirmed():
#             track_id = track.track_id
#             ltrb = track.to_ltrb()
#             class_id = track.get_det_class()
#             x1, y1, x2, y2 = map(int, ltrb)
#             color = colors[class_id]
#             B, G, R = map(int, color)

#             label = f"{class_names[class_id]}-{track_id}"
#             cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
#             cv2.rectangle(frame, (x1 - 1, y1 - 20), (x1 + len(label) * 12, y1), (B, G, R), -1)
#             cv2.putText(frame, label, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

#     return frame

# # API WebSocket để theo dõi đối tượng
# @app.websocket("/ws/object_tracking")
# async def websocket_object_tracking(websocket: WebSocket):
#     await websocket.accept()

#     cap = cv2.VideoCapture(video_path)

#     if not cap.isOpened():
#         await websocket.close()
#         return

#     try:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             frame = detect_objects(frame)
#             _, buffer = cv2.imencode('.jpg', frame)
#             jpg_as_text = base64.b64encode(buffer).decode('utf-8')

#             await websocket.send_text(jpg_as_text)
#             await asyncio.sleep(0.03)  # Gửi mỗi frame 30 FPS

#     finally:
#         cap.release()
#         await websocket.close()

# # Chạy server với Uvicorn
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import APIRouter

router = APIRouter()

@router.get("/object")
async def home():
    return {"message": "ok"}