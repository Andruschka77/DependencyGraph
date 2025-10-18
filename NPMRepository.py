import urllib.request
import urllib.error
import json
from typing import List, Dict

# Класс для получения информации о пакетах из NPM registry
class NPMRepository:
    def __init__(self, registry_url: str = "https://registry.npmjs.org"):
        self.registry_url = registry_url
        self._cache = {}  # Кэш для уменьшения количества запросов

    # Получает полную информацию о пакете
    def get_package(self, package_name: str) -> Dict:
        dependencies = self._get_npm_dependencies(package_name)
        return {
            'version': '1.0.0',
            'dependencies': dependencies
        }

    # Получает список зависимостей пакета
    def get_dependencies(self, package_name: str) -> List[str]:
        dependencies = self._get_npm_dependencies(package_name)
        return [dep['name'] for dep in dependencies]

    # Внутренний метод для получения зависимостей из NPM API
    def _get_npm_dependencies(self, package_name: str) -> List[Dict]:
        # Проверяем кэш
        if package_name in self._cache:
            print(f"   Используем кэшированные данные для {package_name}")
            return self._cache[package_name]

        try:
            # Формируем URL для запроса
            url = f"{self.registry_url.rstrip('/')}/{package_name}"

            print(f"   Запрос информации о пакете {package_name}...")
            print(f"   URL: {url}")

            # Создаем HTTP запрос с заголовками
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'DependencyVisualizer/1.0',
                    'Accept': 'application/json'
                }
            )

            # Выполняем запрос
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"HTTP ошибка: {response.status}")
                # Читаем и парсим json ответ
                data = json.loads(response.read().decode('utf-8'))

            # Определяем последнюю версию
            if 'dist-tags' in data and 'latest' in data['dist-tags']:
                latest_version = data['dist-tags']['latest']
            else:
                versions = list(data.get('versions', {}).keys())
                if not versions:
                    raise Exception("Не найдено ни одной версии пакета")
                latest_version = sorted(versions)[-1]

            version_data = data['versions'].get(latest_version) # Получаем данные конкретной версии
            if not version_data:
                raise Exception(f"Данные для версии {latest_version} не найдены")

            dependencies = [] # Собираем все типы зависимостей
            dependency_sections = ['dependencies', 'peerDependencies', 'optionalDependencies']

            for section in dependency_sections:
                if section in version_data and version_data[section]:
                    for dep_name, dep_version in version_data[section].items():
                        dependencies.append({
                            'name': dep_name,
                            'version': dep_version,
                            'type': section.replace('Dependencies', '')
                        })

            print(f"   Найдена версия: {latest_version}")

            # Сохраняем в кэш
            self._cache[package_name] = dependencies
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