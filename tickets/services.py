import io

import segno


def generate_qr_png(qr_token):
    qr = segno.make(qr_token, error="M")
    buffer = io.BytesIO()
    qr.save(buffer, kind="png", scale=8, border=2)
    return buffer.getvalue()
