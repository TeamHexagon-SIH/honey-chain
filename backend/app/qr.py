import os
from urllib.parse import quote

import qrcode
from fastapi import Request


def generate_qr(batch_code: str, request: Request):

    # Determine the current laptop hostname/IP
    host = request.headers.get("host", "127.0.0.1:8000")

    # Remove backend port
    if ":" in host:
        hostname = host.rsplit(":", 1)[0]
    else:
        hostname = host

    # Frontend runs on port 5500
    frontend_url = f"http://{hostname}:5500"

    verification_url = (
        f"{frontend_url}/index.html"
        f"?batch={quote(batch_code)}"
    )

    # QR storage directory
    qr_directory = "backend/data/qr"

    os.makedirs(
        qr_directory,
        exist_ok=True
    )

    file_path = (
        f"{qr_directory}/{batch_code}.png"
    )

    # Generate QR
    qr = qrcode.make(verification_url)

    qr.save(file_path)

    return {
        "batch_code": batch_code,
        "verification_url": verification_url,
        "qr_file": file_path,
        "qr_image_url": f"/qr/{batch_code}.png"
    }