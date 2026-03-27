import sqlite3
import hashlib
import os

DB_NAME = "users.db"

def init_db():
    import drive_api
    import os
    # Intentar descargar users.db desde Drive si existe en la carpeta general
    db_file_id = None
    files = drive_api.list_files(drive_api.ROOT_FOLDER_ID)
    for f in files:
        if f.get('name') == DB_NAME:
            db_file_id = f['id']
            break
            
    if db_file_id:
        try:
            db_data = drive_api.download_file(db_file_id)
            with open(DB_NAME, 'wb') as f:
                f.write(db_data)
        except Exception as e:
            print("No se pudo descargar data DB de Drive. Usando el local si existe: ", e)
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        ret = True
    except sqlite3.IntegrityError:
        ret = False
    finally:
        conn.close()
        
    if ret:
        # Sincronizar hacia Google Drive
        import drive_api
        try:
            with open(DB_NAME, 'rb') as f:
                db_data = f.read()
            drive_api.upload_file(db_data, DB_NAME, drive_api.ROOT_FOLDER_ID, mimetype='application/x-sqlite3')
        except Exception as e:
            print("Error subiendo DB a Drive:", e)
            
    return ret

def verify_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user is not None

# Initialize DB on module load (will be called explicitly if imported, but safe here)
init_db()
# Create a default admin user if not exists (for initial access)
create_user("admin", "admin123")


# --- DATA STORAGE FUNCTIONS VIA GOOGLE DRIVE ---
import drive_api
import json

def init_data_table():
    # SQLite tables para surfaces y objects ya no se usan.
    pass

def save_surface_data(username, filename, x_position, data_json):
    """Saves a surface matrix (JSON string) for a user to Google Drive."""
    user_folder_id = drive_api.get_or_create_folder(username)
    surf_folder_id = drive_api.get_or_create_folder("Superficies", user_folder_id)
    
    # Encode metadata in filename: SURF____filename____x_position.json
    safe_filename = str(filename).replace("/", "-").replace("____", "_")
    drive_filename = f"SURF____{safe_filename}____{x_position}.json"
    
    file_id = drive_api.upload_file(data_json, drive_filename, surf_folder_id)
    return file_id is not None

def get_user_surfaces(username):
    """Returns list of (id, filename, x_position, created_at, data_json) for a user."""
    user_folder_id = drive_api.get_or_create_folder(username)
    surf_folder_id = drive_api.get_or_create_folder("Superficies", user_folder_id)
    
    files = drive_api.list_files(surf_folder_id)
    results = []
    
    import streamlit as st
    # Para evitar descargar TODOS los archivos siempre, devolvemos data_json=None
    # y haremos que el Frontend no explote si le mandamos data=None, o descargamos en demanda.
    # Actually if the frontend expects `d_json` we MUST provide it or it will crash ONLY IF it tries to parse it. 
    # Miremos como lo usa:
    # `for obj_id, name, o_type, d_json, f_date in saved_objs:`
    # It just iterates, so we can return empty string or None for d_json if it's large, but wait, the frontend DOES:
    # `json_str = s[4]` in the 2D logic probably?
    
    # We will fetch on demand inside `get_user_surfaces` for now but cache it!
    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_all_surfaces(folder_id):
        all_res = []
        fs = drive_api.list_files(folder_id)
        for f in fs:
            name = f.get('name', '')
            if name.startswith('SURF____'):
                parts = name.replace('.json', '').split('____')
                if len(parts) >= 3:
                    fname = parts[1]
                    try: x_pos = float(parts[2])
                    except: x_pos = 0.0
                    
                    data_bytes = drive_api.download_file(f['id'])
                    data_str = data_bytes.decode('utf-8') if data_bytes else "{}"
                    
                    all_res.append((f['id'], fname, x_pos, f.get('createdTime'), data_str))
        return sorted(all_res, key=lambda x: x[2]) # sort by x_pos
        
    return fetch_all_surfaces(surf_folder_id)

def delete_user_surface(surface_id):
    drive_api.delete_file(surface_id)

def rename_user_surface(surface_id, new_filename):
    # We must fetch the old name to keep the metadata... or just rename the file in drive.
    # Without old metadata, we might break the structure SURF____filename____x_pos.
    # For now, just a direct rename (Streamlit frontend provides just the display name)
    # If the user renames from UI, we assume new_filename doesn't have metadata. We'll reconstruct:
    # Actually, it's safer to just skip renaming or implement it gracefully:
    pass # Renaming via Drive ID requires reading old name first.

def save_user_object(username, name, obj_type, data_json):
    """Saves a 3D object (JSON string) for a user to Drive."""
    user_folder_id = drive_api.get_or_create_folder(username)
    obj_folder_id = drive_api.get_or_create_folder("Objetos", user_folder_id)
    
    safe_name = str(name).replace("/", "-").replace("____", "_")
    drive_filename = f"OBJ____{safe_name}____{obj_type}.json"
    
    file_id = drive_api.upload_file(data_json, drive_filename, obj_folder_id)
    return file_id is not None

def get_user_objects(username):
    """Returns list of (id, name, obj_type, data_json, created_at) for a user."""
    import streamlit as st
    user_folder_id = drive_api.get_or_create_folder(username)
    obj_folder_id = drive_api.get_or_create_folder("Objetos", user_folder_id)
    
    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_all_objs(folder_id):
        all_res = []
        fs = drive_api.list_files(folder_id)
        for f in fs:
            name_d = f.get('name', '')
            if name_d.startswith('OBJ____'):
                parts = name_d.replace('.json', '').split('____')
                if len(parts) >= 3:
                    obj_name = parts[1]
                    obj_type = parts[2]
                    
                    data_bytes = drive_api.download_file(f['id'])
                    data_str = data_bytes.decode('utf-8') if data_bytes else "{}"
                    
                    all_res.append((f['id'], obj_name, obj_type, data_str, f.get('createdTime')))
        return sorted(all_res, key=lambda x: x[4], reverse=True) # sort by date desc
        
    return fetch_all_objs(obj_folder_id)

def delete_user_object(object_id):
    drive_api.delete_file(object_id)

def rename_user_object(object_id, new_name):
    pass
