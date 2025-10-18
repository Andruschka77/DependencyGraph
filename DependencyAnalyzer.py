from collections import deque
from typing import Set
from DependencyGraph import DependencyGraph
from DependencyVisualizer import DependencyVisualizer

# Основной класс для анализа зависимостей пакетов
class DependencyAnalyzer:
    def __init__(self, repository, max_depth: int = 5, filter_str: str = ""):
        self.repository = repository # Источник данных о пакетах
        self.max_depth = max_depth # Ограничение глубины поиска
        self.filter_str = filter_str.lower() # Фильтр (приводим к нижнему регистру)
        self.graph = DependencyGraph() # Граф для хранения зависимостей
        self.visited = set() # Множество посещенных пакетов
        self.cycles_detected = [] # Список обнаруженных циклов

    # Проверяет, должен ли пакет быть включен в анализ
    def should_include_package(self, package_name: str) -> bool:
        if self.filter_str and self.filter_str in package_name.lower():
            return False # Пропускаем пакет - он содержит фильтр
        return True # Включаем пакет в анализ

    # Основной метод анализа зависимостей, использует DFS для обхода графа зависимостей
    def analyze_dependencies(self, root_package: str) -> DependencyGraph:
        print(f"\nНачинаем анализ зависимостей для {root_package}...")
        print(f"   Максимальная глубина: {self.max_depth}")
        print(f"   Фильтр: '{self.filter_str}'" if self.filter_str else "   Фильтр: не используется")

        stack = deque() # Используем стек для DFS
        stack.append((root_package, 0))

        while stack: # Обход в глубину
            package_name, depth = stack.pop() # Берем пакет из стека

            if depth > self.max_depth: # Проверка глубины
                print(f"   Пропускаем {package_name} (превышена глубина {self.max_depth})")
                continue

            if not self.should_include_package(package_name): # Применение фильтра
                print(f"   Пропускаем {package_name} (фильтр: '{self.filter_str}')")
                continue

            # Если уже посещали этот пакет, проверяем на циклы
            if package_name in self.visited:
                # Проверяем, создает ли это цикл
                if any(package_name in path for path in self.cycles_detected):
                    print(f"   Обнаружен цикл с пакетом {package_name}")
                continue

            self.visited.add(package_name) # Обработка нового пакета
            print(f"   Анализируем {package_name} (глубина {depth})")

            try:
                # Получаем информацию о пакете
                package = self.repository.get_package(package_name)
                self.graph.add_package(package_name, package.get('version', '1.0.0'), package.get('dependencies', []))

                # Получаем зависимости
                dependencies = self.repository.get_dependencies(package_name)

                for dep_name in dependencies:
                    # Проверяем фильтр для зависимости
                    if not self.should_include_package(dep_name):
                        print(f"      Пропускаем зависимость {dep_name} (фильтр)")
                        continue

                    self.graph.add_dependency(package_name, dep_name) # Добавляем связь в граф

                    # Добавляем зависимость в стек для дальнейшего анализа
                    if dep_name not in self.visited:
                        stack.append((dep_name, depth + 1)) # Добавляем зависимость в стек
                        print(f"      Добавляем зависимость: {dep_name}")
                    else:
                        print(f"      Зависимость {dep_name} уже анализировалась")

            except Exception as e:
                print(f"   Ошибка при анализе {package_name}: {e}")
                continue

        # Проверяем циклы после построения графа
        if self.graph.has_cycle():
            self.cycles_detected = self.graph.get_cycles()
            print(f"\nОбнаружены циклические зависимости!")
            for i, cycle in enumerate(self.cycles_detected, 1):
                print(f"   Цикл {i}: {' -> '.join(cycle)} -> {cycle[0]}")

        return self.graph

    def display_analysis_results(self, root_package: str):
        print(f"\nРЕЗУЛЬТАТЫ АНАЛИЗА {root_package}:")
        print(f"\nВсего пакетов в графе: {len(self.graph.nodes)}")
        print(f"Всего зависимостей: {sum(len(deps) for deps in self.graph.edges.values())}")
        print(f"Максимальная глубина анализа: {self.max_depth}")

        if self.cycles_detected:
            print(f"Обнаружено циклов: {len(self.cycles_detected)}")
        else:
            print("Циклические зависимости: не обнаружены")

        if self.filter_str:
            print(f"Применен фильтр: '{self.filter_str}'")

        # Показываем граф в виде дерева
        print(f"\nГРАФ ЗАВИСИМОСТЕЙ:")
        self._display_tree(root_package)
        print("=" * 50)

    def display_load_order(self, root_package: str):
        print(f"ПОРЯДОК ЗАГРУЗКИ ЗАВИСИМОСТЕЙ ДЛЯ {root_package}:")

        try:
            # Топологическая сортировка (наш алгоритм)
            load_order = self.graph.get_load_order(root_package)
            print("\nНаш алгоритм (топологическая сортировка):")
            for i, package in enumerate(load_order, 1):
                print(f"   {i:2d}. {package}")

            # Уровни зависимостей (BFS-based)
            print("\nУровни зависимостей (BFS):")
            levels = self.graph.get_dependency_levels(root_package)
            for level in sorted(levels.keys()):
                packages = levels[level]
                level_name = "Корневой пакет" if level == 0 else f"Уровень {level}"
                print(f"   {level_name}: {', '.join(sorted(packages))}")

            # Сравнение с реальными менеджерами пакетов
            print("\nСРАВНЕНИЕ С РЕАЛЬНЫМИ МЕНЕДЖЕРАМИ ПАКЕТОВ:")
            print("   • npm/yarn: обычно используют BFS-подобный подход")
            print("   • Наш алгоритм: использует DFS с пост-порядком (зависимости загружаются первыми)")
            print("   • Расхождения возможны из-за:")
            print("     - Разных алгоритмов обхода графа")
            print("     - Обработки опциональных зависимостей")
            print("     - Параллельной загрузки в реальных менеджерах")

            if self.cycles_detected:
                print("\n  Внимание: наличие циклов может влиять на порядок загрузки!")

        except Exception as e:
            print(f"   Ошибка при определении порядка загрузки: {e}")

    def _display_tree(self, root: str, visited: Set = None, prefix: str = "", is_last: bool = True):
        if visited is None:
            visited = set()

        if root in visited:
            print(f"{prefix}↳ {root} [ЦИКЛ]")
            return

        visited.add(root)

        # Выводим текущий узел
        if prefix == "":
            print(f"    {root}")
        else:
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{root}")

        # Получаем зависимости и сортируем для consistent отображения
        dependencies = sorted(self.graph.get_dependencies(root))

        # Выводим зависимости
        for i, dep in enumerate(dependencies):
            is_last_child = i == len(dependencies) - 1
            new_prefix = prefix + ("    " if is_last else "│   ")

            if dep in visited:
                connector = "└── " if is_last_child else "├── "
                print(f"{new_prefix}{connector}↳ {dep} [ЦИКЛ]")
            else:
                self._display_tree(dep, visited.copy(), new_prefix, is_last_child)

        visited.remove(root)

    # Визуализация графа зависимостей
    def visualize_dependencies(self, root_package: str, ascii_tree: bool = False, generate_image: bool = False):
        print(f"\nВИЗУАЛИЗАЦИЯ ГРАФА ЗАВИСИМОСТЕЙ {root_package}:")
        visualizer = DependencyVisualizer(self.graph) # Создаем визуализатор

        d2_code = visualizer.generate_d2_diagram(root_package) # Генерация D2 кода
        print("\n1. ТЕКСТОВОЕ ПРЕДСТАВЛЕНИЕ НА D2:")
        print(d2_code)

        print("\n2. ГРАФИЧЕСКОЕ ПРЕДСТАВЛЕНИЕ:")
        if generate_image:
            visualizer.generate_and_display_image(root_package)
        else:
            print("D2 не установлен. Установите его для генерации изображений:")
            print("   https://d2lang.com/tour/install")
            print("\nD2 код для ручной визуализации:")
            print(d2_code)

        if ascii_tree:
            print("\n3. ASCII-ДЕРЕВО:")
            visualizer.display_ascii_tree(root_package)

        print("\n4. СРАВНЕНИЕ С ИНСТРУМЕНТАМИ NPM:")
        visualizer.compare_with_npm_tools()
        print("=" * 60)