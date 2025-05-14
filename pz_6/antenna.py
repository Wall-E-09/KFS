import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.widgets import Button, Slider
from typing import List, Tuple, Dict

class AntennaPlacementOptimizer:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(bottom=0.3)
        
        # Ініціалізація параметрів
        self.antennas = []
        self.obstacles = []
        self.interest_points = []
        self.coverage_radius = 15
        self.antenna_types = {
            'small': {'radius': 10, 'cost': 100},
            'medium': {'radius': 15, 'cost': 200},
            'large': {'radius': 20, 'cost': 300}
        }
        
        # Інтерактивні елементи
        self._init_ui()
        
    def _init_ui(self):
        """Ініціалізація інтерфейсу користувача"""
        # Кнопки
        ax_add_antenna = plt.axes([0.15, 0.15, 0.15, 0.05])
        ax_add_obstacle = plt.axes([0.35, 0.15, 0.15, 0.05])
        ax_add_interest = plt.axes([0.55, 0.15, 0.15, 0.05])
        ax_random = plt.axes([0.15, 0.05, 0.15, 0.05])
        ax_optimize = plt.axes([0.55, 0.05, 0.15, 0.05])
        
        self.btn_add_antenna = Button(ax_add_antenna, 'Додати антену')
        self.btn_add_obstacle = Button(ax_add_obstacle, 'Додати перешкоду')
        self.btn_add_interest = Button(ax_add_interest, 'Додати точку інтересу')
        self.btn_random = Button(ax_random, 'Випадкове розміщення')
        self.btn_optimize = Button(ax_optimize, 'Оптимізувати')
        
        # Обробники подій
        self.btn_add_antenna.on_clicked(self._add_antenna)
        self.btn_add_obstacle.on_clicked(self._add_obstacle)
        self.btn_add_interest.on_clicked(self._add_interest_point)
        self.btn_random.on_clicked(self._random_placement)
        self.btn_optimize.on_clicked(self._run_optimization)
        
        # Слайдери
        ax_radius = plt.axes([0.15, 0.22, 0.7, 0.02])
        ax_ants = plt.axes([0.15, 0.25, 0.7, 0.02])
        ax_iter = plt.axes([0.15, 0.28, 0.7, 0.02])
        
        self.slider_radius = Slider(ax_radius, 'Радіус покриття', 5, 30, valinit=15)
        self.slider_ants = Slider(ax_ants, 'Кількість мурах', 5, 50, valinit=20)
        self.slider_iter = Slider(ax_iter, 'Кількість ітерацій', 10, 200, valinit=50)
        
        # Обробник кліків на графіку
        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        
        self._update_plot()
    
    def _on_click(self, event):
        """Обробник кліків на графіку"""
        if event.inaxes != self.ax:
            return
        
        if event.button == 1:  # Ліва кнопка миші
            self.antennas.append((event.xdata, event.ydata, 'medium'))
        elif event.button == 3:  # Права кнопка миші
            self.obstacles.append((event.xdata, event.ydata))
        
        self._update_plot()
    
    def _add_antenna(self, event):
        """Додати антену вручну"""
        x, y = np.random.rand(2) * [self.width, self.height]
        self.antennas.append((x, y, 'medium'))
        self._update_plot()
    
    def _add_obstacle(self, event):
        """Додати перешкоду вручну"""
        x, y = np.random.rand(2) * [self.width, self.height]
        self.obstacles.append((x, y))
        self._update_plot()
    
    def _add_interest_point(self, event):
        """Додати точку інтересу вручну"""
        x, y = np.random.rand(2) * [self.width, self.height]
        self.interest_points.append((x, y))
        self._update_plot()
    
    def _random_placement(self, event):
        """Випадкове розміщення об'єктів"""
        n_antennas = random.randint(3, 10)
        n_obstacles = random.randint(5, 15)
        n_interest = random.randint(10, 20)
        
        self.antennas = [(np.random.rand() * self.width, 
                         np.random.rand() * self.height,
                         random.choice(list(self.antenna_types.keys())))
                        for _ in range(n_antennas)]
        
        self.obstacles = [(np.random.rand() * self.width, 
                          np.random.rand() * self.height)
                         for _ in range(n_obstacles)]
        
        self.interest_points = [(np.random.rand() * self.width, 
                               np.random.rand() * self.height)
                              for _ in range(n_interest)]
        
        self._update_plot()
    
    def _run_optimization(self, event):
        """Запуск оптимізації"""
        if not self.interest_points:
            print("Додайте точки інтересу перед оптимізацією!")
            return
        
        # Параметри алгоритму
        n_ants = int(self.slider_ants.val)
        n_iterations = int(self.slider_iter.val)
        self.coverage_radius = int(self.slider_radius.val)
        
        # Запуск мурашиного алгоритму
        best_solution = self._ant_colony_optimization(n_ants, n_iterations)
        
        # Оновлення антен з оптимальними позиціями
        self.antennas = [(x, y, 'medium') for x, y in best_solution]
        self._update_plot()
    
    def _ant_colony_optimization(self, n_ants: int, n_iterations: int) -> List[Tuple[float, float]]:
        """Мурашиний алгоритм для оптимізації розміщення антен"""
        # Ініціалізація феромонів
        pheromone = np.ones((len(self.interest_points), len(self.interest_points))) / len(self.interest_points)
        
        best_solution = None
        best_coverage = -1
        
        for iteration in range(n_iterations):
            solutions = []
            
            for _ in range(n_ants):
                # Генерація рішення (вибір точок для антен)
                solution = self._generate_solution(pheromone)
                coverage = self._calculate_coverage(solution)
                solutions.append((solution, coverage))
                
                # Оновлення найкращого рішення
                if coverage > best_coverage:
                    best_coverage = coverage
                    best_solution = solution
            
            # Оновлення феромонів
            pheromone = self._update_pheromones(pheromone, solutions)
            
            # Випаровування феромонів
            pheromone *= 0.95
            
            # Візуалізація прогресу
            if iteration % 10 == 0:
                print(f"Iteration {iteration}: Best coverage = {best_coverage:.2f}%")
                self._visualize_progress(best_solution, iteration, best_coverage)
        
        return best_solution
    
    def _generate_solution(self, pheromone: np.ndarray) -> List[Tuple[float, float]]:
        """Генерація рішення для однієї мурахи"""
        if not self.interest_points:
            return []
            
        # Перевірка, що кількість точок для антен не перевищує кількість точок інтересу
        n_points = min(5, len(self.interest_points))
        selected_points = random.sample(self.interest_points, n_points)
        return [(x, y) for x, y in selected_points]
    
    def _calculate_coverage(self, antennas: List[Tuple[float, float]]) -> float:
        """Розрахунок відсотка покриття"""
        if not self.interest_points:  # Якщо немає точок інтересу
            return 0.0
            
        covered = 0
        radius = self.coverage_radius
        
        for ip_x, ip_y in self.interest_points:
            for ant_x, ant_y in antennas:
                # Перевірка, що координати антен валідні
                if not isinstance(ant_x, (int, float)) or not isinstance(ant_y, (int, float)):
                    continue
                    
                distance = np.sqrt((ip_x - ant_x)**2 + (ip_y - ant_y)**2)
                if distance <= radius and not self._is_obstructed((ant_x, ant_y), (ip_x, ip_y)):
                    covered += 1
                    break
        
        return (covered / len(self.interest_points)) * 100
    
    def _is_obstructed(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> bool:
        """Перевірка на наявність перешкод між двома точками"""
        if not self.obstacles:  # Якщо немає перешкод
            return False
            
        for obs_x, obs_y in self.obstacles:
            # Спрощена перевірка - якщо перешкода ближче ніж 5 одиниць до лінії
            distance = self._distance_to_line(point1, point2, (obs_x, obs_y))
            if distance < 5:
                return True
        return False
    
    def _distance_to_line(self, p1, p2, p3):
        """Відстань від точки p3 до лінії між p1 і p2"""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        # Якщо точки p1 і p2 збігаються, повертаємо відстань між p1 і p3
        if x1 == x2 and y1 == y2:
            return np.sqrt((x3 - x1)**2 + (y3 - y1)**2)
        
        px = x2 - x1
        py = y2 - y1
        norm = px*px + py*py
        
        u = ((x3 - x1) * px + (y3 - y1) * py) / float(norm)
        u = max(0, min(1, u))
        
        x = x1 + u * px
        y = y1 + u * py
        
        dx = x - x3
        dy = y - y3
        
        return np.sqrt(dx*dx + dy*dy)
    
    def _update_pheromones(self, pheromone: np.ndarray, solutions: List) -> np.ndarray:
        """Оновлення матриці феромонів"""
        # Спрощена реалізація
        best_solution, best_coverage = max(solutions, key=lambda x: x[1])
        for i in range(len(best_solution)):
            for j in range(i+1, len(best_solution)):
                idx_i = self.interest_points.index(best_solution[i])
                idx_j = self.interest_points.index(best_solution[j])
                pheromone[idx_i][idx_j] += best_coverage / 100
                pheromone[idx_j][idx_i] += best_coverage / 100
        
        return pheromone
    
    def _visualize_progress(self, solution: List[Tuple[float, float]], iteration: int, coverage: float):
        """Тимчасова візуалізація прогресу"""
        self.ax.set_title(f'Оптимізація: Ітерація {iteration}, Покриття: {coverage:.1f}%')
        self._update_plot(solution)
        plt.pause(0.1)
    
    def _update_plot(self, temp_solution=None):
        """Оновлення графічного відображення"""
        self.ax.clear()
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.grid(True)
        
        # Відображення перешкод
        for x, y in self.obstacles:
            self.ax.plot(x, y, 'ks', markersize=8)
        
        # Відображення точок інтересу
        for x, y in self.interest_points:
            self.ax.plot(x, y, 'go', markersize=5, alpha=0.5)
        
        # Відображення антен
        for x, y, ant_type in self.antennas:
            radius = self.antenna_types[ant_type]['radius']
            self.ax.plot(x, y, 'ro', markersize=8)
            circle = plt.Circle((x, y), radius, color='r', alpha=0.1)
            self.ax.add_patch(circle)
        
        # Відображення тимчасового рішення (під час оптимізації)
        if temp_solution:
            for x, y in temp_solution:
                self.ax.plot(x, y, 'bo', markersize=10)
                circle = plt.Circle((x, y), self.coverage_radius, color='b', alpha=0.1)
                self.ax.add_patch(circle)
        
        self.fig.canvas.draw()

# Запуск програми
if __name__ == "__main__":
    optimizer = AntennaPlacementOptimizer()
    plt.show()