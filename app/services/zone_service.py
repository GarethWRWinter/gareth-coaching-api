"""Power and HR zone calculations."""

from app.core.formulas import hr_zones as calc_hr_zones
from app.core.formulas import power_zones as calc_power_zones
from app.models.user import User


def get_zones(user: User) -> dict:
    """Get power and HR zones for a user based on their FTP and max HR."""
    result = {"ftp": user.ftp, "power_zones": None, "hr_zones": None}

    if user.ftp and user.ftp > 0:
        result["power_zones"] = calc_power_zones(user.ftp)

    if user.max_hr and user.max_hr > 0:
        result["hr_zones"] = calc_hr_zones(user.max_hr, user.resting_hr)

    return result
