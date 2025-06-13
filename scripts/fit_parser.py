import os
from fitparse import FitFile

# Set FTP from environment or fallback to default (308W)
FTP = int(os.getenv("FTP", 308))

def parse_fit_file(file_path):
    fitfile = FitFile(file_path)
    records = []

    for record in fitfile.get_messages("record"):
        data = {}
        for field in record:
            data[field.name] = field.value
        records.append(data)

    return records
