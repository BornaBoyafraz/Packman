import pygame


# Layout constants
PANEL_WIDTH = 460
PANEL_PADDING = 24
PANEL_RADIUS = 16
BUTTON_HEIGHT = 54
BUTTON_GAP = 12
HUD_HEIGHT = 50

# Palette
COLOR_BG_TOP = (8, 14, 36)
COLOR_BG_BOTTOM = (2, 6, 16)
COLOR_PANEL = (18, 32, 70)
COLOR_PANEL_BORDER = (80, 120, 200)
COLOR_BUTTON = (30, 52, 110)
COLOR_BUTTON_HOVER = (45, 76, 150)
COLOR_BUTTON_ACTIVE = (26, 44, 92)
COLOR_ACCENT = (252, 206, 78)
COLOR_TEXT = (245, 246, 250)
COLOR_TEXT_DIM = (170, 182, 210)
COLOR_HUD_BG = (10, 16, 34)
COLOR_WIN = (110, 226, 154)
COLOR_LOSE = (255, 112, 120)


def create_fonts():
    return {
        "title": pygame.font.Font("freesansbold.ttf", 48),
        "heading": pygame.font.Font("freesansbold.ttf", 30),
        "body": pygame.font.Font("freesansbold.ttf", 22),
        "small": pygame.font.Font("freesansbold.ttf", 16),
    }


def draw_gradient_background(surface, width, height):
    for y_pos in range(height):
        blend = y_pos / max(1, height - 1)
        red = int(COLOR_BG_TOP[0] + (COLOR_BG_BOTTOM[0] - COLOR_BG_TOP[0]) * blend)
        green = int(COLOR_BG_TOP[1] + (COLOR_BG_BOTTOM[1] - COLOR_BG_TOP[1]) * blend)
        blue = int(COLOR_BG_TOP[2] + (COLOR_BG_BOTTOM[2] - COLOR_BG_TOP[2]) * blend)
        pygame.draw.line(surface, (red, green, blue), (0, y_pos), (width, y_pos))


def draw_panel(surface, rect, alpha=230):
    shadow_rect = rect.move(0, 8)
    shadow = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 80))
    surface.blit(shadow, shadow_rect.topleft)

    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.fill((*COLOR_PANEL, alpha))
    pygame.draw.rect(panel, (*COLOR_PANEL, alpha), panel.get_rect(), border_radius=PANEL_RADIUS)
    pygame.draw.rect(panel, COLOR_PANEL_BORDER, panel.get_rect(), 2, border_radius=PANEL_RADIUS)
    surface.blit(panel, rect.topleft)


def draw_centered_text(surface, font, text, color, center):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, text_rect)
    return text_rect


def _draw_button(surface, font, text, rect, selected, hovered, pressed):
    color = COLOR_BUTTON
    if hovered or selected:
        color = COLOR_BUTTON_HOVER
    if pressed and hovered:
        color = COLOR_BUTTON_ACTIVE

    pygame.draw.rect(surface, color, rect, border_radius=12)
    border_color = COLOR_ACCENT if selected else COLOR_PANEL_BORDER
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=12)
    draw_centered_text(surface, font, text, COLOR_TEXT, rect.center)


def draw_menu(surface, fonts, title, subtitle, options, selected_index, mouse_pos, mouse_down):
    panel_height = 190 + len(options) * (BUTTON_HEIGHT + BUTTON_GAP)
    panel_rect = pygame.Rect(
        (surface.get_width() - PANEL_WIDTH) // 2,
        (surface.get_height() - panel_height) // 2,
        PANEL_WIDTH,
        panel_height,
    )
    draw_panel(surface, panel_rect)

    title_y = panel_rect.top + PANEL_PADDING + 20
    draw_centered_text(surface, fonts["title"], title, COLOR_TEXT, (panel_rect.centerx, title_y))
    draw_centered_text(surface, fonts["small"], subtitle, COLOR_TEXT_DIM, (panel_rect.centerx, title_y + 34))

    button_rects = []
    buttons_top = panel_rect.top + 110
    for index, option in enumerate(options):
        button_rect = pygame.Rect(
            panel_rect.left + PANEL_PADDING,
            buttons_top + index * (BUTTON_HEIGHT + BUTTON_GAP),
            panel_rect.width - PANEL_PADDING * 2,
            BUTTON_HEIGHT,
        )
        hovered = button_rect.collidepoint(mouse_pos)
        selected = index == selected_index
        _draw_button(surface, fonts["body"], option, button_rect, selected, hovered, mouse_down)
        button_rects.append(button_rect)
    return button_rects


def draw_controls_screen(surface, fonts, selected_index, mouse_pos, mouse_down, music_on, sfx_on):
    options = [
        f"Music: {'On' if music_on else 'Off'}",
        f"SFX: {'On' if sfx_on else 'Off'}",
        "Back",
    ]
    panel_height = 440
    panel_rect = pygame.Rect(
        (surface.get_width() - PANEL_WIDTH) // 2,
        (surface.get_height() - panel_height) // 2,
        PANEL_WIDTH,
        panel_height,
    )
    draw_panel(surface, panel_rect)

    draw_centered_text(surface, fonts["heading"], "Controls & Settings", COLOR_TEXT, (panel_rect.centerx, panel_rect.top + 42))
    control_lines = [
        "Arrow Keys: Move",
        "P or Esc: Pause/Resume",
        "F: Toggle FPS Counter",
        "R: Restart (pause/end screens)",
    ]
    line_y = panel_rect.top + 84
    for line in control_lines:
        draw_centered_text(surface, fonts["small"], line, COLOR_TEXT_DIM, (panel_rect.centerx, line_y))
        line_y += 24

    button_rects = []
    buttons_top = panel_rect.top + 200
    for index, option in enumerate(options):
        button_rect = pygame.Rect(
            panel_rect.left + PANEL_PADDING,
            buttons_top + index * (BUTTON_HEIGHT + BUTTON_GAP),
            panel_rect.width - PANEL_PADDING * 2,
            BUTTON_HEIGHT,
        )
        hovered = button_rect.collidepoint(mouse_pos)
        selected = index == selected_index
        _draw_button(surface, fonts["body"], option, button_rect, selected, hovered, mouse_down)
        button_rects.append(button_rect)

    footer = "Use arrows + Enter or mouse click"
    draw_centered_text(surface, fonts["small"], footer, COLOR_TEXT_DIM, (panel_rect.centerx, panel_rect.bottom - 22))
    return button_rects


def draw_hud(surface, fonts, score, high_score, lives, level_number, show_fps, fps_value, score_pop_timer):
    hud_rect = pygame.Rect(0, surface.get_height() - HUD_HEIGHT, surface.get_width(), HUD_HEIGHT)
    pygame.draw.rect(surface, COLOR_HUD_BG, hud_rect)
    pygame.draw.line(surface, COLOR_PANEL_BORDER, (0, hud_rect.top), (hud_rect.right, hud_rect.top), 2)

    score_scale = 1.0
    if score_pop_timer > 0:
        score_scale = 1.0 + min(0.22, score_pop_timer * 0.02)
    score_surface = fonts["body"].render(f"Score: {score}", True, COLOR_ACCENT)
    if score_scale != 1.0:
        score_surface = pygame.transform.smoothscale(
            score_surface,
            (int(score_surface.get_width() * score_scale), int(score_surface.get_height() * score_scale)),
        )
    score_rect = score_surface.get_rect(midleft=(18, hud_rect.centery))
    surface.blit(score_surface, score_rect)

    high_surface = fonts["small"].render(f"High Score: {high_score}", True, COLOR_TEXT)
    high_rect = high_surface.get_rect(midleft=(250, hud_rect.centery))
    surface.blit(high_surface, high_rect)

    lives_surface = fonts["small"].render(f"Lives: {lives}", True, COLOR_TEXT)
    lives_rect = lives_surface.get_rect(midleft=(470, hud_rect.centery))
    surface.blit(lives_surface, lives_rect)

    level_surface = fonts["small"].render(f"Level: {level_number}", True, COLOR_TEXT)
    level_rect = level_surface.get_rect(midleft=(620, hud_rect.centery))
    surface.blit(level_surface, level_rect)

    if show_fps:
        fps_surface = fonts["small"].render(f"FPS: {fps_value:.0f}", True, COLOR_TEXT_DIM)
        fps_rect = fps_surface.get_rect(midright=(surface.get_width() - 18, hud_rect.centery))
        surface.blit(fps_surface, fps_rect)


def draw_end_screen(surface, fonts, is_win, score, high_score):
    panel_height = 280
    panel_rect = pygame.Rect(
        (surface.get_width() - PANEL_WIDTH) // 2,
        (surface.get_height() - panel_height) // 2,
        PANEL_WIDTH,
        panel_height,
    )
    draw_panel(surface, panel_rect)

    title = "You Win!" if is_win else "Game Over"
    title_color = COLOR_WIN if is_win else COLOR_LOSE
    draw_centered_text(surface, fonts["title"], title, title_color, (panel_rect.centerx, panel_rect.top + 58))

    draw_centered_text(
        surface,
        fonts["body"],
        f"Score: {score}   High Score: {high_score}",
        COLOR_TEXT,
        (panel_rect.centerx, panel_rect.top + 118),
    )
    draw_centered_text(
        surface,
        fonts["small"],
        "Press R to restart / Esc to quit",
        COLOR_TEXT_DIM,
        (panel_rect.centerx, panel_rect.top + 170),
    )


def draw_fade_overlay(surface, alpha):
    if alpha <= 0:
        return
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, max(0, min(255, int(alpha)))))
    surface.blit(overlay, (0, 0))
