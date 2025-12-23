"""QR code generation service."""
import io
import qrcode
from PIL import Image


def generate_qr_code(ticket_token: str, size: int = 400) -> bytes:
    """
    Generate QR code image as bytes.
    
    Args:
        ticket_token: Unique token for the ticket
        size: Size of the QR code image (default: 400x400)
    
    Returns:
        Bytes of the QR code image (PNG format)
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(ticket_token)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize to desired size
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    
    return img_bytes.read()
