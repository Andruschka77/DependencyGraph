import argparse
import sys
import os
from DependencyAnalyzer import DependencyAnalyzer
from NPMRepository import NPMRepository
from FileRepository import FileRepository

def main():
    parser = argparse.ArgumentParser(description='Анализатор зависимостей пакетов')
    parser.add_argument('--package', type=str, required=True, help='Имя пакета для анализа (например: react, lodash, express)')
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--url', type=str, help='URL репозитория (например: https://registry.npmjs.org)')
    source_group.add_argument('--file', type=str, help='Путь к файлу с тестовыми данными (например: test_repo.json)')
    parser.add_argument('--test-mode', action='store_true', help='Включить тестовый режим работы')
    parser.add_argument('--max-depth', type=int, default=5, help='Максимальная глубина поиска зависимостей')
    parser.add_argument('--filter', type=str, default='', help='Фильтровать пакеты по названию (например: "test" чтобы исключить тестовые пакеты)')
    parser.add_argument('--load-order', action='store_true', help='Показать порядок загрузки зависимостей')

    try:
        args = parser.parse_args()
    except SystemExit:
        print("\nИспользуйте --help чтобы увидеть все параметры")
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
        if not os.path.exists(args.file):
            errors.append(f"Файл '{args.file}' не существует")
        elif not args.file.lower().endswith('.json'):
            warnings.append("Рекомендуется использовать .json файлы")

    # Проверка глубины
    if args.max_depth <= 0:
        errors.append("Глубина должна быть больше 0")
    elif args.max_depth > 20:
        warnings.append("Большая глубина может работать медленно")

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

    print("\nЭТАП 3:")
    print("=" * 50)

    try:
        if args.file or args.test_mode:
            print("Используется файловый репозиторий")
            repository = FileRepository(args.file)
        else:
            print("Используется npm репозиторий")
            repository = NPMRepository(args.url)

        analyzer = DependencyAnalyzer(
            repository=repository,
            max_depth=args.max_depth,
            filter_str=args.filter
        )

        # Запускаем анализ графа зависимостей
        analyzer.analyze_dependencies(args.package)

        # Показываем результаты этапа 3
        analyzer.display_analysis_results(args.package)

        if args.load_order:
            print("\nЭТАП 4:")
            print("=" * 50)
            analyzer.display_load_order(args.package)
            print("=" * 50)

    except Exception as e:
        print(f"\nОшибка при построении графа: {e}")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()