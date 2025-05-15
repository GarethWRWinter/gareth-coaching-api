import io
from fitparse import FitFile

def parse_fit_file(filepath: str) -> list[dict]:
    with open(filepath, "rb") as f:  # ✅ Binary mode
        fit_content = f.read()

    fitfile = FitFile(io.BytesIO(fit_content))

    data = []
    for record in fitfile.get_messages("record"):
        fields = {field.name: field.value for field in record}
        data.append(fields)

    return data
