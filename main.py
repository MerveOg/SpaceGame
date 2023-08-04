import pygame
import os
import time
import random

pygame.font.init()

pygame.display.set_caption("Space Shooter Tutorial")
WIDTH, HEIGHT = 1200, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
bottom_window_rect = pygame.Rect(0, HEIGHT - 10, WIDTH, 10)

# Load images
alien = pygame.transform.scale(pygame.image.load(os.path.join("assets", "alien1.png")), (50, 50))
alien2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "alien2.png")), (50, 50))
alien3 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "alien3.png")), (50, 50))
user = pygame.transform.scale(pygame.image.load(os.path.join("assets", "spaceship.png")), (50, 50))
alien_laser = pygame.transform.scale(pygame.image.load(os.path.join("assets", "laserRed.png")), (10, 10))
user_laser = pygame.transform.scale(pygame.image.load(os.path.join("assets", "laser.png")), (10, 10))
space1 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space.png")), (WIDTH, HEIGHT))
space2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space2.png")), (WIDTH, HEIGHT))
space3 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space3.png")), (WIDTH, HEIGHT))
heart = pygame.transform.scale(pygame.image.load(os.path.join("assets", "heart.png")), (30, 30))
replayButton = pygame.transform.scale(pygame.image.load(os.path.join("assets", "replayButton.png")), (WIDTH, HEIGHT))
bonusPoint_img = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bonuspoint.png")), (30, 30))  # Bonus güç görseli
bonusPoint_x = random.randint(0, WIDTH - 30)  # Bonus gücün x konumu
bonusPoint_y = random.randint(0, HEIGHT - 30)  # Bonus gücün y konumu
bonusPoint_timer = 0  # Bonus gücün süresi
point = 0

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=3):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 1
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Aliens(Ship):
    COLOR_MAP = {
        "alien": (alien, alien_laser),
        "alien2": (alien2, alien_laser),
        "alien3": (alien3, alien_laser)
    }

    def __init__(self, x, y, color, health=1):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.direction = 1  # Hareket yönü: 1 sağa, -1 sola
        self.step = 50  # Her adımda hareket edilen mesafe (piksel)
        self.move_count = 0
        self.shoot_countdown = random.randint(1, 50)  # İlk ateş etme süresini rastgele belirle

    def move(self, vel):
        self.x += vel * self.direction
        if self.x <= 0 or self.x >= WIDTH - self.get_width():
            self.y += self.step
            self.direction *= -1
            if self.y >= HEIGHT - self.get_height():
                self.y = 0
                self.x += self.step * self.direction


    def update_shoot_countdown(self):
        if self.shoot_countdown > 0:
            self.shoot_countdown -= 1
        else:
            self.shoot_countdown = 2  # Yeni ateş etme süresini rastgele belirle

    def shoot(self):
        if self.cool_down_counter == 0 and self.shoot_countdown == 0:  # Ateş etme süresi dolmuşsa ateş et
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
        elif self.shoot_countdown > 0:  # Ateş etme süresi dolmamışsa süreyi güncelle
            self.update_shoot_countdown()

        self.update_shoot_countdown()  # Her seferinde ateş etme süresini güncelle


class Player(Ship):
    def __init__(self, x, y, health=3):
        super().__init__(x, y, health)
        self.ship_img = user
        self.laser_img = user_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            # Puanı arttır
                            global point
                            point += 10


    def draw(self, window):
        super().draw(window)
        self.draw_health(window)

    def draw_health(self, window):
        for i in range(self.health):
            window.blit(heart, (10 + i * 40, 10))


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60

    pygame.mixer.init()

    enemies = []

    bonusPoint_timer = 0  # Bonus gücün süresi

    clock = pygame.time.Clock()
    start_time = time.time()
    last_move_time = time.time()

    player_vel = 5
    laser_vel = 5

    wave_length = 1
    enemy_vel = 3
    enemy_spawn_delay = 200  # Uzaylıların arka arkaya gelme gecikme süresi
    enemy_spawn_timer = 0  # Uzaylıların arka arkaya gelme zamanlayıcısı

    player = Player(550, 540)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    #herhangi bir uzaylı pencerenin alt kenarına değerse true döner
    def check_collision(aliens):
        for alien in aliens:
            alien_rect = pygame.Rect(alien.x, alien.y, alien.get_width(), alien.get_height())
            if alien_rect.colliderect(bottom_window_rect):
                return True
        return False


    def redraw_window(elapsed_time):
        if player.health == 3:
            WIN.blit(space1, (0, 0))
        elif player.health == 2:
            WIN.blit(space2, (0, 0))
        elif player.health == 1:
            WIN.blit(space3, (0, 0))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if bonusPoint_timer > 0:
            WIN.blit(bonusPoint_img, (bonusPoint_x, bonusPoint_y))

        if lost:
            gameOverPage(False)
        draw_timer(elapsed_time)
        draw_point()
        pygame.display.update()

    def move_aliens_down(enemies):
        for enemy in enemies:
            enemy.y += enemy.get_height()

    def draw_timer(elapsed_time):
        font = pygame.font.SysFont("centurygothic", 20, bold=True)
        timer_label = font.render("Time: " + format_time(elapsed_time), True, (255, 255, 255))
        WIN.blit(timer_label, (1070, 10))

    def draw_point():
        font = pygame.font.SysFont("centurygothic", 20, bold=True)
        point_label = font.render("Point: " + str(point), True, (255, 255, 255))
        WIN.blit(point_label, (1070, 40))

    def format_time(secs):
        minutes = int(secs // 60)
        seconds = int(secs % 60)
        return "{:02d}:{:02d}".format(minutes, seconds)

    def gameOverPage(win):
        nonlocal run
        run = False

        end_screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Game Over")

        font = pygame.font.SysFont("centurygothic", 40, bold=True)
        if(win==True):
            end_label = font.render("You are winner!", True, (255, 255, 255))
        else:
            end_label = font.render("Game Over", True, (255, 255, 255))
        mainPoint = int(point + int(last_move_time)/1000 + player.health*10)
        point_label = font.render("Point: " + str(mainPoint), True, (255, 255, 255))
        replay_button = pygame.transform.scale(pygame.image.load(os.path.join("assets", "replayButton.png")), (150, 50))

        end_screen.blit(space1, (0, 0))
        end_screen.blit(end_label, (WIDTH // 2 - end_label.get_width() // 2, HEIGHT // 2 - 150))
        end_screen.blit(point_label, (WIDTH // 2 - point_label.get_width() // 2, HEIGHT // 2 - 100))
        replay_rect = replay_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        end_screen.blit(replay_button, replay_rect)
        pygame.display.update()

        replay = False
        while not replay:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    replay = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if replay_rect.collidepoint(mouse_pos):
                        replay = True

        run = True  # Oyun döngüsünü yeniden başlatmak için run değişkenini True yap

        pygame.mixer.music.stop()  # Oyun müziğini durdur
        main_menu()  # Oyunu yeniden başlat

    pygame.mixer.music.load(os.path.join("assets", "gameMusic.mp3"))
    pygame.mixer.music.play(-1)  # -1 plays the music indefinitely
    pygame.mixer.music.set_volume(0.5)  # Set the volume to 50%

    while run:
        elapsed_time = time.time() - start_time
        clock.tick(FPS)
        redraw_window(elapsed_time)

        if player.health <= 0:
            lost = True
            lost_count += 1

        if check_collision(enemies):
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        global point
        if point != 0 and len(enemies) == 0:
            point =0
            gameOverPage(True)

        if bonusPoint_timer == 0:
            bonusPoint_timer = 300  # Bonus puanı her 10 saniyede bir belirsin
            bonusPoint_x = random.randint(0, WIDTH - 30)
            bonusPoint_y = random.randint(0, HEIGHT - 30)
        elif bonusPoint_timer > 0:
            bonusPoint_timer -= 1  # Bonus puanı süresini azalt
        else:
            if bonusPoint_timer == -180:  # Bonus puanı görünme süresi (3 saniye) sona erdiğinde
                bonusPoint_timer = 420  # Bonus puanı 7 saniye bekle
                bonusPoint_x = -100  # Bonus puanını ekran dışına taşı
                bonusPoint_y = -100
            else:
                bonusPoint_timer -= 1  # Bonus puanını bekletme süresini azalt

        if len(enemies) == 0:
            wave_length += 5
            for i in range(wave_length):
                enemy = Aliens(0, 50, random.choice(["alien", "alien2", "alien3"]))
                enemies.append(enemy)
            enemy_spawn_timer = enemy_spawn_delay  # Uzaylıların hemen ardışık olarak gelmesini sağlamak için zamanlayıcıyı ayarlayın

        enemy_spawn_timer -= 1  # Her döngüde zamanlayıcıyı azaltın

        if enemy_spawn_timer <= 0:
            enemy = Aliens(0, 50, random.choice(["alien", "alien2", "alien3"]))
            enemies.append(enemy)
            enemy_spawn_timer = enemy_spawn_delay  # Yeni bir uzaylı oluşturduktan sonra zamanlayıcıyı yeniden ayarlayın

        #20sn de bir hepsi aşağı
        if time.time() - last_move_time >= 20:
            move_aliens_down(enemies)
            last_move_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # sol
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # sağ
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # yukarı
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # aşağı
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    run = True
    while run:
        WIN.blit(space1, (0, 0))
        pygame.display.update()
        main()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    pygame.quit()

main_menu()
