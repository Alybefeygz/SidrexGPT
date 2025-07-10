import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings

GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')  # .env'den alınmalı
SCOPES = ['https://www.googleapis.com/auth/drive']

def upload_pdf_to_drive(file_obj, filename):
    """
    Verilen dosya objesini Google Drive'a yükler ve paylaşım linkini döndürür.
    :param file_obj: Django UploadedFile veya BytesIO
    :param filename: Dosya adı
    :return: Paylaşım linki (str)
    """
    # Environment variables'tan service account bilgilerini al
    if all(settings.GOOGLE_SERVICE_ACCOUNT_INFO.values()):
        # Environment variables'tan credentials oluştur
        credentials = service_account.Credentials.from_service_account_info(
            settings.GOOGLE_SERVICE_ACCOUNT_INFO, scopes=SCOPES
        )
    else:
        # Fallback: JSON dosyasından oku (backward compatibility)
        GOOGLE_SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sidrexgpts-4f64e5e46ab0.json')
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
    service = build('drive', 'v3', credentials=credentials)

    media = MediaIoBaseUpload(file_obj, mimetype='application/pdf')
    file_metadata = {
        'name': filename,
        'parents': [GOOGLE_DRIVE_FOLDER_ID],
        'mimeType': 'application/pdf',
    }
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    file_id = uploaded.get('id')

    # Dosyayı herkesle paylaş
    service.permissions().create(
        fileId=file_id,
        body={
            'type': 'anyone',
            'role': 'reader',
        },
    ).execute()

    # Paylaşım linkini oluştur
    share_link = f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'
    return share_link 