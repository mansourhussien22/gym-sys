import os
import qrcode
from typing import Optional


class QRManager:
    QR_FOLDER = "data/qrcodes"

    @classmethod
    def generate_qr(cls, user_id: int, token: str, role: str = "user") -> str:
        os.makedirs(cls.QR_FOLDER, exist_ok=True)
        file_path = os.path.join(cls.QR_FOLDER, f"{role}_{user_id}.png")
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(token)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)
        return file_path

    @classmethod
    def decode_qr_image(cls, image_path: str) -> str:
        import cv2
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not open image file: {image_path}")
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        if not data:
            raise ValueError("No QR code detected in the image.")
        return data

    @classmethod
    def scan_from_webcam(cls) -> Optional[str]:
        if os.environ.get("HEADLESS", "0") == "1":
            raise RuntimeError("Webcam GUI scanner is disabled in headless server mode.")
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return None
            detector = cv2.QRCodeDetector()
            token = None
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                data, bbox, _ = detector.detectAndDecode(frame)
                if data:
                    token = data
                    break
                try:
                    cv2.imshow("FitZone QR Scanner (Press Q to quit)", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                except Exception:
                    break
            cap.release()
            cv2.destroyAllWindows()
            return token
        except Exception as e:
            raise RuntimeError(f"Webcam scan error: {e}")