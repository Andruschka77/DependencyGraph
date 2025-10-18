import os
import tempfile
import subprocess
from DependencyGraph import DependencyGraph

# Класс для визуализации графа зависимостей
class DependencyVisualizer:
    def __init__(self, graph: DependencyGraph):
        self.graph = graph

    # Генерирует код на языке D2 для визуализации графа
    def generate_d2_diagram(self, root_package: str) -> str:
        d2_lines = []

        # Добавляем все узлы
        for node in self.graph.nodes:
            d2_lines.append(f'{node}')

        # Добавляем все связи
        for from_node, dependencies in self.graph.edges.items():
            for to_node in dependencies:
                d2_lines.append(f'{from_node} -> {to_node}')

        # Выделяем корневой пакет
        d2_lines.append(f'{root_package}.style: {{fill: "#d4f1f9"}}')

        return '\n'.join(d2_lines)

    # Выводит ASCII-дерево зависимостей
    def display_ascii_tree(self, root_package: str):
        print(f"ASCII-ДЕРЕВО ЗАВИСИМОСТЕЙ {root_package}:")
        self._display_ascii_tree_recursive(root_package)

    # Рекурсивная функция для построения ASCII-дерева
    def _display_ascii_tree_recursive(self, node: str, prefix: str = "", is_last: bool = True, visited: set = None):
        if visited is None:
            visited = set()

        # Проверяем циклы
        if node in visited:
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{node} [ЦИКЛ]")
            return

        visited.add(node)

        # Обнаружение текущего узла
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{node}")

        # Получаем и сортируем зависимости
        dependencies = sorted(self.graph.get_dependencies(node))
        new_prefix = prefix + ("    " if is_last else "│   ")

        # Рекурсивно отображаем зависимости
        for i, dep in enumerate(dependencies):
            is_last_child = i == len(dependencies) - 1
            self._display_ascii_tree_recursive(dep, new_prefix, is_last_child, visited.copy())

    # Генерирует и отображает изображение графа с помощью D2
    def generate_and_display_image(self, root_package: str):
        try:
            # Генерируем D2 код
            d2_code = self.generate_d2_diagram(root_package)

            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as f:
                f.write(d2_code)
                d2_file = f.name

            # Создаем файл для изображения
            output_file = d2_file.replace('.d2', '.png')

            # Запускаем D2 для генерации изображения
            result = subprocess.run(['d2', d2_file, output_file],
                                    capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print(f"Изображение графа сохранено: {output_file}")

                # Пытаемся открыть изображение
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(output_file)
                    elif os.name == 'posix':  # Linux/Mac
                        subprocess.run(['open', output_file] if os.uname().sysname == 'Darwin'
                                       else ['xdg-open', output_file])
                    print("Изображение открыто в программе просмотра по умолчанию")
                except:
                    print(f"Не удалось открыть изображение автоматически. Файл: {output_file}")
            else:
                print(f"Ошибка генерации изображения: {result.stderr}")
                print("D2 код:")
                print(d2_code)

            # Удаляем временный D2 файл
            os.unlink(d2_file)

        except FileNotFoundError:
            print("D2 не установлен. Установите его для генерации изображений:")
            print("   https://d2lang.com/tour/install")
            print("\nD2 код для ручной визуализации:")
            print(self.generate_d2_diagram(root_package))
        except Exception as e:
            print(f"Ошибка при генерации изображения: {e}")

    # Сравнивает наш инструмент с стандартными инструментами npm
    def compare_with_npm_tools(self):
        print("   • npm ls - дерево зависимостей npm")
        print("   • Наш инструмент - полный граф всех зависимостей")
        print("   • Расхождения возможны из-за:")
        print("     - npm ls показывает только установленные зависимости")
        print("     - Наш инструмент показывает все возможные зависимости")
        print("     - Разные алгоритмы обработки peer-зависимостей")
        print("     - npm может скрывать некоторые вложенные зависимости")