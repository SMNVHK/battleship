import pygame
import math

class Menu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.buttons = [
            {"text": "Start Game", "action": "start", "rect": pygame.Rect(width // 2 - 100, height // 2, 200, 50)},
            {"text": "Options", "action": "options", "rect": pygame.Rect(width // 2 - 100, height // 2 + 70, 200, 50)},
            {"text": "Quit", "action": "quit", "rect": pygame.Rect(width // 2 - 100, height // 2 + 140, 200, 50)}
        ]
        self.background = pygame.image.load('assets/images/menu_background.jpg')
        self.background = pygame.transform.scale(self.background, (width, height))
        self.wave_offset = 0
        self.hover_button = None
        self.water_tiles = pygame.image.load('assets/images/water_tiles.png')
        self.water_tiles = pygame.transform.scale(self.water_tiles, (width, height))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button["rect"].collidepoint(event.pos):
                    return button["action"]
        elif event.type == pygame.MOUSEMOTION:
            self.hover_button = next((b for b in self.buttons if b["rect"].collidepoint(event.pos)), None)
        return None

    def draw(self, screen):
        # Draw animated water background
        screen.blit(self.background, (0, 0))
        self.draw_animated_water(screen)

        # Draw title with glow effect
        title = self.title_font.render("Advanced Battleship", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        self.draw_text_with_glow(screen, title, title_rect)

        # Draw buttons with improved design
        for button in self.buttons:
            self.draw_button(screen, button)

        self.wave_offset += 0.05

    def draw_animated_water(self, screen):
        tile_size = 64
        for y in range(0, self.height, tile_size):
            for x in range(0, self.width, tile_size):
                offset_y = int(math.sin((x + self.wave_offset) * 0.05) * 5)
                screen.blit(self.water_tiles, (x, y + offset_y))

    def draw_button(self, screen, button):
        color = (100, 200, 255) if button == self.hover_button else (50, 150, 200)
        pygame.draw.rect(screen, color, button["rect"], border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), button["rect"], 2, border_radius=10)
        
        # Add shadow effect
        shadow_rect = button["rect"].copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        text = self.font.render(button["text"], True, (255, 255, 255))
        text_rect = text.get_rect(center=button["rect"].center)
        screen.blit(text, text_rect)

    def draw_text_with_glow(self, screen, text, rect):
        glow_color = (100, 200, 255)
        for offset in range(5, 0, -1):
            glow_rect = rect.copy()
            glow_rect.x -= offset
            glow_rect.y -= offset
            glow_rect.width += offset * 2
            glow_rect.height += offset * 2
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*glow_color, 10), (0, 0, glow_rect.width, glow_rect.height), border_radius=10)
            screen.blit(glow_surface, glow_rect)
        screen.blit(text, rect)
