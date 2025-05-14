import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.integrate import solve_ivp

class LorenzAttractor:
    def __init__(self, sigma=10, rho=28, beta=8/3):
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
    
    def equations(self, t, state):
        x, y, z = state
        dxdt = self.sigma * (y - x)
        dydt = x * (self.rho - z) - y
        dzdt = x * y - self.beta * z
        return [dxdt, dydt, dzdt]
    
    def solve(self, initial_state, t_span, t_eval):
        solution = solve_ivp(
            self.equations,
            t_span,
            initial_state,
            t_eval=t_eval,
            rtol=1e-6,
            atol=1e-9
        )
        return solution
    
    def plot_attractor(self, solution, title="Атрактор Лоренца"):
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(solution.y[0], solution.y[1], solution.y[2], lw=0.5)
        ax.set_title(title)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        plt.show()
    
    def compare_trajectories(self, initial_state1, initial_state2, t_span, t_eval):
        sol1 = self.solve(initial_state1, t_span, t_eval)
        sol2 = self.solve(initial_state2, t_span, t_eval)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), subplot_kw={'projection': '3d'})
        
        ax1.plot(sol1.y[0], sol1.y[1], sol1.y[2], lw=0.5)
        ax1.set_title("Траєкторія 1")
        
        ax2.plot(sol2.y[0], sol2.y[1], sol2.y[2], lw=0.5)
        ax2.set_title("Траєкторія 2")
        
        plt.suptitle("Порівняння траєкторій з різними початковими умовами")
        plt.show()
        
        distance = np.sqrt(
            (sol1.y[0] - sol2.y[0])**2 +
            (sol1.y[1] - sol2.y[1])**2 +
            (sol1.y[2] - sol2.y[2])**2
        )
        
        plt.figure(figsize=(10, 6))
        plt.plot(t_eval, distance)
        plt.title("Відстань між траєкторіями в часі")
        plt.xlabel("Час")
        plt.ylabel("Відстань")
        plt.grid(True)
        plt.show()

t_span = (0, 40)
t_eval = np.linspace(t_span[0], t_span[1], 10000)

lorenz = LorenzAttractor()

initial_state1 = [1.0, 1.0, 1.0]
solution1 = lorenz.solve(initial_state1, t_span, t_eval)
lorenz.plot_attractor(solution1)

initial_state2 = [1.0001, 1.0001, 1.0001]
solution2 = lorenz.solve(initial_state2, t_span, t_eval)

lorenz.compare_trajectories(initial_state1, initial_state2, t_span, t_eval)
