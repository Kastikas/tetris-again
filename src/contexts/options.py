import pygame

import sys
import configuration.config as config
import color
import json
from .base import Context

TEXT_INCREMENT = 60
RESERVED_KEYS = ["esc", "enter"]
screen_w, screen_h = config.SCREEN_RESOUTION


class ConfigPlayerContext(Context):
    def __init__(self, drawer):
        super(ConfigPlayerContext, self).__init__(drawer)

    def draw_options(self):
        self.drawer.fill(color.BLACK)
        try:
            configuration = json.load(open(config.OPTIONS_FILE))
        except Exception as e:
            print(e)

        font = pygame.font.Font(config.FONT_FILE, 40)
        # List used to track which options to set and which keys are being used
        list_of_options = []
        list_of_used_keys = ["return", "escape"]
        width_pos = (screen_w / 100) * 5
        # Drawing the options and their respective cubes
        draw_dict = configuration.copy()
        pygame.draw.line(
            self.drawer._surface,
            color.WHITE,
            (screen_w / 2 - 10, 50),
            (screen_w / 2 - 10, screen_h)
        )
        for set in range(int(len(configuration) / 5)):
            height_pos = 50
            width_pos = (screen_w / 100) * (5 + 50 * set)
            option_enumeration = 0
            for count, options in enumerate(draw_dict):

                option = Option(
                    height_pos,
                    width_pos,
                    options,
                    option_enumeration,
                    configuration[options]
                )

                option.set_surface()

                option.set_text(color.WHITE)

                list_of_options.append(option)
                list_of_used_keys.append(configuration[options])
                height_pos += 100
                option_enumeration += 1
                if count == 4:
                    break
            confirm_font = font.render("Press Enter to confirm", 1, color.WHITE, color.BLACK)
            self.drawer.blit(
                confirm_font,
                ((screen_w - confirm_font.get_width()) / 2, screen_h - 40)
            )
            remove_list = []
            for key in draw_dict:
                remove_list.append(key)
            remove_list = remove_list[0:5:]
            for d in remove_list:
                draw_dict.pop(d)
        self.execute(list_of_options, list_of_used_keys)

    def execute(self, options, keys_used):

        fpsClock = pygame.time.Clock()
        font = pygame.font.Font(config.FONT_FILE, 40)
        setting_key = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if setting_key is False:
                        for option in options:
                            # Checking which option the user Clicked
                            if option.check_collision(pygame.mouse.get_pos()):
                                setting_key = True
                                new_key_option = option
                                # Changing the color to yellow for better User Experience
                                new_key_option.surface.fill(color.YELLOW)
                                new_key_option.set_surface()
                                new_key_option.set_text(color.YELLOW)
                    else:
                        eraser_box = pygame.Surface((screen_w, 50))
                        eraser_box.fill(color.BLACK)
                        self.drawer.blit(
                            eraser_box,
                            (0, 0)
                        )
                        error_font = font.render(
                            "Already selecting a key",
                            1,
                            color.RED
                        )
                        self.drawer.blit(
                            error_font,
                            ((screen_w - error_font.get_width()) / 2, 0)
                        )
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == pygame.K_RETURN:
                        # Dumping the new options (or old if no changes are made) to JSON
                        dumpdict = {}

                        for option in options:
                            dumpdict[option.option] = option.key
                        json_dump = json.dumps(dumpdict)

                        with open(config.OPTIONS_FILE, "w") as file:
                            file.write(json_dump)
                        return "Back to the Menu"

                    if setting_key is True:
                        if pygame.key.name(event.key) not in keys_used:
                            # Removing the existing key to the used keys list
                            # and adding the new one
                            keys_used.remove(new_key_option.key)
                            keys_used.append(pygame.key.name(event.key))
                            new_key_option.key = pygame.key.name(event.key)

                            # Erasing the existing text
                            new_key_option.erase_text()
                            eraser_box = pygame.Surface((screen_w, 50))
                            eraser_box.fill(color.BLACK)
                            self.drawer.blit(
                                eraser_box,
                                (0, 0)
                            )
                            # Changing the color to white to represent set option.
                            new_key_option.surface.fill(color.WHITE)
                            new_key_option.set_surface()
                            new_key_option.set_text()
                            setting_key = False
                        else:
                            if pygame.key.name(event.key) not in RESERVED_KEYS:
                                for option in options:
                                    if option.key == pygame.key.name(event.key):
                                        option.key = new_key_option.key
                                        # Erasing the swapped key test
                                        option.erase_text()
                                        # Placing the new text
                                        option.set_text(color.WHITE)
                                        break
                                new_key_option.key = pygame.key.name(event.key)
                                new_key_option.surface.fill(color.WHITE)
                                # Erasing old text
                                new_key_option.erase_text()
                                # Changing the surface color
                                new_key_option.set_surface()
                                # inserting new text
                                new_key_option.set_text(color.WHITE)

                                setting_key = False

                            else:
                                # In case that the key is reserved, show error.
                                eraser_box = pygame.Surface((screen_w, 50))
                                eraser_box.fill(color.BLACK)
                                self.drawer.blit(
                                    eraser_box,
                                    (0, 0)
                                )
                                error_font = font.render(
                                    "Key reserved",
                                    1,
                                    color.RED
                                )
                                self.drawer.blit(
                                    error_font,
                                    ((screen_w - error_font.get_width()) / 2, 0)
                                )

            pygame.display.flip()
            fpsClock.tick(32)


class Option():
    def __init__(self, height, width, option, count, key):
        self.height = height
        self.width = width
        self.option = option
        self.key = key
        self.count = count
        self.surface = pygame.Surface((50, 50))
        self.rect = self.surface.get_rect(topleft=(width, height))
        self.surface.fill(color.WHITE)

    def check_collision(self, pos):
        if self.rect.collidepoint(pos):
            return True
        return False

    def set_surface(self):
        pygame.display.get_surface().blit(
            self.surface,
            (self.width, self.height)
        )

    def set_text(self, text_color):
        font = pygame.font.Font(config.FONT_FILE, 40)
        pygame.display.get_surface().blit(
            font.render(str(self.key), 1, text_color, color.BLACK),
            (self.width + TEXT_INCREMENT, (self.count * 100) + 50)
        )

    def erase_text(self):
        eraser_box = pygame.Surface(((screen_w / 100) * 30, 50))
        eraser_box.fill(color.BLACK)
        pygame.display.get_surface().blit(
            eraser_box,
            (self.width + TEXT_INCREMENT, (self.count * 100) + 50)
        )
