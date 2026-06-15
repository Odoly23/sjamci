# kni/utils.py
import qrcode
from io import BytesIO
import base64

def generate_qrcode_base64(data, size=150):
    """
    Generate QR Code dari data dan return sebagai base64 string
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # ← Perhatikan: ERROR_CORRECT_L (bukan ERROR_CORRECTION_L)
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    
    return f"data:image/png;base64,{image_base64}"