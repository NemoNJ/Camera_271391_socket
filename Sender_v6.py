# send_dual_cam_tcp_fixed.py
import cv2
import socket
import struct
import time

SERVER_IP = "192.168.0.51"   # IP ของคอมที่รันเซิร์ฟเวอร์
SERVER_PORT = 5001

# เปลี่ยนจาก index 0,2 -> เป็นอุปกรณ์ที่มีจริง (จากที่คุณ list มา)
CAM_DEVS = ['/dev/video1', '/dev/video4']  # ถ้าไม่ขึ้นลองสลับ /dev/video3, /dev/video5

def open_cam(dev, w=320, h=240, fps=15):
    cap = cv2.VideoCapture(dev, cv2.CAP_V4L2)
    if not cap.isOpened():
        return None
    # รูปแบบที่เสถียรกับกล้อง USB ส่วนใหญ่
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    cap.set(cv2.CAP_PROP_FPS, fps)
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass
    return cap

def connect_to_server():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # ลด latency ของ TCP เล็กน้อย
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.connect((SERVER_IP, SERVER_PORT))
            print("Connected to server.")
            return s
        except OSError:
            print("Connection failed. Retrying in 3 seconds...")
            time.sleep(3)

def main():
    cap1 = open_cam(CAM_DEVS[0])
    cap2 = open_cam(CAM_DEVS[1])
    if not (cap1 and cap2):
        raise RuntimeError(f'เปิดกล้องไม่ครบ: {[(d, c is not None) for d,c in zip(CAM_DEVS, [cap1, cap2])]}')

    sock = connect_to_server()
    try:
        while True:
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()
            if not (ret1 and ret2):
                print("Failed to capture frame from one or both cameras.")
                time.sleep(0.3)
                continue

            ok1, enc1 = cv2.imencode('.jpg', frame1, [cv2.IMWRITE_JPEG_QUALITY, 80])
            ok2, enc2 = cv2.imencode('.jpg', frame2, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not (ok1 and ok2):
                print("JPEG encode failed.")
                time.sleep(0.1)
                continue

            data1 = enc1.tobytes()
            data2 = enc2.tobytes()

            # โปรโตคอล: [cam_id (1B)][len (8B big-endian)][jpg] x2
            message = (
                b'\x01' + struct.pack('!Q', len(data1)) + data1 +
                b'\x02' + struct.pack('!Q', len(data2)) + data2
            )

            try:
                sock.sendall(message)
            except OSError:
                print("Connection lost. Reconnecting...")
                try:
                    sock.close()
                except Exception:
                    pass
                sock = connect_to_server()

    except KeyboardInterrupt:
        print("\nStopping stream...")
    finally:
        try:
            sock.close()
        except Exception:
            pass
        cap1.release()
        cap2.release()
        print("Connection closed.")

if __name__ == "__main__":
    main()
