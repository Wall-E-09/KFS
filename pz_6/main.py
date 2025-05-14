import numpy as np
import matplotlib.pyplot as plt
import random
import time
from typing import List, Tuple

class AntColonyVisualizer:
    """Клас для візуалізації роботи мурашиного алгоритму"""
    
    def __init__(self, cities: np.ndarray):
        self.cities = cities
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        plt.ion()  # Увімкнути інтерактивний режим
        
    def plot_cities(self):
        """Відобразити міста на графіку"""
        self.ax.clear()
        self.ax.scatter(self.cities[:, 0], self.cities[:, 1], c='blue', s=100)
        for i, city in enumerate(self.cities):
            self.ax.text(city[0], city[1], str(i), fontsize=12)
    
    def plot_path(self, path: List[int], pheromone_level: float = 1.0, color: str = 'gray', alpha: float = 0.3):
        """Відобразити шлях на графіку"""
        for i in range(len(path)-1):
            start = self.cities[path[i]]
            end = self.cities[path[i+1]]
            self.ax.plot([start[0], end[0]], [start[1], end[1]], 
                        color=color, linewidth=pheromone_level*3, alpha=alpha)
    
    def highlight_best_path(self, path: List[int], length: float, iteration: int):
        """Виділити найкращий шлях"""
        for i in range(len(path)-1):
            start = self.cities[path[i]]
            end = self.cities[path[i+1]]
            self.ax.plot([start[0], end[0]], [start[1], end[1]], 
                        'r-', linewidth=2)
        
        self.ax.set_title(f"Iteration: {iteration}, Best Path Length: {length:.2f}")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        time.sleep(0.1)

class AntColony:
    """Клас для реалізації мурашиного алгоритму з візуалізацією"""
    
    def __init__(self, cities: np.ndarray, n_ants: int = 10, n_iterations: int = 100,
                 decay: float = 0.5, alpha: float = 1, beta: float = 2):
        # Координати міст
        self.cities = cities
        self.n = len(cities)
        
        # Розрахунок матриці відстаней
        self.distances = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                self.distances[i,j] = np.linalg.norm(cities[i] - cities[j])
        
        # Параметри алгоритму
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        
        # Ініціалізація феромонів
        self.pheromone = np.ones((self.n, self.n)) / self.n
        self.all_cities = range(self.n)
        
        # Найкращий шлях
        self.best_path = None
        self.best_length = float('inf')
        
        # Візуалізація
        self.visualizer = AntColonyVisualizer(cities)
        self.visualizer.plot_cities()
    
    def run(self) -> Tuple[List[int], float]:
        """Запуск алгоритму з візуалізацією"""
        for iteration in range(self.n_iterations):
            # Генерація шляхів для всіх мурах
            ants_paths = self._generate_ants_paths()
            
            # Оновлення феромонів
            self._update_pheromones(ants_paths)
            
            # Знаходження найкращого шляху в поточній ітерації
            current_best_path, current_best_length = min(ants_paths, key=lambda x: x[1])
            
            # Оновлення глобально найкращого шляху
            if current_best_length < self.best_length:
                self.best_path = current_best_path
                self.best_length = current_best_length
            
            # Візуалізація
            self._visualize_iteration(iteration, ants_paths, current_best_path, current_best_length)
            
            # Випаровування феромонів
            self.pheromone *= self.decay
        
        plt.ioff()
        plt.show()
        return self.best_path, self.best_length
    
    def _visualize_iteration(self, iteration: int, ants_paths: List[Tuple[List[int], float]], 
                           current_best_path: List[int], current_best_length: float):
        """Візуалізація поточної ітерації"""
        self.visualizer.plot_cities()
        
        # Відображення всіх шляхів мурах
        for path, length in ants_paths:
            self.visualizer.plot_path(path)
        
        # Відображення поточного найкращого шляху
        self.visualizer.highlight_best_path(current_best_path, current_best_length, iteration)
    
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
        probabilities = [p/total for p in probabilities] if total > 0 else [1/len(unvisited)]*len(unvisited)
        
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

# Приклад використання
if __name__ == "__main__":
    # Генерація випадкових міст
    np.random.seed(42)
    n_cities = 15
    cities = np.random.rand(n_cities, 2) * 100
    
    # Параметри алгоритму
    n_ants = 20
    n_iterations = 100
    decay = 0.5
    alpha = 1
    beta = 2
    
    # Створення та запуск алгоритму
    colony = AntColony(cities, n_ants=n_ants, n_iterations=n_iterations, 
                      decay=decay, alpha=alpha, beta=beta)
    best_path, best_length = colony.run()
    
    print("\nРезультати:")
    print(f"Найкращий шлях: {best_path}")
    print(f"Довжина шляху: {best_length:.2f}")