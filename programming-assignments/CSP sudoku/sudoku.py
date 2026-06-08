import time
import tracemalloc
from collections import deque
from copy import deepcopy


# ============================================================
# SUDOKU COMO CSP
# ============================================================

class SudokuCSP:
    def __init__(self, board):
        self.board = board
        self.variables = [(r, c) for r in range(9) for c in range(9)]
        self.domains = self.create_domains()
        self.neighbors = self.create_neighbors()

    def create_domains(self):
        domains = {}

        for r in range(9):
            for c in range(9):
                if self.board[r][c] != 0:
                    domains[(r, c)] = {self.board[r][c]}
                else:
                    domains[(r, c)] = set(range(1, 10))

        return domains

    def create_neighbors(self):
        neighbors = {}

        for r in range(9):
            for c in range(9):
                cell = (r, c)
                related = set()

                # Misma fila y columna
                for k in range(9):
                    if k != c:
                        related.add((r, k))
                    if k != r:
                        related.add((k, c))

                # Mismo bloque 3x3
                start_row = 3 * (r // 3)
                start_col = 3 * (c // 3)

                for i in range(start_row, start_row + 3):
                    for j in range(start_col, start_col + 3):
                        if (i, j) != cell:
                            related.add((i, j))

                neighbors[cell] = related

        return neighbors

    def is_consistent(self, variable, value, assignment):
        for neighbor in self.neighbors[variable]:
            if neighbor in assignment and assignment[neighbor] == value:
                return False
        return True

    def get_legal_values(self, variable, assignment):
        legal_values = []

        for value in self.domains[variable]:
            if self.is_consistent(variable, value, assignment):
                legal_values.append(value)

        return legal_values

    def validate_initial_board(self):
        """
        Verifica que el tablero inicial no tenga conflictos.
        """
        assignment = {}

        for r in range(9):
            for c in range(9):
                value = self.board[r][c]

                if value != 0:
                    variable = (r, c)

                    if value < 1 or value > 9:
                        return False

                    if not self.is_consistent(variable, value, assignment):
                        return False

                    assignment[variable] = value

        return True


# ============================================================
# SOLUCIONADOR DE SUDOKU
# ============================================================

class SudokuSolver:
    def __init__(
        self,
        csp,
        use_mrv=True,
        use_lcv=False,
        use_forward_checking=False,
        use_ac3=False
    ):
        self.csp = csp
        self.use_mrv = use_mrv
        self.use_lcv = use_lcv
        self.use_forward_checking = use_forward_checking
        self.use_ac3 = use_ac3

        self.nodes_visited = 0
        self.backtracks = 0
        self.execution_time = 0
        self.memory_used = 0

    def solve(self):
        if not self.csp.validate_initial_board():
            return None

        tracemalloc.start()
        start_time = time.time()

        if self.use_ac3:
            if not self.ac3():
                return None

        assignment = {}

        for variable, domain in self.csp.domains.items():
            if len(domain) == 1:
                assignment[variable] = next(iter(domain))

        result = self.backtrack(assignment)

        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        self.execution_time = end_time - start_time
        self.memory_used = peak / 1024

        if result is None:
            return None

        return self.assignment_to_board(result)

    def backtrack(self, assignment):
        self.nodes_visited += 1

        if len(assignment) == len(self.csp.variables):
            return assignment

        variable = self.select_unassigned_variable(assignment)
        values = self.order_domain_values(variable, assignment)

        for value in values:
            if self.csp.is_consistent(variable, value, assignment):
                assignment[variable] = value

                saved_domains = None

                if self.use_forward_checking:
                    saved_domains = self.forward_check(variable, value, assignment)

                    if saved_domains is None:
                        del assignment[variable]
                        self.backtracks += 1
                        continue

                result = self.backtrack(assignment)

                if result is not None:
                    return result

                del assignment[variable]
                self.backtracks += 1

                if self.use_forward_checking and saved_domains is not None:
                    self.restore_domains(saved_domains)

        return None

    def select_unassigned_variable(self, assignment):
        unassigned = [v for v in self.csp.variables if v not in assignment]

        if not self.use_mrv:
            return unassigned[0]

        # MRV: escoge la variable con menos valores legales disponibles
        return min(
            unassigned,
            key=lambda var: len(self.csp.get_legal_values(var, assignment))
        )

    def order_domain_values(self, variable, assignment):
        values = self.csp.get_legal_values(variable, assignment)

        if not self.use_lcv:
            return values

        # LCV: escoge primero el valor que menos restringe a los vecinos
        def count_restrictions(value):
            count = 0

            for neighbor in self.csp.neighbors[variable]:
                if neighbor not in assignment and value in self.csp.domains[neighbor]:
                    count += 1

            return count

        return sorted(values, key=count_restrictions)

    def forward_check(self, variable, value, assignment):
        saved_domains = {}

        for neighbor in self.csp.neighbors[variable]:
            if neighbor not in assignment:
                saved_domains[neighbor] = self.csp.domains[neighbor].copy()

                if value in self.csp.domains[neighbor]:
                    self.csp.domains[neighbor].remove(value)

                if len(self.csp.domains[neighbor]) == 0:
                    self.restore_domains(saved_domains)
                    return None

        return saved_domains

    def restore_domains(self, saved_domains):
        for variable, domain in saved_domains.items():
            self.csp.domains[variable] = domain

    def ac3(self):
        queue = deque()

        for xi in self.csp.variables:
            for xj in self.csp.neighbors[xi]:
                queue.append((xi, xj))

        while queue:
            xi, xj = queue.popleft()

            if self.revise(xi, xj):
                if len(self.csp.domains[xi]) == 0:
                    return False

                for xk in self.csp.neighbors[xi]:
                    if xk != xj:
                        queue.append((xk, xi))

        return True

    def revise(self, xi, xj):
        revised = False
        values_to_remove = []

        for x in self.csp.domains[xi]:
            # Restricción binaria: xi != xj
            supported = any(x != y for y in self.csp.domains[xj])

            if not supported:
                values_to_remove.append(x)

        for x in values_to_remove:
            self.csp.domains[xi].remove(x)
            revised = True

        return revised

    def assignment_to_board(self, assignment):
        board = [[0 for _ in range(9)] for _ in range(9)]

        for (r, c), value in assignment.items():
            board[r][c] = value

        return board


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def print_board(board):
    if board is None:
        print("No se encontró solución.")
        return

    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)

        for c in range(9):
            if c % 3 == 0 and c != 0:
                print("|", end=" ")

            print(board[r][c] if board[r][c] != 0 else ".", end=" ")

        print()


def load_puzzle(difficulty):
    puzzles = {
        "Easy": [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ],

        "Medium": [
            [0, 0, 0, 2, 0, 0, 0, 6, 3],
            [3, 0, 0, 0, 0, 5, 4, 0, 1],
            [0, 0, 1, 0, 0, 3, 9, 8, 0],
            [0, 0, 0, 0, 0, 0, 0, 9, 0],
            [0, 5, 0, 7, 0, 0, 0, 0, 4],
            [6, 0, 9, 0, 0, 0, 0, 1, 0],
            [9, 0, 0, 6, 0, 0, 3, 0, 0],
            [2, 0, 8, 0, 0, 9, 0, 0, 7],
            [0, 0, 0, 0, 0, 2, 0, 0, 0]
        ],

        "Hard": [
            [0, 0, 0, 6, 0, 0, 4, 0, 0],
            [7, 0, 0, 0, 0, 3, 6, 0, 0],
            [0, 0, 0, 0, 9, 1, 0, 8, 0],
            [0, 0, 0, 0, 0, 0, 0, 2, 0],
            [0, 0, 2, 0, 0, 0, 9, 0, 5],
            [0, 9, 0, 0, 5, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 8, 0, 0, 6],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 4, 0, 0, 0, 8, 0, 0]
        ]
    }

    return puzzles[difficulty]


# ============================================================
# ANÁLISIS DE ALGORITMOS
# ============================================================

def run_solver(difficulty, config_name, use_mrv, use_lcv, use_fc, use_ac3):
    puzzle = load_puzzle(difficulty)

    csp = SudokuCSP(deepcopy(puzzle))

    solver = SudokuSolver(
        csp,
        use_mrv=use_mrv,
        use_lcv=use_lcv,
        use_forward_checking=use_fc,
        use_ac3=use_ac3
    )

    solution = solver.solve()

    return {
        "Difficulty": difficulty,
        "Algorithm": config_name,
        "Solved": solution is not None,
        "Time": round(solver.execution_time, 6),
        "Nodes": solver.nodes_visited,
        "Backtracks": solver.backtracks,
        "Memory_KB": round(solver.memory_used, 2),
        "Solution": solution
    }


def compare_algorithms():
    difficulties = ["Easy", "Medium", "Hard"]

    algorithms = [
        {
            "name": "Backtracking simple",
            "use_mrv": False,
            "use_lcv": False,
            "use_fc": False,
            "use_ac3": False
        },
        {
            "name": "Backtracking + MRV",
            "use_mrv": True,
            "use_lcv": False,
            "use_fc": False,
            "use_ac3": False
        },
        {
            "name": "Backtracking + MRV + Forward Checking",
            "use_mrv": True,
            "use_lcv": False,
            "use_fc": True,
            "use_ac3": False
        },
        {
            "name": "Backtracking + MRV + LCV + Forward Checking",
            "use_mrv": True,
            "use_lcv": True,
            "use_fc": True,
            "use_ac3": False
        },
        {
            "name": "Backtracking + MRV + LCV + Forward Checking + AC-3",
            "use_mrv": True,
            "use_lcv": True,
            "use_fc": True,
            "use_ac3": True
        }
    ]

    results = []

    for difficulty in difficulties:
        print("\n" + "=" * 70)
        print(f"Sudoku {difficulty}")
        print("=" * 70)

        print("\nTablero inicial:")
        print_board(load_puzzle(difficulty))

        for algorithm in algorithms:
            result = run_solver(
                difficulty,
                algorithm["name"],
                algorithm["use_mrv"],
                algorithm["use_lcv"],
                algorithm["use_fc"],
                algorithm["use_ac3"]
            )

            results.append(result)

            print("\nAlgoritmo:", result["Algorithm"])
            print("Resuelto:", result["Solved"])
            print("Tiempo:", result["Time"], "segundos")
            print("Nodos visitados:", result["Nodes"])
            print("Retrocesos:", result["Backtracks"])
            print("Memoria:", result["Memory_KB"], "KB")

        print("\nSolución encontrada:")
        print_board(results[-1]["Solution"])

    print("\n\n" + "=" * 90)
    print("TABLA FINAL DE RESULTADOS")
    print("=" * 90)

    print(
        f"{'Dificultad':<12} "
        f"{'Algoritmo':<55} "
        f"{'Tiempo':<12} "
        f"{'Nodos':<10} "
        f"{'Backtracks':<12} "
        f"{'Memoria KB':<12}"
    )

    print("-" * 120)

    for r in results:
        print(
            f"{r['Difficulty']:<12} "
            f"{r['Algorithm']:<55} "
            f"{r['Time']:<12} "
            f"{r['Nodes']:<10} "
            f"{r['Backtracks']:<12} "
            f"{r['Memory_KB']:<12}"
        )


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    compare_algorithms()