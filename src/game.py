import pygame
import random
import math

class Ship:
    def __init__(self, size):
        self.size = size
        self.hits = 0
        self.positions = []

    def is_sunk(self):
        return self.hits == self.size

class Player:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.ships = []
        self.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        self.opponent_grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

    def place_ships(self, ship_sizes):
        for size in ship_sizes:
            while True:
                x = random.randint(0, self.grid_size - 1)
                y = random.randint(0, self.grid_size - 1)
                direction = random.choice(['horizontal', 'vertical'])
                
                if self.can_place_ship(x, y, size, direction):
                    self.place_ship(x, y, size, direction)
                    break

    def can_place_ship(self, x, y, size, direction):
        if direction == 'horizontal':
            if x + size > self.grid_size:
                return False
            return all(self.grid[y][x+i] == 0 for i in range(size))
        else:
            if y + size > self.grid_size:
                return False
            return all(self.grid[y+i][x] == 0 for i in range(size))

    def place_ship(self, x, y, size, direction):
        ship = Ship(size)
        if direction == 'horizontal':
            for i in range(size):
                self.grid[y][x+i] = 1
                ship.positions.append((x+i, y))
        else:
            for i in range(size):
                self.grid[y+i][x] = 1
                ship.positions.append((x, y+i))
        self.ships.append(ship)

    def receive_attack(self, x, y):
        if self.grid[y][x] == 1:
            self.grid[y][x] = 2  # Hit
            for ship in self.ships:
                if (x, y) in ship.positions:
                    ship.hits += 1
                    return True, ship.is_sunk()
        else:
            self.grid[y][x] = 3  # Miss
        return False, False

class Game:
    def __init__(self, width, height, sound_effects):
        self.width = width
        self.height = height
        self.grid_size = 10
        self.cell_size = min(width, height) // (self.grid_size * 2 + 1)
        self.margin = (width - self.cell_size * self.grid_size * 2) // 3
        self.players = [Player(self.grid_size), Player(self.grid_size)]
        self.current_player = 0
        self.font = pygame.font.Font(None, 36)
        self.ship_sizes = [4, 3, 3, 2, 2, 2]
        self.players[0].place_ships(self.ship_sizes)
        self.players[1].place_ships(self.ship_sizes)
        self.sound_effects = sound_effects
        self.animations = []
        self.water_offset = 0
        self.load_assets()

    def load_assets(self):
        self.water_tiles = pygame.image.load('assets/images/water_tiles.png')
        self.water_tiles = pygame.transform.scale(self.water_tiles, (self.cell_size * 4, self.cell_size * 4))
        self.hit_marker = pygame.image.load('assets/images/explosion.png')
        self.hit_marker = pygame.transform.scale(self.hit_marker, (self.cell_size, self.cell_size))
        self.miss_marker = pygame.image.load('assets/images/splash.png')
        self.miss_marker = pygame.transform.scale(self.miss_marker, (self.cell_size, self.cell_size))
        self.ship_tiles = pygame.image.load('assets/images/ship_tiles.png')
        self.ship_tiles = pygame.transform.scale(self.ship_tiles, (self.cell_size * 5, self.cell_size * 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            grid_x = (x - self.margin - self.cell_size * self.grid_size) // self.cell_size
            grid_y = (y - self.margin) // self.cell_size
            
            if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
                opponent = self.players[1 - self.current_player]
                if opponent.opponent_grid[grid_y][grid_x] == 0:
                    hit, sunk = opponent.receive_attack(grid_x, grid_y)
                    if hit:
                        self.sound_effects['hit'].play()
                        opponent.opponent_grid[grid_y][grid_x] = 2
                        self.add_animation('hit', grid_x, grid_y)
                        if sunk:
                            if all(ship.is_sunk() for ship in opponent.ships):
                                return True, self.current_player + 1
                    else:
                        self.sound_effects['miss'].play()
                        opponent.opponent_grid[grid_y][grid_x] = 3
                        self.add_animation('miss', grid_x, grid_y)
                    self.current_player = 1 - self.current_player
        return False, None

    def add_animation(self, anim_type, x, y):
        if anim_type == 'hit':
            self.animations.append({
                'type': 'hit',
                'x': x,
                'y': y,
                'frame': 0,
                'max_frame': 10
            })
        elif anim_type == 'miss':
            self.animations.append({
                'type': 'miss',
                'x': x,
                'y': y,
                'frame': 0,
                'max_frame': 10
            })

    def update_animations(self):
        for anim in self.animations:
            anim['frame'] += 1
        self.animations = [anim for anim in self.animations if anim['frame'] < anim['max_frame']]
        self.water_offset += 0.05

    def draw(self, screen):
        screen.fill((0, 64, 128))  # Ocean blue background
        
        for i, player in enumerate(self.players):
            offset_x = self.margin + (self.margin + self.grid_size * self.cell_size) * i
            self.draw_grid(screen, offset_x, self.margin, player.grid if i == self.current_player else player.opponent_grid)
        
        # Draw player labels
        for i in range(2):
            text = self.font.render(f"Player {i+1}", True, (255, 255, 255))
            offset_x = self.margin + (self.margin + self.grid_size * self.cell_size) * i
            screen.blit(text, (offset_x, self.margin // 2))
        
        # Draw current player indicator
        text = self.font.render(f"Current Player: {self.current_player + 1}", True, (255, 255, 0))
        screen.blit(text, (self.width // 2 - text.get_width() // 2, self.height - self.margin // 2))

        self.draw_animations(screen)
        self.update_animations()

    def draw_grid(self, screen, offset_x, offset_y, grid):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = pygame.Rect(offset_x + x * self.cell_size, offset_y + y * self.cell_size, self.cell_size, self.cell_size)
                water_y_offset = int(math.sin((x + y + self.water_offset) * 0.5) * 2)
                tile_x = (x % 2) * self.cell_size
                tile_y = (y % 2) * self.cell_size
                screen.blit(self.water_tiles, (rect.x, rect.y + water_y_offset), (tile_x, tile_y, self.cell_size, self.cell_size))
                
                if grid[y][x] == 1:  # Ship
                    ship_tile_x = (x % 5) * self.cell_size
                    ship_tile_y = (y % 2) * self.cell_size
                    screen.blit(self.ship_tiles, rect, (ship_tile_x, ship_tile_y, self.cell_size, self.cell_size))
                elif grid[y][x] == 2:  # Hit
                    screen.blit(self.hit_marker, rect)
                elif grid[y][x] == 3:  # Miss
                    screen.blit(self.miss_marker, rect)
        
        # Highlight current player's turn
        if self.current_player == 0:
            pygame.draw.rect(screen, (255, 255, 0), (offset_x - 5, offset_y - 5, self.grid_size * self.cell_size + 10, self.grid_size * self.cell_size + 10), 5)
        else:
            pygame.draw.rect(screen, (255, 255, 0), (offset_x + self.grid_size * self.cell_size + self.margin - 5, offset_y - 5, self.grid_size * self.cell_size + 10, self.grid_size * self.cell_size + 10), 5)

    def draw_animations(self, screen):
        for anim in self.animations:
            if anim['type'] == 'hit':
                self.draw_hit_animation(screen, anim)
            elif anim['type'] == 'miss':
                self.draw_miss_animation(screen, anim)

    def draw_hit_animation(self, screen, anim):
        x = self.margin + self.cell_size * self.grid_size + anim['x'] * self.cell_size
        y = self.margin + anim['y'] * self.cell_size
        radius = int((anim['frame'] / anim['max_frame']) * self.cell_size)
        pygame.draw.circle(screen, (255, 100, 100, 128), (x + self.cell_size // 2, y + self.cell_size // 2), radius)

    def draw_miss_animation(self, screen, anim):
        x = self.margin + self.cell_size * self.grid_size + anim['x'] * self.cell_size
        y = self.margin + anim['y'] * self.cell_size
        size = int((1 - anim['frame'] / anim['max_frame']) * self.cell_size)
        pygame.draw.rect(screen, (255, 255, 255, 128), (x + (self.cell_size - size) // 2, y + (self.cell_size - size) // 2, size, size))
