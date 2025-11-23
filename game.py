import pygame
import random
import sys
import math
import json
import os
import numpy as np

# High score file path
SCORE_FILE = os.path.join(os.path.dirname(__file__), "highscores.json")

def load_high_scores():
    """Load high scores from file"""
    try:
        with open(SCORE_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_high_scores(scores):
    """Save high scores to file"""
    try:
        with open(SCORE_FILE, 'w') as f:
            json.dump(scores, f)
    except:
        pass

def is_high_score(score, scores):
    """Check if score qualifies for top 5"""
    if len(scores) < 5:
        return True
    return score > min(s['score'] for s in scores)

def add_high_score(name, score, scores):
    """Add new high score and keep top 5"""
    scores.append({'name': name, 'score': score})
    scores.sort(key=lambda x: x['score'], reverse=True)
    return scores[:5]

# Initialize pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Game constants
CHAR_WIDTH = 10
CHAR_HEIGHT = 18
SCREEN_COLS = 80
SCREEN_ROWS = 25
SCREEN_WIDTH = SCREEN_COLS * CHAR_WIDTH
SCREEN_HEIGHT = SCREEN_ROWS * CHAR_HEIGHT

GROUND_HEIGHT = 20
GRAVITY = 0.03
JUMP_FORCE = -1.1
MAX_JUMPS = 1
BASE_SCROLL_SPEED = 0.3
SPEED_PROGRESSION = 3000  # Score needed to double speed

# Jump physics calculated for 2x largest obstacle (house: 8 tall, 10 wide)
# Height: 1.1^2 / (2*0.03) = 20 rows (need 16)
# Time: 1.1/0.03 * 2 = 73 frames
# Horizontal: 73 * 0.3 = 22 cols (need 20)

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 100, 100)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)
PURPLE = (148, 0, 211)
LIME = (50, 255, 50)
BLUE = (100, 100, 255)

# Psychedelic colors for acid trip
PSYCHEDELIC_COLORS = [MAGENTA, CYAN, PINK, PURPLE, ORANGE, LIME, YELLOW, RED, BLUE]

# Player character - more detailed
PLAYER_CHAR = [
    "  ,O,  ",
    " /|X|\\ ",
    "  |_|  ",
    " _/ \\_ ",
]

PLAYER_JUMP_CHAR = [
    " \\,O,/ ",
    "  |X|  ",
    "  |_|  ",
    " /   \\ ",
]

# Obstacles - Easy (more detailed)
OBSTACLE_CHARS_EASY = [
    # Rock pile
    [
        "   ___   ",
        "  /. .\\  ",
        " /. . .\\ ",
        "/_._._._\\",
    ],
    # Traffic cone
    [
        "   /\\   ",
        "  /  \\  ",
        " / || \\ ",
        "/______\\",
    ],
    # Crate stack
    [
        " [====] ",
        " |    | ",
        " [====] ",
        " |    | ",
        " [====] ",
    ],
    # Barrel
    [
        " .----. ",
        "(|    |)",
        " |====| ",
        "(|    |)",
        " '----' ",
    ],
]

# Obstacles - Hard (unlocked at higher scores)
BIRD_CHAR = [
    "   ___   ",
    "\\<(o  )>/",
    "   ^^    ",
]

COW_CHAR = [
    "   ^__^   ",
    "  (oo)\\_  ",
    "  (__)\\  )",
    "   ||--|| ",
]

HOUSE_CHAR = [
    "    /\\    ",
    "   /  \\   ",
    "  /    \\  ",
    " /______\\ ",
    " |  []  | ",
    " | .__. | ",
    " | |  | | ",
    " |_|__|_| ",
]

# Cactus (desert obstacle)
CACTUS_CHAR = [
    "   |   ",
    "  \\|/  ",
    "   |   ",
    "  \\|   ",
    "   |   ",
]

# Spike trap
SPIKE_CHAR = [
    " /\\ /\\ ",
    "/\\/\\/\\",
]

# Powerup types
POWERUP_PISTOL = "pistol"
POWERUP_JETPACK = "jetpack"
POWERUP_BEANS = "beans"
POWERUP_ACID = "acid"
POWERUP_STOPWATCH = "stopwatch"

POWERUP_CHARS = {
    POWERUP_PISTOL: [
        " ___ ",
        "[===>",
        " ^^^ ",
    ],
    POWERUP_JETPACK: [
        " _|_ ",
        "<|J|>",
        " |^| ",
    ],
    POWERUP_BEANS: [
        " .-. ",
        "{B&B}",
        " '-' ",
    ],
    POWERUP_ACID: [
        " /*\\ ",
        "<*@*>",
        " \\*/ ",
    ],
    POWERUP_STOPWATCH: [
        " .O. ",
        "((@))",
        " '-' ",
    ],
}

POWERUP_COLORS = {
    POWERUP_PISTOL: ORANGE,
    POWERUP_JETPACK: CYAN,
    POWERUP_BEANS: LIME,
    POWERUP_ACID: MAGENTA,
    POWERUP_STOPWATCH: YELLOW,
}

# Generate chiptune sounds
def generate_square_wave(frequency, duration, volume=0.3):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    wave = np.sign(np.sin(2 * np.pi * frequency * t)) * volume
    stereo_wave = np.column_stack((wave, wave))
    sound_array = (stereo_wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(sound_array)

def generate_noise(duration, volume=0.3):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    wave = np.random.uniform(-1, 1, n_samples) * volume
    envelope = np.exp(-np.linspace(0, 5, n_samples))
    wave = wave * envelope
    stereo_wave = np.column_stack((wave, wave))
    sound_array = (stereo_wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(sound_array)

def generate_music():
    melody = [
        (262, 0.15), (330, 0.15), (392, 0.15), (523, 0.3),
        (392, 0.15), (330, 0.15), (262, 0.3),
        (294, 0.15), (370, 0.15), (440, 0.15), (587, 0.3),
        (440, 0.15), (370, 0.15), (294, 0.3),
        (330, 0.15), (415, 0.15), (494, 0.15), (659, 0.3),
        (494, 0.15), (415, 0.15), (330, 0.3),
        (392, 0.15), (494, 0.15), (587, 0.15), (784, 0.3),
        (659, 0.15), (587, 0.15), (523, 0.15), (494, 0.3),
    ]
    return [generate_square_wave(freq, dur, 0.2) for freq, dur in melody]

def generate_jump_sound():
    sample_rate = 22050
    duration = 0.1
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    freq = np.linspace(200, 600, n_samples)
    wave = np.sign(np.sin(2 * np.pi * freq * t / sample_rate * np.arange(n_samples))) * 0.3
    stereo_wave = np.column_stack((wave, wave))
    sound_array = (stereo_wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(sound_array)

def generate_death_sound():
    sample_rate = 22050
    duration = 0.3
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    freq = np.linspace(400, 100, n_samples)
    wave = np.sign(np.sin(2 * np.pi * freq * t / sample_rate * np.arange(n_samples))) * 0.3
    stereo_wave = np.column_stack((wave, wave))
    sound_array = (stereo_wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(sound_array)

def generate_shoot_sound():
    sample_rate = 22050
    duration = 0.08
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    freq = np.linspace(800, 200, n_samples)
    wave = np.sign(np.sin(2 * np.pi * freq * t / sample_rate * np.arange(n_samples))) * 0.25
    stereo_wave = np.column_stack((wave, wave))
    sound_array = (stereo_wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(sound_array)

def generate_pickup_sound():
    sample_rate = 22050
    duration = 0.15
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    freq = np.concatenate([
        np.full(n_samples//3, 400),
        np.full(n_samples//3, 600),
        np.full(n_samples//3 + n_samples%3, 800)
    ])
    wave = np.sign(np.sin(2 * np.pi * freq * t / sample_rate * np.arange(n_samples))) * 0.3
    stereo_wave = np.column_stack((wave, wave))
    sound_array = (stereo_wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(sound_array)

def generate_fart_sound():
    """Deep, rumbling fart sound"""
    sample_rate = 22050
    duration = 0.4
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)

    # Low frequency rumble
    low_freq = 60 + 20 * np.sin(2 * np.pi * 3 * t)  # Wobbling low tone
    rumble = np.sin(2 * np.pi * low_freq * t / sample_rate * np.arange(n_samples)) * 0.4

    # Add filtered noise for texture
    noise = np.random.uniform(-0.3, 0.3, n_samples)

    # Combine and apply envelope
    wave = rumble + noise
    envelope = np.exp(-np.linspace(0, 4, n_samples))
    wave = wave * envelope * 0.5

    stereo_wave = np.column_stack((wave, wave))
    sound_array = (stereo_wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(sound_array)

def generate_acid_sound():
    """Wobbly trippy sound"""
    sample_rate = 22050
    duration = 0.5
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    # Wobbling frequency
    freq = 300 + 200 * np.sin(2 * np.pi * 8 * t)
    wave = np.sign(np.sin(2 * np.pi * freq * t / sample_rate * np.arange(n_samples))) * 0.25
    stereo_wave = np.column_stack((wave, wave))
    sound_array = (stereo_wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(sound_array)

def generate_stopwatch_sound():
    """Tick-tock sound"""
    sample_rate = 22050
    sounds = []
    for freq in [800, 600, 800, 600]:
        duration = 0.05
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        wave = np.sign(np.sin(2 * np.pi * freq * t)) * 0.25
        stereo_wave = np.column_stack((wave, wave))
        sound_array = (stereo_wave * 32767).astype(np.int16)
        sounds.append(pygame.sndarray.make_sound(sound_array))
    return sounds

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.char = "->"

    def update(self):
        self.x += self.speed

    def is_off_screen(self):
        return self.x >= SCREEN_COLS

class FartPuff:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 15
        self.chars = ["~", "o", "*", "."]

    def update(self):
        self.life -= 1
        self.y += 0.2  # Float down slightly

    def is_done(self):
        return self.life <= 0

    def get_char(self):
        idx = min(3, (15 - self.life) // 4)
        return self.chars[idx]

class LavaBlob:
    def __init__(self):
        self.x = random.randint(0, SCREEN_COLS - 1)
        self.y = SCREEN_ROWS + random.randint(0, 5)
        self.speed = random.uniform(0.1, 0.3)
        self.wobble = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.05, 0.15)
        self.size = random.choice([1, 2, 3])
        self.color = random.choice(PSYCHEDELIC_COLORS)
        # Blob shapes
        if self.size == 1:
            self.char = "o"
        elif self.size == 2:
            self.char = "O"
        else:
            self.char = "@"

    def update(self):
        self.y -= self.speed
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * 0.3

    def is_off_screen(self):
        return self.y < -2

class Powerup:
    def __init__(self, x, powerup_type):
        self.x = x
        self.type = powerup_type
        self.char = POWERUP_CHARS[powerup_type]
        self.color = POWERUP_COLORS[powerup_type]
        self.height = len(self.char)
        self.width = len(self.char[0])
        self.y = GROUND_HEIGHT - self.height - random.randint(0, 8)

    def update(self, scroll_speed):
        self.x -= scroll_speed

    def is_off_screen(self):
        return self.x + self.width < 0

class Player:
    def __init__(self):
        self.x = 10
        self.y = GROUND_HEIGHT - 4  # 4 rows tall now
        self.vel_y = 0
        self.jumps_left = MAX_JUMPS
        self.on_ground = True
        self.jetpack_jumps = 0  # Extra jumps from jetpack
        self.has_beans = False
        self.beans_timer = 0
        self.ammo = 0  # Pistol ammo
        self.acid_timer = 0
        self.width = 7  # Character width
        self.height = 4  # Character height

    def get_max_jumps(self):
        return MAX_JUMPS + (1 if self.jetpack_jumps > 0 else 0)

    def jump(self):
        if self.jumps_left > 0:
            self.vel_y = JUMP_FORCE
            self.jumps_left -= 1
            self.on_ground = False
            # Use jetpack jump if we're doing a double jump
            if not self.on_ground and self.jetpack_jumps > 0:
                self.jetpack_jumps -= 1
            return True
        return False

    def fart_jump(self):
        self.vel_y = JUMP_FORCE * 0.8
        self.on_ground = False

    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        if self.y >= GROUND_HEIGHT - self.height:
            self.y = GROUND_HEIGHT - self.height
            self.vel_y = 0
            self.jumps_left = self.get_max_jumps()
            self.on_ground = True

        if self.has_beans:
            self.beans_timer -= 1
            if self.beans_timer <= 0:
                self.has_beans = False

        if self.acid_timer > 0:
            self.acid_timer -= 1

    def get_char(self):
        return PLAYER_JUMP_CHAR if not self.on_ground else PLAYER_CHAR

class Obstacle:
    def __init__(self, x, obstacle_type="easy"):
        self.x = x
        self.obstacle_type = obstacle_type
        self.flying = False

        if obstacle_type == "easy":
            self.char = random.choice(OBSTACLE_CHARS_EASY)
        elif obstacle_type == "bird":
            self.char = BIRD_CHAR
            self.flying = True
            self.fly_y = random.randint(8, 14)  # Flying height
        elif obstacle_type == "cow":
            self.char = COW_CHAR
        elif obstacle_type == "house":
            self.char = HOUSE_CHAR
        elif obstacle_type == "cactus":
            self.char = CACTUS_CHAR
        elif obstacle_type == "spike":
            self.char = SPIKE_CHAR
        else:
            self.char = random.choice(OBSTACLE_CHARS_EASY)

        self.height = len(self.char)
        self.width = max(len(row) for row in self.char)

        if self.flying:
            self.y = self.fly_y
        else:
            self.y = GROUND_HEIGHT - self.height
        self.alive = True

    def update(self, scroll_speed):
        self.x -= scroll_speed
        # Birds bob up and down
        if self.flying:
            self.y = self.fly_y + math.sin(self.x * 0.1) * 2

    def is_off_screen(self):
        return self.x + self.width < 0

class Game:
    def __init__(self):
        self.player = Player()
        self.obstacles = []
        self.powerups = []
        self.bullets = []
        self.fart_puffs = []
        self.lava_blobs = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_delay = 40
        self.powerup_timer = 0
        self.scroll_speed = BASE_SCROLL_SPEED
        self.stopwatch_timer = 0
        self.stopwatch_speed_reduction = 0
        self.music_notes = generate_music()
        self.jump_sound = generate_jump_sound()
        self.death_sound = generate_death_sound()
        self.shoot_sound = generate_shoot_sound()
        self.pickup_sound = generate_pickup_sound()
        self.fart_sound = generate_fart_sound()
        self.acid_sound = generate_acid_sound()
        self.stopwatch_sounds = generate_stopwatch_sound()
        self.current_note = 0
        self.music_timer = 0
        self.high_score = 0
        self.frame = 0

    def spawn_obstacle(self):
        if self.spawn_timer <= 0:
            # Choose obstacle type based on score
            obstacle_type = "easy"
            if self.score > 300:
                # Start spawning cactus and spikes
                r = random.random()
                if r < 0.15:
                    obstacle_type = "cactus"
                elif r < 0.25:
                    obstacle_type = "spike"
            if self.score > 800:
                # Start spawning birds
                r = random.random()
                if r < 0.15:
                    obstacle_type = "bird"
                elif r < 0.25:
                    obstacle_type = "cactus"
                elif r < 0.35:
                    obstacle_type = "spike"
            if self.score > 1500:
                # Start spawning cows
                r = random.random()
                if r < 0.12:
                    obstacle_type = "bird"
                elif r < 0.22:
                    obstacle_type = "cow"
                elif r < 0.32:
                    obstacle_type = "cactus"
                elif r < 0.40:
                    obstacle_type = "spike"
            if self.score > 2500:
                # Start spawning houses
                r = random.random()
                if r < 0.08:
                    obstacle_type = "bird"
                elif r < 0.16:
                    obstacle_type = "cow"
                elif r < 0.24:
                    obstacle_type = "house"
                elif r < 0.32:
                    obstacle_type = "cactus"
                elif r < 0.40:
                    obstacle_type = "spike"

            self.obstacles.append(Obstacle(SCREEN_COLS, obstacle_type))
            # More random spacing - increased for larger obstacles
            self.spawn_timer = random.randint(50, 120) + random.randint(0, 50)
            if self.spawn_delay > 15:
                self.spawn_delay -= 0.05
        else:
            self.spawn_timer -= 1

    def spawn_powerup(self):
        self.powerup_timer -= 1
        if self.powerup_timer <= 0:
            powerup_type = random.choice([POWERUP_PISTOL, POWERUP_JETPACK, POWERUP_BEANS, POWERUP_ACID, POWERUP_STOPWATCH])
            self.powerups.append(Powerup(SCREEN_COLS, powerup_type))
            self.powerup_timer = random.randint(80, 180)

    def check_collision(self):
        px, py = int(self.player.x), int(self.player.y)
        player_width, player_height = self.player.width, self.player.height
        for obs in self.obstacles:
            if not obs.alive:
                continue
            ox, oy = int(obs.x), int(obs.y)
            if (px < ox + obs.width and
                px + player_width > ox and
                py < oy + obs.height and
                py + player_height > oy):
                return True
        return False

    def check_powerup_collision(self):
        px, py = int(self.player.x), int(self.player.y)
        player_width, player_height = self.player.width, self.player.height
        for powerup in self.powerups[:]:
            ox, oy = int(powerup.x), int(powerup.y)
            if (px < ox + powerup.width and
                px + player_width > ox and
                py < oy + powerup.height and
                py + player_height > oy):
                self.pickup_sound.play()
                if powerup.type == POWERUP_JETPACK:
                    self.player.jetpack_jumps += 10
                    self.player.jumps_left = self.player.get_max_jumps()
                elif powerup.type == POWERUP_BEANS:
                    self.player.has_beans = True
                    self.player.beans_timer = 600
                elif powerup.type == POWERUP_PISTOL:
                    self.player.ammo += 10
                elif powerup.type == POWERUP_ACID:
                    self.player.acid_timer = random.randint(300, 600)  # 5-10 seconds at 60fps
                    self.acid_sound.play()
                elif powerup.type == POWERUP_STOPWATCH:
                    self.stopwatch_timer = 300  # 5 seconds at 60fps
                    self.stopwatch_speed_reduction = self.scroll_speed * 0.6
                    for sound in self.stopwatch_sounds:
                        sound.play()
                self.powerups.remove(powerup)

    def check_bullet_hits(self):
        for bullet in self.bullets[:]:
            bx, by = int(bullet.x), int(bullet.y)
            for obs in self.obstacles:
                if not obs.alive:
                    continue
                ox, oy = int(obs.x), int(obs.y)
                if (bx >= ox and bx < ox + obs.width and
                    by >= oy and by < oy + obs.height):
                    obs.alive = False
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

    def fire_weapon(self):
        if self.player.ammo > 0:
            self.bullets.append(Bullet(self.player.x + self.player.width, self.player.y + 1))
            self.shoot_sound.play()
            self.player.ammo -= 1
            return True
        return False

    def update(self):
        if self.game_over:
            return

        self.frame += 1
        self.player.update()
        self.spawn_obstacle()
        self.spawn_powerup()

        # Calculate base scroll speed
        base_speed = BASE_SCROLL_SPEED + (self.score / SPEED_PROGRESSION)

        # Apply stopwatch slowdown
        if self.stopwatch_timer > 0:
            self.stopwatch_timer -= 1
            effect_ratio = self.stopwatch_timer / 300
            self.scroll_speed = base_speed - (self.stopwatch_speed_reduction * effect_ratio)
        else:
            self.scroll_speed = base_speed
            self.stopwatch_speed_reduction = 0

        for obs in self.obstacles:
            obs.update(self.scroll_speed)
        for powerup in self.powerups:
            powerup.update(self.scroll_speed)
        for bullet in self.bullets:
            bullet.update()
        for puff in self.fart_puffs:
            puff.update()

        # Update lava blobs during acid trip
        if self.player.acid_timer > 0:
            for blob in self.lava_blobs:
                blob.update()
            # Spawn new blobs
            if random.random() < 0.15:
                self.lava_blobs.append(LavaBlob())
            self.lava_blobs = [b for b in self.lava_blobs if not b.is_off_screen()]
        else:
            self.lava_blobs = []

        self.obstacles = [obs for obs in self.obstacles if not obs.is_off_screen() and obs.alive]
        self.powerups = [p for p in self.powerups if not p.is_off_screen()]
        self.bullets = [b for b in self.bullets if not b.is_off_screen()]
        self.fart_puffs = [p for p in self.fart_puffs if not p.is_done()]

        self.check_powerup_collision()
        self.check_bullet_hits()

        # Random fart from beans
        if self.player.has_beans and random.random() < 0.005:
            self.player.fart_jump()
            self.fart_sound.play()
            # Add fart puff
            self.fart_puffs.append(FartPuff(self.player.x + self.player.width // 2, self.player.y + self.player.height))

        if self.check_collision():
            self.game_over = True
            self.death_sound.play()
            if self.score > self.high_score:
                self.high_score = self.score
        else:
            self.score += 1

        self.music_timer += 1
        if self.music_timer >= 16:
            self.music_notes[self.current_note].play()
            self.current_note = (self.current_note + 1) % len(self.music_notes)
            self.music_timer = 0

    def get_screen_buffer(self):
        # Buffer now stores (char, color) tuples
        screen = [[(' ', BLACK) for _ in range(SCREEN_COLS)] for _ in range(SCREEN_ROWS)]

        # Draw lava blobs (background, behind everything)
        for blob in self.lava_blobs:
            x, y = int(blob.x), int(blob.y)
            if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                screen[y][x] = (blob.char, blob.color)

        # Draw ground
        ground_color = GREEN
        if self.player.acid_timer > 0:
            ground_color = random.choice(PSYCHEDELIC_COLORS)
        for x in range(SCREEN_COLS):
            char = '#' if x % 4 == 0 else '='
            screen[GROUND_HEIGHT][x] = (char, ground_color)

        # Draw obstacles
        for obs in self.obstacles:
            if not obs.alive:
                continue
            obs_color = RED
            if self.player.acid_timer > 0:
                obs_color = random.choice(PSYCHEDELIC_COLORS)
            for i, row in enumerate(obs.char):
                for j, char in enumerate(row):
                    x, y = int(obs.x) + j, int(obs.y) + i
                    if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                        screen[y][x] = (char, obs_color)

        # Draw powerups
        for powerup in self.powerups:
            for i, row in enumerate(powerup.char):
                for j, char in enumerate(row):
                    x, y = int(powerup.x) + j, int(powerup.y) + i
                    if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                        screen[y][x] = (char, powerup.color)

        # Draw fart puffs
        for puff in self.fart_puffs:
            x, y = int(puff.x), int(puff.y)
            if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                screen[y][x] = (puff.get_char(), LIME)

        # Draw bullets
        for bullet in self.bullets:
            x, y = int(bullet.x), int(bullet.y)
            for i, char in enumerate(bullet.char):
                if 0 <= x + i < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                    screen[y][x + i] = (char, ORANGE)

        # Draw player
        player_color = CYAN
        if self.player.acid_timer > 0:
            player_color = PSYCHEDELIC_COLORS[self.frame % len(PSYCHEDELIC_COLORS)]
        player_char = self.player.get_char()
        for i, row in enumerate(player_char):
            for j, char in enumerate(row):
                x, y = int(self.player.x) + j, int(self.player.y) + i
                if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                    screen[y][x] = (char, player_color)

        return screen

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.powerups = []
        self.bullets = []
        self.fart_puffs = []
        self.lava_blobs = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 180  # Give player 3 seconds before first obstacle
        self.spawn_delay = 40
        self.powerup_timer = 120  # Delay first powerup too
        self.scroll_speed = BASE_SCROLL_SPEED
        self.stopwatch_timer = 0
        self.stopwatch_speed_reduction = 0

def render_buffer(screen, font, buffer):
    for y, row in enumerate(buffer):
        x_pos = 0
        for char, color in row:
            if char != ' ' or color != BLACK:
                surface = font.render(char, True, color if color != BLACK else GREEN)
                screen.blit(surface, (x_pos, y * CHAR_HEIGHT))
            x_pos += CHAR_WIDTH

def show_intro(screen, font, high_scores):
    screen.fill(BLACK)

    # Title
    title_lines = [
        "    ___   _____ ______________   ____  __  ___   ___   ______________",
        "   /   | / ___// ____/  _/  _/  / __ \\/ / / / | / / | / / ____/ __ \\",
        "  / /| | \\__ \\/ /    / / / /   / /_/ / / / /  |/ /  |/ / __/ / /_/ /",
        " / ___ |___/ / /____/ /_/ /   / _, _/ /_/ / /|  / /|  / /___/ _, _/ ",
        "/_/  |_/____/\\____/___/___/  /_/ |_|\\____/_/ |_/_/ |_/_____/_/ |_|  ",
    ]

    colors = [CYAN, MAGENTA, YELLOW, GREEN, CYAN]
    for i, line in enumerate(title_lines):
        surface = font.render(line, True, colors[i])
        screen.blit(surface, (0, (i + 1) * CHAR_HEIGHT))

    # Controls box
    y = 7
    controls = [
        "+-----------------------------------+",
        "|     PRESS  SPACE  TO  START       |",
        "|                                   |",
        "|   [SPACE] - Jump & Shoot          |",
        "|   [ESC]   - Quit                  |",
        "+-----------------------------------+",
    ]
    for i, line in enumerate(controls):
        surface = font.render(line, True, GREEN)
        screen.blit(surface, (50, (y + i) * CHAR_HEIGHT))

    # Powerups info
    y = 14
    powerups = [
        "POWERUPS (run into to collect):",
        "[=> Gun (10 shots)  <J> Jetpack (10)",
        "{B} Beans (farts!)  <*> Acid Trip",
        "(O) Stopwatch (slow time)",
    ]
    for i, line in enumerate(powerups):
        color = ORANGE if i == 0 else WHITE
        surface = font.render(line, True, color)
        screen.blit(surface, (50, (y + i) * CHAR_HEIGHT))

    # High scores
    y = 18
    surface = font.render("HIGH SCORES:", True, YELLOW)
    screen.blit(surface, (500, (y) * CHAR_HEIGHT))

    if high_scores:
        for i, hs in enumerate(high_scores[:5]):
            score_text = f"{i+1}. {hs['name']:<5} {hs['score']:>6}"
            surface = font.render(score_text, True, WHITE)
            screen.blit(surface, (500, (y + 1 + i) * CHAR_HEIGHT))
    else:
        surface = font.render("No scores yet!", True, WHITE)
        screen.blit(surface, (500, (y + 1) * CHAR_HEIGHT))

    pygame.display.flip()

    # Play intro music
    intro_notes = [
        (523, 0.2), (659, 0.2), (784, 0.2), (1047, 0.4),
        (784, 0.2), (659, 0.2), (523, 0.4),
    ]
    for freq, dur in intro_notes:
        sound = generate_square_wave(freq, dur, 0.25)
        sound.play()
        pygame.time.wait(int(dur * 1000))

def get_player_name(screen, font, score):
    """Get 5 character name for high score"""
    name = ""
    clock = pygame.time.Clock()

    while True:
        screen.fill(BLACK)

        # Title
        surface = font.render("NEW HIGH SCORE!", True, YELLOW)
        screen.blit(surface, (SCREEN_WIDTH // 2 - 80, 100))

        # Score
        score_text = f"Score: {score}"
        surface = font.render(score_text, True, GREEN)
        screen.blit(surface, (SCREEN_WIDTH // 2 - 50, 150))

        # Name entry
        surface = font.render("Enter your name (5 chars):", True, WHITE)
        screen.blit(surface, (SCREEN_WIDTH // 2 - 120, 220))

        # Name with cursor
        display_name = name + "_" * (5 - len(name))
        surface = font.render(display_name, True, CYAN)
        screen.blit(surface, (SCREEN_WIDTH // 2 - 25, 260))

        # Instructions
        surface = font.render("Press ENTER when done", True, WHITE)
        screen.blit(surface, (SCREEN_WIDTH // 2 - 100, 320))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "ANON"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(name) > 0:
                    return name.upper().ljust(5)[:5]
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 5 and event.unicode.isalnum():
                    name += event.unicode.upper()

        clock.tick(60)

def show_game_over(screen, font, score, high_score):
    lines = [
        "",
        "",
        "",
        "",
        "              +-----------------------------------+",
        "              |                                   |",
        "              |          GAME  OVER!              |",
        "              |                                   |",
        f"              |      Score: {score:>6}                |",
        f"              |      High:  {high_score:>6}                |",
        "              |                                   |",
        "              |   [SPACE] - Play Again            |",
        "              |   [ESC]   - Quit                  |",
        "              |                                   |",
        "              +-----------------------------------+",
    ]

    for i, line in enumerate(lines):
        surface = font.render(line, True, RED)
        screen.blit(surface, (0, (i + 5) * CHAR_HEIGHT))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ASCII RUNNER")

    try:
        font = pygame.font.SysFont('consolas', 14)
    except:
        font = pygame.font.SysFont('courier', 14)

    clock = pygame.time.Clock()
    game = Game()
    high_scores = load_high_scores()
    score_entered = False

    show_intro(screen, font, high_scores)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        clock.tick(60)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.game_over:
                        # Check for high score before reset
                        if not score_entered and is_high_score(game.score, high_scores):
                            name = get_player_name(screen, font, game.score)
                            high_scores = add_high_score(name, game.score, high_scores)
                            save_high_scores(high_scores)
                        score_entered = False
                        game.reset()
                    else:
                        # Fire weapon if we have ammo
                        game.fire_weapon()
                        # Also try to jump
                        if game.player.jump():
                            game.jump_sound.play()
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Check for high score when game just ended
        if game.game_over and not score_entered:
            if is_high_score(game.score, high_scores):
                name = get_player_name(screen, font, game.score)
                high_scores = add_high_score(name, game.score, high_scores)
                save_high_scores(high_scores)
            score_entered = True

        game.update()

        screen.fill(BLACK)
        buffer = game.get_screen_buffer()
        render_buffer(screen, font, buffer)

        # Draw HUD - Score on right
        score_text = f"Score: {game.score}"
        surface = font.render(score_text, True, YELLOW)
        screen.blit(surface, (SCREEN_WIDTH - 120, 5))

        # Jumps indicator
        jumps_text = f"Jumps: {'*' * game.player.jumps_left}"
        surface = font.render(jumps_text, True, WHITE)
        screen.blit(surface, (SCREEN_WIDTH - 120, 25))

        # Left side - Active powerups with timers
        y_offset = 5

        # Ammo
        if game.player.ammo > 0:
            ammo_text = f"[=> x{game.player.ammo}"
            surface = font.render(ammo_text, True, ORANGE)
            screen.blit(surface, (10, y_offset))
            y_offset += 18

        # Jetpack jumps
        if game.player.jetpack_jumps > 0:
            jet_text = f"<J> x{game.player.jetpack_jumps}"
            surface = font.render(jet_text, True, CYAN)
            screen.blit(surface, (10, y_offset))
            y_offset += 18

        # Beans timer
        if game.player.has_beans:
            secs = game.player.beans_timer // 60
            beans_text = f"{{B}} {secs}s"
            surface = font.render(beans_text, True, LIME)
            screen.blit(surface, (10, y_offset))
            y_offset += 18

        # Acid timer
        if game.player.acid_timer > 0:
            secs = game.player.acid_timer // 60
            acid_text = f"<*> {secs}s"
            surface = font.render(acid_text, True, MAGENTA)
            screen.blit(surface, (10, y_offset))
            y_offset += 18

        # Stopwatch timer
        if game.stopwatch_timer > 0:
            secs = game.stopwatch_timer // 60
            watch_text = f"(O) {secs}s"
            surface = font.render(watch_text, True, YELLOW)
            screen.blit(surface, (10, y_offset))
            y_offset += 18

        if game.game_over:
            show_game_over(screen, font, game.score, game.high_score)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
