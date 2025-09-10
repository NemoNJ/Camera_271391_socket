import cv2
import socket
import struct
import numpy as np

# Set up socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 8080))
# server_socket.bind(("192.168.0.1", 8080))
server_socket.listen(5)

print("Waiting for connection...")

def receive_video(conn):
    data = b""
    payload_size = struct.calcsize("Q")
    
    # Create windows for both cameras
    cv2.namedWindow("Camera 1", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Camera 2", cv2.WINDOW_NORMAL)

    try:
        while True:
            # Receive data
            while len(data) < (payload_size + 1):  # +1 for camera ID
                packet = conn.recv(4096)
                if not packet:
                    print("Client disconnected.")
                    return
                data += packet
            # # 💡 ถ้า data เกินไป ให้ตัดทิ้ง ไม่งั้นจะ delay
            # if len(data) > msg_size * 2:
            #     # ตัด buffer ให้เหลือเฉพาะ frame ล่าสุด
            #     data = data[-msg_size:]
                
            # Extract camera ID (1 byte)
            camera_id = data[0]
            data = data[1:]
            
            # Extract frame size (8 bytes)
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            # Receive the rest of the frame data
            while len(data) < msg_size:
                data += conn.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            # Decode JPEG frame
            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)

            # Draw lines and text only on Camera 1
            if camera_id == 1:
                height, width, _ = frame.shape
                
                # Calculate the center of the image
                center_x = width // 2
                center_y = height // 2

                # Set new shorter length (1/3 shorter than the original)
                line_length = 100  # Original line length (100 pixels)
                reduced_length = int(line_length)  # Reduce length by 1/3
                # # Draw the yellow line (vertical) - starting from the center, going up
                # cv2.line(frame, (center_x, center_y - reduced_length), (center_x, center_y), (0, 255, 255), 2)  # Yellow

                # # Draw the red line (vertical) - starting from where yellow line ends
                # cv2.line(frame, (center_x, center_y), (center_x, center_y + reduced_length), (0, 0, 255), 2)  # Red

                # Add the "7.5 cm" text
                # font = cv2.FONT_HERSHEY_SIMPLEX
                # cv2.putText(frame, "7.5 cm", (center_x + 10, center_y - reduced_length ), font, 0.5, (0, 255, 255), 2)  # Yellow
                # cv2.putText(frame, "7.5 cm", (center_x + 10, center_y + reduced_length + 10), font, 0.5, (0, 0, 255), 2)  # Red

                # Draw green lines parallel to the yellow line (200 pixels long)
                green_line_length = 62 #ปรับ ความยาวเส้น
                green_line_length_2 = 200 #ปรับ ระดับสูงสุด
                reduced_length = 46 #ปรับ position frame
                #(0, 255, 0) green
                #(0, 0, 255) red
                #vertical line
                # Green line 1 (on the left side of yellow line, 90 pixels offset)
                cv2.line(frame, (center_x - green_line_length, center_y - green_line_length_2), (center_x - green_line_length, center_y + green_line_length_2), (0, 0, 255), 2) 

                # Green line 2 (on the right side of yellow line, 90 pixels offset)
                cv2.line(frame, (center_x + green_line_length, center_y - green_line_length_2), (center_x + green_line_length, center_y + green_line_length_2), (0, 0, 255), 2)  
                cv2.line(frame,(center_x , center_y - green_line_length_2 - reduced_length),(center_x , center_y + green_line_length_2 - reduced_length),(0, 0, 255), 1)
                #horizontal line
                # Green line 1 (อยู่ด้านบนของเส้นเหลือง offset 75 pixels)
                #lower
                cv2.line(frame,(center_x - green_line_length, center_y - green_line_length- reduced_length),(center_x + green_line_length, center_y - green_line_length - reduced_length),(0, 255, 255), 1)

                # Green line 2 (อยู่ด้านล่างของเส้นเหลือง offset 75 pixels)
                cv2.line(frame,(center_x - green_line_length, center_y + green_line_length - reduced_length),(center_x + green_line_length, center_y + green_line_length - reduced_length),(0, 255, 255), 1)
                #center
                cv2.line(frame,(center_x - green_line_length, center_y - reduced_length) ,(center_x + green_line_length, center_y - reduced_length),(0, 0, 255), 1)
                #upper
                cv2.line(frame,(center_x - green_line_length, center_y + 2*green_line_length - reduced_length),(center_x + green_line_length, center_y + 2*green_line_length - reduced_length),(0, 0, 255), 1)
            if camera_id == 2:
                height, width, _ = frame.shape
                # Set new shorter length (1/3 shorter than the original)
                center_x = width // 2
                center_y = height // 2

                # วาดเส้นแนวนอนสีฟ้า ยาว 200 px (100px ซ้าย + 100px ขวา)
                # cv2.line(frame,(center_x - 200, center_y - 50), (center_x + 200, center_y - 50), (0, 255, 255),2)
                # cv2.line(frame,(center_x , center_y - 150), (center_x , center_y + 150), (0, 0, 255),2)
                # cv2.line(frame,(center_x + 100 , center_y - 150), (center_x + 100 , center_y + 150), (0, 0, 255),2)
                # cv2.line(frame,(center_x - 100, center_y - 150), (center_x - 100, center_y + 150), (0, 0, 255),2)
            # Display in appropriate window
            if camera_id == 1:
                frame = cv2.flip(frame, -1)
                cv2.imshow("Camera 1", frame)
            elif camera_id == 2:
                # frame = cv2.flip(frame, -1)
                cv2.imshow("Camera 2", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Stopping stream...")
                return

    except (ConnectionResetError, BrokenPipeError):
        print("Connection lost. Waiting for new connection...")
        return
    finally:
        cv2.destroyAllWindows()

while True:
    conn, addr = server_socket.accept()
    print(f"Connected to {addr}")
    receive_video(conn)
    conn.close()

server_socket.close()
cv2.destroyAllWindows()
