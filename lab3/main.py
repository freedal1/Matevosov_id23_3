import pygame
import pygame_gui
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
        return self.amplitude * np.sin(2 * np.pi * (x / self.period - self.position)) + self.vertical_offset

    def update_position(self, dt):
        self.position += self.speed * dt


class Float:
    def __init__(self, mass, volume, wave_index):
        self.mass = mass
        self.volume = volume
        self.x = 200  # начальная позиция по оси x
        self.y = 200  # начальная позиция по оси y
        self.wave_index = wave_index  # индекс волны
        self.time = 0  # для изменения позиции во времени
        self.density_water = 1000
        self.g = 9.81
        self.coef = mass * volume
        self.oscillation_amplitude = 2.0

        self.archimedes_factor = 0.00133

    def calculate_buoyant_force(self):
        return self.density_water * self.volume * self.g * self.archimedes_factor

    def update_position(self, waves, dt):
        wave_y = waves[self.wave_index].get_y_values(self.x)
        force_gravity = self.mass * self.g
        buoyant_force = self.calculate_buoyant_force()
        net_force = buoyant_force - force_gravity
        oscillation = (net_force / self.coef) * np.sin(2 * np.pi * self.time)
        self.y = wave_y + oscillation * self.oscillation_amplitude
        self.time += dt


def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        data = {
            "waves": [
                {"amplitude": 50.0, "period": 200.0, "speed": 0.5, "phase": 0.0, "vertical_offset": 200.0},
                {"amplitude": 50.0, "period": 200.0, "speed": 0.5, "phase": 0.5, "vertical_offset": 400.0}
            ],
            "floats": [
                {"mass": 5.0, "volume": 1.0, "wave_index": 0},
                {"mass": 2.0, "volume": 0.5, "wave_index": 1}
            ]
        }
        with open(filename, 'w') as file:
            json.dump(data, file)
        return data


def modify_float_properties(manager, float_obj):
    """Создает красивое окно для изменения свойств поплавка."""
    window_rect = pygame.Rect((250, 200), (300, 200))
    modify_window = pygame_gui.elements.UIWindow(
        rect=window_rect,
        manager=manager,
        window_display_title="Modify Float Properties"
    )

    mass_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 10), (100, 30)),
        text="Mass:",
        manager=manager,
        container=modify_window
    )

    mass_input = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((120, 10), (150, 30)),
        manager=manager,
        container=modify_window
    )
    mass_input.set_text(str(float_obj.mass))

    volume_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((10, 50), (100, 30)),
        text="Volume:",
        manager=manager,
        container=modify_window
    )

    volume_input = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((120, 50), (150, 30)),
        manager=manager,
        container=modify_window
    )
    volume_input.set_text(str(float_obj.volume))

    save_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((90, 100), (120, 30)),
        text="Save",
        manager=manager,
        container=modify_window
    )

    return modify_window, mass_input, volume_input, save_button


def draw_info(screen, font, waves, floats):
    """Отображает информацию о волнах и поплавках на экране."""
    y_offset = 10
    for i, wave in enumerate(waves):
        wave_text = f"Wave {i+1}: Amplitude={wave.amplitude:.2f}, Period={wave.period:.2f}, Speed={wave.speed:.2f}"
        wave_label = font.render(wave_text, True, (0, 0, 0))
        screen.blit(wave_label, (10, y_offset))
        y_offset += 20

    for i, float_obj in enumerate(floats):
        float_text = f"Float {i+1}: Mass={float_obj.mass:.2f}, Volume={float_obj.volume:.2f}, Y={float_obj.y:.2f}"
        float_label = font.render(float_text, True, (0, 0, 0))
        screen.blit(float_label, (10, y_offset))
        y_offset += 20


def main():
    filename = 'data.json'
    data = load_data(filename)

    waves = [Wave(**wave) for wave in data['waves']]
    floats = [Float(**float_data) for float_data in data['floats']]

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    manager = pygame_gui.UIManager((800, 600))

    # Ползунки для изменения параметров двух волн
    wave1_amplitude_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 520), (200, 20)),
        start_value=waves[0].amplitude,
        value_range=(10.0, 200.0),
        manager=manager
    )

    wave1_period_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((10, 550), (200, 20)),
        start_value=waves[0].period,
        value_range=(50.0, 500.0),
        manager=manager
    )

    wave2_amplitude_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((300, 520), (200, 20)),
        start_value=waves[1].amplitude,
        value_range=(10.0, 200.0),
        manager=manager
    )

    wave2_period_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((300, 550), (200, 20)),
        start_value=waves[1].period,
        value_range=(50.0, 500.0),
        manager=manager
    )

    # Кнопки добавления и удаления волн
    add_wave_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((550, 520), (100, 30)),
        text="Add Wave",
        manager=manager
    )

    remove_wave_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((670, 520), (100, 30)),
        text="Remove Wave",
        manager=manager
    )

    modify_window = None
    running = True
    selected_float = None

    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if modify_window and event.ui_element == save_button:
                        try:
                            new_mass = float(mass_input.get_text())
                            new_volume = float(volume_input.get_text())
                            selected_float.mass = new_mass
                            selected_float.volume = new_volume
                        except ValueError:
                            print("Invalid input for mass or volume.")
                        modify_window.kill()
                        modify_window = None
                    elif event.ui_element == add_wave_button:
                        # Добавляем новую волну с дефолтными параметрами
                        waves.append(Wave(50.0, 200.0, 0.5, 0.0, 300.0))
                    elif event.ui_element == remove_wave_button and waves:
                        # Удаляем последнюю волну
                        waves.pop()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    for i, float_obj in enumerate(floats):
                        if abs(event.pos[0] - float_obj.x) < 20 and abs(event.pos[1] - float_obj.y) < 20:
                            modify_window, mass_input, volume_input, save_button = modify_float_properties(manager, float_obj)
                            selected_float = float_obj

        # Обновление ползунков
        waves[0].amplitude = wave1_amplitude_slider.get_current_value()
        waves[0].period = wave1_period_slider.get_current_value()
        waves[1].amplitude = wave2_amplitude_slider.get_current_value()
        waves[1].period = wave2_period_slider.get_current_value()

        # Обновление волн и поплавков
        for wave in waves:
            wave.update_position(dt)

        for float_obj in floats:
            float_obj.update_position(waves, dt)

        # Отрисовка
        screen.fill((255, 255, 255))

        for x in range(800):
            for wave in waves:
                wave_y = wave.get_y_values(x)
                pygame.draw.circle(screen, (0, 0, 255), (x, int(wave_y)), 3)

        for float_obj in floats:
            pygame.draw.circle(screen, (255, 0, 0), (float_obj.x, int(float_obj.y)), 18)

        draw_info(screen, font, waves, floats)

        manager.update(dt)
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
