def get_latest_dropbox_file(dbx, folder_path):
    print(f"Looking for .FIT files in: {folder_path}")
    
    try:
        result = dbx.files_list_folder(folder_path)
    except Exception as e:
        print(f"Error accessing Dropbox folder: {e}")
        return None

    # Filter for .fit files only
    fit_files = [
        entry for entry in result.entries
        if entry.name.lower().endswith(".fit") and hasattr(entry, "server_modified")
    ]

    if not fit_files:
        print("No .FIT files found in folder.")
        return None

    # Sort by most recent modified date
    latest_file = sorted(fit_files, key=lambda f: f.server_modified, reverse=True)[0]
    print(f"Latest .FIT file found: {latest_file.name} ({latest_file.server_modified})")
    return latest_file
