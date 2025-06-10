import dropbox
from dropbox.files import FileMetadata

def list_fit_files_in_dropbox(access_token: str, folder_path: str = "/Apps/WahooFitness") -> list[str]:
    dbx = dropbox.Dropbox(access_token)
    fit_files = []
    try:
        result = dbx.files_list_folder(folder_path)
        for entry in result.entries:
            if isinstance(entry, FileMetadata) and entry.name.endswith(".fit"):
                fit_files.append(entry.name)
    except Exception as e:
        print(f"Error listing .fit files: {e}")
    return sorted(fit_files, reverse=True)

def download_fit_file_from_dropbox(access_token: str, folder_path: str, file_name: str, local_path: str) -> None:
    dbx = dropbox.Dropbox(access_token)
    dropbox_path = f"{folder_path}/{file_name}"
    try:
        with open(local_path, "wb") as f:
            metadata, res = dbx.files_download(path=dropbox_path)
            f.write(res.content)
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")
