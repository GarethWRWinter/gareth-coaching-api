# scripts/get_latest_file.py

def get_latest_dropbox_file(dbx, folder_path):
    """
    Fetch the most recently modified file from the given Dropbox folder.
    """
    try:
        result = dbx.files_list_folder(folder_path)

        if not result.entries:
            raise Exception(f"No files found in folder: {folder_path}")

        latest_entry = max(
            result.entries,
            key=lambda entry: entry.server_modified
        )

        metadata, response = dbx.files_download(latest_entry.path_display)
        return response

    except Exception as e:
        print(f"Error fetching latest Dropbox file: {e}")
        raise
