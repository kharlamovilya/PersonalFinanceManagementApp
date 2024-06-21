from calendar import monthrange
from datetime import date as dt

from InquirerPy import inquirer
from InquirerPy.separator import Separator


def select_transaction_date() -> str | None:
    """Menus of transactions' date selection.
    :return: date as a string of format YYYY-MM-DD or None"""
    year = __select_year()
    if year is None:
        return None
    month = __select_month()
    if month is None:
        return None
    day = __select_day(year, month)
    if day is None:
        return None
    return str(dt(year, month, day))


def __select_year() -> int | None:
    """Menu of year selection.
    :return: year as a number from present year to 10 years before present"""
    cur_year = dt.today().year
    cmds = ([str(year + 1) for year in range(cur_year - 10, cur_year)] + [(Separator(line=15 * '_'))] + [
        "Back to menu"])
    cmd = inquirer.select("Choose year of the transaction:", choices=cmds, default=cmds[9]).execute()
    if cmd == "Back to menu":
        return None
    return int(cmd)


def __select_month() -> int | None:
    """Menu of month selection.
    :return: month as a number from 1 to 12 or None
    """
    cur_month = dt.today().month
    cmds = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
            "November", "December", Separator(line=15 * '_'), "Back to menu"]
    cmd = inquirer.select("Choose a month of the transaction:", choices=cmds, default=cmds[cur_month - 1]).execute()
    if cmd == "Back to menu":
        return None
    return cmds.index(cmd) + 1


def __select_day(year: int, month: int) -> int | None:
    """Menu of day selection.
    :return: day as a number from 1 to 31 or None"""
    cur_day = dt.today().day
    days_in_month = monthrange(year, month)[1]
    cmds = [i + 1 for i in range(0, days_in_month)] + [Separator(line=15 * '_')] + ["Back to menu"]
    cmd = inquirer.select("Choose a day of the transaction:", choices=cmds, default=cmds[cur_day - 1]).execute()
    if cmd == "Back to menu":
        return None
    return int(cmd)
