# Вариант 10

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def string_displacement(t, L, A0, gamma):
    omega0 = np.pi / L
    omega = np.sqrt(omega0 ** 2 - gamma ** 2)
    return A0 * np.exp(-gamma * t) * np.cos(omega * t)


def update(frame):
    global line, t
    t += dt
    y = string_displacement(t, L.get(), A0.get(), gamma.get())
    line.set_ydata([y, -y])
    return line,


def start_animation():
    global ani, t
    t = 0  # Сброс времени
    ani = FuncAnimation(fig, update, frames=range(200), interval=dt * 1000, blit=True)


def reset():
    global ani, t, line
    t = 0
    if ani:
        ani.event_source.stop()
    line.set_ydata([0, 0])
    canvas.draw()


root = tk.Tk()
root.title("Симуляция затухающих колебаний струны")

L = tk.DoubleVar(value=1.0)
A0 = tk.DoubleVar(value=1.0)
gamma = tk.DoubleVar(value=0.1)

dt = 0.05
ani = None

fig, ax = plt.subplots(figsize=(6, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
ax.set_xlim(-0.5, 0.5)
ax.set_ylim(-1.5, 1.5)
line, = ax.plot([0, 0], [0, 0], lw=2)

frame_controls = ttk.Frame(root)
frame_controls.pack(side=tk.BOTTOM, fill=tk.X)

ttk.Label(frame_controls, text="Длина струны (L):").pack(side=tk.LEFT, padx=5)
spinbox_L = ttk.Spinbox(frame_controls, from_=0.5, to=5.0, increment=0.1, textvariable=L)
spinbox_L.pack(side=tk.LEFT)

ttk.Label(frame_controls, text="Амплитуда (A0):").pack(side=tk.LEFT, padx=5)
slider_A0 = ttk.Scale(frame_controls, from_=0.1, to=2.0, variable=A0, orient=tk.HORIZONTAL)
slider_A0.pack(side=tk.LEFT)

ttk.Label(frame_controls, text="Затухание (γ):").pack(side=tk.LEFT, padx=5)
slider_gamma = ttk.Scale(frame_controls, from_=0.01, to=0.5, variable=gamma, orient=tk.HORIZONTAL)
slider_gamma.pack(side=tk.LEFT)

btn_start = ttk.Button(frame_controls, text="Старт", command=start_animation)
btn_start.pack(side=tk.LEFT, padx=5)
btn_reset = ttk.Button(frame_controls, text="Сброс", command=reset)
btn_reset.pack(side=tk.LEFT, padx=5)

root.mainloop()