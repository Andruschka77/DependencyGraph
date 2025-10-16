import argparse
import sys
import os
import urllib.request
import urllib.error
import json
from typing import List, Dict

def get_npm_dependencies(package_name: str, registry_url: str) -> List[str]:
    try:
        # Формируем URL для запроса информации о пакете
        url = f"{registry_url.rstrip('/')}/{package_name}"

        print(f"Запрос информации о пакете {package_name}...")
        print(f"URL: {url}")

        # Создаем запрос с заголовками
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'DependencyVisualizer/1.0',
                'Accept': 'application/json'
            }
        )

        # Выполняем HTTP запрос
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status != 200:
                raise Exception(f"HTTP ошибка: {response.status}")

            data = json.loads(response.read().decode('utf-8'))

        # Извлекаем информацию о последней версии
        if 'dist-tags' in data and 'latest' in data['dist-tags']:
            latest_version = data['dist-tags']['latest']
        else:
            # Если нет latest тега, берем последнюю версию из списка
            versions = list(data.get('versions', {}).keys())
            if not versions:
                raise Exception("Не найдено ни одной версии пакета")
            latest_version = sorted(versions)[-1]

        # Получаем данные о конкретной версии
        version_data = data['versions'].get(latest_version)
        if not version_data:
            raise Exception(f"Данные для версии {latest_version} не найдены")

        # Извлекаем зависимости
        dependencies = []

        # Проверяем разные типы зависимостей
        dependency_sections = ['dependencies', 'peerDependencies', 'optionalDependencies']

        for section in dependency_sections:
            if section in version_data and version_data[section]:
                for dep_name, dep_version in version_data[section].items():
                    dependencies.append({
                        'name': dep_name,
                        'version': dep_version,
                        'type': section.replace('Dependencies', '')
                    })

        print(f"Найдена версия: {latest_version}")
        return dependencies

    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise Exception(f"Пакет '{package_name}' не найден в репозитории")
        else:
            raise Exception(f"HTTP ошибка при запросе пакета: {e.code}")
    except urllib.error.URLError as e:
        raise Exception(f"Ошибка сети: {e.reason}")
    except json.JSONDecodeError as e:
        raise Exception(f"Ошибка разбора JSON ответа: {e}")
    except Exception as e:
        raise Exception(f"Ошибка при получении зависимостей: {e}")


def display_dependencies(package_name: str, dependencies: List[Dict]):
    print(f"ПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА - {package_name}:")

    if not dependencies:
        print("\nУ этого пакета нет зависимостей")
        print("=" * 50)
        return

    # Простой вывод без группировки - сначала убедимся что зависимости есть
    print("\nВСЕ ЗАВИСИМОСТИ:")
    for i, dep in enumerate(dependencies, 1):
        print(f"   {i:2d}. {dep['name']} — {dep['version']}")

    print(f"\nВсего зависимостей: {len(dependencies)}")
    print("=" * 50)

def main():
    parser = argparse.ArgumentParser(
        description='Настройка визуализатора зависимостей'
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
        print("\nПодсказка: используйте --help чтобы увидеть все параметры")
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

    if args.url and not args.test_mode:
        print("\nЭТАП 2:")
        print("=" * 50)

        try:
            dependencies = get_npm_dependencies(args.package, args.url)
            display_dependencies(args.package, dependencies)

        except Exception as e:
            print(f"\nОшибка при получении зависимостей: {e}")
            print("\nПроверьте:")
            print("   • Правильность имени пакета")
            print("   • Доступность npm registry")
            print("   • Интернет-соединение")
            print("=" * 50)
            sys.exit(1)

if __name__ == "__main__":
    main()