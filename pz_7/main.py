import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

SUSCEPTIBLE = 0
INFECTED = 1
RECOVERED = 2

class EpidemicModel:
    def __init__(self, size=50, p_infect=0.3, t_recover=5, initial_infected=5):
        self.size = size
        self.p_infect = p_infect
        self.t_recover = t_recover
        self.grid = np.zeros((size, size), dtype=int)
        self.time_infected = np.zeros((size, size), dtype=int)
        
        for _ in range(initial_infected):
            x, y = np.random.randint(0, size, 2)
            self.grid[x, y] = INFECTED
            self.time_infected[x, y] = 1
    
    def count_neighbors(self, x, y):
        infected = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = x + i, y + j
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.grid[nx, ny] == INFECTED:
                        infected += 1
        return infected
    
    def update(self):
        new_grid = self.grid.copy()
        new_time = self.time_infected.copy()
        
        for x in range(self.size):
            for y in range(self.size):
                if self.grid[x, y] == SUSCEPTIBLE:
                    infected_neighbors = self.count_neighbors(x, y)
                    if infected_neighbors > 0 and np.random.random() < self.p_infect * infected_neighbors / 8:
                        new_grid[x, y] = INFECTED
                        new_time[x, y] = 1
                
                elif self.grid[x, y] == INFECTED:
                    if self.time_infected[x, y] >= self.t_recover:
                        new_grid[x, y] = RECOVERED
                        new_time[x, y] = 0
                    else:
                        new_time[x, y] += 1
        
        self.grid = new_grid
        self.time_infected = new_time
    
    def get_counts(self):
        s = np.sum(self.grid == SUSCEPTIBLE)
        i = np.sum(self.grid == INFECTED)
        r = np.sum(self.grid == RECOVERED)
        return s, i, r

def visual(model, steps=100):
    plt.style.use('default')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.6
    
    fig = plt.figure(figsize=(14, 7))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.5])
    
    ax1 = fig.add_subplot(gs[:, 0])
    
    ax2 = fig.add_subplot(gs[0, 1])
    
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.axis('off')
    
    cmap = ListedColormap(['#2ecc71', '#e74c3c', '#95a5a6'])
    norm = plt.Normalize(vmin=-0.5, vmax=2.5)
    
    img = ax1.imshow(model.grid, cmap=cmap, norm=norm, interpolation='none')
    ax1.set_title('Просторовий розподіл станів', pad=20)
    
    susceptible_patch = mpatches.Patch(color='#2ecc71', label='Здорові (S)')
    infected_patch = mpatches.Patch(color='#e74c3c', label='Інфіковані (I)')
    recovered_patch = mpatches.Patch(color='#95a5a6', label='Одужавші (R)')
    ax1.legend(handles=[susceptible_patch, infected_patch, recovered_patch], 
               loc='upper right', bbox_to_anchor=(1.35, 1))
    
    ax2.set_xlim(0, steps)
    ax2.set_ylim(0, model.size**2)
    ax2.set_xlabel('Час (кроки)', fontsize=10)
    ax2.set_ylabel('Кількість клітин', fontsize=10)
    ax2.set_title('Динаміка епідемії', pad=20)
    ax2.grid(True)
    
    line_s, = ax2.plot([], [], '#2ecc71', linewidth=2, label='Здорові (S)')
    line_i, = ax2.plot([], [], '#e74c3c', linewidth=2, label='Інфіковані (I)')
    line_r, = ax2.plot([], [], '#95a5a6', linewidth=2, label='Одужавші (R)')
    ax2.legend(loc='upper right')
    
    info_text = ax3.text(0.1, 0.5, '', fontsize=10, va='center')
    
    time_points = []
    s_counts = []
    i_counts = []
    r_counts = []
    
    def init():
        s, i, r = model.get_counts()
        s_counts.append(s)
        i_counts.append(i)
        r_counts.append(r)
        time_points.append(0)
        
        line_s.set_data(time_points, s_counts)
        line_i.set_data(time_points, i_counts)
        line_r.set_data(time_points, r_counts)
        
        info_text.set_text(
            f"Поточний стан:\n"
            f"Здорові: {s} ({s/model.size**2:.1%})\n"
            f"Інфіковані: {i} ({i/model.size**2:.1%})\n"
            f"Одужавші: {r} ({r/model.size**2:.1%})\n\n"
            f"Параметри моделі:\n"
            f"Ймовірність інфікування: {model.p_infect}\n"
            f"Час одужання: {model.t_recover} кроків"
        )
        
        return img, line_s, line_i, line_r, info_text
    
    def update(frame):
        model.update()
        s, i, r = model.get_counts()
        
        s_counts.append(s)
        i_counts.append(i)
        r_counts.append(r)
        time_points.append(frame + 1)
        
        img.set_array(model.grid)
        line_s.set_data(time_points, s_counts)
        line_i.set_data(time_points, i_counts)
        line_r.set_data(time_points, r_counts)
        
        info_text.set_text(
            f"Поточний стан (крок {frame+1}):\n"
            f"Здорові: {s} ({s/model.size**2:.1%})\n"
            f"Інфіковані: {i} ({i/model.size**2:.1%})\n"
            f"Одужавші: {r} ({r/model.size**2:.1%})\n\n"
            f"Параметри моделі:\n"
            f"Ймовірність інфікування: {model.p_infect}\n"
            f"Час одужання: {model.t_recover} кроків"
        )
        
        if frame == 5:
            max_y = max(max(s_counts), max(i_counts), max(r_counts))
            ax2.set_ylim(0, max_y * 1.1)
        
        return img, line_s, line_i, line_r, info_text
    
    ani = FuncAnimation(fig, update, frames=steps, init_func=init, 
                        blit=True, interval=300, repeat=False)
    
    plt.tight_layout()
    plt.show()
    
    return ani

model = EpidemicModel(p_infect=0.4, t_recover=6, size=30)
visual(model, steps=50)

model = EpidemicModel(p_infect=0.2, t_recover=12, size=30)
visual(model, steps=50)
