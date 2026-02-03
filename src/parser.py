import logging
from collections import deque
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from .constants import MAX_PAGES, REQUEST_TIMEOUT, USER_AGENT
from .utils import extract_emails, extract_links, extract_phones, normalize_url

# Настройка базового логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)


def parse(start_url: str) -> dict:
    """
    Основная функция парсера сайта с логированием.

    Аргументы:
        start_url (str): Абсолютный URL сайта, с которого начинается обход.

    Возвращает словарь:
        {
            'url': start_url,
            'emails': [...],  # найденные email-адреса
            'phones': [...]   # найденные номера телефонов
        }
    """

    start_url = normalize_url(start_url)
    base_netloc = urlparse(start_url).netloc

    visited: set[str] = set()
    queue: deque[str] = deque([start_url])

    emails: set[str] = set()
    phones: set[str] = set()

    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})

    with tqdm(total=MAX_PAGES, desc='Обход страниц', unit='стр.') as pbar:
        while queue and len(visited) < MAX_PAGES:
            current_url = normalize_url(queue.popleft())
            parsed_current = urlparse(current_url)

            if current_url in visited or parsed_current.netloc != base_netloc:
                logging.debug(
                    f'Skipping URL '
                    f'(visited or different domain): {current_url}'
                )
                pbar.update(1)
                continue

            visited.add(current_url)

            try:
                response = session.get(
                    current_url,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
            except requests.RequestException as e:
                logging.warning(f'Failed to fetch {current_url}: {e}')
                pbar.update(1)
                continue

            final_url = normalize_url(str(response.url))
            if urlparse(final_url).netloc != base_netloc:
                logging.debug(
                    f'Redirected to different domain, skipping: {final_url}'
                )
                pbar.update(1)
                continue

            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                logging.debug(
                    f'Skipping no-HTML content: {current_url} ({content_type})'
                )
                pbar.update(1)
                continue

            response.encoding = response.apparent_encoding

            try:
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                logging.warning(f'Failed to parse HTML {current_url}: {e}')
                pbar.update(1)
                continue

            # Извлечение контактов с логированием найденного количества
            page_emails = extract_emails(soup)
            page_phones = extract_phones(soup)

            emails.update(page_emails)
            phones.update(page_phones)

            # Извлечение ссылок
            page_links = extract_links(
                soup=soup,
                base_url=final_url,
                base_netloc=base_netloc
            )

            for link in page_links:
                if link not in visited and link not in queue:
                    queue.append(link)

            pbar.update(1)

    return {
        'url': start_url,
        'emails': sorted(emails),
        'phones': sorted(phones),
    }
