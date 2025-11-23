# ASCII Runner - Core Game Engine
# Pure Python game logic loaded by Pyodide for web rendering

import random
import math

# Game constants
CHAR_WIDTH = 10
CHAR_HEIGHT = 18
SCREEN_COLS = 80
SCREEN_ROWS = 25
SCREEN_WIDTH = SCREEN_COLS * CHAR_WIDTH
SCREEN_HEIGHT = SCREEN_ROWS * CHAR_HEIGHT

GROUND_HEIGHT = 22  # Moved down for more headspace
MAX_JUMPS = 1
CAMERA_FOLLOW_THRESHOLD = 5  # Start following when player is this many rows from top
BASE_SCROLL_SPEED = 0.3
SPEED_PROGRESSION = 2000  # +0.1 speed per 200 points
JUMP_CLEARANCE_MULTIPLIER = 1.2

FLAT_TOP_OBSTACLES = ["easy"]
ORGANIC_OBSTACLES = ["bird", "cow"]  # Can be stomped Mario-style

# Colors as RGB tuples (renderer converts to platform format)
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

PSYCHEDELIC_COLORS = [MAGENTA, CYAN, PINK, PURPLE, ORANGE, LIME, YELLOW, RED, BLUE]

# Background ASCII art (from web version)
SUN_CHAR = [
    " \\ | / ",
    "-- O --",
    " / | \\ "
]

MOON_CHAR = [
    " .-. ",
    "( @ )",
    " '-' "
]

SNOWMAN_CHAR = [
    "  _  ",
    " (o) ",
    "(ooo)",
    " /_\\ "
]

SNOW_DRIFT_CHAR = [
    "  __  ",
    "_/  \\_"
]

MOUNTAIN_CHAR = [
    "     /\\     ",
    "    /  \\    ",
    "   / /\\ \\   ",
    "  / /  \\ \\  ",
    " / /    \\ \\ ",
    "/_/______\\_\\"
]

SMALL_MOUNTAIN_CHAR = [
    "   /\\   ",
    "  /  \\  ",
    " /    \\ ",
    "/______\\"
]

# Gates of Hell death screen - full screen elaborate version
GATES_OF_HELL = [
    "                    A B A N D O N   A L L   H O P E                     ",
    "                                                                        ",
    "      )  (  )  (          ^ ^ ^ ^ ^ ^          )  (  )  (               ",
    "     (    )(    )       ^  ^ ^ ^ ^ ^  ^       (    )(    )              ",
    "      )  (  )  (       ^ ^ ^ ^ ^ ^ ^ ^ ^       )  (  )  (               ",
    "    ___|    |___      /|             |\\      ___|    |___               ",
    "   /   |    |   \\    / |   ) ( ) (   | \\    /   |    |   \\              ",
    "  /    |    |    \\  /  |  (     ) (  |  \\  /    |    |    \\             ",
    " |     |    |     ||   | ) ( ) ( ) ( |   ||     |    |     |            ",
    " |  ___|    |___  ||   |(    )(    )|   ||  ___|    |___  |            ",
    " | |   |    |   | ||   | )  (  )  ( |   || |   |    |   | |            ",
    " | |   |    |   | ||   |    ) (     |   || |   |    |   | |            ",
    " | |   | /\\ |   | ||   |  (    ) (  |   || |   | /\\ |   | |            ",
    " | |   |/  \\|   | ||   |)  (  )  (  |   || |   |/  \\|   | |            ",
    " | |   |    |   | ||   |  ) (  ) (  |   || |   |    |   | |            ",
    " | |___|    |___| ||   | (   )(   ) |   || |___|    |___| |            ",
    " |/   /|    |\\   \\||  /|             |\\  ||/   /|    |\\   \\|            ",
    " /   / |    | \\   \\| / |             | \\ |/   / |    | \\   \\            ",
    "|   /  |    |  \\   | /                \\ |   /  |    |  \\   |            ",
    "|  /   | o  |   \\  |/                  \\|  /   |    |   \\  |            ",
    "| /   /|/|\\|\\   \\ |                    | /   /|    |\\   \\ |            ",
    "|/___/ | | | \\___\\|____________________|/___/ |    | \\___\\|            ",
]

# Small player figure for death screen
DEATH_PLAYER = [
    " o ",
    "/|\\",
    "/ \\",
]

# Environment definitions
ENVIRONMENTS = {
    "grass": {
        "ground_color": GREEN,
        "ground_chars": ('#', '=', '"', ','),
        "bg_color": (0, 180, 0),
        "bg_chars": ('^', 'Y', '*', 'T'),
        "fill_color": (100, 80, 50),
        "fill_char": '.',
    },
    "desert": {
        "ground_color": YELLOW,
        "ground_chars": ('~', '.', '_', ':'),
        "bg_color": (200, 150, 50),
        "bg_chars": ('A', 'n', '^', 'o'),
        "fill_color": (180, 130, 40),
        "fill_char": ':',
    },
    "snow": {
        "ground_color": WHITE,
        "ground_chars": ('*', '.', '~', '_'),
        "bg_color": (200, 200, 220),
        "bg_chars": ('^', 'A', '*', 'T'),
        "fill_color": (180, 180, 200),
        "fill_char": '.',
    },
    "cave": {
        "ground_color": (150, 150, 150),
        "ground_chars": ('#', '=', '_', '.'),
        "bg_color": (100, 100, 100),
        "bg_chars": ('^', 'V', '|', 'M'),
        "fill_color": (80, 80, 80),
        "fill_char": '#',
    },
    "lava": {
        "ground_color": (200, 50, 0),
        "ground_chars": ('#', '=', '~', '^'),
        "bg_color": (255, 100, 0),
        "bg_chars": ('^', 'M', 'W', '~'),
        "fill_color": (150, 30, 0),
        "fill_char": '.',
    },
}

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

# Player characters
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

PLAYER_LOTUS_CHAR = [
    " o   ",
    "\\|/  ",
    "/_\\  ",
    "| |  ",
]

# Rainbow eye for nirvana
RAINBOW_EYE = [
    "    .~~~~~.    ",
    "   /   _   \\   ",
    "  |  ((@))  |  ",
    "  |   \\_/   |  ",
    "   \\_______/   ",
]

# Flash text
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

# Trippy symbols for emoji mode
EMOJI_CHARS = {
    'o': '@', 'O': '0', '|': '!', '/': '\\', '\\': '/',
    '_': '~', '-': '=', '=': '-', '#': '%', '.': 'o',
    '^': 'v', 'v': '^', '<': '>', '>': '<', '[': '{', ']': '}',
    '(': '[', ')': ']', '{': '(', '}': ')', '*': '+', '+': '*',
    'A': 'V', 'V': 'A', 'M': 'W', 'W': 'M', 'T': 'Y', 'Y': 'T',
}

# Obstacles
OBSTACLE_CHARS_EASY = [
    ["   ___   ", "  /. .\\  ", " /. . .\\ ", "/_._._._\\"],
    ["   /\\   ", "  /  \\  ", " / || \\ ", "/______\\"],
    [" [====] ", " |    | ", " [====] ", " |    | ", " [====] "],
    [" .----. ", "(|    |)", " |====| ", "(|    |)", " '----' "],
]

BIRD_CHAR = ["   ___   ", "\\<(o  )>/", "   ^^    "]
COW_CHAR = ["   ^__^   ", "  (oo)\\_  ", "  (__)\\  )", "   ||--|| "]
HOUSE_CHAR = ["    /\\    ", "   /  \\   ", "  /    \\  ", " /______\\ ", " |  []  | ", " | .__. | ", " | |  | | ", " |_|__|_| "]
CACTUS_CHAR = ["   |   ", "  \\|/  ", "   |   ", "  \\|   ", "   |   "]
SPIKE_CHAR = [" /\\ /\\ ", "/\\/\\/\\"]

# Obstacle colors (simplified - full color data would be here)
# For brevity, using basic color assignments

# Powerup types
POWERUP_PISTOL = "pistol"
POWERUP_JETPACK = "jetpack"
POWERUP_BEANS = "beans"
POWERUP_ACID = "acid"
POWERUP_STOPWATCH = "stopwatch"

POWERUP_CHARS = {
    POWERUP_PISTOL: ["[=>"],
    POWERUP_JETPACK: ["<J>"],
    POWERUP_BEANS: ["{B}"],
    POWERUP_ACID: ["<*>"],
    POWERUP_STOPWATCH: ["(O)"],
}

POWERUP_COLORS = {
    POWERUP_PISTOL: ORANGE,
    POWERUP_JETPACK: CYAN,
    POWERUP_BEANS: LIME,
    POWERUP_ACID: MAGENTA,
    POWERUP_STOPWATCH: YELLOW,
}

# Calculate physics
def get_max_obstacle_height():
    all_obstacles = OBSTACLE_CHARS_EASY + [BIRD_CHAR, COW_CHAR, HOUSE_CHAR, CACTUS_CHAR, SPIKE_CHAR]
    return max(len(obs) for obs in all_obstacles)

MAX_OBSTACLE_HEIGHT = get_max_obstacle_height()
DESIRED_JUMP_HEIGHT = MAX_OBSTACLE_HEIGHT * JUMP_CLEARANCE_MULTIPLIER
GRAVITY = 0.035
JUMP_FORCE = -math.sqrt(2 * GRAVITY * DESIRED_JUMP_HEIGHT)
JUMP_DURATION = 2 * (-JUMP_FORCE / GRAVITY)


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
        self.y += 0.2

    def is_done(self):
        return self.life <= 0

    def get_char(self):
        idx = min(3, (15 - self.life) // 4)
        return self.chars[idx]


class LavaBlob:
    def __init__(self, horizontal=False):
        self.horizontal = horizontal
        if horizontal:
            self.x = SCREEN_COLS + random.randint(0, 5)
            self.y = random.randint(5, SCREEN_ROWS - 3)
            self.speed = random.uniform(0.3, 0.6)
        else:
            self.x = random.randint(0, SCREEN_COLS - 1)
            self.y = SCREEN_ROWS + random.randint(0, 5)
            self.speed = random.uniform(0.1, 0.3)
        self.wobble = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.05, 0.15)
        self.size = random.choice([1, 2, 3])
        self.color = random.choice(PSYCHEDELIC_COLORS)
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


class Snowflake:
    def __init__(self):
        self.x = random.randint(0, SCREEN_COLS - 1)
        self.y = random.randint(-10, 0)
        self.speed = random.uniform(0.05, 0.15)
        self.drift = random.uniform(-0.02, 0.02)
        self.char = random.choice(['*', '.', '+', 'o'])

    def update(self):
        self.y += self.speed
        self.x += self.drift
        if self.x < 0:
            self.x = SCREEN_COLS - 1
        elif self.x >= SCREEN_COLS:
            self.x = 0

    def is_off_screen(self):
        return self.y >= SCREEN_ROWS


class BackgroundElement:
    def __init__(self, element_type, x):
        self.type = element_type
        self.x = x
        self.speed = 0.05  # Slow parallax scrolling

        if element_type == "mountain":
            self.char = MOUNTAIN_CHAR
            self.y = 6  # High up
            self.color = (100, 100, 120)
        elif element_type == "small_mountain":
            self.char = SMALL_MOUNTAIN_CHAR
            self.y = 8
            self.color = (80, 80, 100)
        elif element_type == "snowman":
            self.char = SNOWMAN_CHAR
            self.y = 8
            self.color = WHITE
        elif element_type == "snow_drift":
            self.char = SNOW_DRIFT_CHAR
            self.y = 10
            self.color = (220, 220, 240)
        else:
            self.char = SMALL_MOUNTAIN_CHAR
            self.y = 8
            self.color = GRAY

        self.width = max(len(row) for row in self.char)
        self.height = len(self.char)

    def update(self, scroll_speed):
        self.x -= scroll_speed * self.speed

    def is_off_screen(self):
        return self.x + self.width < 0


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
        self.y = GROUND_HEIGHT - 4
        self.vel_y = 0
        self.jumps_left = MAX_JUMPS
        self.on_ground = True
        self.jetpack_jumps = 0
        self.has_beans = False
        self.beans_timer = 0
        self.ammo = 0
        self.acid_timer = 0
        self.acid_flash_timer = 0
        self.nirvana_flash_timer = 0
        self.was_in_nirvana = False
        self.grace_period = 0  # Invulnerability after nirvana ends
        self.width = 5
        self.height = 4

    def get_acid_level(self):
        if self.acid_timer <= 0:
            return 0
        secs = self.acid_timer / 60
        if secs <= 10:
            return 1
        elif secs <= 20:
            return 2
        else:
            return 3

    def is_invincible(self):
        return self.get_acid_level() == 3 or self.grace_period > 0

    def get_max_jumps(self):
        return MAX_JUMPS + (1 if self.jetpack_jumps > 0 else 0)

    def jump(self):
        if self.jumps_left > 0:
            self.vel_y = JUMP_FORCE
            self.jumps_left -= 1
            self.on_ground = False
            if not self.on_ground and self.jetpack_jumps > 0:
                self.jetpack_jumps -= 1
            return True
        return False

    def fart_jump(self):
        self.vel_y = JUMP_FORCE * 0.8
        self.on_ground = False

    def stomp_bounce(self):
        """Bounce after stomping an enemy Mario-style"""
        self.vel_y = JUMP_FORCE * 0.6  # Smaller bounce than full jump
        self.on_ground = False

    def update(self):
        current_nirvana = self.get_acid_level() == 3
        if current_nirvana and not self.was_in_nirvana:
            self.nirvana_flash_timer = 60
        # Start grace period when nirvana ends
        if self.was_in_nirvana and not current_nirvana:
            self.grace_period = 120  # 2 seconds at 60fps
        self.was_in_nirvana = current_nirvana

        # Decrement grace period
        if self.grace_period > 0:
            self.grace_period -= 1

        if self.get_acid_level() == 3:
            target_y = 6
            self.y += (target_y - self.y) * 0.1
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
        if (frame // 8) % 2 == 0:
            return PLAYER_RUN_1
        else:
            return PLAYER_RUN_2


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
            self.fly_y = random.randint(8, 14)
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
        if self.flying:
            self.y = self.fly_y + math.sin(self.x * 0.1) * 2

    def is_off_screen(self):
        return self.x + self.width < 0


class GameEngine:
    """Core game logic - platform independent"""

    def __init__(self):
        self.reset()
        self.high_score = 0
        self.frame = 0

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.powerups = []
        self.bullets = []
        self.fart_puffs = []
        self.lava_blobs = []
        self.snowflakes = []
        self.background_elements = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 180
        self.spawn_delay = 40
        self.powerup_timer = 120
        self.bg_element_timer = 0
        self.scroll_speed = BASE_SCROLL_SPEED
        self.stopwatch_timer = 0
        self.stopwatch_speed_reduction = 0
        self.scroll_offset = 0.0  # Track world scroll for ground/background
        self.bg_scroll_offset = 0.0  # Slower scroll for background parallax
        self.camera_y = 0  # Vertical camera offset (negative = looking up)

        # Generate starfield (two screen heights above)
        self.stars = []
        for _ in range(100):
            star_x = random.randint(0, SCREEN_COLS - 1)
            star_y = random.randint(-SCREEN_ROWS * 2, -1)  # Above the screen
            star_char = random.choice(['.', '*', '+', 'o'])
            star_brightness = random.choice([(100, 100, 120), (150, 150, 180), (200, 200, 255), (255, 255, 255)])
            self.stars.append((star_x, star_y, star_char, star_brightness))

        # Initialize some background elements
        for i in range(3):
            x = i * 30 + random.randint(0, 10)
            element_type = random.choice(["mountain", "small_mountain"])
            self.background_elements.append(BackgroundElement(element_type, x))

    def spawn_obstacle(self):
        if self.spawn_timer <= 0:
            obstacle_type = "easy"
            if self.score > 300:
                r = random.random()
                if r < 0.15:
                    obstacle_type = "cactus"
                elif r < 0.25:
                    obstacle_type = "spike"
            if self.score > 800:
                r = random.random()
                if r < 0.15:
                    obstacle_type = "bird"
                elif r < 0.25:
                    obstacle_type = "cactus"
                elif r < 0.35:
                    obstacle_type = "spike"
            if self.score > 1500:
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

            jump_distance = JUMP_DURATION * self.scroll_speed
            landing_buffer = 8
            min_distance = jump_distance + new_obstacle.width + landing_buffer
            min_frames = int(min_distance / max(self.scroll_speed, 0.1))
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
        """Check for collisions. Returns (collision, stomped) tuple."""
        px, py = int(self.player.x), int(self.player.y)
        player_width, player_height = self.player.width, self.player.height

        hitbox_padding = 1
        px += hitbox_padding
        player_width -= hitbox_padding * 2
        py += hitbox_padding
        player_height -= hitbox_padding
        player_bottom = py + player_height

        stomped = False

        for obs in self.obstacles:
            if not obs.alive:
                continue
            ox, oy = int(obs.x), int(obs.y)

            if px < ox + obs.width and px + player_width > ox:
                if py < oy + obs.height and player_bottom > oy:
                    # Check if landing on top
                    landing_on_top = player_bottom <= oy + 3 and self.player.vel_y >= 0

                    if landing_on_top:
                        # Stomp organic enemies (Mario-style)
                        if obs.obstacle_type in ORGANIC_OBSTACLES:
                            obs.alive = False
                            self.player.stomp_bounce()
                            stomped = True
                            continue
                        # Land on flat-top obstacles
                        elif obs.obstacle_type in FLAT_TOP_OBSTACLES:
                            self.player.y = oy - self.player.height
                            self.player.vel_y = 0
                            self.player.jumps_left = self.player.get_max_jumps()
                            self.player.on_ground = True
                            continue

                    # Regular collision - death
                    return (True, stomped)

        return (False, stomped)

    def check_powerup_collision(self):
        px, py = int(self.player.x), int(self.player.y)
        player_width, player_height = self.player.width, self.player.height
        collected = []

        for powerup in self.powerups[:]:
            ox, oy = int(powerup.x), int(powerup.y)
            if (px < ox + powerup.width and
                px + player_width > ox and
                py < oy + powerup.height and
                py + player_height > oy):

                collected.append(powerup.type)

                if powerup.type == POWERUP_JETPACK:
                    self.player.jetpack_jumps += 10
                    self.player.jumps_left = self.player.get_max_jumps()
                elif powerup.type == POWERUP_BEANS:
                    self.player.has_beans = True
                    self.player.beans_timer = 600
                elif powerup.type == POWERUP_PISTOL:
                    self.player.ammo += 10
                elif powerup.type == POWERUP_ACID:
                    self.player.acid_timer += 600  # Add 10 seconds per pickup
                    self.player.acid_flash_timer = 60
                elif powerup.type == POWERUP_STOPWATCH:
                    self.stopwatch_timer = 300
                    self.stopwatch_speed_reduction = self.scroll_speed * 0.6

                self.powerups.remove(powerup)

        return collected

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
            self.player.ammo -= 1
            return True
        return False

    def update(self):
        """Main game update - returns events dict for renderer"""
        if self.game_over:
            return {"game_over": True}

        events = {
            "game_over": False,
            "jumped": False,
            "shot": False,
            "died": False,
            "farted": False,
            "collected": [],
        }

        self.frame += 1
        self.player.update()
        self.spawn_obstacle()
        self.spawn_powerup()

        # Camera follows player upward
        if self.player.y < CAMERA_FOLLOW_THRESHOLD:
            target_camera = -(CAMERA_FOLLOW_THRESHOLD - self.player.y)
            self.camera_y += (target_camera - self.camera_y) * 0.1  # Smooth follow
        else:
            # Return camera to normal when player is lower
            self.camera_y += (0 - self.camera_y) * 0.1

        base_speed = BASE_SCROLL_SPEED + (self.score / SPEED_PROGRESSION)

        if self.stopwatch_timer > 0:
            self.stopwatch_timer -= 1
            effect_ratio = self.stopwatch_timer / 300
            self.scroll_speed = base_speed - (self.stopwatch_speed_reduction * effect_ratio)
        else:
            self.scroll_speed = base_speed
            self.stopwatch_speed_reduction = 0

        # Update scroll offsets for terrain movement
        self.scroll_offset += self.scroll_speed
        self.bg_scroll_offset += self.scroll_speed * 0.3  # Background moves slower (parallax)

        for obs in self.obstacles:
            obs.update(self.scroll_speed)
        for powerup in self.powerups:
            powerup.update(self.scroll_speed)
        for bullet in self.bullets:
            bullet.update()
        for puff in self.fart_puffs:
            puff.update()

        if self.player.acid_timer > 0:
            for blob in self.lava_blobs:
                blob.update()
            if random.random() < 0.15:
                horizontal = random.random() < 0.5
                self.lava_blobs.append(LavaBlob(horizontal=horizontal))
            self.lava_blobs = [b for b in self.lava_blobs if not b.is_off_screen()]
        else:
            self.lava_blobs = []

        # Update snowflakes in snow environment
        env_name = get_environment_for_score(self.score)
        if env_name == "snow":
            for flake in self.snowflakes:
                flake.update()
            self.snowflakes = [f for f in self.snowflakes if not f.is_off_screen()]
            # Spawn new snowflakes
            if len(self.snowflakes) < 30 and random.random() < 0.1:
                self.snowflakes.append(Snowflake())
        else:
            self.snowflakes = []

        # Update background elements
        for elem in self.background_elements:
            elem.update(self.scroll_speed)
        self.background_elements = [e for e in self.background_elements if not e.is_off_screen()]

        # Spawn new background elements
        self.bg_element_timer -= 1
        if self.bg_element_timer <= 0:
            if env_name == "snow":
                element_type = random.choice(["mountain", "small_mountain", "snowman", "snow_drift"])
            elif env_name == "desert":
                element_type = random.choice(["small_mountain"])
            else:
                element_type = random.choice(["mountain", "small_mountain"])
            self.background_elements.append(BackgroundElement(element_type, SCREEN_COLS + 5))
            self.bg_element_timer = random.randint(200, 400)

        self.obstacles = [obs for obs in self.obstacles if not obs.is_off_screen() and obs.alive]
        self.powerups = [p for p in self.powerups if not p.is_off_screen()]
        self.bullets = [b for b in self.bullets if not b.is_off_screen()]
        self.fart_puffs = [p for p in self.fart_puffs if not p.is_done()]

        events["collected"] = self.check_powerup_collision()
        self.check_bullet_hits()

        if self.player.has_beans and random.random() < 0.005:
            self.player.fart_jump()
            self.fart_puffs.append(FartPuff(self.player.x + self.player.width // 2, self.player.y + self.player.height))
            events["farted"] = True

        collision, stomped = self.check_collision()
        events["stomped"] = stomped

        if collision and not self.player.is_invincible():
            self.game_over = True
            events["died"] = True
            events["game_over"] = True
            if self.score > self.high_score:
                self.high_score = self.score
        else:
            self.score += 1

        return events

    def get_screen_buffer(self):
        """Returns 2D array of (char, color, depth) tuples
        Depth: 0 = far background (smallest), 1 = mid background, 2 = foreground (largest)"""
        screen = [[(' ', BLACK, 2) for _ in range(SCREEN_COLS)] for _ in range(SCREEN_ROWS)]

        # Camera offset for vertical scrolling
        cam_y = int(self.camera_y)

        env_name = get_environment_for_score(self.score)
        env = ENVIRONMENTS[env_name]

        # Draw stars (visible when camera looks up)
        for star_x, star_y, star_char, star_color in self.stars:
            screen_y = star_y - cam_y
            if 0 <= screen_y < SCREEN_ROWS and 0 <= star_x < SCREEN_COLS:
                screen[screen_y][star_x] = (star_char, star_color, 0)

        # Draw sun or moon based on day cycle (score-based) - depth 0 (far)
        is_day = (self.score // 500) % 2 == 0
        if env_name != "cave":  # No sun/moon in caves
            if is_day:
                sun_x = 65
                sun_y = 1 - cam_y
                sun_color = YELLOW
                for i, row in enumerate(SUN_CHAR):
                    for j, char in enumerate(row):
                        x, y = sun_x + j, sun_y + i
                        if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                            screen[y][x] = (char, sun_color, 0)
            else:
                moon_x = 65
                moon_y = 1 - cam_y
                moon_color = (200, 200, 220)
                for i, row in enumerate(MOON_CHAR):
                    for j, char in enumerate(row):
                        x, y = moon_x + j, moon_y + i
                        if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                            screen[y][x] = (char, moon_color, 0)

        # Draw background elements (mountains, snowmen) - depth 0 (far)
        for elem in self.background_elements:
            color = elem.color
            if self.player.acid_timer > 0:
                color = random.choice(PSYCHEDELIC_COLORS)
            for i, row in enumerate(elem.char):
                for j, char in enumerate(row):
                    x, y = int(elem.x) + j, elem.y + i - cam_y
                    if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                        screen[y][x] = (char, color, 0)

        # Draw snowflakes - depth 1 (mid)
        for flake in self.snowflakes:
            x, y = int(flake.x), int(flake.y) - cam_y
            if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                flake_color = WHITE
                if self.player.acid_timer > 0:
                    flake_color = random.choice(PSYCHEDELIC_COLORS)
                screen[y][x] = (flake.char, flake_color, 1)

        # Draw lava blobs - depth 1 (mid)
        for blob in self.lava_blobs:
            x, y = int(blob.x), int(blob.y) - cam_y
            if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                screen[y][x] = (blob.char, blob.color, 1)

        # Background terrain - depth 1 (mid)
        BG_TERRAIN_TOP = 12
        BG_TERRAIN_BOTTOM = 17

        bg_color = env["bg_color"]
        bg_chars = env["bg_chars"]
        if self.player.acid_timer > 0:
            bg_color = random.choice(PSYCHEDELIC_COLORS)

        # Use scroll offset for background (slower parallax)
        bg_offset = int(self.bg_scroll_offset)
        for x in range(SCREEN_COLS):
            height_offset = ((x + bg_offset) // 8) % 3 - 1
            terrain_top = BG_TERRAIN_TOP + height_offset - cam_y
            if 0 <= terrain_top < SCREEN_ROWS:
                char = bg_chars[(x + bg_offset) % len(bg_chars)]
                screen[terrain_top][x] = (char, bg_color, 1)

        # Fill - scrolling fill pattern - depth 1 (mid)
        fill_color = env["fill_color"]
        fill_char = env["fill_char"]
        fill_chars = [fill_char, '.', fill_char, ':']  # Varied pattern for movement
        if self.player.acid_timer > 0:
            fill_color = random.choice(PSYCHEDELIC_COLORS)

        fill_offset = int(self.scroll_offset * 0.5)
        for y in range(BG_TERRAIN_BOTTOM, GROUND_HEIGHT):
            screen_y = y - cam_y
            if 0 <= screen_y < SCREEN_ROWS:
                for x in range(SCREEN_COLS):
                    char = fill_chars[(x + fill_offset + y) % len(fill_chars)]
                    screen[screen_y][x] = (char, fill_color, 1)

        # Ground - scrolling at full speed - depth 2 (foreground)
        ground_color = env["ground_color"]
        ground_chars = env["ground_chars"]
        if self.player.acid_timer > 0:
            ground_color = random.choice(PSYCHEDELIC_COLORS)
        ground_offset = int(self.scroll_offset)
        ground_screen_y = GROUND_HEIGHT - cam_y
        if 0 <= ground_screen_y < SCREEN_ROWS:
            for x in range(SCREEN_COLS):
                char = ground_chars[(x + ground_offset) % len(ground_chars)]
                screen[ground_screen_y][x] = (char, ground_color, 2)

        # Obstacles - depth 2 (foreground)
        for obs in self.obstacles:
            if not obs.alive:
                continue
            obs_color = RED
            if self.player.acid_timer > 0:
                obs_color = random.choice(PSYCHEDELIC_COLORS)
            for i, row in enumerate(obs.char):
                for j, char in enumerate(row):
                    x, y = int(obs.x) + j, int(obs.y) + i - cam_y
                    if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                        if char == ' ':
                            screen[y][x] = (' ', BLACK, 2)
                        else:
                            screen[y][x] = (char, obs_color, 2)

        # Powerups - depth 2 (foreground)
        for powerup in self.powerups:
            for i, row in enumerate(powerup.char):
                for j, char in enumerate(row):
                    x, y = int(powerup.x) + j, int(powerup.y) + i - cam_y
                    if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                        screen[y][x] = (char, powerup.color, 2)

        # Fart puffs - depth 2 (foreground)
        for puff in self.fart_puffs:
            x, y = int(puff.x), int(puff.y) - cam_y
            if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                screen[y][x] = (puff.get_char(), LIME, 2)

        # Bullets - depth 2 (foreground)
        for bullet in self.bullets:
            x, y = int(bullet.x), int(bullet.y) - cam_y
            for i, char in enumerate(bullet.char):
                if 0 <= x + i < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                    screen[y][x + i] = (char, ORANGE, 2)

        # Rainbow eye during nirvana - depth 2 (foreground)
        acid_level = self.player.get_acid_level()
        if acid_level == 3:
            eye_width = len(RAINBOW_EYE[0])
            eye_x = int(self.player.x) + (self.player.width // 2) - (eye_width // 2)
            eye_y = int(self.player.y) - 1 - cam_y

            for i, row in enumerate(RAINBOW_EYE):
                for j, char in enumerate(row):
                    x, y = eye_x + j, eye_y + i
                    if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                        color_idx = (i + j + self.frame // 3) % len(PSYCHEDELIC_COLORS)
                        screen[y][x] = (char, PSYCHEDELIC_COLORS[color_idx], 2)

        # Player - depth 2 (foreground)
        player_color = CYAN
        if self.player.acid_timer > 0:
            player_color = PSYCHEDELIC_COLORS[self.frame % len(PSYCHEDELIC_COLORS)]
        # Flash during grace period
        if self.player.grace_period > 0 and (self.frame // 4) % 2 == 0:
            player_color = WHITE
        player_char = self.player.get_char(self.frame)
        for i, row in enumerate(player_char):
            for j, char in enumerate(row):
                x, y = int(self.player.x) + j, int(self.player.y) + i - cam_y
                if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                    screen[y][x] = (char, player_color, 2)

        # Flash text - depth 2 (foreground)
        if self.player.acid_flash_timer > 0:
            flash_text = ACID_FLASH_TEXT
            flash_y = 2
            flash_x = (SCREEN_COLS - len(flash_text[0])) // 2
            if self.player.acid_flash_timer % 6 < 3:
                for i, row in enumerate(flash_text):
                    for j, char in enumerate(row):
                        x, y = flash_x + j, flash_y + i
                        if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                            color = PSYCHEDELIC_COLORS[(i + j + self.frame) % len(PSYCHEDELIC_COLORS)]
                            screen[y][x] = (char, color, 2)

        if self.player.nirvana_flash_timer > 0:
            flash_text = NIRVANA_FLASH_TEXT
            flash_y = 2
            flash_x = (SCREEN_COLS - len(flash_text[0])) // 2
            if self.player.nirvana_flash_timer % 6 < 3:
                for i, row in enumerate(flash_text):
                    for j, char in enumerate(row):
                        x, y = flash_x + j, flash_y + i
                        if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                            color = PSYCHEDELIC_COLORS[(i + j + self.frame) % len(PSYCHEDELIC_COLORS)]
                            screen[y][x] = (char, color, 2)

        # Emoji mode
        if acid_level == 2:
            for y in range(SCREEN_ROWS):
                for x in range(SCREEN_COLS):
                    char, color, depth = screen[y][x]
                    if char in EMOJI_CHARS:
                        screen[y][x] = (EMOJI_CHARS[char], color, depth)

        return screen

    def get_state(self):
        """Get current game state for serialization"""
        return {
            "score": self.score,
            "high_score": self.high_score,
            "game_over": self.game_over,
            "player": {
                "jumps_left": self.player.jumps_left,
                "ammo": self.player.ammo,
                "jetpack_jumps": self.player.jetpack_jumps,
                "has_beans": self.player.has_beans,
                "beans_timer": self.player.beans_timer,
                "acid_timer": self.player.acid_timer,
                "acid_level": self.player.get_acid_level(),
                "grace_period": self.player.grace_period,
            },
            "stopwatch_timer": self.stopwatch_timer,
            "frame": self.frame,
        }

    def get_game_over_buffer(self):
        """Returns game over screen with Gates of Hell"""
        screen = [[(' ', BLACK, 2) for _ in range(SCREEN_COLS)] for _ in range(SCREEN_ROWS)]

        flame_chars = ['^', 'W', 'M', '*', '~', 'v', 'A']

        # Fill background with dark red gradient
        for y in range(SCREEN_ROWS):
            for x in range(SCREEN_COLS):
                if random.random() < 0.1:
                    darkness = 50 + int(y * 3)
                    screen[y][x] = ('.', (darkness, 0, 0), 2)

        # Gates of Hell - centered
        gates_width = len(GATES_OF_HELL[0]) if GATES_OF_HELL else 0
        gates_x = (SCREEN_COLS - gates_width) // 2
        gates_y = 0

        for i, row in enumerate(GATES_OF_HELL):
            for j, char in enumerate(row):
                x, y = gates_x + j, gates_y + i
                if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS:
                    if char != ' ':
                        # Color based on character type
                        if char in '()':
                            # Flames coming from gates - animated
                            if random.random() < 0.7:
                                color = random.choice([RED, ORANGE, YELLOW, (255, 50, 0)])
                            else:
                                color = (255, 200, 0)
                        elif char == '^':
                            # Rising flames
                            color = random.choice([ORANGE, YELLOW, RED])
                        elif char in 'ABANDONALLHOPE':
                            # Title text - ominous glow
                            if random.random() < 0.9:
                                color = (200, 0, 0)
                            else:
                                color = (255, 100, 0)
                        elif char in '|_/\\':
                            # Gate structure - dark iron
                            if random.random() < 0.85:
                                color = (80, 80, 90)
                            else:
                                color = (120, 60, 0)  # Rust
                        elif char == 'o':
                            # Player head
                            color = CYAN
                        else:
                            # Default gate color
                            color = (100, 100, 110)
                        screen[y][x] = (char, color, 2)

        # Draw player figure in front of gates (centered at bottom of gate opening)
        player_x = SCREEN_COLS // 2 - 1
        player_y = 19
        for i, row in enumerate(DEATH_PLAYER):
            for j, char in enumerate(row):
                x, y = player_x + j, player_y + i
                if 0 <= x < SCREEN_COLS and 0 <= y < SCREEN_ROWS and char != ' ':
                    screen[y][x] = (char, CYAN, 2)

        # Animated flames pouring out from gate opening
        gate_center = SCREEN_COLS // 2
        for _ in range(40):
            fx = gate_center + random.randint(-8, 8)
            fy = random.randint(8, 18)
            if 0 <= fx < SCREEN_COLS and 0 <= fy < SCREEN_ROWS:
                char = random.choice(flame_chars)
                color = random.choice([RED, ORANGE, YELLOW, (255, 100, 0)])
                # Only draw if not overwriting important stuff
                if screen[fy][fx][0] in ' .':
                    screen[fy][fx] = (char, color, 2)

        # Ground - charred earth
        for x in range(SCREEN_COLS):
            char = random.choice(['#', '=', '_', '~'])
            color = (40, 20, 10) if random.random() < 0.7 else (60, 30, 0)
            screen[SCREEN_ROWS - 3][x] = (char, color, 2)

        # Score display - bottom of screen
        score_text = f"Score: {self.score}  High: {self.high_score}"
        restart_text = "PRESS SPACE TO CONTINUE"

        score_x = (SCREEN_COLS - len(score_text)) // 2
        restart_x = (SCREEN_COLS - len(restart_text)) // 2

        for i, char in enumerate(score_text):
            if 0 <= score_x + i < SCREEN_COLS:
                screen[SCREEN_ROWS - 2][score_x + i] = (char, (150, 150, 150), 2)

        # Blinking restart text
        if (self.frame // 30) % 2 == 0:
            for i, char in enumerate(restart_text):
                if 0 <= restart_x + i < SCREEN_COLS:
                    screen[SCREEN_ROWS - 1][restart_x + i] = (char, CYAN, 2)

        return screen
