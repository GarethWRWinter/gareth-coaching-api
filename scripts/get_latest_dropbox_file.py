import dropbox
from dropbox.exceptions import ApiError

def get_latest_dropbox_file(access_token: str, folder_path: str):
    print(f"Looking for .FIT files in: {folder_path}")
    try:
        dbx = dropbox.Dropbox(access_token)
        result = dbx.files_list_folder(folder_path)
    except Exception as e:
        print(f"Error accessing Dropbox folder: {e}")
        return None

    latest_file = None
    latest_time = None

    for entry in result.entries:
        if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith(".fit"):
            file_time = entry.server_modified
            if latest_time is None or file_time > latest_time:
                latest_file = entry
                latest_time = file_time

    if latest_file:
        print(f"Latest .FIT file found: {latest_file.name} ({latest_time})")
    else:
        print("No .FIT files found in Dropbox.")

    return latest_file
