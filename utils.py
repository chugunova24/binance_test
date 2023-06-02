from datetime import datetime


def to_timestamp(time: str) -> int:
    """
    :param time: Дата и время в виде строки.
    :return: Возвращает временную отметку в int.
    """

    return int(time.timestamp() * 1000)


def from_timestamp(time: int) -> str:
    """
    :param time: Дата и время в виде временной отметки (int).
    :return: Возвращает дату и время в виде строки.
    """

    return datetime.fromtimestamp(int(time) / 1000)

