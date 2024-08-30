import pygame
import sys
from game import Game
from menu import Menu

# Initialize Pygame
pygame.init()

# Set up the display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Advanced Battleship")

# Initialize game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
OPTIONS = 3

class Battleship:
    def __init__(self):
        self.state = MENU
        self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.game = None
        self.load_assets()
        self.transition_alpha = 255
        self.transitioning = False

    def load_assets(self):
        # Load sound effects
        pygame.mixer.init()
        self.sound_effects = {
            'shot': pygame.mixer.Sound('assets/sounds/shot.wav'),
            'hit': pygame.mixer.Sound('assets/sounds/hit.wav'),
            'miss': pygame.mixer.Sound('assets/sounds/miss.wav'),
            'victory': pygame.mixer.Sound('assets/sounds/victory.wav'),
        }
        # Load background music
        pygame.mixer.music.load('assets/sounds/ocean_ambience.mp3')
        pygame.mixer.music.play(-1)  # Loop indefinitely
        
        # Load images
        self.menu_background = pygame.image.load('assets/images/menu_background.jpg')
        self.water_tiles = pygame.image.load('assets/images/water_tiles.png')
        self.ship_tiles = pygame.image.load('assets/images/ship_tiles.png')
        self.explosion = pygame.image.load('assets/images/explosion.png')
        self.splash = pygame.image.load('assets/images/splash.png')

    def run(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state == MENU:
                    action = self.menu.handle_event(event)
                    if action == "start":
                        self.transition_to(PLAYING)
                    elif action == "options":
                        self.transition_to(OPTIONS)
                    elif action == "quit":
                        pygame.quit()
                        sys.exit()
                elif self.state == PLAYING:
                    game_over, winner = self.game.handle_event(event)
                    if game_over:
                        self.transition_to(GAME_OVER)
                        self.sound_effects['victory'].play()
                elif self.state == GAME_OVER:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.transition_to(MENU)
                elif self.state == OPTIONS:
                    # Handle options menu events here
                    pass

            screen.fill((0, 0, 0))  # Clear screen

            if self.state == MENU:
                self.menu.draw(screen)
            elif self.state == PLAYING:
                self.game.draw(screen)
            elif self.state == GAME_OVER:
                self.draw_game_over(screen, winner)
            elif self.state == OPTIONS:
                self.draw_options(screen)

            if self.transitioning:
                self.draw_transition(screen)

            pygame.display.flip()
            clock.tick(60)

    def draw_game_over(self, screen, winner):
        font = pygame.font.Font(None, 74)
        text = font.render(f"Player {winner} Wins!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)

        font = pygame.font.Font(None, 36)
        text = font.render("Click to return to menu", True, (200, 200, 200))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(text, text_rect)

    def draw_options(self, screen):
        font = pygame.font.Font(None, 48)
        text = font.render("Options", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(text, text_rect)

        # Add options menu items here

    def transition_to(self, new_state):
        self.transitioning = True
        self.transition_alpha = 0
        self.new_state = new_state

    def draw_transition(self, screen):
        if self.transition_alpha < 255:
            self.transition_alpha += 15
            transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            transition_surface.fill((0, 0, 0))
            transition_surface.set_alpha(self.transition_alpha)
            screen.blit(transition_surface, (0, 0))
        else:
            self.state = self.new_state
            if self.state == PLAYING:
                self.game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, self.sound_effects)
            self.transitioning = False
            self.transition_alpha = 255

def main():
    battleship = Battleship()
    battleship.run()

if __name__ == "__main__":
    main()
