import os
import dropbox
from dropbox.exceptions import ApiError

def get_latest_fit_file_from_dropbox(access_token: str, folder_path: str = "/WahooFitness") -> tuple:
    dbx = dropbox.Dropbox(access_token)
    fit_files = []

    try:
        result = dbx.files_list_folder(folder_path)

        while True:
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata) and entry.name.lower().endswith(".fit"):
                    fit_files.append(entry)

            if not result.has_more:
                break

            result = dbx.files_list_folder_continue(result.cursor)

    except ApiError as e:
        print(f"Dropbox API error: {e}")
        return None, None

    if not fit_files:
        return None, None

    fit_files.sort(key=lambda x: x.server_modified, reverse=True)
    latest_file = fit_files[0]
    local_path = f"/tmp/{latest_file.name}"
    return latest_file.name, local_path

def list_fit_files_in_dropbox(access_token: str, folder_path: str = "/WahooFitness") -> list[str]:
    dbx = dropbox.Dropbox(access_token)
    fit_files = []

    try:
        result = dbx.files_list_folder(folder_path)

        while True:
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata) and entry.name.lower().endswith(".fit"):
                    fit_files.append(entry.name)

            if not result.has_more:
                break

            result = dbx.files_list_folder_continue(result.cursor)

    except ApiError as e:
        print(f"Dropbox API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return fit_files

def download_fit_file_from_dropbox(access_token: str, folder_path: str, file_name: str, local_path: str) -> None:
    dbx = dropbox.Dropbox(access_token)
    file_path = f"{folder_path}/{file_name}"

    try:
        metadata, res = dbx.files_download(path=file_path)
        with open(local_path, "wb") as f:
            f.write(res.content)
        print(f"Downloaded {file_name} to {local_path}")

    except ApiError as e:
        print(f"Dropbox API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
