import cv2
import websockets
import asyncio
import base64
import numpy as np

async def send_frame():
    uri = "ws://10.16.175.13:<PORT>"  # ระบุ IP ของคอมพิวเตอร์และพอร์ตที่ใช้งาน
    async with websockets.connect(uri) as websocket:
        cap = cv2.VideoCapture(0)  # เปิดกล้อง
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # แปลงภาพเป็น JPEG
            _, jpeg = cv2.imencode('.jpg', frame)
            jpeg_bytes = jpeg.tobytes()

            # แปลงเป็น base64 และส่งผ่าน WebSocket
            encoded_image = base64.b64encode(jpeg_bytes).decode('utf-8')
            await websocket.send(encoded_image)

        cap.release()

# เริ่มทำงาน
asyncio.get_event_loop().run_until_complete(send_frame())
