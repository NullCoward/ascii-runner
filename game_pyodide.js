// ASCII Runner - Pyodide Web Version
// Uses Python game_engine via Pyodide - single source of truth

let pyodide = null;
let gameEngine = null;
let canvas = null;
let ctx = null;
let animationId = null;
let audioContext = null;

// Game state
let gameState = 'loading'; // loading, intro, playing, gameover, highscore
let highScores = [];
let playerName = '';
let scoreEntered = false;

const CHAR_WIDTH = 10;
const CHAR_HEIGHT = 18;
const SCREEN_COLS = 80;
const SCREEN_ROWS = 25;
const SCREEN_WIDTH = SCREEN_COLS * CHAR_WIDTH;
const SCREEN_HEIGHT = SCREEN_ROWS * CHAR_HEIGHT;

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

// Sound generation
function createOscillator(frequency, duration, type = 'square', volume = 0.3) {
    if (!audioContext) return;

    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.type = type;
    oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);

    gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.start();
    oscillator.stop(audioContext.currentTime + duration);
}

function playJumpSound() {
    if (!audioContext) return;
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            createOscillator(200 + i * 100, 0.02, 'square', 0.2);
        }, i * 20);
    }
}

function playDeathSound() {
    if (!audioContext) return;
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            createOscillator(400 - i * 60, 0.06, 'square', 0.3);
        }, i * 60);
    }
}

function playShootSound() {
    createOscillator(800, 0.05, 'square', 0.2);
    setTimeout(() => createOscillator(400, 0.03, 'square', 0.15), 30);
}

function playPickupSound() {
    createOscillator(400, 0.05, 'square', 0.2);
    setTimeout(() => createOscillator(600, 0.05, 'square', 0.2), 50);
    setTimeout(() => createOscillator(800, 0.05, 'square', 0.2), 100);
}

function playFartSound() {
    if (!audioContext) return;
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.type = 'sawtooth';
    oscillator.frequency.setValueAtTime(60, audioContext.currentTime);
    oscillator.frequency.linearRampToValueAtTime(40, audioContext.currentTime + 0.3);

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.3);
}

function playAcidSound() {
    if (!audioContext) return;
    for (let i = 0; i < 8; i++) {
        setTimeout(() => {
            const freq = 300 + Math.sin(i * 0.8) * 200;
            createOscillator(freq, 0.06, 'square', 0.2);
        }, i * 60);
    }
}

function playStopwatchSound() {
    if (!audioContext) return;
    [800, 600, 800, 600].forEach((freq, i) => {
        setTimeout(() => createOscillator(freq, 0.05, 'square', 0.25), i * 80);
    });
}

function playStompSound() {
    if (!audioContext) return;
    // Satisfying "boing" sound for stomping enemies
    createOscillator(150, 0.08, 'square', 0.3);
    setTimeout(() => createOscillator(300, 0.1, 'square', 0.25), 50);
}

// Music
let musicTimer = 0;
let currentNote = 0;
const melody = [
    [262, 0.15], [330, 0.15], [392, 0.15], [523, 0.3],
    [392, 0.15], [330, 0.15], [262, 0.3],
    [294, 0.15], [370, 0.15], [440, 0.15], [587, 0.3],
    [440, 0.15], [370, 0.15], [294, 0.3],
    [330, 0.15], [415, 0.15], [494, 0.15], [659, 0.3],
    [494, 0.15], [415, 0.15], [330, 0.3],
    [392, 0.15], [494, 0.15], [587, 0.15], [784, 0.3],
    [659, 0.15], [587, 0.15], [523, 0.15], [494, 0.3]
];

function playMusic() {
    if (!audioContext) return;
    musicTimer++;
    if (musicTimer >= 16) {
        const [freq, dur] = melody[currentNote];
        createOscillator(freq, dur, 'square', 0.15);
        currentNote = (currentNote + 1) % melody.length;
        musicTimer = 0;
    }
}

// High score management
function loadHighScores() {
    try {
        highScores = JSON.parse(localStorage.getItem('asciiRunnerHighScores') || '[]');
    } catch {
        highScores = [];
    }
    return highScores;
}

function saveHighScores() {
    try {
        localStorage.setItem('asciiRunnerHighScores', JSON.stringify(highScores));
    } catch {
        // Ignore storage errors
    }
}

function isHighScore(score) {
    if (highScores.length < 5) return true;
    return score > Math.min(...highScores.map(s => s.score));
}

function addHighScore(name, score) {
    highScores.push({ name: name.toUpperCase(), score });
    highScores.sort((a, b) => b.score - a.score);
    highScores = highScores.slice(0, 5);
    saveHighScores();

    // Update engine high score
    if (gameEngine && score > gameEngine.high_score) {
        gameEngine.high_score = score;
    }
}

// Initialize Pyodide and game engine
async function initGame() {
    // Show loading message
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading';
    loadingDiv.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);color:#0f0;font-family:monospace;font-size:20px;text-align:center;z-index:9999;background:#000;padding:20px;border:2px solid #0f0;';
    loadingDiv.innerHTML = 'Loading Pyodide...<br><span style="font-size:12px;color:#666;">First load may take a moment</span>';
    document.body.appendChild(loadingDiv);

    try {
        // Check if Pyodide script loaded
        if (typeof loadPyodide === 'undefined') {
            throw new Error('Pyodide script failed to load. Check your internet connection.');
        }

        // Load Pyodide with timeout
        loadingDiv.innerHTML = 'Loading Python runtime...<br><span style="font-size:12px;color:#666;">This may take 30-60 seconds on mobile</span>';

        const pyodidePromise = loadPyodide();
        const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Pyodide load timeout (60s)')), 60000)
        );

        pyodide = await Promise.race([pyodidePromise, timeoutPromise]);
        loadingDiv.innerHTML = 'Loading game engine...';

        // Fetch and load game_engine.py
        const response = await fetch('game_engine.py');
        if (!response.ok) {
            throw new Error(`Failed to fetch game_engine.py: ${response.status}`);
        }
        const engineCode = await response.text();

        // Run the engine code
        loadingDiv.innerHTML = 'Initializing game...';
        await pyodide.runPythonAsync(engineCode);

        // Create game instance
        await pyodide.runPythonAsync(`game = GameEngine()`);

        gameEngine = pyodide.globals.get('game');

        if (!gameEngine) {
            throw new Error('Failed to create game engine instance');
        }

        // Load high scores
        loadHighScores();

        // Set high score in engine
        if (highScores.length > 0) {
            gameEngine.high_score = highScores[0].score;
        }

        // Remove loading message
        loadingDiv.remove();

        // Setup canvas
        setupCanvas();

        // Setup input
        setupInput();

        // Go to intro
        gameState = 'intro';

        // Start game loop
        requestAnimationFrame(gameLoop);

    } catch (error) {
        console.error('Failed to initialize game:', error);
        loadingDiv.style.color = '#f00';
        loadingDiv.innerHTML = `<strong>Error loading game:</strong><br><br>${error.message}<br><br><span style="font-size:12px;color:#888;">Try refreshing the page.<br>Pyodide requires ~40MB download on first load.</span>`;
    }
}

function initAudio() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function setupCanvas() {
    // Always use the fullscreen mobile canvas for better scaling
    canvas = document.getElementById('mobileGameCanvas');

    // Hide TV container, show fullscreen
    const tvContainer = document.querySelector('.tv-container');
    const mobileContainer = document.getElementById('mobile-game-container');
    const instructions = document.querySelector('.instructions');

    if (tvContainer) tvContainer.style.display = 'none';
    if (mobileContainer) mobileContainer.style.display = 'block';
    if (instructions) instructions.style.display = 'none';

    canvas.width = SCREEN_WIDTH;
    canvas.height = SCREEN_HEIGHT;

    // Scale to fit window
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    ctx = canvas.getContext('2d');
    ctx.font = '14px Consolas, "Courier New", monospace';
    ctx.textBaseline = 'top';
}

function resizeCanvas() {
    const width = window.innerWidth;
    const height = window.innerHeight;

    const gameAspect = SCREEN_WIDTH / SCREEN_HEIGHT;
    const screenAspect = width / height;

    let canvasWidth, canvasHeight;

    if (screenAspect > gameAspect) {
        canvasHeight = height;
        canvasWidth = height * gameAspect;
    } else {
        canvasWidth = width;
        canvasHeight = width / gameAspect;
    }

    canvas.style.width = canvasWidth + 'px';
    canvas.style.height = canvasHeight + 'px';
    canvas.style.position = 'absolute';
    canvas.style.left = ((width - canvasWidth) / 2) + 'px';
    canvas.style.top = ((height - canvasHeight) / 2) + 'px';
}

function setupInput() {
    document.addEventListener('keydown', (e) => {
        initAudio();

        if (e.code === 'Space') {
            e.preventDefault();
            handleAction();
        } else if (e.code === 'Escape') {
            if (gameState === 'playing' || gameState === 'gameover') {
                gameState = 'intro';
                gameEngine.reset();
                scoreEntered = false;
                playerName = '';
            }
        } else if (gameState === 'highscore') {
            // Name entry
            if (e.code === 'Enter' || e.code === 'NumpadEnter') {
                if (playerName.length > 0) {
                    const stateProxy = gameEngine.get_state();
                    const state = stateProxy.toJs({dict_converter: Object.fromEntries});
                    addHighScore(playerName, state.score);
                    gameState = 'gameover';
                    scoreEntered = true;
                }
            } else if (e.code === 'Backspace') {
                playerName = playerName.slice(0, -1);
            } else if (e.key.length === 1 && playerName.length < 5) {
                const char = e.key.toUpperCase();
                if (/[A-Z0-9]/.test(char)) {
                    playerName += char;
                }
            }
        }
    });

    // Touch controls
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault();
        initAudio();

        // Request fullscreen on mobile
        if (!document.fullscreenElement) {
            const elem = document.documentElement;
            if (elem.requestFullscreen) {
                elem.requestFullscreen().catch(() => {});
            }
        }

        handleAction();
    });
}

function handleAction() {
    if (gameState === 'intro') {
        gameState = 'playing';
        gameEngine.reset();
        scoreEntered = false;
        playerName = '';
    } else if (gameState === 'playing') {
        // Fire weapon
        const fired = gameEngine.fire_weapon();
        if (fired) playShootSound();

        // Jump
        const jumped = gameEngine.player.jump();
        if (jumped) playJumpSound();
    } else if (gameState === 'gameover') {
        gameState = 'playing';
        gameEngine.reset();
        scoreEntered = false;
        playerName = '';
    } else if (gameState === 'highscore') {
        // Touch to submit name if we have one
        if (playerName.length > 0) {
            const stateProxy = gameEngine.get_state();
            const state = stateProxy.toJs({dict_converter: Object.fromEntries});
            addHighScore(playerName, state.score);
            gameState = 'gameover';
            scoreEntered = true;
        }
    }
}

// Convert Python color tuple to CSS
function colorToCSS(color) {
    if (!color) return '#000';
    // Handle both array and proxy access
    const r = color[0] !== undefined ? color[0] : (color.get ? color.get(0) : 0);
    const g = color[1] !== undefined ? color[1] : (color.get ? color.get(1) : 0);
    const b = color[2] !== undefined ? color[2] : (color.get ? color.get(2) : 0);
    return `rgb(${r},${g},${b})`;
}

let lastDied = false;
let frame = 0;

function gameLoop() {
    try {
        frame++;

        if (gameState === 'intro') {
            renderIntro();
            playMusic();
        } else if (gameState === 'playing') {
            // Update game - convert Pyodide proxy to JS object
            const eventsProxy = gameEngine.update();
            const events = eventsProxy.toJs({dict_converter: Object.fromEntries});

            // Play sounds based on events
            if (events.died && !lastDied) {
                playDeathSound();

                // Check for high score
                const stateProxy = gameEngine.get_state();
                const state = stateProxy.toJs({dict_converter: Object.fromEntries});
                if (isHighScore(state.score)) {
                    gameState = 'highscore';
                } else {
                    gameState = 'gameover';
                    scoreEntered = true;
                }
            }
            lastDied = events.died || false;

            if (events.farted) {
                playFartSound();
            }

            if (events.stomped) {
                playStompSound();
            }

            const collected = events.collected || [];
            for (const powerupType of collected) {
                playPickupSound();
                if (powerupType === 'acid') {
                    playAcidSound();
                } else if (powerupType === 'stopwatch') {
                    playStopwatchSound();
                }
            }

            // Play music
            playMusic();

            // Render game
            renderGame();
        } else if (gameState === 'gameover') {
            renderGameOver();
        } else if (gameState === 'highscore') {
            renderHighScoreEntry();
        }

        animationId = requestAnimationFrame(gameLoop);
    } catch (error) {
        console.error('Game loop error:', error);
        // Display error on screen
        ctx.fillStyle = '#f00';
        ctx.font = '14px monospace';
        ctx.fillText('Error: ' + error.message, 10, 50);
        // Continue trying to run
        animationId = requestAnimationFrame(gameLoop);
    }
}

function renderIntro() {
    ctx.fillStyle = BLACK;
    ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

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
        ctx.fillStyle = colors[i];
        ctx.fillText(line, 50, (i + 2) * CHAR_HEIGHT);
    });

    // Controls box
    const controls = [
        "+-----------------------------------+",
        "|     PRESS  SPACE  TO  START       |",
        "|                                   |",
        "|   [SPACE] - Jump & Shoot          |",
        "|   [ESC]   - Quit                  |",
        "+-----------------------------------+"
    ];

    ctx.fillStyle = GREEN;
    controls.forEach((line, i) => {
        ctx.fillText(line, 100, (8 + i) * CHAR_HEIGHT);
    });

    // Powerups info
    const powerups = [
        "POWERUPS (run into to collect):",
        "[=> Gun (10 shots)  <J> Jetpack (10)",
        "{B} Beans (farts!)  <*> Acid Trip",
        "(O) Stopwatch (slow time)"
    ];

    powerups.forEach((line, i) => {
        ctx.fillStyle = i === 0 ? ORANGE : WHITE;
        ctx.fillText(line, 100, (15 + i) * CHAR_HEIGHT);
    });

    // High scores
    ctx.fillStyle = YELLOW;
    ctx.fillText("HIGH SCORES:", 500, 8 * CHAR_HEIGHT);

    if (highScores.length > 0) {
        highScores.slice(0, 5).forEach((hs, i) => {
            ctx.fillStyle = WHITE;
            const text = `${i + 1}. ${hs.name.padEnd(5)} ${String(hs.score).padStart(6)}`;
            ctx.fillText(text, 500, (9 + i) * CHAR_HEIGHT);
        });
    } else {
        ctx.fillStyle = WHITE;
        ctx.fillText("No scores yet!", 500, 9 * CHAR_HEIGHT);
    }

    // Blinking prompt
    if (Math.floor(frame / 30) % 2 === 0) {
        ctx.fillStyle = CYAN;
        ctx.fillText(">>> PRESS SPACE <<<", 280, 22 * CHAR_HEIGHT);
    }
}

// Font sizes for different depths (parallax effect)
const DEPTH_FONTS = {
    0: '8px Consolas, "Courier New", monospace',   // Far background - smallest
    1: '10px Consolas, "Courier New", monospace',  // Mid background
    2: '14px Consolas, "Courier New", monospace'   // Foreground - largest
};

// Y offsets to align different font sizes to same baseline
const DEPTH_Y_OFFSET = {
    0: 2,  // Smaller font needs less offset
    1: 1,
    2: 0
};

function renderGame() {
    // Clear screen
    ctx.fillStyle = BLACK;
    ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

    // Get screen buffer from Python engine
    const bufferProxy = gameEngine.get_screen_buffer();
    const buffer = bufferProxy.toJs();

    // Draw buffer with depth-based font sizes
    for (let y = 0; y < buffer.length; y++) {
        const row = buffer[y];
        for (let x = 0; x < row.length; x++) {
            const cell = row[x];
            // Handle both array and proxy access
            const char = cell[0] || cell.get(0);
            const color = cell[1] || cell.get(1);
            const depth = (cell[2] !== undefined ? cell[2] : (cell.get ? cell.get(2) : 2)) || 2;

            if (char && char !== ' ') {
                ctx.font = DEPTH_FONTS[depth] || DEPTH_FONTS[2];
                ctx.fillStyle = colorToCSS(color);
                const yPos = y * CHAR_HEIGHT + (DEPTH_Y_OFFSET[depth] || 0);
                ctx.fillText(char, x * CHAR_WIDTH, yPos);
            }
        }
    }

    // Reset font to default for HUD
    ctx.font = '14px Consolas, "Courier New", monospace';

    // Draw HUD
    const stateProxy = gameEngine.get_state();
    const state = stateProxy.toJs({dict_converter: Object.fromEntries});

    // Score
    ctx.fillStyle = YELLOW;
    ctx.fillText(`Score: ${state.score}`, SCREEN_WIDTH - 120, 5);

    // Jumps with asterisks
    const jumpsLeft = state.player.jumps_left;
    const maxJumps = state.player.jetpack_jumps > 0 ? 2 : 1;
    ctx.fillStyle = WHITE;
    ctx.fillText(`Jumps: ${'*'.repeat(jumpsLeft)}${'-'.repeat(maxJumps - jumpsLeft)}`, SCREEN_WIDTH - 120, 23);

    // Power-up indicators
    let yOffset = 5;

    if (state.player.ammo > 0) {
        ctx.fillStyle = ORANGE;
        ctx.fillText(`[=> x${state.player.ammo}`, 10, yOffset);
        yOffset += 18;
    }

    if (state.player.jetpack_jumps > 0) {
        ctx.fillStyle = CYAN;
        ctx.fillText(`<J> x${state.player.jetpack_jumps}`, 10, yOffset);
        yOffset += 18;
    }

    if (state.player.has_beans) {
        const secs = Math.floor(state.player.beans_timer / 60);
        ctx.fillStyle = LIME;
        ctx.fillText(`{B} ${secs}s`, 10, yOffset);
        yOffset += 18;
    }

    if (state.player.acid_timer > 0) {
        const secs = Math.floor(state.player.acid_timer / 60);
        const acidLevel = state.player.acid_level;

        if (acidLevel === 3) {
            ctx.fillStyle = PSYCHEDELIC_COLORS[Math.floor(frame / 5) % PSYCHEDELIC_COLORS.length];
            ctx.fillText(`NIRVANA ${secs}s`, 10, yOffset);
        } else if (acidLevel === 2) {
            ctx.fillStyle = YELLOW;
            ctx.fillText(`TRIPPY ${secs}s`, 10, yOffset);
        } else {
            ctx.fillStyle = MAGENTA;
            ctx.fillText(`<*> ${secs}s`, 10, yOffset);
        }
        yOffset += 18;
    }

    if (state.stopwatch_timer > 0) {
        const secs = Math.floor(state.stopwatch_timer / 60);
        ctx.fillStyle = YELLOW;
        ctx.fillText(`(O) ${secs}s`, 10, yOffset);
        yOffset += 18;
    }

    // Grace period indicator (post-nirvana invulnerability)
    if (state.player.grace_period > 0) {
        const secs = (state.player.grace_period / 60).toFixed(1);
        // Flashing effect
        if (Math.floor(frame / 4) % 2 === 0) {
            ctx.fillStyle = WHITE;
            ctx.fillText(`PROTECTED ${secs}s`, 10, yOffset);
        }
    }
}

function renderGameOver() {
    // Clear screen
    ctx.fillStyle = BLACK;
    ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

    // Get game over buffer from Python engine
    const bufferProxy = gameEngine.get_game_over_buffer();
    const buffer = bufferProxy.toJs();

    // Draw buffer with depth-based font sizes
    for (let y = 0; y < buffer.length; y++) {
        const row = buffer[y];
        for (let x = 0; x < row.length; x++) {
            const cell = row[x];
            // Handle both array and proxy access
            const char = cell[0] || cell.get(0);
            const color = cell[1] || cell.get(1);
            const depth = (cell[2] !== undefined ? cell[2] : (cell.get ? cell.get(2) : 2)) || 2;

            if (char && char !== ' ') {
                ctx.font = DEPTH_FONTS[depth] || DEPTH_FONTS[2];
                ctx.fillStyle = colorToCSS(color);
                const yPos = y * CHAR_HEIGHT + (DEPTH_Y_OFFSET[depth] || 0);
                ctx.fillText(char, x * CHAR_WIDTH, yPos);
            }
        }
    }
}

function renderHighScoreEntry() {
    ctx.fillStyle = BLACK;
    ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

    const stateProxy = gameEngine.get_state();
    const state = stateProxy.toJs({dict_converter: Object.fromEntries});

    // Title
    ctx.fillStyle = YELLOW;
    ctx.font = '28px Consolas, monospace';
    ctx.fillText("NEW HIGH SCORE!", SCREEN_WIDTH / 2 - 130, 80);

    // Score
    ctx.fillStyle = GREEN;
    ctx.font = '20px Consolas, monospace';
    ctx.fillText(`Score: ${state.score}`, SCREEN_WIDTH / 2 - 60, 140);

    // Prompt
    ctx.fillStyle = WHITE;
    ctx.font = '14px Consolas, monospace';
    ctx.fillText("Enter your name (5 chars max):", SCREEN_WIDTH / 2 - 130, 200);

    // Name entry box
    ctx.strokeStyle = CYAN;
    ctx.lineWidth = 2;
    ctx.strokeRect(SCREEN_WIDTH / 2 - 60, 230, 120, 40);

    // Name with cursor
    const displayName = playerName + (Math.floor(frame / 15) % 2 === 0 ? '_' : ' ');
    ctx.fillStyle = CYAN;
    ctx.font = '24px Consolas, monospace';
    ctx.fillText(displayName.padEnd(6), SCREEN_WIDTH / 2 - 50, 240);

    // Instructions
    ctx.fillStyle = WHITE;
    ctx.font = '14px Consolas, monospace';
    ctx.fillText("Type name, then press ENTER", SCREEN_WIDTH / 2 - 120, 300);
    ctx.fillText("(or TAP on mobile)", SCREEN_WIDTH / 2 - 80, 320);

    // Show current high scores
    ctx.fillStyle = YELLOW;
    ctx.fillText("Current Top Scores:", SCREEN_WIDTH / 2 - 80, 370);

    highScores.slice(0, 3).forEach((hs, i) => {
        ctx.fillStyle = WHITE;
        const text = `${i + 1}. ${hs.name.padEnd(5)} ${String(hs.score).padStart(6)}`;
        ctx.fillText(text, SCREEN_WIDTH / 2 - 70, (390 + i * 18));
    });
}

// Start the game when page loads
window.addEventListener('load', initGame);
