// ASCII Runner - Web Version
// Ported from Python/Pygame

// Game constants
const CHAR_WIDTH = 10;
const CHAR_HEIGHT = 18;
const SCREEN_COLS = 80;
const SCREEN_ROWS = 25;
const SCREEN_WIDTH = SCREEN_COLS * CHAR_WIDTH;
const SCREEN_HEIGHT = SCREEN_ROWS * CHAR_HEIGHT;

const GROUND_HEIGHT = 20;
const GRAVITY = 0.12;
const JUMP_FORCE = -1.2;
const MAX_JUMPS = 1;
const BASE_SCROLL_SPEED = 1;

// Colors
const BLACK = '#000000';
const GREEN = '#00ff00';
const WHITE = '#ffffff';
const YELLOW = '#ffff00';
const RED = '#ff6464';
const CYAN = '#00ffff';
const MAGENTA = '#ff00ff';
const ORANGE = '#ffa500';
const PINK = '#ff69b4';
const PURPLE = '#9400d3';
const LIME = '#32ff32';
const BLUE = '#6464ff';

const PSYCHEDELIC_COLORS = [MAGENTA, CYAN, PINK, PURPLE, ORANGE, LIME, YELLOW, RED, BLUE];

// Character definitions
const PLAYER_CHAR = [
    " O ",
    "/|\\",
    "/ \\"
];

const PLAYER_JUMP_CHAR = [
    "\\O/",
    " | ",
    "/ \\"
];

const OBSTACLE_CHARS_EASY = [
    ["###", "###", "###"],
    [" A ", "/|\\", "/_\\"],
    ["[=]", "[=]", "[=]", "[=]"]
];

const BIRD_CHAR = [
    "\\v/",
    " O "
];

const COW_CHAR = [
    " ^__^",
    "(oo) ",
    " \\/ ",
    " || "
];

const HOUSE_CHAR = [
    "  /\\  ",
    " /  \\ ",
    "/    \\",
    "|    |",
    "|  o |",
    "|____|"
];

// Powerup types
const POWERUP_PISTOL = "pistol";
const POWERUP_JETPACK = "jetpack";
const POWERUP_BEANS = "beans";
const POWERUP_ACID = "acid";
const POWERUP_STOPWATCH = "stopwatch";

const POWERUP_CHARS = {
    [POWERUP_PISTOL]: ["[=>"],
    [POWERUP_JETPACK]: ["<J>"],
    [POWERUP_BEANS]: ["{B}"],
    [POWERUP_ACID]: ["<*>"],
    [POWERUP_STOPWATCH]: ["(O)"]
};

const POWERUP_COLORS = {
    [POWERUP_PISTOL]: ORANGE,
    [POWERUP_JETPACK]: CYAN,
    [POWERUP_BEANS]: LIME,
    [POWERUP_ACID]: MAGENTA,
    [POWERUP_STOPWATCH]: YELLOW
};

// Audio context
let audioCtx = null;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function playSquareWave(frequency, duration, volume = 0.3) {
    if (!audioCtx) return;

    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = 'square';
    oscillator.frequency.setValueAtTime(frequency, audioCtx.currentTime);

    gainNode.gain.setValueAtTime(volume, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + duration);
}

function playJumpSound() {
    if (!audioCtx) return;

    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = 'square';
    oscillator.frequency.setValueAtTime(200, audioCtx.currentTime);
    oscillator.frequency.linearRampToValueAtTime(600, audioCtx.currentTime + 0.1);

    gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.1);
}

function playDeathSound() {
    if (!audioCtx) return;

    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = 'square';
    oscillator.frequency.setValueAtTime(400, audioCtx.currentTime);
    oscillator.frequency.linearRampToValueAtTime(100, audioCtx.currentTime + 0.3);

    gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.3);
}

function playShootSound() {
    if (!audioCtx) return;

    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = 'square';
    oscillator.frequency.setValueAtTime(800, audioCtx.currentTime);
    oscillator.frequency.linearRampToValueAtTime(200, audioCtx.currentTime + 0.08);

    gainNode.gain.setValueAtTime(0.25, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.08);
}

function playPickupSound() {
    if (!audioCtx) return;

    [400, 600, 800].forEach((freq, i) => {
        setTimeout(() => playSquareWave(freq, 0.05, 0.3), i * 50);
    });
}

function playFartSound() {
    if (!audioCtx) return;

    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = 'sawtooth';
    oscillator.frequency.setValueAtTime(60, audioCtx.currentTime);

    gainNode.gain.setValueAtTime(0.4, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.4);
}

function playAcidSound() {
    if (!audioCtx) return;

    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = 'square';
    oscillator.frequency.setValueAtTime(300, audioCtx.currentTime);

    // Wobble effect
    const lfo = audioCtx.createOscillator();
    const lfoGain = audioCtx.createGain();
    lfo.frequency.setValueAtTime(8, audioCtx.currentTime);
    lfoGain.gain.setValueAtTime(200, audioCtx.currentTime);
    lfo.connect(lfoGain);
    lfoGain.connect(oscillator.frequency);
    lfo.start();
    lfo.stop(audioCtx.currentTime + 0.5);

    gainNode.gain.setValueAtTime(0.25, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.5);
}

function playStopwatchSound() {
    if (!audioCtx) return;

    // Tick-tock sound
    [800, 600, 800, 600].forEach((freq, i) => {
        setTimeout(() => playSquareWave(freq, 0.05, 0.25), i * 80);
    });
}

// Music system
const MELODY = [
    [262, 0.15], [330, 0.15], [392, 0.15], [523, 0.3],
    [392, 0.15], [330, 0.15], [262, 0.3],
    [294, 0.15], [370, 0.15], [440, 0.15], [587, 0.3],
    [440, 0.15], [370, 0.15], [294, 0.3],
    [330, 0.15], [415, 0.15], [494, 0.15], [659, 0.3],
    [494, 0.15], [415, 0.15], [330, 0.3],
    [392, 0.15], [494, 0.15], [587, 0.15], [784, 0.3],
    [659, 0.15], [587, 0.15], [523, 0.15], [494, 0.3]
];

// Game classes
class Bullet {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.speed = 3;
        this.char = "->";
    }

    update() {
        this.x += this.speed;
    }

    isOffScreen() {
        return this.x >= SCREEN_COLS;
    }
}

class FartPuff {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.life = 15;
        this.chars = ["~", "o", "*", "."];
    }

    update() {
        this.life -= 1;
        this.y += 0.2;
    }

    isDone() {
        return this.life <= 0;
    }

    getChar() {
        const idx = Math.min(3, Math.floor((15 - this.life) / 4));
        return this.chars[idx];
    }
}

class LavaBlob {
    constructor() {
        this.x = Math.floor(Math.random() * SCREEN_COLS);
        this.y = SCREEN_ROWS + Math.floor(Math.random() * 6);
        this.speed = Math.random() * 0.2 + 0.1;
        this.wobble = Math.random() * Math.PI * 2;
        this.wobbleSpeed = Math.random() * 0.1 + 0.05;
        this.size = Math.floor(Math.random() * 3) + 1;
        this.color = PSYCHEDELIC_COLORS[Math.floor(Math.random() * PSYCHEDELIC_COLORS.length)];

        if (this.size === 1) this.char = "o";
        else if (this.size === 2) this.char = "O";
        else this.char = "@";
    }

    update() {
        this.y -= this.speed;
        this.wobble += this.wobbleSpeed;
        this.x += Math.sin(this.wobble) * 0.3;
    }

    isOffScreen() {
        return this.y < -2;
    }
}

class Powerup {
    constructor(x, type) {
        this.x = x;
        this.type = type;
        this.char = POWERUP_CHARS[type];
        this.color = POWERUP_COLORS[type];
        this.height = this.char.length;
        this.width = this.char[0].length;
        this.y = GROUND_HEIGHT - this.height - Math.floor(Math.random() * 9);
    }

    update(scrollSpeed) {
        this.x -= scrollSpeed;
    }

    isOffScreen() {
        return this.x + this.width < 0;
    }
}

class Player {
    constructor() {
        this.x = 10;
        this.y = GROUND_HEIGHT - 3;
        this.velY = 0;
        this.jumpsLeft = MAX_JUMPS;
        this.onGround = true;
        this.jetpackJumps = 0; // Extra jumps from jetpack
        this.hasBeans = false;
        this.beansTimer = 0;
        this.ammo = 0;
        this.acidTimer = 0;
    }

    getMaxJumps() {
        return MAX_JUMPS + (this.jetpackJumps > 0 ? 1 : 0);
    }

    jump() {
        if (this.jumpsLeft > 0) {
            this.velY = JUMP_FORCE;
            this.jumpsLeft -= 1;
            this.onGround = false;
            // Use jetpack jump if we're doing a double jump
            if (!this.onGround && this.jetpackJumps > 0) {
                this.jetpackJumps -= 1;
            }
            return true;
        }
        return false;
    }

    fartJump() {
        this.velY = JUMP_FORCE * 0.8;
        this.onGround = false;
    }

    update() {
        this.velY += GRAVITY;
        this.y += this.velY;

        if (this.y >= GROUND_HEIGHT - 3) {
            this.y = GROUND_HEIGHT - 3;
            this.velY = 0;
            this.jumpsLeft = this.getMaxJumps();
            this.onGround = true;
        }

        if (this.hasBeans) {
            this.beansTimer -= 1;
            if (this.beansTimer <= 0) {
                this.hasBeans = false;
            }
        }

        if (this.acidTimer > 0) {
            this.acidTimer -= 1;
        }
    }

    getChar() {
        return this.onGround ? PLAYER_CHAR : PLAYER_JUMP_CHAR;
    }
}

class Obstacle {
    constructor(x, type = "easy") {
        this.x = x;
        this.obstacleType = type;
        this.flying = false;

        if (type === "easy") {
            this.char = OBSTACLE_CHARS_EASY[Math.floor(Math.random() * OBSTACLE_CHARS_EASY.length)];
        } else if (type === "bird") {
            this.char = BIRD_CHAR;
            this.flying = true;
            this.flyY = Math.floor(Math.random() * 7) + 8;
        } else if (type === "cow") {
            this.char = COW_CHAR;
        } else if (type === "house") {
            this.char = HOUSE_CHAR;
        } else {
            this.char = OBSTACLE_CHARS_EASY[Math.floor(Math.random() * OBSTACLE_CHARS_EASY.length)];
        }

        this.height = this.char.length;
        this.width = Math.max(...this.char.map(row => row.length));

        if (this.flying) {
            this.y = this.flyY;
        } else {
            this.y = GROUND_HEIGHT - this.height;
        }
        this.alive = true;
    }

    update(scrollSpeed) {
        this.x -= scrollSpeed;
        if (this.flying) {
            this.y = this.flyY + Math.sin(this.x * 0.1) * 2;
        }
    }

    isOffScreen() {
        return this.x + this.width < 0;
    }
}

class Game {
    constructor() {
        this.reset();
        this.currentNote = 0;
        this.musicTimer = 0;
        this.highScore = this.loadHighScore();
        this.frame = 0;
    }

    loadHighScore() {
        try {
            const scores = JSON.parse(localStorage.getItem('asciiRunnerHighScores') || '[]');
            return scores.length > 0 ? scores[0].score : 0;
        } catch {
            return 0;
        }
    }

    loadHighScores() {
        try {
            return JSON.parse(localStorage.getItem('asciiRunnerHighScores') || '[]');
        } catch {
            return [];
        }
    }

    saveHighScores(scores) {
        try {
            localStorage.setItem('asciiRunnerHighScores', JSON.stringify(scores));
        } catch {
            // Ignore storage errors
        }
    }

    isHighScore(score) {
        const scores = this.loadHighScores();
        if (scores.length < 5) return true;
        return score > Math.min(...scores.map(s => s.score));
    }

    addHighScore(name, score) {
        const scores = this.loadHighScores();
        scores.push({ name, score });
        scores.sort((a, b) => b.score - a.score);
        const topScores = scores.slice(0, 5);
        this.saveHighScores(topScores);
        return topScores;
    }

    reset() {
        this.player = new Player();
        this.obstacles = [];
        this.powerups = [];
        this.bullets = [];
        this.fartPuffs = [];
        this.lavaBlobs = [];
        this.score = 0;
        this.gameOver = false;
        this.spawnTimer = 0;
        this.spawnDelay = 40;
        this.powerupTimer = 0;
        this.scrollSpeed = BASE_SCROLL_SPEED;
        this.stopwatchTimer = 0;
        this.stopwatchSpeedReduction = 0;
    }

    spawnObstacle() {
        if (this.spawnTimer <= 0) {
            let obstacleType = "easy";

            if (this.score > 500) {
                if (Math.random() < 0.2) {
                    obstacleType = "bird";
                }
            }
            if (this.score > 1000) {
                const r = Math.random();
                if (r < 0.15) {
                    obstacleType = "bird";
                } else if (r < 0.3) {
                    obstacleType = "cow";
                }
            }
            if (this.score > 2000) {
                const r = Math.random();
                if (r < 0.1) {
                    obstacleType = "bird";
                } else if (r < 0.2) {
                    obstacleType = "cow";
                } else if (r < 0.3) {
                    obstacleType = "house";
                }
            }

            this.obstacles.push(new Obstacle(SCREEN_COLS, obstacleType));
            this.spawnTimer = Math.floor(Math.random() * 41) + 20 + Math.floor(Math.random() * 31);
            if (this.spawnDelay > 15) {
                this.spawnDelay -= 0.1;
            }
        } else {
            this.spawnTimer -= 1;
        }
    }

    spawnPowerup() {
        this.powerupTimer -= 1;
        if (this.powerupTimer <= 0) {
            const types = [POWERUP_PISTOL, POWERUP_JETPACK, POWERUP_BEANS, POWERUP_ACID, POWERUP_STOPWATCH];
            const type = types[Math.floor(Math.random() * types.length)];
            this.powerups.push(new Powerup(SCREEN_COLS, type));
            this.powerupTimer = Math.floor(Math.random() * 101) + 80;
        }
    }

    checkCollision() {
        const px = Math.floor(this.player.x);
        const py = Math.floor(this.player.y);
        const playerWidth = 3;
        const playerHeight = 3;

        for (const obs of this.obstacles) {
            if (!obs.alive) continue;
            const ox = Math.floor(obs.x);
            const oy = Math.floor(obs.y);
            if (px < ox + obs.width &&
                px + playerWidth > ox &&
                py < oy + obs.height &&
                py + playerHeight > oy) {
                return true;
            }
        }
        return false;
    }

    checkPowerupCollision() {
        const px = Math.floor(this.player.x);
        const py = Math.floor(this.player.y);
        const playerWidth = 3;
        const playerHeight = 3;

        for (let i = this.powerups.length - 1; i >= 0; i--) {
            const powerup = this.powerups[i];
            const ox = Math.floor(powerup.x);
            const oy = Math.floor(powerup.y);

            if (px < ox + powerup.width &&
                px + playerWidth > ox &&
                py < oy + powerup.height &&
                py + playerHeight > oy) {

                playPickupSound();

                if (powerup.type === POWERUP_JETPACK) {
                    this.player.jetpackJumps += 10;
                    this.player.jumpsLeft = this.player.getMaxJumps();
                } else if (powerup.type === POWERUP_BEANS) {
                    this.player.hasBeans = true;
                    this.player.beansTimer = 600;
                } else if (powerup.type === POWERUP_PISTOL) {
                    this.player.ammo += 10;
                } else if (powerup.type === POWERUP_ACID) {
                    this.player.acidTimer = Math.floor(Math.random() * 301) + 300;
                    playAcidSound();
                } else if (powerup.type === POWERUP_STOPWATCH) {
                    this.stopwatchTimer = 300; // 5 seconds at 60fps
                    this.stopwatchSpeedReduction = this.scrollSpeed * 0.6; // Reduce by 60%
                    playStopwatchSound();
                }

                this.powerups.splice(i, 1);
            }
        }
    }

    checkBulletHits() {
        for (let i = this.bullets.length - 1; i >= 0; i--) {
            const bullet = this.bullets[i];
            const bx = Math.floor(bullet.x);
            const by = Math.floor(bullet.y);

            for (const obs of this.obstacles) {
                if (!obs.alive) continue;
                const ox = Math.floor(obs.x);
                const oy = Math.floor(obs.y);

                if (bx >= ox && bx < ox + obs.width &&
                    by >= oy && by < oy + obs.height) {
                    obs.alive = false;
                    this.bullets.splice(i, 1);
                    break;
                }
            }
        }
    }

    fireWeapon() {
        if (this.player.ammo > 0) {
            this.bullets.push(new Bullet(this.player.x + 3, this.player.y + 1));
            playShootSound();
            this.player.ammo -= 1;
            return true;
        }
        return false;
    }

    update() {
        if (this.gameOver) return;

        this.frame += 1;
        this.player.update();
        this.spawnObstacle();
        this.spawnPowerup();

        // Calculate base scroll speed
        let baseSpeed = BASE_SCROLL_SPEED + (this.score / 1000);

        // Apply stopwatch slowdown
        if (this.stopwatchTimer > 0) {
            this.stopwatchTimer -= 1;
            // Gradually reduce the slowdown effect as timer runs out
            const effectRatio = this.stopwatchTimer / 300;
            this.scrollSpeed = baseSpeed - (this.stopwatchSpeedReduction * effectRatio);
        } else {
            this.scrollSpeed = baseSpeed;
            this.stopwatchSpeedReduction = 0;
        }

        for (const obs of this.obstacles) {
            obs.update(this.scrollSpeed);
        }
        for (const powerup of this.powerups) {
            powerup.update(this.scrollSpeed);
        }
        for (const bullet of this.bullets) {
            bullet.update();
        }
        for (const puff of this.fartPuffs) {
            puff.update();
        }

        // Lava blobs during acid trip
        if (this.player.acidTimer > 0) {
            for (const blob of this.lavaBlobs) {
                blob.update();
            }
            if (Math.random() < 0.15) {
                this.lavaBlobs.push(new LavaBlob());
            }
            this.lavaBlobs = this.lavaBlobs.filter(b => !b.isOffScreen());
        } else {
            this.lavaBlobs = [];
        }

        // Cleanup
        this.obstacles = this.obstacles.filter(obs => !obs.isOffScreen() && obs.alive);
        this.powerups = this.powerups.filter(p => !p.isOffScreen());
        this.bullets = this.bullets.filter(b => !b.isOffScreen());
        this.fartPuffs = this.fartPuffs.filter(p => !p.isDone());

        this.checkPowerupCollision();
        this.checkBulletHits();

        // Random fart from beans
        if (this.player.hasBeans && Math.random() < 0.005) {
            this.player.fartJump();
            playFartSound();
            this.fartPuffs.push(new FartPuff(this.player.x + 1, this.player.y + 3));
        }

        if (this.checkCollision()) {
            this.gameOver = true;
            playDeathSound();
            if (this.score > this.highScore) {
                this.highScore = this.score;
            }
        } else {
            this.score += 1;
        }

        // Music
        this.musicTimer += 1;
        if (this.musicTimer >= 16) {
            const [freq, dur] = MELODY[this.currentNote];
            playSquareWave(freq, dur, 0.2);
            this.currentNote = (this.currentNote + 1) % MELODY.length;
            this.musicTimer = 0;
        }
    }

    getScreenBuffer() {
        const screen = Array(SCREEN_ROWS).fill(null).map(() =>
            Array(SCREEN_COLS).fill(null).map(() => [' ', BLACK])
        );

        // Lava blobs
        for (const blob of this.lavaBlobs) {
            const x = Math.floor(blob.x);
            const y = Math.floor(blob.y);
            if (x >= 0 && x < SCREEN_COLS && y >= 0 && y < SCREEN_ROWS) {
                screen[y][x] = [blob.char, blob.color];
            }
        }

        // Ground
        let groundColor = GREEN;
        if (this.player.acidTimer > 0) {
            groundColor = PSYCHEDELIC_COLORS[Math.floor(Math.random() * PSYCHEDELIC_COLORS.length)];
        }
        for (let x = 0; x < SCREEN_COLS; x++) {
            const char = x % 4 === 0 ? '#' : '=';
            screen[GROUND_HEIGHT][x] = [char, groundColor];
        }

        // Obstacles
        for (const obs of this.obstacles) {
            if (!obs.alive) continue;
            let obsColor = RED;
            if (this.player.acidTimer > 0) {
                obsColor = PSYCHEDELIC_COLORS[Math.floor(Math.random() * PSYCHEDELIC_COLORS.length)];
            }
            for (let i = 0; i < obs.char.length; i++) {
                for (let j = 0; j < obs.char[i].length; j++) {
                    const x = Math.floor(obs.x) + j;
                    const y = Math.floor(obs.y) + i;
                    if (x >= 0 && x < SCREEN_COLS && y >= 0 && y < SCREEN_ROWS) {
                        screen[y][x] = [obs.char[i][j], obsColor];
                    }
                }
            }
        }

        // Powerups
        for (const powerup of this.powerups) {
            for (let i = 0; i < powerup.char.length; i++) {
                for (let j = 0; j < powerup.char[i].length; j++) {
                    const x = Math.floor(powerup.x) + j;
                    const y = Math.floor(powerup.y) + i;
                    if (x >= 0 && x < SCREEN_COLS && y >= 0 && y < SCREEN_ROWS) {
                        screen[y][x] = [powerup.char[i][j], powerup.color];
                    }
                }
            }
        }

        // Fart puffs
        for (const puff of this.fartPuffs) {
            const x = Math.floor(puff.x);
            const y = Math.floor(puff.y);
            if (x >= 0 && x < SCREEN_COLS && y >= 0 && y < SCREEN_ROWS) {
                screen[y][x] = [puff.getChar(), LIME];
            }
        }

        // Bullets
        for (const bullet of this.bullets) {
            const x = Math.floor(bullet.x);
            const y = Math.floor(bullet.y);
            for (let i = 0; i < bullet.char.length; i++) {
                if (x + i >= 0 && x + i < SCREEN_COLS && y >= 0 && y < SCREEN_ROWS) {
                    screen[y][x + i] = [bullet.char[i], ORANGE];
                }
            }
        }

        // Player
        let playerColor = CYAN;
        if (this.player.acidTimer > 0) {
            playerColor = PSYCHEDELIC_COLORS[this.frame % PSYCHEDELIC_COLORS.length];
        }
        const playerChar = this.player.getChar();
        for (let i = 0; i < playerChar.length; i++) {
            for (let j = 0; j < playerChar[i].length; j++) {
                const x = Math.floor(this.player.x) + j;
                const y = Math.floor(this.player.y) + i;
                if (x >= 0 && x < SCREEN_COLS && y >= 0 && y < SCREEN_ROWS && playerChar[i][j] !== ' ') {
                    screen[y][x] = [playerChar[i][j], playerColor];
                }
            }
        }

        return screen;
    }
}

// Renderer
class GameRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.canvas.width = SCREEN_WIDTH;
        this.canvas.height = SCREEN_HEIGHT;
        this.ctx.font = '14px Consolas, "Courier New", monospace';
    }

    clear() {
        this.ctx.fillStyle = BLACK;
        this.ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
    }

    renderBuffer(buffer) {
        for (let y = 0; y < buffer.length; y++) {
            for (let x = 0; x < buffer[y].length; x++) {
                const [char, color] = buffer[y][x];
                if (char !== ' ' || color !== BLACK) {
                    this.ctx.fillStyle = color === BLACK ? GREEN : color;
                    this.ctx.fillText(char, x * CHAR_WIDTH, y * CHAR_HEIGHT + 14);
                }
            }
        }
    }

    renderHUD(game) {
        // Score
        this.ctx.fillStyle = YELLOW;
        this.ctx.fillText(`Score: ${game.score}`, SCREEN_WIDTH - 120, 15);

        // Jumps
        this.ctx.fillStyle = WHITE;
        this.ctx.fillText(`Jumps: ${'*'.repeat(game.player.jumpsLeft)}`, SCREEN_WIDTH - 120, 33);

        // Powerups
        let yOffset = 15;

        if (game.player.ammo > 0) {
            this.ctx.fillStyle = ORANGE;
            this.ctx.fillText(`[=> x${game.player.ammo}`, 10, yOffset);
            yOffset += 18;
        }

        if (game.player.jetpackJumps > 0) {
            this.ctx.fillStyle = CYAN;
            this.ctx.fillText(`<J> x${game.player.jetpackJumps}`, 10, yOffset);
            yOffset += 18;
        }

        if (game.player.hasBeans) {
            this.ctx.fillStyle = LIME;
            const secs = Math.floor(game.player.beansTimer / 60);
            this.ctx.fillText(`{B} ${secs}s`, 10, yOffset);
            yOffset += 18;
        }

        if (game.player.acidTimer > 0) {
            this.ctx.fillStyle = MAGENTA;
            const secs = Math.floor(game.player.acidTimer / 60);
            this.ctx.fillText(`<*> ${secs}s`, 10, yOffset);
            yOffset += 18;
        }

        if (game.stopwatchTimer > 0) {
            this.ctx.fillStyle = YELLOW;
            const secs = Math.floor(game.stopwatchTimer / 60);
            this.ctx.fillText(`(O) ${secs}s`, 10, yOffset);
        }
    }

    renderIntro(highScores) {
        this.clear();

        // Title
        const titleLines = [
            "    ___   _____ ______________   ____  __  ___   ___   ______________",
            "   /   | / ___// ____/  _/  _/  / __ \\/ / / / | / / | / / ____/ __ \\",
            "  / /| | \\__ \\/ /    / / / /   / /_/ / / / /  |/ /  |/ / __/ / /_/ /",
            " / ___ |___/ / /____/ /_/ /   / _, _/ /_/ / /|  / /|  / /___/ _, _/ ",
            "/_/  |_/____/\\____/___/___/  /_/ |_|\\____/_/ |_/_/ |_/_____/_/ |_|  "
        ];

        const colors = [CYAN, MAGENTA, YELLOW, GREEN, CYAN];
        titleLines.forEach((line, i) => {
            this.ctx.fillStyle = colors[i];
            this.ctx.fillText(line, 0, (i + 2) * CHAR_HEIGHT);
        });

        // Controls
        const controls = [
            "+-----------------------------------+",
            "|     PRESS  SPACE  TO  START       |",
            "|                                   |",
            "|   [SPACE] - Jump & Shoot          |",
            "|   [ESC]   - Quit                  |",
            "+-----------------------------------+"
        ];

        this.ctx.fillStyle = GREEN;
        controls.forEach((line, i) => {
            this.ctx.fillText(line, 50, (8 + i) * CHAR_HEIGHT);
        });

        // Powerups info
        const powerups = [
            "POWERUPS (run into to collect):",
            "[=> Gun (10 shots)  <J> Jetpack (10)",
            "{B} Beans (farts!)  <*> Acid Trip",
            "(O) Stopwatch (slow time)"
        ];

        powerups.forEach((line, i) => {
            this.ctx.fillStyle = i === 0 ? ORANGE : WHITE;
            this.ctx.fillText(line, 50, (15 + i) * CHAR_HEIGHT);
        });

        // High scores
        this.ctx.fillStyle = YELLOW;
        this.ctx.fillText("HIGH SCORES:", 500, 19 * CHAR_HEIGHT);

        if (highScores.length > 0) {
            highScores.slice(0, 5).forEach((hs, i) => {
                this.ctx.fillStyle = WHITE;
                const text = `${i + 1}. ${hs.name.padEnd(5)} ${String(hs.score).padStart(6)}`;
                this.ctx.fillText(text, 500, (20 + i) * CHAR_HEIGHT);
            });
        } else {
            this.ctx.fillStyle = WHITE;
            this.ctx.fillText("No scores yet!", 500, 20 * CHAR_HEIGHT);
        }
    }

    renderGameOver(score, highScore) {
        const lines = [
            "              +-----------------------------------+",
            "              |                                   |",
            "              |          GAME  OVER!              |",
            "              |                                   |",
            `              |      Score: ${String(score).padStart(6)}                |`,
            `              |      High:  ${String(highScore).padStart(6)}                |`,
            "              |                                   |",
            "              |   [SPACE] - Play Again            |",
            "              |   [ESC]   - Quit                  |",
            "              |                                   |",
            "              +-----------------------------------+"
        ];

        this.ctx.fillStyle = RED;
        lines.forEach((line, i) => {
            this.ctx.fillText(line, 0, (6 + i) * CHAR_HEIGHT);
        });
    }
}

// Main game controller
class GameController {
    constructor() {
        // Detect mobile
        this.isMobile = this.detectMobile();

        // Select appropriate canvas
        if (this.isMobile) {
            this.canvas = document.getElementById('mobileGameCanvas');
            this.setupMobileCanvas();
        } else {
            this.canvas = document.getElementById('gameCanvas');
        }

        this.renderer = new GameRenderer(this.canvas);
        this.game = new Game();
        this.state = 'intro'; // intro, playing, gameover, highscore
        this.scoreEntered = false;
        this.playerName = '';

        // Fixed timestep for smooth gameplay
        this.targetFPS = 60;
        this.frameTime = 1000 / this.targetFPS;
        this.lastTime = 0;
        this.accumulator = 0;

        this.setupInput();

        // Handle resize for mobile
        if (this.isMobile) {
            window.addEventListener('resize', () => this.setupMobileCanvas());
            window.addEventListener('orientationchange', () => {
                setTimeout(() => this.setupMobileCanvas(), 100);
            });
        }

        this.gameLoop(0);
    }

    detectMobile() {
        return (('ontouchstart' in window) ||
                (navigator.maxTouchPoints > 0) ||
                (navigator.msMaxTouchPoints > 0)) &&
               (window.matchMedia('(hover: none) and (pointer: coarse)').matches);
    }

    setupMobileCanvas() {
        const container = document.getElementById('mobile-game-container');
        const width = window.innerWidth;
        const height = window.innerHeight;

        // Calculate scale to fill screen while maintaining aspect ratio
        const gameAspect = SCREEN_WIDTH / SCREEN_HEIGHT;
        const screenAspect = width / height;

        let canvasWidth, canvasHeight;

        if (screenAspect > gameAspect) {
            // Screen is wider than game - fit to height
            canvasHeight = height;
            canvasWidth = height * gameAspect;
        } else {
            // Screen is taller than game - fit to width
            canvasWidth = width;
            canvasHeight = width / gameAspect;
        }

        // Set canvas internal resolution
        this.canvas.width = SCREEN_WIDTH;
        this.canvas.height = SCREEN_HEIGHT;

        // Set canvas display size to fill screen
        this.canvas.style.width = canvasWidth + 'px';
        this.canvas.style.height = canvasHeight + 'px';
        this.canvas.style.position = 'absolute';
        this.canvas.style.left = ((width - canvasWidth) / 2) + 'px';
        this.canvas.style.top = ((height - canvasHeight) / 2) + 'px';
    }

    setupInput() {
        document.addEventListener('keydown', (e) => {
            initAudio();

            if (e.code === 'Space') {
                e.preventDefault();

                if (this.state === 'intro') {
                    this.state = 'playing';
                    this.game.reset();
                } else if (this.state === 'playing') {
                    this.game.fireWeapon();
                    if (this.game.player.jump()) {
                        playJumpSound();
                    }
                } else if (this.state === 'gameover') {
                    this.state = 'playing';
                    this.game.reset();
                    this.scoreEntered = false;
                } else if (this.state === 'highscore') {
                    if (this.playerName.length > 0) {
                        this.game.addHighScore(this.playerName.toUpperCase().padEnd(5).slice(0, 5), this.game.score);
                        this.state = 'gameover';
                        this.scoreEntered = true;
                    }
                }
            } else if (e.code === 'Escape') {
                if (this.state === 'playing' || this.state === 'gameover') {
                    this.state = 'intro';
                    this.game.reset();
                }
            } else if (this.state === 'highscore') {
                if (e.code === 'Backspace') {
                    this.playerName = this.playerName.slice(0, -1);
                } else if (e.code === 'Enter' && this.playerName.length > 0) {
                    this.game.addHighScore(this.playerName.toUpperCase().padEnd(5).slice(0, 5), this.game.score);
                    this.state = 'gameover';
                    this.scoreEntered = true;
                } else if (e.key.length === 1 && this.playerName.length < 5 && /[a-zA-Z0-9]/.test(e.key)) {
                    this.playerName += e.key.toUpperCase();
                }
            }
        });

        // Touch support
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            initAudio();

            if (this.state === 'intro') {
                this.state = 'playing';
                this.game.reset();
            } else if (this.state === 'playing') {
                this.game.fireWeapon();
                if (this.game.player.jump()) {
                    playJumpSound();
                }
            } else if (this.state === 'gameover') {
                this.state = 'playing';
                this.game.reset();
                this.scoreEntered = false;
            }
        });
    }

    renderHighScoreEntry() {
        this.renderer.clear();

        this.renderer.ctx.fillStyle = YELLOW;
        this.renderer.ctx.fillText("NEW HIGH SCORE!", SCREEN_WIDTH / 2 - 80, 100);

        this.renderer.ctx.fillStyle = GREEN;
        this.renderer.ctx.fillText(`Score: ${this.game.score}`, SCREEN_WIDTH / 2 - 50, 150);

        this.renderer.ctx.fillStyle = WHITE;
        this.renderer.ctx.fillText("Enter your name (5 chars):", SCREEN_WIDTH / 2 - 120, 220);

        this.renderer.ctx.fillStyle = CYAN;
        const displayName = this.playerName + '_'.repeat(5 - this.playerName.length);
        this.renderer.ctx.fillText(displayName, SCREEN_WIDTH / 2 - 25, 260);

        this.renderer.ctx.fillStyle = WHITE;
        this.renderer.ctx.fillText("Press ENTER when done", SCREEN_WIDTH / 2 - 100, 320);
    }

    gameLoop(currentTime) {
        // Initialize lastTime on first frame
        if (this.lastTime === 0) {
            this.lastTime = currentTime;
        }

        const deltaTime = currentTime - this.lastTime;
        this.lastTime = currentTime;

        // Prevent spiral of death - cap to max 2 frames worth
        const cappedDelta = Math.min(deltaTime, this.frameTime * 2);
        this.accumulator += cappedDelta;

        if (this.state === 'intro') {
            this.renderer.renderIntro(this.game.loadHighScores());
        } else if (this.state === 'playing') {
            // Fixed timestep updates
            while (this.accumulator >= this.frameTime) {
                this.game.update();
                this.accumulator -= this.frameTime;

                if (this.game.gameOver && !this.scoreEntered) {
                    if (this.game.isHighScore(this.game.score)) {
                        this.state = 'highscore';
                        this.playerName = '';
                    } else {
                        this.state = 'gameover';
                        this.scoreEntered = true;
                    }
                    break;
                }
            }

            this.renderer.clear();
            this.renderer.renderBuffer(this.game.getScreenBuffer());
            this.renderer.renderHUD(this.game);
        } else if (this.state === 'gameover') {
            this.renderer.clear();
            this.renderer.renderBuffer(this.game.getScreenBuffer());
            this.renderer.renderHUD(this.game);
            this.renderer.renderGameOver(this.game.score, this.game.highScore);
        } else if (this.state === 'highscore') {
            this.renderHighScoreEntry();
        }

        requestAnimationFrame((time) => this.gameLoop(time));
    }
}

// Start game when page loads
window.addEventListener('load', () => {
    new GameController();
});
