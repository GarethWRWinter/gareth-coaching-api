import dropbox

def get_latest_fit_file_from_dropbox(access_token, folder_path="/WahooFitness"):
    dbx = dropbox.Dropbox(access_token)
    res = dbx.files_list_folder(folder_path)
    fit_files = [entry for entry in res.entries if entry.name.endswith(".fit")]
    fit_files.sort(key=lambda x: x.client_modified, reverse=True)

    if fit_files:
        latest_file = fit_files[0]
        local_path = f"/tmp/{latest_file.name}"
        metadata, response = dbx.files_download(path=latest_file.path_display)
        with open(local_path, "wb") as f:
            f.write(response.content)
        return latest_file.name, local_path
    else:
        return None, None
