import json
from typing import List, Dict

# Класс для работы с тестовыми данными из JSON файлов
class FileRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.packages = self._load_packages() # Загружаем данные при инициализации

    # Загружает данные о пакетах из JSON файла
    def _load_packages(self) -> Dict:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Поддерживаем два формата файлов
            if 'packages' in data:
                return data['packages'] # Формат с ключом 'packages'
            else:
                return data # Прямой формат

        except Exception as e:
            raise Exception(f"Ошибка загрузки файла {self.file_path}: {e}")

    # Получает информацию о пакете из загруженных данных
    def get_package(self, package_name: str) -> Dict:
        if package_name not in self.packages:
            raise Exception(f"Пакет {package_name} не найден в файле")

        package_data = self.packages[package_name]

        # Нормализуем формат данных
        if isinstance(package_data, str):
            return {'version': '1.0.0', 'dependencies': []} # Простой формат: "A": "версия"
        elif isinstance(package_data, list):
            # Формат: "A": ["B", "C"]
            return {'version': '1.0.0', 'dependencies': [{'name': dep, 'version': '*'} for dep in package_data]}
        else:
            return package_data # Полный формат: "A": {"version": "...", "dependencies": [...]}

    # Получает список зависимостей пакета
    def get_dependencies(self, package_name: str) -> List[str]:
        package = self.get_package(package_name)

        if 'dependencies' in package:
            if isinstance(package['dependencies'], list):
                if package['dependencies'] and isinstance(package['dependencies'][0], dict):
                    return [dep['name'] for dep in package['dependencies']] # Формат: [{"name": "B", "version": "1.0.0"}, ...]
                else:
                    return package['dependencies'] # Формат: ["B", "C", ...]

        return [] # Нет зависимостей