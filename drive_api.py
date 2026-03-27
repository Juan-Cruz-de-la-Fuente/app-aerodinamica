import os
import io
import json
import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']
# ID de la carpeta en Google Drive donde se guardará todo
ROOT_FOLDER_ID = '1mkmYGx0uNmWxxvHTKKrUfGUDZlqTfeOs'

def get_service():
    creds = None
    # Intentamos usar el token OAuth local (token.json)
    token_path = 'token.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    else:
        try:
            # Si no existe local, intentamos buscarlo en los Secrets de Streamlit Cloud
            import streamlit as st
            # Intentar leer desde formato TOML diccionario
            if "gcp_service_account" in st.secrets:
                secret_dict = dict(st.secrets["gcp_service_account"])
                creds = Credentials.from_authorized_user_info(secret_dict, SCOPES)
            # Intentar leer desde formato Texto/JSON crudo pegado 
            elif "google_token_json" in st.secrets:
                try:
                    import json
                    token_str = st.secrets["google_token_json"]
                    secret_dict = json.loads(token_str)
                    creds = Credentials.from_authorized_user_info(secret_dict, SCOPES)
                except Exception as json_e:
                    print("Error interpretando el JSON pegado en secrets:", json_e)
    
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(folder_name, parent_id=ROOT_FOLDER_ID):
    """Busca una carpeta por nombre. Si no existe, la crea y devuelve su ID."""
    service = get_service()
    if not service: return None
    
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', supportsAllDrives=True, includeItemsFromAllDrives=True, fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if not items:
        # Crear la carpeta si no existe
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = service.files().create(body=file_metadata, fields='id', supportsAllDrives=True).execute()
        return folder.get('id')
    return items[0].get('id')

def upload_file(file_content, filename, parent_id, mimetype='application/json'):
    """Sube un archivo a Google Drive dentro de un parent_id (Folder ID) específico."""
    service = get_service()
    if not service: return None
    
    file_metadata = {
        'name': filename,
        'parents': [parent_id]
    }
    
    # Manejar el contenido si es string vs bytes
    if isinstance(file_content, str):
        file_content_io = io.BytesIO(file_content.encode('utf-8'))
    else:
        file_content_io = io.BytesIO(file_content)
        
    media = MediaIoBaseUpload(file_content_io, mimetype=mimetype, resumable=True)
    
    # Revisar si ya hay un archivo con este nombre para sobrescribirlo y no duplicar
    query = f"name='{filename}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', supportsAllDrives=True, includeItemsFromAllDrives=True, fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
        file_id = items[0].get('id')
        service.files().update(fileId=file_id, media_body=media, supportsAllDrives=True).execute()
        return file_id
    else:
        created_file = service.files().create(body=file_metadata, media_body=media, fields='id', supportsAllDrives=True).execute()
        return created_file.get('id')

def list_files(parent_id):
    """Devuelve la lista de archivos dentro de una carpeta."""
    service = get_service()
    if not service: return []
    query = f"'{parent_id}' in parents and mimeType!='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', supportsAllDrives=True, includeItemsFromAllDrives=True, fields='files(id, name, createdTime)').execute()
    return results.get('files', [])

def download_file(file_id):
    """Descarga un archivo dado su ID y lo devuelve como bytes o string."""
    service = get_service()
    if not service: return None
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return fh.getvalue()

def delete_file(file_id):
    """Mueve un archivo a la papelera (para no borrarlo permanentemente por error)."""
    service = get_service()
    if not service: return
    try:
        service.files().update(fileId=file_id, body={'trashed': True}).execute()
    except Exception as e:
        print(f"Error borrando archivo: {e}")

def rename_file(file_id, new_name):
    """Renombra un archivo manteniendo su ID intacto."""
    service = get_service()
    if not service: return
    try:
        service.files().update(fileId=file_id, body={'name': new_name}).execute()
    except Exception as e:
        print(f"Error renombrando archivo: {e}")
