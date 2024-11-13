import tkinter as tk
import math

class MovingPointApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Moving Point on Circle")
        self.canvas = tk.Canvas(master, width=600, height=600, bg="white")
        self.canvas.pack()

        self.radius = 200
        self.center_x = 300
        self.center_y = 300
        self.angle = 0
        self.speed = 0.02  # Измените это значение для изменения скорости

        self.draw_circle()

        self.animate()

    def draw_circle(self):

        x0 = self.center_x - self.radius
        y0 = self.center_y - self.radius
        x1 = self.center_x + self.radius
        y1 = self.center_y + self.radius
        self.canvas.create_oval(x0, y0, x1, y1, outline="blue")

    def animate(self):
        self.canvas.delete("point")


        point_x = self.center_x + self.radius * math.cos(self.angle)
        point_y = self.center_y + self.radius * math.sin(self.angle)

        self.canvas.create_oval(point_x - 5, point_y - 5, point_x + 5, point_y + 5, fill="red", tags="point")

        self.angle += self.speed


        self.master.after(20, self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    app = MovingPointApp(root)
    root.mainloop()