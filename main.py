import argparse
import sys
import os
from DependencyAnalyzer import DependencyAnalyzer
from NPMRepository import NPMRepository
from FileRepository import FileRepository


def main():
    # Создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(description='Анализатор и визуализатор зависимостей пакетов')

    # Обязательные аргументы
    parser.add_argument('--package', type=str, required=True, help='Имя пакета для анализа')

    # Взаимоисключающая группа (либо URL, либо файл)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--url', type=str, help='URL репозитория')
    source_group.add_argument('--file', type=str, help='Путь к файлу с тестовыми данными')

    # Опциональные аргументы
    parser.add_argument('--test-mode', action='store_true', help='Включить тестовый режим работы')
    parser.add_argument('--max-depth', type=int, default=5, help='Максимальная глубина поиска зависимостей')
    parser.add_argument('--filter', type=str, default='', help='Фильтровать пакеты по названию')

    # Аргументы для визуализации
    parser.add_argument('--visualize', action='store_true', help='Визуализировать граф зависимостей')
    parser.add_argument('--ascii-tree', action='store_true', help='Показать ASCII-дерево зависимостей')
    parser.add_argument('--generate-image', action='store_true', help='Сгенерировать изображение графа')

    try:
        args = parser.parse_args()
    except SystemExit:
        print("\nИспользуйте --help чтобы увидеть все параметры")
        sys.exit(1)

    # Проверки и обработка ошибок
    errors = []
    warnings = []

    if not args.package.strip():
        errors.append("Имя пакета не может быть пустым")
    if args.url and not args.url.startswith(('http://', 'https://')):
        errors.append("URL должен начинаться с http:// или https://")
    if args.file and not os.path.exists(args.file):
        errors.append(f"Файл '{args.file}' не существует")
    if args.max_depth <= 0:
        errors.append("Глубина должна быть больше 0")

    # Выводим предупреждения и ошибки
    for warning in warnings:
        print(f"Предупреждение: {warning}")
    if errors:
        print("\nОшибки в параметрах:")
        for error in errors:
            print(f"   - {error}")
        print("\nИсправьте ошибки и попробуйте снова")
        sys.exit(1)

    print("\nЭТАП 5")
    print("=" * 60)

    try:
        if args.file or args.test_mode:
            # Используем файловый репозиторий для тестовых данных
            repository = FileRepository(args.file)
        else:
            # Используем NPM репозиторий для реальных данных
            repository = NPMRepository(args.url)

        analyzer = DependencyAnalyzer(
            repository=repository, # Источник данных
            max_depth=args.max_depth, # Макс. глубина анализа
            filter_str=args.filter # Фильтр пакетов
        )

        # Запускаем анализ зависимостей
        analyzer.analyze_dependencies(args.package)

        # Визуализация результатов
        if args.visualize or args.ascii_tree or args.generate_image:
            analyzer.visualize_dependencies(
                args.package,
                ascii_tree=args.ascii_tree, # Показать ASCII-дерево
                generate_image=args.generate_image # Сгенерировать изображение
            )

    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()