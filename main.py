import pygame
import random
import math

# --- Конфигурация ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Цвета (Пастельная палитра)
COLOR_BG = (255, 240, 245)  # Lavender Blush
COLOR_PARK = (230, 255, 230)
COLOR_HEART = (255, 105, 180) # Hot Pink
COLOR_TEXT = (100, 50, 50)
COLOR_HUMAN = (100, 150, 255)
COLOR_DOG = (210, 180, 140)  # Tan
COLOR_UI_BAR = (255, 182, 193) # Light Pink

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(10, 20)
        self.lifetime = 1.0
        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-4, -1)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 0.02
        self.size -= 0.2

    def draw(self, surface):
        if self.lifetime > 0:
            # Рисуем сердечко (упрощенно двумя кругами и треугольником)
            alpha = int(self.lifetime * 255)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*COLOR_HEART, alpha), (self.size // 2, self.size // 2), self.size // 2)
            pygame.draw.circle(s, (*COLOR_HEART, alpha), (self.size + self.size // 2, self.size // 2), self.size // 2)
            pygame.draw.polygon(s, (*COLOR_HEART, alpha), [(0, self.size // 2), (self.size * 2, self.size // 2), (self.size, self.size * 2)])
            surface.blit(s, (self.x - self.size, self.y - self.size))

class Dog:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.target = pygame.Vector2(x, y)
        self.speed = 3
        self.state = "IDLE" # IDLE, FOLLOW, FETCH, EAT
        self.angle = 0
        self.love_level = 0
        self.size = 40

    def update(self, player_pos):
        if self.state == "FOLLOW":
            dist = self.pos.distance_to(player_pos)
            if dist > 80:
                dir = (player_pos - self.pos).normalize()
                self.pos += dir * self.speed
        
        # Легкое покачивание (анимация дыхания/хвоста)
        self.angle = math.sin(pygame.time.get_ticks() * 0.01) * 5

    def draw(self, surface):
        # Тело собаки
        rect = pygame.Rect(0, 0, self.size, self.size // 1.5)
        rect.center = self.pos
        
        # Хвост
        tail_end = self.pos + pygame.Vector2(-25, -5).rotate(self.angle * 2)
        pygame.draw.line(surface, COLOR_DOG, self.pos + (-15, 0), tail_end, 8)

        # Рисуем корпус
        pygame.draw.ellipse(surface, COLOR_DOG, rect)
        # Голова
        head_pos = self.pos + (15, -10)
        pygame.draw.circle(surface, COLOR_DOG, (int(head_pos.x), int(head_pos.y)), 15)
        # Ухо
        pygame.draw.ellipse(surface, (139, 69, 19), (head_pos.x - 5, head_pos.y - 5, 10, 15))
        # Глаз
        pygame.draw.circle(surface, (0, 0, 0), (int(head_pos.x + 5), int(head_pos.y - 2)), 2)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Верная любовь: Человек и Собака")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.running = True

        self.player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.player_speed = 5
        self.dog = Dog(WIDTH // 2 - 100, HEIGHT // 2)
        self.particles = []
        self.love_meter = 0
        self.max_love = 100
        
        self.items = [] # Мячики, еда и т.д.

    def spawn_hearts(self, count=5):
        for _ in range(count):
            self.particles.append(Particle(self.dog.pos.x, self.dog.pos.y - 20))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.player_pos.x -= self.player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.player_pos.x += self.player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.player_pos.y -= self.player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.player_pos.y += self.player_speed

        # Границы экрана
        self.player_pos.x = max(50, min(WIDTH - 50, self.player_pos.x))
        self.player_pos.y = max(50, min(HEIGHT - 50, self.player_pos.y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_SPACE: # Погладить
                    if self.player_pos.distance_to(self.dog.pos) < 100:
                        self.love_meter = min(self.max_love, self.love_meter + 5)
                        self.spawn_hearts()
                if event.key == pygame.K_f: # Кормить
                    self.items.append({"type": "food", "pos": self.player_pos.copy()})
                if event.key == pygame.K_p: # Играть (мяч)
                    self.items.append({"type": "ball", "pos": self.player_pos.copy(), "vel": pygame.Vector2(random.uniform(-5, 5), random.uniform(-5, 5))})
                if event.key == pygame.K_k: # Сделать фото
                    pygame.image.save(self.screen, "happiness.png")
                    print("Фото сохранено как happiness.png")

    def update(self):
        # Определение цели для собаки
        target_item = None
        
        # Сначала ищем еду
        for item in self.items:
            if item["type"] == "food":
                target_item = item
                break
        
        # Если еды нет, ищем мячик
        if not target_item:
            for item in self.items:
                if item["type"] == "ball":
                    target_item = item
                    break

        if target_item:
            self.dog.state = "FETCH"
            dist = self.dog.pos.distance_to(target_item["pos"])
            if dist > 5:
                dir = (target_item["pos"] - self.dog.pos).normalize()
                self.dog.pos += dir * (self.dog.speed + 1)
            else:
                # Собака достигла предмета
                if target_item["type"] == "food":
                    self.love_meter = min(self.max_love, self.love_meter + 10)
                    self.spawn_hearts(8)
                else: # Мячик
                    self.love_meter = min(self.max_love, self.love_meter + 7)
                    self.spawn_hearts(5)
                
                if target_item in self.items:
                    self.items.remove(target_item)
        else:
            self.dog.state = "FOLLOW"
            self.dog.update(self.player_pos)

        # Обновление физики мячиков (инерция)
        for item in self.items:
            if item["type"] == "ball" and "vel" in item:
                item["pos"] += item["vel"]
                item["vel"] *= 0.95 # Трение/замедление
                # Отскок от стен
                if item["pos"].x < 10 or item["pos"].x > WIDTH - 10: item["vel"].x *= -1
                if item["pos"].y < 10 or item["pos"].y > HEIGHT - 10: item["vel"].y *= -1

        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Рисуем "парк" (несколько деревьев или просто зеленые пятна для атмосферы)
        pygame.draw.circle(self.screen, COLOR_PARK, (200, 200), 150)
        pygame.draw.circle(self.screen, COLOR_PARK, (600, 450), 200)

        # Рисуем игрока
        pygame.draw.circle(self.screen, COLOR_HUMAN, (int(self.player_pos.x), int(self.player_pos.y)), 20)
        pygame.draw.circle(self.screen, (255, 224, 189), (int(self.player_pos.x), int(self.player_pos.y - 25)), 15) # Голова

        # Элементы (еда/мяч)
        for item in self.items:
            if item["type"] == "food":
                pygame.draw.circle(self.screen, (139, 69, 19), (int(item["pos"].x), int(item["pos"].y)), 10)
            elif item["type"] == "ball":
                pygame.draw.circle(self.screen, (255, 0, 0), (int(item["pos"].x), int(item["pos"].y)), 8)

        self.dog.draw(self.screen)

        for p in self.particles:
            p.draw(self.screen)

        # UI: Шкала любви
        ui_rect_bg = pygame.Rect(50, 50, 200, 30)
        pygame.draw.rect(self.screen, (200, 200, 200), ui_rect_bg, border_radius=15)
        
        love_width = (self.love_meter / self.max_love) * 200
        if love_width > 0:
            ui_rect_love = pygame.Rect(50, 50, love_width, 30)
            pygame.draw.rect(self.screen, COLOR_UI_BAR, ui_rect_love, border_radius=15)
        
        pygame.draw.rect(self.screen, COLOR_TEXT, ui_rect_bg, 3, border_radius=15)
        
        txt = self.font.render(f"Любовь: {self.love_meter}%", True, COLOR_TEXT)
        self.screen.blit(txt, (60, 52))

        # Инструкции
        instr = [
            "WASD / Стрелки: Движение",
            "Space: Погладить | F: Еда | P: Мяч",
            "K: Сделать фото | Esc: Выход"
        ]
        for i, line in enumerate(instr):
            t = self.font.render(line, True, COLOR_TEXT)
            self.screen.blit(t, (20, HEIGHT - 100 + i * 25))

        if self.love_meter >= self.max_love:
            win_txt = self.font.render("ВЫ - ЛУЧШИЙ ХОЗЯИН! ❤️", True, COLOR_HEART)
            self.screen.blit(win_txt, (WIDTH // 2 - 120, HEIGHT // 2 - 50))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
