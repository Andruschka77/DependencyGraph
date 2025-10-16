import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(
        description='Настройка визуализатора зависимостей (Этап 1)'
    )

    parser.add_argument(
        '--package',
        type=str,
        required=True,
        help='Имя пакета для анализа (например: react, lodash, express)'
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        '--url',
        type=str,
        help='URL репозитория (например: https://registry.npmjs.org)'
    )
    source_group.add_argument(
        '--file',
        type=str,
        help='Путь к файлу с тестовыми данными (например: test_repo.json)'
    )

    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Включить тестовый режим работы'
    )

    parser.add_argument(
        '--ascii-tree',
        action='store_true',
        help='Показывать зависимости в виде ASCII-дерева'
    )

    parser.add_argument(
        '--max-depth',
        type=int,
        default=5,
        help='Максимальная глубина поиска зависимостей (по умолчанию: 5)'
    )

    parser.add_argument(
        '--filter',
        type=str,
        default='',
        help='Фильтровать пакеты по названию (например: "test" чтобы исключить тестовые пакеты)'
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        print("\n💡 Подсказка: используйте --help чтобы увидеть все параметры")
        sys.exit(1)

    errors = []
    warnings = []

    # Проверка имени пакета
    if not args.package.strip():
        errors.append("Имя пакета не может быть пустым")

    if len(args.package) > 100:
        errors.append("Имя пакета слишком длинное")

    # Проверка URL
    if args.url:
        if not args.url.startswith(('http://', 'https://')):
            errors.append("URL должен начинаться с http:// или https://")

    # Проверка файла
    if args.file:
        # Проверяем существует ли директория
        dir_name = os.path.dirname(args.file)
        if dir_name and not os.path.exists(dir_name):
            warnings.append(f"Директория '{dir_name}' не существует")

        # Проверяем расширение файла
        if not args.file.lower().endswith('.json'):
            warnings.append("Рекомендуется использовать .json файлы")

    # Проверка глубины
    if args.max_depth <= 0:
        errors.append("Глубина должна быть больше 0")
    elif args.max_depth > 20:
        warnings.append("Большая глубина может работать медленно")

    # Проверка тестового режима
    if args.test_mode and not args.file:
        warnings.append("Тестовый режим обычно используется с файлами")

    # Показываем предупреждения
    for warning in warnings:
        print(f"Предупреждение: {warning}")

    # Если есть ошибки - показываем и выходим
    if errors:
        print("\nОшибки в параметрах:")
        for error in errors:
            print(f"   - {error}")
        print("\nИсправьте ошибки и попробуйте снова")
        sys.exit(1)

    print("=" * 50)
    print("НАСТРОЙКИ КОТОРЫЕ ВЫ ВЫБРАЛИ:")
    print("=" * 50)
    print(f"Пакет для анализа: {args.package}")

    if args.url:
        print(f"Источник данных:   URL репозитория")
        print(f"URL:               {args.url}")
    else:
        print(f"Источник данных:   Файл")
        print(f"Файл:              {args.file}")

    print(f"Тестовый режим:    {'Да' if args.test_mode else 'Нет'}")
    print(f"ASCII-дерево:      {'Да' if args.ascii_tree else 'Нет'}")
    print(f"Макс. глубина:     {args.max_depth}")
    print(f"Фильтр:            '{args.filter}'" if args.filter else "Фильтр:            не используется")
    print("=" * 50)

if __name__ == "__main__":
    main()