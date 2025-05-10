import io
import dropbox
import pandas as pd
from fitparse import FitFile
import os

def fitfile_to_dataframe(filename: str, access_token: str) -> pd.DataFrame:
    dbx = dropbox.Dropbox(access_token)
    dropbox_path = f"{os.environ.get('DROPBOX_FOLDER', '')}/{filename}"

    # Download the file into a BytesIO buffer
    metadata, res = dbx.files_download(dropbox_path)
    file_stream = io.BytesIO(res.content)

    # Parse the FIT file
    fitfile = FitFile(file_stream)
    records = []

    for record in fitfile.get_messages("record"):
        row = {}
        for field in record:
            row[field.name] = field.value
        records.append(row)

    df = pd.DataFrame(records)
    return df
