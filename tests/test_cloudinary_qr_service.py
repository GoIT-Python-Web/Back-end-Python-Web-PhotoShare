import pytest
from unittest.mock import patch, MagicMock
from fastapi import UploadFile
from io import BytesIO
from src.services.cloudinary_qr_service import UploadFileService, QrService

# ==== UploadFileService ====

@pytest.mark.asyncio
@patch("src.services.cloudinary_qr_service.cloudinary.uploader.upload")
@patch("src.services.cloudinary_qr_service.cloudinary.CloudinaryImage")
@patch("src.services.cloudinary_qr_service.UploadFileService.configure_cloudinary")
async def test_upload_with_filters_success(mock_configure, mock_cloudinary_image, mock_upload):
    # Мокаємо результат upload
    mock_upload.return_value = {
        "public_id": "test_id",
        "version": "123"
    }

    # Мокаємо метод build_url
    mock_image_instance = MagicMock()
    mock_image_instance.build_url.return_value = "https://example.com/transformed_image.jpg"
    mock_cloudinary_image.return_value = mock_image_instance

    # Створюємо фейковий UploadFile
    file = UploadFile(filename="test.png", file=BytesIO(b"fake image data"))

    result = await UploadFileService.upload_with_filters(file, width=100, height=200, crop="fill", effect="grayscale")

    assert result == "https://example.com/transformed_image.jpg"
    mock_configure.assert_called_once()
    mock_upload.assert_called_once()
    mock_cloudinary_image.assert_called_once_with("test_id")
    mock_image_instance.build_url.assert_called_once()


@pytest.mark.asyncio
@patch("src.services.cloudinary_qr_service.cloudinary.uploader.upload", side_effect=Exception("Upload failed"))
@patch("src.services.cloudinary_qr_service.UploadFileService.configure_cloudinary")
async def test_upload_with_filters_failure(mock_configure, mock_upload):
    file = UploadFile(filename="test.png", file=BytesIO(b"fake image data"))

    with pytest.raises(Exception) as exc_info:
        await UploadFileService.upload_with_filters(file)

    assert "Upload with filters failed" in str(exc_info.value)

# ==== QrService ====

def test_generate_qr_code():
    url = "https://example.com"
    qr_code_data = QrService.generate_qr_code(url)

    assert qr_code_data.startswith("data:image/png;base64,")
    assert isinstance(qr_code_data, str)
