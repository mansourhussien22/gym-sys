import os
from typing import Optional
import cv2
import qrcode

class QRManager:
    QR_FOLDER = os.path.join("data", "qrcodes")

    @classmethod
    def generate_qr(cls, member_id: int, token: str) -> str:
        os.makedirs(cls.QR_FOLDER, exist_ok=True)
        file_path = os.path.join(cls.QR_FOLDER, f"member_{member_id}.png")

        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4,
        )
        qr.add_data(token)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)
        return file_path

    @classmethod
    def decode_qr_image(cls, file_path: str) -> str:
        detector = cv2.QRCodeDetector()
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Could not read image file.")
        data, _, _ = detector.detectAndDecode(img)
        if not data:
            raise ValueError("No valid QR code detected in the selected image.")
        return data.strip()

    @classmethod
    def scan_from_webcam(cls) -> Optional[str]:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Webcam not accessible. Please check your camera permissions.")

        # ضبط دقة الكاميرا لتكون نافذة صغيرة وأنيقة
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        detector = cv2.QRCodeDetector()
        scanned_token = None
        win_title = "FitZone Fast QR Scanner"

        cv2.namedWindow(win_title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(win_title, 560, 420)

        while True:
            # إذا ضغط المستخدم على علامة X الخاصة بالنافذة
            if cv2.getWindowProperty(win_title, cv2.WND_PROP_VISIBLE) < 1:
                break

            ret, frame = cap.read()
            if not ret:
                break

            # قلب الصورة لتبدو كالمرآة
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            # رسم مربع الاستهداف في منتصف الشاشة (Target Box)
            box_size = 220
            x1 = (w - box_size) // 2
            y1 = (h - box_size) // 2
            x2 = x1 + box_size
            y2 = y1 + box_size

            # الكشف عن الكود
            data, bbox, _ = detector.detectAndDecode(frame)
            if data and data.strip():
                scanned_token = data.strip()
                # إظهار إطار أخضر مضيء عند النجاح
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.imshow(win_title, frame)
                cv2.waitKey(200)
                break

            # رسم إطار التصويب وإرشادات الاستخدام
            cv2.rectangle(frame, (x1, y1), (x2, y2), (45, 212, 191), 2)
            cv2.putText(
                frame,
                "Point QR Code inside the box",
                (30, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (45, 212, 191),
                2,
            )
            cv2.putText(
                frame,
                "Press 'ESC' or 'q' to close",
                (30, h - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (180, 180, 180),
                1,
            )

            cv2.imshow(win_title, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord('q'), ord('Q')):
                break

        cap.release()
        cv2.destroyAllWindows()
        return scanned_token