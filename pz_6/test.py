import numpy as np
import matplotlib.pyplot as plt
import random
import unittest
from typing import List, Tuple

class AntColony:
    """Клас для реалізації мурашиного алгоритму"""
    
    def __init__(self, distances: np.ndarray, n_ants: int = 10, n_iterations: int = 100,
                 decay: float = 0.5, alpha: float = 1, beta: float = 2):
        """
        Ініціалізація параметрів
        
        :param distances: матриця відстаней між містами
        :param n_ants: кількість мурах
        :param n_iterations: кількість ітерацій
        :param decay: коефіцієнт випаровування феромонів
        :param alpha: вага феромонів у ймовірності вибору шляху
        :param beta: вага евристичної інформації (1/відстань)
        """
        # 1. Ініціалізація феромонів
        self.distances = distances
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.pheromone = np.ones(self.distances.shape) / len(distances)
        self.all_cities = range(len(distances))
        self.best_path = None
        self.best_length = float('inf')
        
    def run(self) -> Tuple[List[int], float]:
        """Запуск алгоритму"""
        for iteration in range(self.n_iterations):
            # 2. Вибір маршруту та 3. Прокладання шляху
            ants_paths = self._generate_ants_paths()
            
            # 4. Оновлення феромонів
            self._update_pheromones(ants_paths)
            
            # 5. Еволюція шляхів (знаходження найкращого)
            current_best_path, current_best_length = min(ants_paths, key=lambda x: x[1])
            if current_best_length < self.best_length:
                self.best_path = current_best_path
                self.best_length = current_best_length
                
            # 6. Випаровування феромонів
            self.pheromone *= self.decay
            
        # 7. Завершення роботи алгоритму
        return self.best_path, self.best_length
    
    def _generate_ants_paths(self) -> List[Tuple[List[int], float]]:
        """Генерація шляхів для всіх мурах"""
        return [self._generate_path() for _ in range(self.n_ants)]
    
    def _generate_path(self) -> Tuple[List[int], float]:
        """Генерація шляху для однієї мурахи"""
        path = []
        visited = set()
        
        # Початкове місто вибирається випадково
        current = random.choice(self.all_cities)
        path.append(current)
        visited.add(current)
        
        # Прокладання шляху
        while len(visited) < len(self.all_cities):
            next_city = self._select_next_city(current, visited)
            path.append(next_city)
            visited.add(next_city)
            current = next_city
        
        # Повернення до початкового міста
        path.append(path[0])
        path_length = self._calculate_path_length(path)
        return path, path_length
    
    def _select_next_city(self, current: int, visited: set) -> int:
        """Вибір наступного міста на основі ймовірностей"""
        unvisited = [city for city in self.all_cities if city not in visited]
        probabilities = []
        
        for city in unvisited:
            pheromone = self.pheromone[current][city] ** self.alpha
            heuristic = (1 / self.distances[current][city]) ** self.beta
            probabilities.append(pheromone * heuristic)
        
        # Нормалізація ймовірностей
        total = sum(probabilities)
        probabilities = [p/total for p in probabilities]
        
        return random.choices(unvisited, weights=probabilities, k=1)[0]
    
    def _update_pheromones(self, ants_paths: List[Tuple[List[int], float]]):
        """Оновлення рівня феромонів на шляхах"""
        for path, length in ants_paths:
            pheromone_amount = 1 / length
            for i in range(len(path)-1):
                self.pheromone[path[i]][path[i+1]] += pheromone_amount
    
    def _calculate_path_length(self, path: List[int]) -> float:
        """Розрахунок довжини шляху"""
        return sum(self.distances[path[i], path[i+1]] for i in range(len(path)-1))


# Тести для перевірки коректності роботи алгоритму
class TestAntColony(unittest.TestCase):
    def setUp(self):
        self.distances = np.array([
            [0, 2, 3, 5],
            [2, 0, 4, 6],
            [3, 4, 0, 7],
            [5, 6, 7, 0]
        ])
        self.colony = AntColony(self.distances, n_ants=5, n_iterations=10)
    
    def test_initialization(self):
        """Тест ініціалізації феромонів"""
        self.assertEqual(self.colony.pheromone.shape, (4, 4))
        self.assertTrue(np.all(self.colony.pheromone > 0))
    
    def test_path_generation(self):
        """Тест генерації шляху"""
        path, length = self.colony._generate_path()
        self.assertEqual(len(path), 5)  # 4 міста + повернення
        self.assertEqual(path[0], path[-1])  # Початок і кінець збігаються
        self.assertEqual(len(set(path[:-1])), 4)  # Всі міста відвідані
    
    def test_path_length_calculation(self):
        """Тест розрахунку довжини шляху"""
        path = [0, 1, 2, 3, 0]
        expected_length = 2 + 4 + 7 + 5
        self.assertEqual(self.colony._calculate_path_length(path), expected_length)
    
    def test_pheromone_update(self):
        """Тест оновлення феромонів"""
        initial_pheromone = self.colony.pheromone.copy()
        paths = [([0, 1, 2, 3, 0], 18), ([0, 2, 1, 3, 0], 20)]
        self.colony._update_pheromones(paths)
        
        # Перевірка, що феромони додалися
        self.assertTrue(np.all(self.colony.pheromone >= initial_pheromone))
        
        # Кращий шлях отримав більше феромонів
        self.assertGreater(self.colony.pheromone[0][1], initial_pheromone[0][1])
        self.assertGreater(self.colony.pheromone[1][2], initial_pheromone[1][2])
    
    def test_full_algorithm(self):
        """Тест повного виконання алгоритму"""
        path, length = self.colony.run()
        self.assertEqual(len(path), 5)
        self.assertEqual(path[0], path[-1])
        self.assertTrue(length < float('inf'))


# Приклад використання
if __name__ == "__main__":
    # Створення матриці відстаней
    cities = 10
    distances = np.random.rand(cities, cities) * 100
    distances = (distances + distances.T) / 2  # Робимо симетричною
    np.fill_diagonal(distances, 0)  # Нульові відстані по діагоналі
    
    # Запуск алгоритму
    colony = AntColony(distances, n_ants=15, n_iterations=100)
    best_path, best_length = colony.run()
    
    print(f"Найкращий знайдений шлях: {best_path}")
    print(f"Довжина шляху: {best_length:.2f}")
    
    # Запуск тестів
    unittest.main()