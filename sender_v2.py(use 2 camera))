import cv2
import socket
import struct
import time

# Set up socket
server_ip = "10.205.101.13"  # Replace with your PC's IP
server_port = 8080

def connect_to_server():
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
            print("Connected to server.")
            return client_socket
        except (socket.error, ConnectionRefusedError):
            print("Connection failed. Retrying in 3 seconds...")
            time.sleep(3)

# Initialize both cameras
cap1 = cv2.VideoCapture(0)  # First camera
cap2 = cv2.VideoCapture(2)  # Second camera (อาจต้องเปลี่ยน index ตามระบบ)

# Reduce resolution for both cameras
for cap in [cap1, cap2]:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 80)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 60)
    cap.set(cv2.CAP_PROP_FPS, 30)

client_socket = connect_to_server()

try:
    while True:
        # Read frames from both cameras
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        
        if not ret1 or not ret2:
            print("Failed to capture frame from one or both cameras.")
            break

        # Encode both frames as JPEG
        _, encoded_frame1 = cv2.imencode('.jpg', frame1, [cv2.IMWRITE_JPEG_QUALITY, 80])
        _, encoded_frame2 = cv2.imencode('.jpg', frame2, [cv2.IMWRITE_JPEG_QUALITY, 80])
        
        # Convert to bytes
        data1 = encoded_frame1.tobytes()
        data2 = encoded_frame2.tobytes()
        
        # Create a combined message with camera identifier
        # Format: [camera_id (1 byte)][size (8 bytes)][data]
        message = (
            b'\x01' + struct.pack("Q", len(data1)) + data1 +
            b'\x02' + struct.pack("Q", len(data2)) + data2
        )

        try:
            client_socket.sendall(message)
        except (socket.error, BrokenPipeError):
            print("Connection lost. Reconnecting...")
            client_socket.close()
            client_socket = connect_to_server()

except KeyboardInterrupt:
    print("\nStopping stream...")

finally:
    cap1.release()
    cap2.release()
    client_socket.close()
    print("Connection closed.")
