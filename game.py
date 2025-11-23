import pygame
import random
import sys
import json
import os
import numpy as np

# Import game engine
from game_engine import (
    GameEngine, SCREEN_COLS, SCREEN_ROWS, CHAR_WIDTH, CHAR_HEIGHT,
    SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_HEIGHT,
    BLACK, GREEN, WHITE, YELLOW, RED, CYAN, MAGENTA, ORANGE, PINK, PURPLE, LIME,
    PSYCHEDELIC_COLORS, POWERUP_PISTOL, POWERUP_JETPACK, POWERUP_BEANS,
    POWERUP_ACID, POWERUP_STOPWATCH
)

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
    low_freq = 60 + 20 * np.sin(2 * np.pi * 3 * t)
    rumble = np.sin(2 * np.pi * low_freq * t / sample_rate * np.arange(n_samples)) * 0.4
    noise = np.random.uniform(-0.3, 0.3, n_samples)
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


class GameRenderer:
    """Pygame renderer for the game engine"""

    def __init__(self):
        self.engine = GameEngine()
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
        self.last_died = False

    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.engine.game_over:
                    return "restart"
                else:
                    # Fire weapon if we have ammo
                    if self.engine.fire_weapon():
                        self.shoot_sound.play()
                    # Also try to jump
                    if self.engine.player.jump():
                        self.jump_sound.play()
        return None

    def update(self):
        """Update game and play sounds based on events"""
        events = self.engine.update()

        # Play sounds based on events
        if events.get("died") and not self.last_died:
            self.death_sound.play()
        self.last_died = events.get("died", False)

        if events.get("farted"):
            self.fart_sound.play()

        for powerup_type in events.get("collected", []):
            self.pickup_sound.play()
            if powerup_type == POWERUP_ACID:
                self.acid_sound.play()
            elif powerup_type == POWERUP_STOPWATCH:
                for sound in self.stopwatch_sounds:
                    sound.play()

        # Play music
        self.music_timer += 1
        if self.music_timer >= 16:
            self.music_notes[self.current_note].play()
            self.current_note = (self.current_note + 1) % len(self.music_notes)
            self.music_timer = 0

        return events

    def reset(self):
        """Reset game"""
        self.engine.reset()
        self.last_died = False


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
                    surface = font.render('?', True, color if color != BLACK else GREEN)
                    screen.blit(surface, (x_pos, y * CHAR_HEIGHT))
            x_pos += CHAR_WIDTH


def show_intro(screen, font, high_scores):
    screen.fill(BLACK)

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

        surface = font.render("NEW HIGH SCORE!", True, YELLOW)
        screen.blit(surface, (SCREEN_WIDTH // 2 - 80, 100))

        score_text = f"Score: {score}"
        surface = font.render(score_text, True, GREEN)
        screen.blit(surface, (SCREEN_WIDTH // 2 - 50, 150))

        surface = font.render("Enter your name (5 chars):", True, WHITE)
        screen.blit(surface, (SCREEN_WIDTH // 2 - 120, 220))

        display_name = name + "_" * (5 - len(name))
        surface = font.render(display_name, True, CYAN)
        screen.blit(surface, (SCREEN_WIDTH // 2 - 25, 260))

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


def render_game_over(screen, font, buffer):
    """Render the game over buffer"""
    for y, row in enumerate(buffer):
        x_pos = 0
        for char, color in row:
            if char != ' ':
                try:
                    surface = font.render(char, True, color)
                    screen.blit(surface, (x_pos, y * CHAR_HEIGHT))
                except:
                    pass
            x_pos += CHAR_WIDTH


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ASCII RUNNER")

    try:
        font = pygame.font.SysFont('consolas', 14)
    except:
        font = pygame.font.SysFont('courier', 14)

    try:
        emoji_font = pygame.font.SysFont('segoeuiemoji', 12)
    except:
        emoji_font = None

    clock = pygame.time.Clock()
    game = GameRenderer()
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
                    if game.engine.game_over:
                        if not score_entered and is_high_score(game.engine.score, high_scores):
                            name = get_player_name(screen, font, game.engine.score)
                            high_scores = add_high_score(name, game.engine.score, high_scores)
                            save_high_scores(high_scores)
                        score_entered = False
                        game.reset()
                    else:
                        result = game.handle_input(event)
                elif event.key == pygame.K_ESCAPE:
                    running = False
            else:
                game.handle_input(event)

        # Check for high score when game just ended
        if game.engine.game_over and not score_entered:
            if is_high_score(game.engine.score, high_scores):
                name = get_player_name(screen, font, game.engine.score)
                high_scores = add_high_score(name, game.engine.score, high_scores)
                save_high_scores(high_scores)
            score_entered = True

        game.update()

        screen.fill(BLACK)

        if game.engine.game_over:
            # Use the game over buffer with Gates of Hell
            buffer = game.engine.get_game_over_buffer()
            render_game_over(screen, font, buffer)
        else:
            # Normal game rendering
            buffer = game.engine.get_screen_buffer()
            render_buffer(screen, font, buffer, emoji_font)

            # Draw HUD
            score_text = f"Score: {game.engine.score}"
            surface = font.render(score_text, True, YELLOW)
            screen.blit(surface, (SCREEN_WIDTH - 120, 5))

            jumps_text = f"Jumps: {'*' * game.engine.player.jumps_left}"
            surface = font.render(jumps_text, True, WHITE)
            screen.blit(surface, (SCREEN_WIDTH - 120, 25))

            y_offset = 5
            state = game.engine.get_state()

            if state["player"]["ammo"] > 0:
                ammo_text = f"[=> x{state['player']['ammo']}"
                surface = font.render(ammo_text, True, ORANGE)
                screen.blit(surface, (10, y_offset))
                y_offset += 18

            if state["player"]["jetpack_jumps"] > 0:
                jet_text = f"<J> x{state['player']['jetpack_jumps']}"
                surface = font.render(jet_text, True, CYAN)
                screen.blit(surface, (10, y_offset))
                y_offset += 18

            if state["player"]["has_beans"]:
                secs = state["player"]["beans_timer"] // 60
                beans_text = f"{{B}} {secs}s"
                surface = font.render(beans_text, True, LIME)
                screen.blit(surface, (10, y_offset))
                y_offset += 18

            if state["player"]["acid_timer"] > 0:
                secs = state["player"]["acid_timer"] // 60
                acid_level = state["player"]["acid_level"]
                if acid_level == 3:
                    acid_text = f"NIRVANA {secs}s"
                    color = PSYCHEDELIC_COLORS[game.engine.frame % len(PSYCHEDELIC_COLORS)]
                elif acid_level == 2:
                    acid_text = f"EMOJI {secs}s"
                    color = YELLOW
                else:
                    acid_text = f"<*> {secs}s"
                    color = MAGENTA
                surface = font.render(acid_text, True, color)
                screen.blit(surface, (10, y_offset))
                y_offset += 18

            if state["stopwatch_timer"] > 0:
                secs = state["stopwatch_timer"] // 60
                watch_text = f"(O) {secs}s"
                surface = font.render(watch_text, True, YELLOW)
                screen.blit(surface, (10, y_offset))
                y_offset += 18

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
