from src.parser import parse


def main():
    while True:
        start_url = input(
            'Введите стартовый URL для парсинга (или "exit" для выхода): '
        ).strip()
        if start_url.lower() == 'exit':
            break
        if not start_url:
            print('Ошибка: пустой URL. Попробуйте снова.\n')
            continue

        print(f'\nЗапускаем парсер для сайта: {start_url} ...\n')

        result = parse(start_url)

        print('--- Результат парсинга ---')
        print(f'URL сайта: {result["url"]}')

        print(f'\nНайденные email адреса ({len(result["emails"])}):')
        if result["emails"]:
            for email in result["emails"]:
                print(f'  - {email}')
        else:
            print('  Не найдено')

        print(f'\nНайденные телефоны ({len(result["phones"])}):')
        if result["phones"]:
            for phone in result["phones"]:
                print(f'  - {phone}')
        else:
            print('  Не найдено')

        print('\n' + '='*40 + '\n')


if __name__ == '__main__':
    main()
