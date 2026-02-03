from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup

from .constants import EMAIL_REGEX, PHONE_REGEX


def normalize_url(url: str) -> str:
    """
    Нормализует URL перед добавлением в очередь обхода.

    На данный момент выполняет две простые, но важные операции:

    1. Удаляет пробелы по краям строки.
    2. Убирает fragment-часть URL (всё после символа '#').

    Пример:
    https://example.com/page#section

    и

    https://example.com/page

    считаются одной и той же страницей для парсера.
    """

    # Убираем лишние пробелы
    url = url.strip()

    # urldefrag удаляет fragment (часть после '#')
    # и возвращает кортеж: (url_without_fragment, fragment)
    url, _ = urldefrag(url)

    return url


def extract_links(
    soup: BeautifulSoup,
    base_url: str,
    base_netloc: str
) -> set[str]:
    """
    Извлекает ссылки со страницы и возвращает только корректные ссылки
    текущего домена.

    Функция:
    - обрабатывает относительные и абсолютные ссылки
    - отбрасывает mailto:, tel:, javascript:
    - нормализует URL
    - возвращает только ссылки того же домена
    """

    links: set[str] = set()

    for link_tag in soup.find_all('a', href=True):
        href = link_tag.get('href')

        if not href:
            continue

        href = href.strip()  # type: ignore

        # Якорные ссылки не ведут на новую страницу
        if href.startswith('#'):
            continue

        # Ссылки на почту, телефон и JS нам не нужны
        if href.startswith('mailto:'):
            continue

        if href.startswith('tel:'):
            continue

        if href.startswith('javascript:'):
            continue

        # Приводим ссылку к абсолютному виду
        absolute_url = urljoin(base_url, href)

        # Убираем fragment (#...)
        absolute_url = normalize_url(absolute_url)

        parsed_link = urlparse(absolute_url)

        # Интересуют только http(s)-страницы
        if parsed_link.scheme not in ('http', 'https'):
            continue

        # Оставляем только ссылки текущего домена
        if parsed_link.netloc != base_netloc:
            continue

        links.add(absolute_url)

    return links


def extract_emails(soup: BeautifulSoup) -> set[str]:
    """
    Извлекает email-адреса из HTML-страницы.

    Поиск выполняется по всему тексту страницы, так как email-адреса
    могут находиться в произвольных местах разметки.
    """

    emails: set[str] = set()

    try:
        page_text = soup.get_text(separator=' ')
    except Exception:
        return emails

    for match in EMAIL_REGEX.findall(page_text):
        emails.add(match.lower())

    return emails


def extract_phones(soup: BeautifulSoup) -> set[str]:
    """
    Извлекает телефоны:
    1) Из тегов <a href="tel:...">
    2) Из текста страницы по PHONE_REGEX
    Возвращает номера как на сайте, включая + и разделители.
    """
    phones: set[str] = set()

    # ищем в тегах <a href="tel:...">
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()  # type: ignore
        if href.lower().startswith('tel:'):
            phones.add(href[4:].strip())  # отбрасываем 'tel:'

    # ищем по тексту с помощью regex
    try:
        page_text = soup.get_text(separator=' ')
    except Exception:
        page_text = ''

    for match in PHONE_REGEX.findall(page_text):
        phones.add(match.strip())

    return phones
