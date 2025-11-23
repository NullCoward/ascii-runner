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
MAX_JUMPS = 1
BASE_SCROLL_SPEED = 0.3
SPEED_PROGRESSION = 2000  # +0.1 speed per 200 points
JUMP_CLEARANCE_MULTIPLIER = 1.2  # Jump 1.2x the tallest obstacle

# Obstacles with flat tops that can be stood on
FLAT_TOP_OBSTACLES = ["easy"]  # Crates, barrels, rock piles have flat tops

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
BROWN = (139, 69, 19)
TAN = (210, 180, 140)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
LIGHT_BLUE = (135, 206, 235)
DARK_GREEN = (0, 100, 0)
DARK_BROWN = (101, 67, 33)
CREAM = (255, 253, 208)

# Psychedelic colors for acid trip
PSYCHEDELIC_COLORS = [MAGENTA, CYAN, PINK, PURPLE, ORANGE, LIME, YELLOW, RED, BLUE]

# Environment definitions
# Each environment has: ground_color, ground_chars, bg_color, bg_chars, fill_char
ENVIRONMENTS = {
    "grass": {
        "ground_color": GREEN,
        "ground_chars": ('#', '=', '"', ','),  # Grass and plants
        "bg_color": (0, 180, 0),  # Darker green for background
        "bg_chars": ('^', 'Y', '*', 'T'),  # Trees and bushes
        "fill_color": (100, 80, 50),  # Brown dirt
        "fill_char": '.',
    },
    "desert": {
        "ground_color": YELLOW,
        "ground_chars": ('~', '.', '_', ':'),  # Sand patterns
        "bg_color": (200, 150, 50),  # Darker sand/rocks
        "bg_chars": ('A', 'n', '^', 'o'),  # Rock formations
        "fill_color": (180, 130, 40),  # Darker sand
        "fill_char": ':',
    },
    "snow": {
        "ground_color": WHITE,
        "ground_chars": ('*', '.', '~', '_'),  # Snow and ice
        "bg_color": (200, 200, 220),  # Blueish snow
        "bg_chars": ('^', 'A', '*', 'T'),  # Snowy peaks and trees
        "fill_color": (180, 180, 200),  # Packed snow
        "fill_char": '.',
    },
    "cave": {
        "ground_color": (150, 150, 150),  # Gray
        "ground_chars": ('#', '=', '_', '.'),  # Stone floor
        "bg_color": (100, 100, 100),  # Darker gray
        "bg_chars": ('^', 'V', '|', 'M'),  # Stalactites and rocks
        "fill_color": (80, 80, 80),  # Dark rock
        "fill_char": '#',
    },
    "lava": {
        "ground_color": (200, 50, 0),  # Dark red
        "ground_chars": ('#', '=', '~', '^'),  # Hardite platform
        "bg_color": (255, 100, 0),  # Orange lava glow
        "bg_chars": ('^', 'M', 'W', '~'),  # Volcanic formations
        "fill_color": (150, 30, 0),  # Dark volcanic rock
        "fill_char": '.',
    },
}

# Environment progression by score
def get_environment_for_score(score):
    if score < 500:
        return "grass"
    elif score < 1200:
        return "desert"
    elif score < 2000:
        return "snow"
    elif score < 3000:
        return "cave"
    else:
        return "lava"

# Player character - side-on running poses (animated)
PLAYER_RUN_1 = [
    " o>  ",
    "/|\\  ",
    " |   ",
    "/ \\  ",
]

PLAYER_RUN_2 = [
    " o>  ",
    "/|\\  ",
    " |   ",
    " /\\  ",
]

PLAYER_JUMP_CHAR = [
    " o>  ",
    "<|\\  ",
    "/ \\  ",
    "     ",
]

# Lotus meditation pose for nirvana
PLAYER_LOTUS_CHAR = [
    " o   ",
    "\\|/  ",
    "/_\\  ",
    "| |  ",
]

# Rainbow eye for nirvana mode (centered behind player)
RAINBOW_EYE = [
    "    .~~~~~.    ",
    "   /   _   \\   ",
    "  |  ((@))  |  ",
    "  |   \\_/   |  ",
    "   \\_______/   ",
]

# Flash text for acid/nirvana
ACID_FLASH_TEXT = [
    "    _    ____ ___ ____  ",
    "   / \\  / ___|_ _|  _ \\ ",
    "  / _ \\| |    | || | | |",
    " / ___ \\ |___ | || |_| |",
    "/_/   \\_\\____|___|____/ ",
]

NIRVANA_FLASH_TEXT = [
    " _   _ ___ ______     ___    _   _    _    ",
    "| \\ | |_ _|  _ \\ \\   / / \\  | \\ | |  / \\   ",
    "|  \\| || || |_) \\ \\ / / _ \\ |  \\| | / _ \\  ",
    "| |\\  || ||  _ < \\ V / ___ \\| |\\  |/ ___ \\ ",
    "|_| \\_|___|_| \\_\\ \\_/_/   \\_\\_| \\_/_/   \\_\\",
]

# Trippy symbol replacements for emoji acid mode
# Uses Unicode symbols that render reliably in most fonts
EMOJI_CHARS = {
    # Player - geometric shapes
    'o': '◉', 'O': '◎', '|': '║', '>': '►', '<': '◄',
    # Ground/terrain - decorative
    '#': '▓', '=': '≡', '"': '※', ',': '·',
    '^': '△', 'Y': '¥', '*': '★', 'T': '†',
    '.': '•', ':': '∷', '~': '≈',
    # Structure - box drawing
    '/': '╱', '\\': '╲', '_': '▁', '-': '─',
    '[': '【', ']': '】', '(': '〔', ')': '〕',
    '{': '〖', '}': '〗',
    # Misc symbols
    '@': '◈', 'A': '▲', 'M': '♠', 'V': '▼', 'W': '♦',
    'n': '∩', '+': '✚', '!': '│',
}

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

# Obstacle color maps - define color for each character position
# Each entry is a list of tuples: (char, color) for each position
OBSTACLE_COLORS_EASY = [
    # Rock pile - gray rocks with some darker spots
    [
        [(' ', None), (' ', None), (' ', None), ('_', GRAY), ('_', GRAY), ('_', GRAY), (' ', None), (' ', None), (' ', None)],
        [(' ', None), (' ', None), ('/', GRAY), ('.', DARK_GRAY), (' ', GRAY), ('.', DARK_GRAY), ('\\', GRAY), (' ', None), (' ', None)],
        [(' ', None), ('/', GRAY), ('.', DARK_GRAY), (' ', GRAY), ('.', DARK_GRAY), (' ', GRAY), ('.', DARK_GRAY), ('\\', GRAY), (' ', None)],
        [('/', GRAY), ('_', GRAY), ('.', DARK_GRAY), ('_', GRAY), ('.', DARK_GRAY), ('_', GRAY), ('.', DARK_GRAY), ('_', GRAY), ('\\', GRAY)],
    ],
    # Traffic cone - orange with white stripes
    [
        [(' ', None), (' ', None), (' ', None), ('/', ORANGE), ('\\', ORANGE), (' ', None), (' ', None), (' ', None)],
        [(' ', None), (' ', None), ('/', ORANGE), (' ', WHITE), (' ', WHITE), ('\\', ORANGE), (' ', None), (' ', None)],
        [(' ', None), ('/', ORANGE), (' ', WHITE), ('|', ORANGE), ('|', ORANGE), (' ', WHITE), ('\\', ORANGE), (' ', None)],
        [('/', ORANGE), ('_', WHITE), ('_', WHITE), ('_', ORANGE), ('_', ORANGE), ('_', WHITE), ('_', WHITE), ('\\', ORANGE)],
    ],
    # Crate stack - brown wood with metal bands
    [
        [(' ', None), ('[', DARK_GRAY), ('=', BROWN), ('=', BROWN), ('=', BROWN), ('=', BROWN), (']', DARK_GRAY), (' ', None)],
        [(' ', None), ('|', BROWN), (' ', TAN), (' ', TAN), (' ', TAN), (' ', TAN), ('|', BROWN), (' ', None)],
        [(' ', None), ('[', DARK_GRAY), ('=', BROWN), ('=', BROWN), ('=', BROWN), ('=', BROWN), (']', DARK_GRAY), (' ', None)],
        [(' ', None), ('|', BROWN), (' ', TAN), (' ', TAN), (' ', TAN), (' ', TAN), ('|', BROWN), (' ', None)],
        [(' ', None), ('[', DARK_GRAY), ('=', BROWN), ('=', BROWN), ('=', BROWN), ('=', BROWN), (']', DARK_GRAY), (' ', None)],
    ],
    # Barrel - brown with metal bands
    [
        [(' ', None), ('.', DARK_GRAY), ('-', DARK_GRAY), ('-', DARK_GRAY), ('-', DARK_GRAY), ('-', DARK_GRAY), ('.', DARK_GRAY), (' ', None)],
        [('(', BROWN), ('|', DARK_GRAY), (' ', BROWN), (' ', BROWN), (' ', BROWN), (' ', BROWN), ('|', DARK_GRAY), (')', BROWN)],
        [(' ', None), ('|', BROWN), ('=', DARK_GRAY), ('=', DARK_GRAY), ('=', DARK_GRAY), ('=', DARK_GRAY), ('|', BROWN), (' ', None)],
        [('(', BROWN), ('|', DARK_GRAY), (' ', BROWN), (' ', BROWN), (' ', BROWN), (' ', BROWN), ('|', DARK_GRAY), (')', BROWN)],
        [(' ', None), ("'", DARK_GRAY), ('-', DARK_GRAY), ('-', DARK_GRAY), ('-', DARK_GRAY), ('-', DARK_GRAY), ("'", DARK_GRAY), (' ', None)],
    ],
]

# Bird colors - blue body, orange beak, yellow eye
BIRD_COLORS = [
    [(' ', None), (' ', None), (' ', None), ('_', LIGHT_BLUE), ('_', LIGHT_BLUE), ('_', LIGHT_BLUE), (' ', None), (' ', None), (' ', None)],
    [('\\', YELLOW), ('<', ORANGE), ('(', LIGHT_BLUE), ('o', BLACK), (' ', LIGHT_BLUE), (' ', LIGHT_BLUE), (')', LIGHT_BLUE), ('>', YELLOW), ('/', YELLOW)],
    [(' ', None), (' ', None), (' ', None), ('^', ORANGE), ('^', ORANGE), (' ', None), (' ', None), (' ', None), (' ', None)],
]

# Cow colors - white body, black spots
COW_COLORS = [
    [(' ', None), (' ', None), (' ', None), ('^', PINK), ('_', WHITE), ('_', WHITE), ('^', PINK), (' ', None), (' ', None), (' ', None)],
    [(' ', None), (' ', None), ('(', WHITE), ('o', BLACK), ('o', BLACK), (')', WHITE), ('\\', WHITE), ('_', WHITE), (' ', None), (' ', None)],
    [(' ', None), (' ', None), ('(', WHITE), ('_', BLACK), ('_', BLACK), (')', WHITE), ('\\', WHITE), (' ', WHITE), (' ', None), (')', WHITE)],
    [(' ', None), (' ', None), (' ', None), ('|', WHITE), ('|', BLACK), ('-', WHITE), ('-', WHITE), ('|', BLACK), ('|', WHITE), (' ', None)],
]

# House colors - brown roof, tan walls, blue windows, red door
HOUSE_COLORS = [
    [(' ', None), (' ', None), (' ', None), (' ', None), ('/', BROWN), ('\\', BROWN), (' ', None), (' ', None), (' ', None), (' ', None)],
    [(' ', None), (' ', None), (' ', None), ('/', BROWN), (' ', DARK_BROWN), (' ', DARK_BROWN), ('\\', BROWN), (' ', None), (' ', None), (' ', None)],
    [(' ', None), (' ', None), ('/', BROWN), (' ', DARK_BROWN), (' ', DARK_BROWN), (' ', DARK_BROWN), (' ', DARK_BROWN), ('\\', BROWN), (' ', None), (' ', None)],
    [(' ', None), ('/', BROWN), ('_', BROWN), ('_', BROWN), ('_', BROWN), ('_', BROWN), ('_', BROWN), ('_', BROWN), ('\\', BROWN), (' ', None)],
    [(' ', None), ('|', TAN), (' ', TAN), (' ', TAN), ('[', LIGHT_BLUE), (']', LIGHT_BLUE), (' ', TAN), (' ', TAN), ('|', TAN), (' ', None)],
    [(' ', None), ('|', TAN), (' ', TAN), ('.', RED), ('_', RED), ('_', RED), ('.', RED), (' ', TAN), ('|', TAN), (' ', None)],
    [(' ', None), ('|', TAN), (' ', TAN), ('|', RED), (' ', DARK_BROWN), (' ', DARK_BROWN), ('|', RED), (' ', TAN), ('|', TAN), (' ', None)],
    [(' ', None), ('|', TAN), ('_', TAN), ('|', RED), ('_', DARK_BROWN), ('_', DARK_BROWN), ('|', RED), ('_', TAN), ('|', TAN), (' ', None)],
]

# Cactus colors - green with darker green details
CACTUS_COLORS = [
    [(' ', None), (' ', None), (' ', None), ('|', GREEN), (' ', None), (' ', None), (' ', None)],
    [(' ', None), (' ', None), ('\\', DARK_GREEN), ('|', GREEN), ('/', DARK_GREEN), (' ', None), (' ', None)],
    [(' ', None), (' ', None), (' ', None), ('|', GREEN), (' ', None), (' ', None), (' ', None)],
    [(' ', None), (' ', None), ('\\', DARK_GREEN), ('|', GREEN), (' ', None), (' ', None), (' ', None)],
    [(' ', None), (' ', None), (' ', None), ('|', GREEN), (' ', None), (' ', None), (' ', None)],
]

# Spike colors - metallic gray
SPIKE_COLORS = [
    [(' ', None), ('/', GRAY), ('\\', GRAY), (' ', None), ('/', GRAY), ('\\', GRAY), (' ', None)],
    [('/', DARK_GRAY), ('\\', GRAY), ('/', DARK_GRAY), ('\\', GRAY), ('/', DARK_GRAY), ('\\', GRAY)],
]

# Calculate max obstacle height dynamically
def get_max_obstacle_height():
    all_obstacles = OBSTACLE_CHARS_EASY + [BIRD_CHAR, COW_CHAR, HOUSE_CHAR, CACTUS_CHAR, SPIKE_CHAR]
    return max(len(obs) for obs in all_obstacles)

MAX_OBSTACLE_HEIGHT = get_max_obstacle_height()
DESIRED_JUMP_HEIGHT = MAX_OBSTACLE_HEIGHT * JUMP_CLEARANCE_MULTIPLIER
GRAVITY = 0.035  # Lower gravity = more hang time = longer jump
JUMP_FORCE = -math.sqrt(2 * GRAVITY * DESIRED_JUMP_HEIGHT)  # v = sqrt(2gh)

# Calculate jump duration (frames in air)
# Time to peak = -JUMP_FORCE / GRAVITY, total air time = 2x that
JUMP_DURATION = 2 * (-JUMP_FORCE / GRAVITY)

# Powerup types
POWERUP_PISTOL = "pistol"
POWERUP_JETPACK = "jetpack"
POWERUP_BEANS = "beans"
POWERUP_ACID = "acid"
POWERUP_STOPWATCH = "stopwatch"

POWERUP_CHARS = {
    POWERUP_PISTOL: [
        "[=>",
    ],
    POWERUP_JETPACK: [
        "<J>",
    ],
    POWERUP_BEANS: [
        "{B}",
    ],
    POWERUP_ACID: [
        "<*>",
    ],
    POWERUP_STOPWATCH: [
        "(O)",
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
    def __init__(self, horizontal=False):
        self.horizontal = horizontal
        if horizontal:
            # Horizontal mode: come from right side
            self.x = SCREEN_COLS + random.randint(0, 5)
            self.y = random.randint(5, SCREEN_ROWS - 3)
            self.speed = random.uniform(0.3, 0.6)
        else:
            # Vertical mode: rise from bottom
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
        self.wobble += self.wobble_speed
        if self.horizontal:
            self.x -= self.speed
            self.y += math.sin(self.wobble) * 0.3
        else:
            self.y -= self.speed
            self.x += math.sin(self.wobble) * 0.3

    def is_off_screen(self):
        if self.horizontal:
            return self.x < -2
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
        self.acid_flash_timer = 0  # Flash "ACID" text
        self.nirvana_flash_timer = 0  # Flash "NIRVANA" text
        self.was_in_nirvana = False  # Track nirvana state transitions
        self.width = 5  # Character width
        self.height = 4  # Character height

    def get_acid_level(self):
        """Return acid level: 0=none, 1=normal(0-10s), 2=emoji(11-20s), 3=nirvana(21-30s)"""
        if self.acid_timer <= 0:
            return 0
        secs = self.acid_timer / 60
        if secs <= 10:
            return 1  # Normal psychedelic
        elif secs <= 20:
            return 2  # Emoji mode
        else:
            return 3  # Nirvana mode

    def is_invincible(self):
        """Player is invincible during nirvana"""
        return self.get_acid_level() == 3

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
        # Check for nirvana transition
        current_nirvana = self.get_acid_level() == 3
        if current_nirvana and not self.was_in_nirvana:
            self.nirvana_flash_timer = 60  # Flash for 1 second
        self.was_in_nirvana = current_nirvana

        # In nirvana, float in the sky
        if self.get_acid_level() == 3:
            target_y = 6  # Float high in sky
            self.y += (target_y - self.y) * 0.1  # Smooth float up
            self.vel_y = 0
            self.on_ground = False
        else:
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

        if self.acid_flash_timer > 0:
            self.acid_flash_timer -= 1

        if self.nirvana_flash_timer > 0:
            self.nirvana_flash_timer -= 1

    def get_char(self, frame=0):
        if self.get_acid_level() == 3:
            return PLAYER_LOTUS_CHAR
        if not self.on_ground:
            return PLAYER_JUMP_CHAR
        # Animate running - switch every 8 frames
        if (frame // 8) % 2 == 0:
            return PLAYER_RUN_1
        else:
            return PLAYER_RUN_2

class Obstacle:
    def __init__(self, x, obstacle_type="easy"):
        self.x = x
        self.obstacle_type = obstacle_type
        self.flying = False
        self.color_data = None  # Per-character color data

        if obstacle_type == "easy":
            idx = random.randint(0, len(OBSTACLE_CHARS_EASY) - 1)
            self.char = OBSTACLE_CHARS_EASY[idx]
            self.color_data = OBSTACLE_COLORS_EASY[idx]
        elif obstacle_type == "bird":
            self.char = BIRD_CHAR
            self.color_data = BIRD_COLORS
            self.flying = True
            self.fly_y = random.randint(8, 14)  # Flying height
        elif obstacle_type == "cow":
            self.char = COW_CHAR
            self.color_data = COW_COLORS
        elif obstacle_type == "house":
            self.char = HOUSE_CHAR
            self.color_data = HOUSE_COLORS
        elif obstacle_type == "cactus":
            self.char = CACTUS_CHAR
            self.color_data = CACTUS_COLORS
        elif obstacle_type == "spike":
            self.char = SPIKE_CHAR
            self.color_data = SPIKE_COLORS
        else:
            idx = random.randint(0, len(OBSTACLE_CHARS_EASY) - 1)
            self.char = OBSTACLE_CHARS_EASY[idx]
            self.color_data = OBSTACLE_COLORS_EASY[idx]

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

            new_obstacle = Obstacle(SCREEN_COLS, obstacle_type)
            self.obstacles.append(new_obstacle)

            # Dynamic spacing based on speed, obstacle size, and jump duration
            # Minimum safe distance = jump distance + obstacle width + landing buffer
            jump_distance = JUMP_DURATION * self.scroll_speed
            landing_buffer = 8  # Extra space for safe landing
            min_distance = jump_distance + new_obstacle.width + landing_buffer

            # Convert distance to frames: frames = distance / scroll_speed
            min_frames = int(min_distance / max(self.scroll_speed, 0.1))

            # Add some randomness on top of minimum (10-50% extra)
            random_extra = int(min_frames * random.uniform(0.1, 0.5))
            self.spawn_timer = min_frames + random_extra
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

        # Add hitbox padding for less sensitive collision
        hitbox_padding = 1  # Pixels of forgiveness
        px += hitbox_padding
        player_width -= hitbox_padding * 2
        py += hitbox_padding
        player_height -= hitbox_padding
        player_bottom = py + player_height

        for obs in self.obstacles:
            if not obs.alive:
                continue
            ox, oy = int(obs.x), int(obs.y)

            # Check if horizontally overlapping
            if px < ox + obs.width and px + player_width > ox:
                # Check if vertically overlapping
                if py < oy + obs.height and player_bottom > oy:
                    # Check if this is a flat-top obstacle we can stand on
                    if obs.obstacle_type in FLAT_TOP_OBSTACLES:
                        # Landing on top: player bottom near obstacle top, falling down
                        landing_on_top = player_bottom <= oy + 2 and self.player.vel_y >= 0
                        if landing_on_top:
                            # Land on the obstacle
                            self.player.y = oy - player_height
                            self.player.vel_y = 0
                            self.player.jumps_left = self.player.get_max_jumps()
                            self.player.on_ground = True
                            continue  # Not a collision, we're standing on it
                    return True  # Collision
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
                    self.player.acid_timer = random.randint(1200, 1800)  # 20-30 seconds at 60fps
                    self.player.acid_flash_timer = 60  # Flash "ACID" for 1 second
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
            # Spawn new blobs - both vertical and horizontal
            if random.random() < 0.15:
                # Mix of vertical and horizontal blobs
                horizontal = random.random() < 0.5
                self.lava_blobs.append(LavaBlob(horizontal=horizontal))
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

        if self.check_collision() and not self.player.is_invincible():
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

        # Get current environment
        env_name = get_environment_for_score(self.score)
        env = ENVIRONMENTS[env_name]

        # Draw lava blobs (background, behind everything)
        for blob in self.lava_blobs:
            x, y = int(blob.x), int(blob.y)
            if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                screen[y][x] = (blob.char, blob.color)

        # Background terrain level (hills/mountains in background)
        BG_TERRAIN_TOP = 12  # Top of background terrain
        BG_TERRAIN_BOTTOM = 17  # Bottom of background terrain

        # Draw background terrain (elevated ground in background)
        bg_color = env["bg_color"]
        bg_chars = env["bg_chars"]
        if self.player.acid_timer > 0:
            bg_color = random.choice(PSYCHEDELIC_COLORS)

        # Draw background terrain top line with decorations
        for x in range(SCREEN_COLS):
            # Vary the height slightly for natural look
            height_offset = (x // 8) % 3 - 1  # -1, 0, or 1
            terrain_top = BG_TERRAIN_TOP + height_offset

            # Draw the top decoration (trees, rocks, etc.)
            if terrain_top >= 0 and terrain_top < SCREEN_ROWS:
                char = bg_chars[x % len(bg_chars)]
                screen[terrain_top][x] = (char, bg_color)

        # Fill between background terrain and foreground ground
        fill_color = env["fill_color"]
        fill_char = env["fill_char"]
        if self.player.acid_timer > 0:
            fill_color = random.choice(PSYCHEDELIC_COLORS)

        for y in range(BG_TERRAIN_BOTTOM, GROUND_HEIGHT):
            for x in range(SCREEN_COLS):
                # Solid fill with the fill character
                screen[y][x] = (fill_char, fill_color)

        # Draw foreground ground
        ground_color = env["ground_color"]
        ground_chars = env["ground_chars"]
        if self.player.acid_timer > 0:
            ground_color = random.choice(PSYCHEDELIC_COLORS)
        for x in range(SCREEN_COLS):
            char = ground_chars[x % len(ground_chars)]
            screen[GROUND_HEIGHT][x] = (char, ground_color)

        # Draw obstacles with per-character colors (fully opaque)
        for obs in self.obstacles:
            if not obs.alive:
                continue
            for i, row in enumerate(obs.char):
                for j, char in enumerate(row):
                    x, y = int(obs.x) + j, int(obs.y) + i
                    if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                        # Get color from color_data if available
                        if obs.color_data and i < len(obs.color_data) and j < len(obs.color_data[i]):
                            _, char_color = obs.color_data[i][j]
                            if char_color is None:
                                continue  # Skip edge spaces only
                        else:
                            char_color = RED  # Fallback

                        # Apply psychedelic effect during acid trip
                        if self.player.acid_timer > 0:
                            char_color = random.choice(PSYCHEDELIC_COLORS)

                        # Draw the character (spaces become solid background)
                        if char == ' ':
                            screen[y][x] = (' ', BLACK)  # Opaque black for interior
                        else:
                            screen[y][x] = (char, char_color)

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

        # Draw rainbow eye behind player during nirvana
        acid_level = self.player.get_acid_level()
        if acid_level == 3:
            # Draw rainbow eye centered behind player
            eye_width = len(RAINBOW_EYE[0])
            eye_height = len(RAINBOW_EYE)
            eye_x = int(self.player.x) + (self.player.width // 2) - (eye_width // 2)
            eye_y = int(self.player.y) - 1  # Slightly above/behind player

            for i, row in enumerate(RAINBOW_EYE):
                for j, char in enumerate(row):
                    x, y = eye_x + j, eye_y + i
                    if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                        # Rainbow colors cycling through the eye
                        color_idx = (i + j + self.frame // 3) % len(PSYCHEDELIC_COLORS)
                        screen[y][x] = (char, PSYCHEDELIC_COLORS[color_idx])

        # Draw player (with animation frame)
        player_color = CYAN
        if self.player.acid_timer > 0:
            player_color = PSYCHEDELIC_COLORS[self.frame % len(PSYCHEDELIC_COLORS)]
        player_char = self.player.get_char(self.frame)
        for i, row in enumerate(player_char):
            for j, char in enumerate(row):
                x, y = int(self.player.x) + j, int(self.player.y) + i
                if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                    screen[y][x] = (char, player_color)

        # Draw flash text for ACID or NIRVANA
        if self.player.acid_flash_timer > 0:
            # Flash "ACID" in middle of sky
            flash_text = ACID_FLASH_TEXT
            flash_y = 2  # Top area, avoiding HUD
            flash_x = (SCREEN_COLS - len(flash_text[0])) // 2
            # Flicker effect
            if self.player.acid_flash_timer % 6 < 3:
                for i, row in enumerate(flash_text):
                    for j, char in enumerate(row):
                        x, y = flash_x + j, flash_y + i
                        if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                            color = PSYCHEDELIC_COLORS[(i + j + self.frame) % len(PSYCHEDELIC_COLORS)]
                            screen[y][x] = (char, color)

        if self.player.nirvana_flash_timer > 0:
            # Flash "NIRVANA" in middle of sky
            flash_text = NIRVANA_FLASH_TEXT
            flash_y = 2  # Top area
            flash_x = (SCREEN_COLS - len(flash_text[0])) // 2
            # Flicker effect
            if self.player.nirvana_flash_timer % 6 < 3:
                for i, row in enumerate(flash_text):
                    for j, char in enumerate(row):
                        x, y = flash_x + j, flash_y + i
                        if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                            color = PSYCHEDELIC_COLORS[(i + j + self.frame) % len(PSYCHEDELIC_COLORS)]
                            screen[y][x] = (char, color)

        # Apply emoji mode for acid level 2 (11-20s)
        if acid_level == 2:
            for y in range(SCREEN_ROWS):
                for x in range(SCREEN_COLS):
                    char, color = screen[y][x]
                    if char in EMOJI_CHARS:
                        screen[y][x] = (EMOJI_CHARS[char], color)

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

def render_buffer(screen, font, buffer, emoji_font=None):
    for y, row in enumerate(buffer):
        x_pos = 0
        for char, color in row:
            if char != ' ' or color != BLACK:
                # Use emoji font for emoji characters
                is_emoji = ord(char) > 127 if len(char) == 1 else True
                render_font = emoji_font if (is_emoji and emoji_font) else font
                try:
                    surface = render_font.render(char, True, color if color != BLACK else GREEN)
                    screen.blit(surface, (x_pos, y * CHAR_HEIGHT))
                except:
                    # Fallback if emoji fails
                    surface = font.render('?', True, color if color != BLACK else GREEN)
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
    # Epic Gates of Hell death screen
    gate_art = [
        "        )  (        )  (        ",
        "       (    )      (    )       ",
        "        )  (        )  (        ",
        "   |\\  /|  |\\      /|  |\\  /|   ",
        "   | \\/  \\ | \\    / |  | \\/  |   ",
        "   |      \\|  \\  /  |  |     |   ",
        "  /|       |   \\/   | /|     |\\  ",
        " / |  G A T E S   O F  |     | \\ ",
        "|  |                   |     |  |",
        "|  |   H   E   L   L   |     |  |",
        "|  |                   |     |  |",
        "|  |___________________|     |  |",
        "|  /                   \\     |  |",
        "| /    YOU  HAVE  DIED  \\    |  |",
        "|/                       \\   |  |",
    ]

    # Draw gate art with fire colors
    fire_colors = [RED, ORANGE, YELLOW, RED, ORANGE]
    y_start = 1
    for i, line in enumerate(gate_art):
        color = fire_colors[i % len(fire_colors)]
        surface = font.render(line, True, color)
        x_pos = (SCREEN_WIDTH - len(line) * CHAR_WIDTH) // 2
        screen.blit(surface, (x_pos, (y_start + i) * CHAR_HEIGHT))

    # Score box below gates
    box_lines = [
        f"      Score: {score:>6}      ",
        f"      High:  {high_score:>6}      ",
        "                          ",
        "   [SPACE] Play Again     ",
        "   [ESC]   Quit           ",
    ]

    y_start = 17
    for i, line in enumerate(box_lines):
        surface = font.render(line, True, WHITE)
        x_pos = (SCREEN_WIDTH - len(line) * CHAR_WIDTH) // 2
        screen.blit(surface, (x_pos, (y_start + i) * CHAR_HEIGHT))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ASCII RUNNER")

    try:
        font = pygame.font.SysFont('consolas', 14)
    except:
        font = pygame.font.SysFont('courier', 14)

    # Load emoji font for emoji acid mode
    try:
        emoji_font = pygame.font.SysFont('segoeuiemoji', 12)
    except:
        emoji_font = None

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
        render_buffer(screen, font, buffer, emoji_font)

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

        # Acid timer with level indicator
        if game.player.acid_timer > 0:
            secs = game.player.acid_timer // 60
            acid_level = game.player.get_acid_level()
            if acid_level == 3:
                acid_text = f"NIRVANA {secs}s"
                color = PSYCHEDELIC_COLORS[game.frame % len(PSYCHEDELIC_COLORS)]
            elif acid_level == 2:
                acid_text = f"EMOJI {secs}s"
                color = YELLOW
            else:
                acid_text = f"<*> {secs}s"
                color = MAGENTA
            surface = font.render(acid_text, True, color)
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
