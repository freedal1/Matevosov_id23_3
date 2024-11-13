import pygame
import numpy as np
import json
import os


class Wave:
    def __init__(self, amplitude, period, speed, phase, vertical_offset):
        self.amplitude = amplitude
        self.period = period
        self.speed = speed
        self.position = phase  # начальная фаза волны
        self.vertical_offset = vertical_offset  # смещение по вертикали

    def get_y_values(self, x):
        # вертикальная позиция волны в зависимости от x
        return self.amplitude * np.sin(2 * np.pi * (x / self.period - self.position)) + self.vertical_offset

    def update_position(self, dt):
        # обновление фазы волны на основе времени dt
        self.position += self.speed * dt


class Float:
    def __init__(self, mass, volume, wave_index):
        self.mass = mass
        self.volume = volume
        self.x = 200  # начальная позиция по оси x
        self.y_offset = 5  # начальное смещение от высоты волны
        self.wave_index = wave_index  # индекс волны
        self.time = 0  # для изменения позиции во времени
        self.density_water = 1000  # плотность воды
        self.g = 9.81  # ускорение свободного падения
        self.coef = mass * volume  # коэффициент, определяющий погружение
        self.oscillation_amplitude = 2.0  # коэффициент для уменьшения амплитуды колебаний

        self.archimedes_factor = 0.00133
        # используется понижающий коэфф для простоты.
        # Его можно убрать, но тогда нужно будет подбирать адекватные значения массы и объема поплавка в той системе координат,
        # которую мы создали в данной программе


    def calculate_buoyant_force(self):
        # Сила Архимеда (подъемная сила) с уменьшением на коэффициент
        return self.density_water * self.volume * self.g * self.archimedes_factor # здесь можно убрать коэфф , но тогда нужно подобрать адекватные массу и объем поплавка

    def update_position(self, waves, dt):
        wave_y = waves[self.wave_index].get_y_values(self.x)  # высота волны на позиции x

        # Расчет силы тяжести поплавка
        force_gravity = self.mass * self.g

        # Сила Архимеда (подъемная сила)
        buoyant_force = self.calculate_buoyant_force()

        # Разница сил Архимеда и силы тяжести
        net_force = buoyant_force - force_gravity

        # Расчет осцилляции с учетом коэффициента погружения
        # Чем выше коэффициент (масса * объем), тем меньше будет погружение
        oscillation = (net_force / self.coef) * np.sin(2 * np.pi * self.time)

        # Уменьшаем амплитуду колебаний
        self.y = wave_y + oscillation * self.oscillation_amplitude  # уменьшенная амплитуда

        # Увеличиваем время для плавного изменения положения
        self.time += dt


# загрузка данных из json
def load_data(filename):
    if os.path.exists(filename):
        # если файл существует, загружаем данные из него
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        # если файла нет, создаем начальные значения
        data = {
            "waves": [
                {"amplitude": 50.0, "period": 200.0, "speed": 0.5, "phase": 0.0, "vertical_offset": 200.0},
                {"amplitude": 50.0, "period": 200.0, "speed": 0.5, "phase": 1.5, "vertical_offset": 400.0}
            ],
            "floats": [
                {"mass": 5.0, "volume": 1.0, "wave_index": 0},
                {"mass": 0.5, "volume": 0.5, "wave_index": 1}
            ]
        }
        # сохраняем в json
        with open(filename, 'w') as file:
            json.dump(data, file)
        return data


def main():
    # данные из JSON
    filename = 'data.json'
    data = load_data(filename)

    # волны на основе данных
    waves = [Wave(**wave) for wave in data['waves']]
    # создаем поплавки с указанием индекса волны
    floats = [Float(**float_data) for float_data in data['floats']]

    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # размер окна
    clock = pygame.time.Clock()  # объект для контроля времени

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # время между кадрами

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # проверка на закрытие окна
                running = False

        for wave in waves:
            wave.update_position(dt)  # обновление позиции волн

        for float_obj in floats:
            float_obj.update_position(waves, dt)  # обновление позиции поплавков

        # состояния на экране
        screen.fill((255, 255, 255))

        # волны на экран
        for x in range(800):
            for wave in waves:
                wave_y = wave.get_y_values(x)  # высота волны для текущего x
                pygame.draw.circle(screen, (0, 0, 255), (x, int(wave_y)), 3)  # рисуем точку волны

        # поплавки на экран
        for float_obj in floats:
            pygame.draw.circle(screen, (255, 0, 0), (float_obj.x, int(float_obj.y)), 18)  # рисуем поплавок

        pygame.display.flip()  # обновление экрана

    pygame.quit()  # завершение работы


if __name__ == "__main__":
    main()
