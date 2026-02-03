import re

MAX_PAGES = 100
REQUEST_TIMEOUT = 10
MIN_PHONE_LENGTH = 6
MAX_PHONE_LENGTH = 18

USER_AGENT = 'Mozilla/5.0 (compatible; SiteParser/1.0)'


EMAIL_REGEX = re.compile(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
)


PHONE_REGEX = re.compile(
    r"""
    ^                       # начало строки
    (?:8|\+7)?              # код страны 8 или +7, необязательный
    [\s\-]?                 # разделитель
    (?:\(?\d{3}\)?[\s\-]?)  # код региона, скобки опционально
    \d{3}                   # первые три цифры номера
    [\s\-]?                 # разделитель
    \d{2}                   # две цифры
    [\s\-]?                 # разделитель
    \d{2}$                  # последние две цифры, конец строки
    """,
    re.VERBOSE
)
