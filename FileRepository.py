import json
from typing import List, Dict

class FileRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.packages = self._load_packages()

    def _load_packages(self) -> Dict:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Поддерживаем два формата файлов
            if 'packages' in data:
                return data['packages']
            else:
                return data

        except Exception as e:
            raise Exception(f"Ошибка загрузки файла {self.file_path}: {e}")

    def get_package(self, package_name: str) -> Dict:
        if package_name not in self.packages:
            raise Exception(f"Пакет {package_name} не найден в файле")

        package_data = self.packages[package_name]

        # Нормализуем формат данных
        if isinstance(package_data, str):
            return {'version': '1.0.0', 'dependencies': []}
        elif isinstance(package_data, list):
            return {'version': '1.0.0', 'dependencies': [{'name': dep, 'version': '*'} for dep in package_data]}
        else:
            return package_data

    def get_dependencies(self, package_name: str) -> List[str]:
        package = self.get_package(package_name)

        if 'dependencies' in package:
            if isinstance(package['dependencies'], list):
                if package['dependencies'] and isinstance(package['dependencies'][0], dict):
                    return [dep['name'] for dep in package['dependencies']]
                else:
                    return package['dependencies']

        return []