import dropbox
from dropbox.exceptions import ApiError

def list_fit_files_in_dropbox(access_token: str, folder_path: str = "/WahooFitness") -> list[str]:
    """
    List all .fit files in the specified Dropbox folder.

    :param access_token: Dropbox access token.
    :param folder_path: Path to the Dropbox folder containing .fit files.
    :return: List of file names.
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
