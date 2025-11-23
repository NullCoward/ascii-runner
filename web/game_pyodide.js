// ASCII Runner - Pyodide Web Version
// Uses Python game_engine via Pyodide

let pyodide = null;
let gameEngine = null;
let canvas = null;
let ctx = null;
let animationId = null;
let audioContext = null;

const CHAR_WIDTH = 10;
const CHAR_HEIGHT = 18;
const SCREEN_COLS = 80;
const SCREEN_ROWS = 25;

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

// Music
let musicTimer = 0;
let currentNote = 0;
const melody = [
    [262, 0.15], [330, 0.15], [392, 0.15], [523, 0.3],
    [392, 0.15], [330, 0.15], [262, 0.3],
    [294, 0.15], [370, 0.15], [440, 0.15], [587, 0.3],
    [440, 0.15], [370, 0.15], [294, 0.3],
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

// Initialize Pyodide and game engine
async function initGame() {
    // Show loading message
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading';
    loadingDiv.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);color:#0f0;font-family:monospace;font-size:20px;';
    loadingDiv.textContent = 'Loading Pyodide...';
    document.body.appendChild(loadingDiv);

    try {
        // Load Pyodide
        pyodide = await loadPyodide();
        loadingDiv.textContent = 'Loading game engine...';

        // Fetch and load game_engine.py
        const response = await fetch('../game_engine.py');
        const engineCode = await response.text();

        // Run the engine code
        await pyodide.runPythonAsync(engineCode);

        // Create game instance
        await pyodide.runPythonAsync(`
game = GameEngine()
`);

        gameEngine = pyodide.globals.get('game');

        // Remove loading message
        loadingDiv.remove();

        // Setup canvas
        setupCanvas();

        // Setup input
        setupInput();

        // Initialize audio on first interaction
        document.addEventListener('click', initAudio, { once: true });
        document.addEventListener('keydown', initAudio, { once: true });

        // Start game loop
        requestAnimationFrame(gameLoop);

    } catch (error) {
        loadingDiv.textContent = 'Error loading game: ' + error.message;
        console.error('Failed to initialize game:', error);
    }
}

function initAudio() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function setupCanvas() {
    // Use desktop canvas or mobile canvas based on screen
    const isMobile = window.innerWidth <= 900;
    canvas = document.getElementById(isMobile ? 'mobileGameCanvas' : 'gameCanvas');

    if (!canvas) {
        canvas = document.createElement('canvas');
        document.body.appendChild(canvas);
    }

    canvas.width = SCREEN_COLS * CHAR_WIDTH;
    canvas.height = SCREEN_ROWS * CHAR_HEIGHT;
    ctx = canvas.getContext('2d');
    ctx.font = '14px Consolas, monospace';
    ctx.textBaseline = 'top';
}

function setupInput() {
    let lastDied = false;

    document.addEventListener('keydown', async (e) => {
        if (e.code === 'Space') {
            e.preventDefault();

            const state = gameEngine.get_state().toJs();

            if (state.game_over) {
                gameEngine.reset();
                lastDied = false;
            } else {
                // Fire weapon
                const fired = gameEngine.fire_weapon();
                if (fired) playShootSound();

                // Jump
                const jumped = gameEngine.player.jump();
                if (jumped) playJumpSound();
            }
        } else if (e.code === 'Escape') {
            // Could add pause/quit functionality
        }
    });

    // Touch controls for mobile
    canvas.addEventListener('touchstart', async (e) => {
        e.preventDefault();
        initAudio();

        const state = gameEngine.get_state().toJs();

        if (state.game_over) {
            gameEngine.reset();
        } else {
            const fired = gameEngine.fire_weapon();
            if (fired) playShootSound();

            const jumped = gameEngine.player.jump();
            if (jumped) playJumpSound();
        }
    });
}

// Convert Python color tuple to CSS
function colorToCSS(color) {
    if (!color || color.length < 3) return '#000';
    const r = color[0];
    const g = color[1];
    const b = color[2];
    return `rgb(${r},${g},${b})`;
}

let lastDied = false;

function gameLoop() {
    // Update game
    const events = gameEngine.update().toJs();

    // Play sounds based on events
    if (events.died && !lastDied) {
        playDeathSound();
    }
    lastDied = events.died || false;

    if (events.farted) {
        playFartSound();
    }

    const collected = events.collected || [];
    for (const powerupType of collected) {
        playPickupSound();
        if (powerupType === 'acid') {
            playAcidSound();
        }
    }

    // Play music
    if (!events.game_over) {
        playMusic();
    }

    // Render
    render();

    animationId = requestAnimationFrame(gameLoop);
}

function render() {
    // Clear screen
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const state = gameEngine.get_state().toJs();

    // Get appropriate buffer
    let buffer;
    if (state.game_over) {
        buffer = gameEngine.get_game_over_buffer().toJs();
    } else {
        buffer = gameEngine.get_screen_buffer().toJs();
    }

    // Draw buffer
    for (let y = 0; y < buffer.length; y++) {
        const row = buffer[y];
        for (let x = 0; x < row.length; x++) {
            const cell = row[x];
            const char = cell[0];
            const color = cell[1];

            if (char && char !== ' ') {
                ctx.fillStyle = colorToCSS(color);
                ctx.fillText(char, x * CHAR_WIDTH, y * CHAR_HEIGHT);
            }
        }
    }

    // Draw HUD if not game over
    if (!state.game_over) {
        // Score
        ctx.fillStyle = '#ff0';
        ctx.fillText(`Score: ${state.score}`, canvas.width - 110, 5);

        // Jumps
        const jumpsLeft = state.player.jumps_left;
        ctx.fillStyle = '#fff';
        ctx.fillText(`Jumps: ${'*'.repeat(jumpsLeft)}`, canvas.width - 110, 23);

        // Power-up indicators
        let yOffset = 5;

        if (state.player.ammo > 0) {
            ctx.fillStyle = '#ffa500';
            ctx.fillText(`[=> x${state.player.ammo}`, 10, yOffset);
            yOffset += 18;
        }

        if (state.player.jetpack_jumps > 0) {
            ctx.fillStyle = '#0ff';
            ctx.fillText(`<J> x${state.player.jetpack_jumps}`, 10, yOffset);
            yOffset += 18;
        }

        if (state.player.has_beans) {
            const secs = Math.floor(state.player.beans_timer / 60);
            ctx.fillStyle = '#0f0';
            ctx.fillText(`{B} ${secs}s`, 10, yOffset);
            yOffset += 18;
        }

        if (state.player.acid_timer > 0) {
            const secs = Math.floor(state.player.acid_timer / 60);
            const acidLevel = state.player.acid_level;

            if (acidLevel === 3) {
                const colors = ['#f0f', '#0ff', '#ff69b4', '#9400d3', '#ffa500', '#32ff32', '#ff0', '#ff6464', '#6464ff'];
                ctx.fillStyle = colors[Math.floor(Date.now() / 100) % colors.length];
                ctx.fillText(`NIRVANA ${secs}s`, 10, yOffset);
            } else if (acidLevel === 2) {
                ctx.fillStyle = '#ff0';
                ctx.fillText(`EMOJI ${secs}s`, 10, yOffset);
            } else {
                ctx.fillStyle = '#f0f';
                ctx.fillText(`<*> ${secs}s`, 10, yOffset);
            }
            yOffset += 18;
        }

        if (state.stopwatch_timer > 0) {
            const secs = Math.floor(state.stopwatch_timer / 60);
            ctx.fillStyle = '#ff0';
            ctx.fillText(`(O) ${secs}s`, 10, yOffset);
        }
    }
}

// Start the game when page loads
window.addEventListener('load', initGame);
