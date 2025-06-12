# scripts/ftp_manager.py

import json
from pathlib import Path

FTP_FILE = Path("/mnt/data/ftp.json")


class FTPManagerError(Exception):
    pass


def load_ftp() -> int:
    if not FTP_FILE.exists():
        raise FTPManagerError("No FTP set. Please POST to /ftp to initialize.")
    data = json.loads(FTP_FILE.read_text())
    return data["ftp"]


def set_ftp(new_ftp: int) -> tuple[int | None, int]:
    old_ftp = None
    if FTP_FILE.exists():
        try:
            old_ftp = load_ftp()
        except FTPManagerError:
            old_ftp = None
    FTP_FILE.write_text(json.dumps({"ftp": new_ftp}))
    return old_ftp, new_ftp
