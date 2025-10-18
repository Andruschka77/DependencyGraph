from typing import Dict, Set, List
from collections import deque

# Класс для представления графа зависимостей пакетов
class DependencyGraph:
    def __init__(self):
        self.nodes: Dict[str, Dict] = {} # Словарь узлов: {имя_пакета: информация_о_пакете}
        self.edges: Dict[str, Set[str]] = {} # Словарь ребер: {от_пакета: {множество_зависимостей}}

    # Добавляет пакет в граф
    def add_package(self, package_name: str, version: str = "1.0.0", dependencies: List[Dict] = None):
        if package_name not in self.nodes:
            self.nodes[package_name] = {
                'name': package_name,
                'version': version,
                'dependencies': dependencies or []
            }
            self.edges[package_name] = set() # Создаем пустое множество зависимостей

    # Добавляет зависимость между пакетами
    def add_dependency(self, from_package: str, to_package: str):
        if from_package in self.edges:
            self.edges[from_package].add(to_package) # Добавляем связь

    # Возвращает зависимости пакета
    def get_dependencies(self, package_name: str) -> Set[str]:
        return self.edges.get(package_name, set())

    # Проверяет наличие циклов в графе с помощью DFS
    def has_cycle(self) -> bool:
        visited = set() # Постоянно посещенные узлы
        recursion_stack = set() # Временно посещенные узлы (для обнаружения циклов)

        def dfs(node): # Вспомогательная функция DFS для поиска циклов
            if node in recursion_stack:
                return True
            if node in visited:
                return False

            # Добавляем узел в текущий путь
            visited.add(node)
            recursion_stack.add(node)

            for neighbor in self.get_dependencies(node): # Рекурсивно проверяем всех соседей
                if dfs(neighbor):
                    return True # Цикл найден в поддереве

            recursion_stack.remove(node) # Убираем узел из текущего пути
            return False

        for node in self.nodes: # Проверяем все узлы графа
            if node not in visited:
                if dfs(node):
                    return True # Найден хотя бы один цикл
        return False # Циклов нет

    # Находит все циклы в графе
    def get_cycles(self) -> List[List[str]]:

        def find_cycles_dfs(node, visited, path, cycles): # Рекурсивный поиск циклов с отслеживанием пути
            if node in path: # Найден цикл, выделяем циклическую часть пути
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                cycles.append(cycle)
                return

            if node in visited:
                return

            # Продолжаем обход
            visited.add(node)
            path.append(node)

            # Рекурсивно обходим зависимости
            for neighbor in self.get_dependencies(node):
                find_cycles_dfs(neighbor, visited, path, cycles)

            path.pop()

        visited = set()
        cycles = []

        for node in self.nodes: # Запускаем поиск циклов из каждого непосещенного узла
            if node not in visited:
                find_cycles_dfs(node, visited, [], cycles)

        return cycles

    # Топологическая сортировка для определения порядка загрузки
    def get_load_order(self, root_package: str) -> List[str]:
        visited = set() # Посещенные узлы
        result = [] # Посещенные узлы
        in_stack = set() # Узлы в текущем пути (для обнаружения циклов)

        def dfs(node): # DFS с пост-порядком обхода
            if node in in_stack:
                # Обнаружен цикл - пропускаем узел
                return
            if node in visited:
                return

            visited.add(node)
            in_stack.add(node)

            # Сначала посещаем все зависимости
            for dep in sorted(self.get_dependencies(node)):
                dfs(dep)

            # Затем добавляем текущий узел
            result.append(node)
            in_stack.remove(node)

        dfs(root_package) # Запускаем обход из корневого пакета
        return result

    # Определяет уровни зависимостей с помощью BFS
    def get_dependency_levels(self, root_package: str) -> Dict[int, List[str]]:
        levels = {} # Уровни зависимостей
        queue = deque([(root_package, 0)]) # Очередь для BFS: (узел, уровень)
        visited = set([root_package]) # Посещенные узлы

        while queue:
            node, level = queue.popleft() # Берем узел из начала очереди

            # Добавляем узел в соответствующий уровень
            if level not in levels:
                levels[level] = []
            levels[level].append(node)

            # Добавляем зависимости текущего узла
            for dep in sorted(self.get_dependencies(node)):
                if dep not in visited:
                    visited.add(dep)
                    queue.append((dep, level + 1)) # Увеличиваем уровень

        return levels