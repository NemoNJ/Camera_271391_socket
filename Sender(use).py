import cv2
import socket
import struct
import time

# Set up socket
#server_ip = "192.168.0.247"  # Replace with your PC's IP
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

cap = cv2.VideoCapture(0)  # Change index if using a different camera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 80)  # Reduce resolution for speed
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 60)
cap.set(cv2.CAP_PROP_FPS, 30)  # Set frame rate

client_socket = connect_to_server()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Encode frame as JPEG to reduce size
        _, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        data = encoded_frame.tobytes()
        size = struct.pack("Q", len(data))  # Send frame size first

        try:
            client_socket.sendall(size + data)  # Send frame
        except (socket.error, BrokenPipeError):
            print("Connection lost. Reconnecting...")
            client_socket.close()
            client_socket = connect_to_server()  # Reconnect to server

except KeyboardInterrupt:
    print("\nStopping stream...")

finally:
    cap.release()
    client_socket.close()
    print("Connection closed.")
