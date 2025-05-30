import os
import dropbox
from dropbox.exceptions import ApiError


def get_latest_fit_file_from_dropbox(access_token: str, folder_path: str = "/WahooFitness") -> str:
    """
    Get the latest .fit file name in the specified Dropbox folder.

    :param access_token: Dropbox access token.
    :param folder_path: Path to the Dropbox folder containing .fit files.
    :return: Name of the latest .fit file.
    """
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
        return None

    if not fit_files:
        return None

    # Sort by server_modified timestamp to get the most recent
    fit_files.sort(key=lambda x: x.server_modified, reverse=True)
    return fit_files[0].name


def list_fit_files_in_dropbox(access_token: str, folder_path: str = "/WahooFitness") -> list[str]:
    """
    List all .fit files in the specified Dropbox folder.

    :param access_token: Dropbox access token.
    :param folder_path: Path to the Dropbox folder containing .fit files.
    :return: List of .fit file names.
    """
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
    """
    Download a .fit file from Dropbox to a local path.

    :param access_token: Dropbox access token.
    :param folder_path: Dropbox folder containing the .fit file.
    :param file_name: Name of the file to download.
    :param local_path: Local path to save the downloaded file.
    """
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
