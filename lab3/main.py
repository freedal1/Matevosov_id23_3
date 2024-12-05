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
        self.position = phase
        self.vertical_offset = vertical_offset

    def get_y_values(self, x):
        return self.amplitude * np.sin(2 * np.pi * (x / self.period - self.position)) + self.vertical_offset

    def update_position(self, dt):
        self.position += self.speed * dt


class Float:
    def __init__(self, mass, volume, wave_index):
        self.mass = mass
        self.volume = volume
        self.x = 200
        self.y = 200
        self.wave_index = wave_index
        self.time = 0
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
    window_rect = pygame.Rect((250, 200), (300, 200))
    modify_window = pygame_gui.elements.UIWindow(
        rect=window_rect,
        manager=manager,
        window_display_title="Modify Float Properties"
    )

    mass_input = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((120, 10), (150, 30)),
        manager=manager,
        container=modify_window
    )
    mass_input.set_text(str(float_obj.mass))

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
    y_offset = 10
    for i, wave in enumerate(waves):
        wave_text = f"Wave {i + 1}: Amplitude={wave.amplitude:.2f}, Period={wave.period:.2f}, Speed={wave.speed:.2f}"
        wave_label = font.render(wave_text, True, (0, 0, 0))
        screen.blit(wave_label, (10, y_offset))
        y_offset += 20

    for i, float_obj in enumerate(floats):
        float_text = f"Float {i + 1}: Mass={float_obj.mass:.2f}, Volume={float_obj.volume:.2f}, Y={float_obj.y:.2f}"
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

    slider_container = pygame_gui.elements.UIScrollingContainer(
        relative_rect=pygame.Rect((10, 450), (780, 140)),
        manager=manager
    )

    amplitude_sliders = []
    period_sliders = []

    def create_sliders(wave, offset):
        amp_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, offset), (360, 20)),
            start_value=wave.amplitude,
            value_range=(10.0, 200.0),
            manager=manager,
            container=slider_container
        )
        period_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((400, offset), (360, 20)),
            start_value=wave.period,
            value_range=(50.0, 500.0),
            manager=manager,
            container=slider_container
        )
        return amp_slider, period_slider

    for i, wave in enumerate(waves):
        amp_slider, period_slider = create_sliders(wave, i * 40)
        amplitude_sliders.append(amp_slider)
        period_sliders.append(period_slider)

    add_wave_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, 410), (100, 30)),
        text="Add Wave",
        manager=manager
    )

    remove_wave_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((120, 410), (100, 30)),
        text="Remove Wave",
        manager=manager
    )

    modify_window = None
    selected_float = None
    selected_wave_index = None
    running = True

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
                        new_wave = Wave(50.0, 200.0, 0.5, 0.0, 300.0)
                        waves.append(new_wave)
                        new_float = Float(mass=5.0, volume=1.0, wave_index=len(waves) - 1)
                        floats.append(new_float)

                        offset = len(waves) * 40
                        amp_slider, period_slider = create_sliders(new_wave, offset)
                        amplitude_sliders.append(amp_slider)
                        period_sliders.append(period_slider)

                        slider_container.set_scrollable_area_dimensions((780, len(waves) * 40))

                    elif event.ui_element == remove_wave_button:
                        if selected_wave_index is not None and 0 <= selected_wave_index < len(waves):
                            waves.pop(selected_wave_index)
                            floats = [f for f in floats if f.wave_index != selected_wave_index]

                            for f in floats:
                                if f.wave_index > selected_wave_index:
                                    f.wave_index -= 1

                            amplitude_sliders[selected_wave_index].kill()
                            period_sliders[selected_wave_index].kill()
                            amplitude_sliders.pop(selected_wave_index)
                            period_sliders.pop(selected_wave_index)

                            selected_wave_index = None
                            slider_container.set_scrollable_area_dimensions((780, len(waves) * 40))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, float_obj in enumerate(floats):
                        if abs(event.pos[0] - float_obj.x) < 20 and abs(event.pos[1] - float_obj.y) < 20:
                            modify_window, mass_input, volume_input, save_button = modify_float_properties(manager, float_obj)
                            selected_float = float_obj

                    for i, wave in enumerate(waves):
                        if abs(event.pos[1] - wave.get_y_values(event.pos[0])) < 10:
                            selected_wave_index = i
                            break

        for i, wave in enumerate(waves):
            wave.amplitude = amplitude_sliders[i].get_current_value()
            wave.period = period_sliders[i].get_current_value()

        for wave in waves:
            wave.update_position(dt)

        for float_obj in floats:
            float_obj.update_position(waves, dt)

        screen.fill((255, 255, 255))

        for x in range(801):
            for i, wave in enumerate(waves):
                wave_y = wave.get_y_values(x)
                color = (255, 0, 0) if i == selected_wave_index else (0, 0, 255)
                pygame.draw.circle(screen, color, (x, int(wave_y)), 3)

        for float_obj in floats:
            pygame.draw.circle(screen, (255, 0, 0), (float_obj.x, int(float_obj.y)), 18)

        draw_info(screen, font, waves, floats)

        manager.update(dt)
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
