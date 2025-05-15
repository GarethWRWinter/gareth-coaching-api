import io
from fitparse import FitFile

def parse_fit_file(fit_bytes: bytes) -> list[dict]:
    fitfile = FitFile(io.BytesIO(fit_bytes))

    data = []
    for record in fitfile.get_messages("record"):
        fields = {field.name: field.value for field in record}
        data.append(fields)

    return data
