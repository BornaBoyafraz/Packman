# PackMan (Pygame)

A classic Pac-Man style arcade game built with Python and Pygame, featuring polished menus, HUD improvements, and smoother game flow.

## Features

- Start menu with `Play`, `Controls`, and `Quit`
- Controls + Settings screen with ready-to-use `Music` and `SFX` toggles
- Pause menu with `Resume`, `Restart`, and `Quit`
- End screens for both **Game Over** and **Win**
- HUD with:
  - Score
  - High Score (saved locally)
  - Lives
  - Level
  - FPS counter (toggle with `F`)
- Fade transitions between screens
- Score pop animation when points increase

## Controls

### In Game

- `Arrow Keys` → Move
- `P` or `Esc` → Pause / Resume
- `F` → Toggle FPS counter
- `Q` → Quit immediately

### Menus

- `Arrow Keys` → Navigate
- `Enter` or `Space` → Select
- Mouse hover/click is also supported

### End Screen

- `R` → Restart
- `Esc` → Quit

### Controls & Settings Screen

- `M` → Toggle Music
- `N` → Toggle SFX

## How To Run

### 1. Install dependencies

```bash
python3 -m pip install pygame
```

### 2. Run the game

```bash
python3 main.py
```

If your system uses `python` instead of `python3`, use:

```bash
python main.py
```

## Folder Structure (Brief)

```text
Packman/
├── main.py               # Main game entry point
├── ui.py                 # UI drawing helpers and style constants
├── board.py              # Maze board data
├── Pack Man.py           # Original script (kept for reference)
├── Packman Images/       # Player animation sprites
├── *.png                 # Ghost and icon assets
├── README.md
└── LICENSE
```

## Screenshots

- Main Menu: `docs/screenshots/main-menu.png` (placeholder)
- Gameplay HUD: `docs/screenshots/gameplay-hud.png` (placeholder)
- Pause Menu: `docs/screenshots/pause-menu.png` (placeholder)
- Win / Game Over: `docs/screenshots/end-screen.png` (placeholder)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
