from typing import Dict, Set, List


class DependencyGraph:
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: Dict[str, Set[str]] = {}

    def add_package(self, package_name: str, version: str = "1.0.0", dependencies: List[Dict] = None):
        if package_name not in self.nodes:
            self.nodes[package_name] = {
                'name': package_name,
                'version': version,
                'dependencies': dependencies or []
            }
            self.edges[package_name] = set()

    def add_dependency(self, from_package: str, to_package: str):
        if from_package in self.edges:
            self.edges[from_package].add(to_package)

    def get_dependencies(self, package_name: str) -> Set[str]:
        return self.edges.get(package_name, set())

    def has_cycle(self) -> bool:
        visited = set()
        recursion_stack = set()

        def dfs(node):
            if node in recursion_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            recursion_stack.add(node)

            for neighbor in self.get_dependencies(node):
                if dfs(neighbor):
                    return True

            recursion_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def get_cycles(self) -> List[List[str]]:

        def find_cycles_dfs(node, visited, path, cycles):
            if node in path:
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in self.get_dependencies(node):
                find_cycles_dfs(neighbor, visited, path, cycles)

            path.pop()

        visited = set()
        cycles = []

        for node in self.nodes:
            if node not in visited:
                find_cycles_dfs(node, visited, [], cycles)

        return cycles