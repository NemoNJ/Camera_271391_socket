import cv2
import socket
import struct
import numpy as np

# Set up socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 8080))  # Listen on all network interfaces
server_socket.listen(5)

print("Waiting for connection...")

def receive_video(conn):
    data = b""
    payload_size = struct.calcsize("Q")

    try:
        while True:
            while len(data) < payload_size:
                packet = conn.recv(4096)
                if not packet:
                    print("Client disconnected.")
                    return
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += conn.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            # Decode JPEG frame
            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)

            cv2.imshow("Real-Time Video", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Stopping stream...")
                return

    except (ConnectionResetError, BrokenPipeError):
        print("Connection lost. Waiting for new connection...")
        return

while True:
    conn, addr = server_socket.accept()
    print(f"Connected to {addr}")
    receive_video(conn)
    conn.close()

server_socket.close()
cv2.destroyAllWindows()
