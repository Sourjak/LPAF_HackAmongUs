import qrcode
import io
import base64


def generate_qr_code(data):
    """
    Generates QR code image and returns Base64 string.
    """

    qr = qrcode.QRCode(
        version=None,
        box_size=10,
        border=4
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return img_base64