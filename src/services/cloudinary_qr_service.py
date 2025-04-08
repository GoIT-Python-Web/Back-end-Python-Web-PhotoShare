import base64
import qrcode 
import cloudinary
import cloudinary.uploader
from io import BytesIO
from fastapi import UploadFile, HTTPException
from src.conf.config import settings


class UploadFileService:
    @staticmethod
    def configure_cloudinary():
        cloudinary.config(
            cloud_name=settings.CLD_NAME,
            api_key=settings.CLD_API_KEY,
            api_secret=settings.CLD_API_SECRET
        )

    @staticmethod
    async def upload_file(file: UploadFile) -> str:
        UploadFileService.configure_cloudinary()

        # Завантаження файлу в Cloudinary
        try:
            result = cloudinary.uploader.upload(file.file)
            public_id = result.get("public_id")

            # Генерація посилання на трансформоване зображення
            src_url = cloudinary.CloudinaryImage(public_id).build_url(
                width=250, height=250, crop="fill", version=result.get("version")
            )
            return src_url
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")


class QrService:
    @staticmethod
    def generate_qr_code(url: str) -> str:
        img = qrcode.make(url)
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        qr_code_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        qr_code_url = f"data:image/png;base64,{qr_code_base64}"
        return qr_code_url
