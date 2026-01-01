#!/usr/bin/env python3
"""
Simple Flappy Bird-like game using Pygame.
Controls: SPACE or Left Mouse Button to flap/start/restart.
"""

import pygame
import random
import sys

# --------- Configuration ----------
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

GROUND_HEIGHT = 100
PIPE_WIDTH = 80
PIPE_GAP = 160  # vertical gap between pipes
PIPE_INTERVAL_MS = 1500  # time between new pipes

BIRD_X = SCREEN_WIDTH // 4
BIRD_RADIUS = 16

GRAVITY = 0.5
FLAP_VELOCITY = -9.5
MAX_DESCENT_SPEED = 12
PIPE_SPEED = 3

BG_COLOR = (135, 206, 235)  # sky blue
GROUND_COLOR = (222, 184, 135)  # burlywood
PIPE_COLOR = (34, 139, 34)  # forest green
BIRD_COLOR = (255, 215, 0)  # gold
TEXT_COLOR = (25, 25, 25)

# ---------------------------------

pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy - Simple")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 28)
SMALL_FONT = pygame.font.SysFont("Arial", 18)

SPAWN_PIPE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_PIPE, PIPE_INTERVAL_MS)


class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = SCREEN_HEIGHT // 2
        self.radius = BIRD_RADIUS
        self.vel = 0.0
        self.angle = 0.0  # degrees for drawing tilt
        self.alive = True

    def flap(self):
        self.vel = FLAP_VELOCITY
        self.angle = -25

    def update(self):
        self.vel += GRAVITY
        if self.vel > MAX_DESCENT_SPEED:
            self.vel = MAX_DESCENT_SPEED
        self.y += self.vel

        # angle gradually rotates down
        if self.angle < 90:
            self.angle += 3.5

    def draw(self, surface):
        # draw simple rotated "winged" circle using a small surface for tilt
        s = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        center = (self.radius * 2, self.radius * 2)
        pygame.draw.circle(s, BIRD_COLOR, center, self.radius)
        # eye
        eye_pos = (center[0] + 6, center[1] - 4)
        pygame.draw.circle(s, (0, 0, 0), eye_pos, 3)
        # rotate surface by angle and blit
        rotated = pygame.transform.rotate(s, self.angle)
        rrect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rrect.topleft)


class Pipe:
    def __init__(self, x):
        self.x = x
        # gap_y is the top of the gap
        margin = 40
        self.gap_y = random.randint(margin + 10, SCREEN_HEIGHT - GROUND_HEIGHT - margin - PIPE_GAP)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, surface):
        # top pipe
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - (self.gap_y + PIPE_GAP))
        pygame.draw.rect(surface, PIPE_COLOR, top_rect)
        pygame.draw.rect(surface, PIPE_COLOR, bottom_rect)
        # pipe caps (rounded look)
        cap_height = 10
        pygame.draw.rect(surface, PIPE_COLOR, (self.x - 2, self.gap_y - cap_height, PIPE_WIDTH + 4, cap_height))

    def collides_with(self, bird: Bird):
        # approximate bird as circle; check overlap with rectangles
        bx, by, br = bird.x, bird.y, bird.radius
        # top rect
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - (self.gap_y + PIPE_GAP))
        # circle-rect collision check
        return circle_rect_collision(bx, by, br, top_rect) or circle_rect_collision(bx, by, br, bottom_rect)


def circle_rect_collision(cx, cy, r, rect: pygame.Rect):
    # find closest point on rect to circle center
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) <= (r * r)


def draw_background(surface):
    surface.fill(BG_COLOR)
    # simple clouds
    for i in range(3):
        cx = (i * 150 + 80) % SCREEN_WIDTH
        pygame.draw.ellipse(surface, (255, 255, 255), (cx, 60, 90, 40))
    # ground
    ground_rect = pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
    pygame.draw.rect(surface, GROUND_COLOR, ground_rect)


def draw_text_center(surface, text, y, font=FONT, color=TEXT_COLOR):
    txt = font.render(text, True, color)
    r = txt.get_rect(center=(SCREEN_WIDTH // 2, y))
    surface.blit(txt, r.topleft)


def reset_game():
    bird = Bird()
    pipes = []
    score = 0
    return bird, pipes, score


def main():
    bird, pipes, score = reset_game()
    running = True
    state = "START"  # START, PLAYING, GAMEOVER

    while running:
        dt = CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if state == "START":
                        state = "PLAYING"
                        bird.flap()
                    elif state == "PLAYING":
                        bird.flap()
                    elif state == "GAMEOVER":
                        bird, pipes, score = reset_game()
                        state = "START"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if state == "START":
                        state = "PLAYING"
                        bird.flap()
                    elif state == "PLAYING":
                        bird.flap()
                    elif state == "GAMEOVER":
                        bird, pipes, score = reset_game()
                        state = "START"

            if event.type == SPAWN_PIPE and state == "PLAYING":
                pipes.append(Pipe(SCREEN_WIDTH + 20))

        # Update
        if state == "PLAYING":
            bird.update()

            # spawn pipes periodically is handled by timer event

            for p in pipes:
                p.update()

            # remove off-screen pipes
            pipes = [p for p in pipes if p.x + PIPE_WIDTH > -50]

            # scoring
            for p in pipes:
                if not p.passed and p.x + PIPE_WIDTH < bird.x:
                    score += 1
                    p.passed = True

            # collisions
            # hit ground or top
            if bird.y + bird.radius >= SCREEN_HEIGHT - GROUND_HEIGHT:
                bird.y = SCREEN_HEIGHT - GROUND_HEIGHT - bird.radius
                state = "GAMEOVER"
                bird.alive = False
            if bird.y - bird.radius <= 0:
                bird.y = bird.radius
                bird.vel = 0

            for p in pipes:
                if p.collides_with(bird):
                    state = "GAMEOVER"
                    bird.alive = False
                    break

        # Draw
        draw_background(SCREEN)

        for p in pipes:
            p.draw(SCREEN)

        # draw ground detail
        pygame.draw.line(SCREEN, (200, 160, 120), (0, SCREEN_HEIGHT - GROUND_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT), 4)

        # draw bird
        bird.draw(SCREEN)

        # UI overlays
        if state == "START":
            draw_text_center(SCREEN, "FLAPPY - Simple", SCREEN_HEIGHT * 0.25)
            draw_text_center(SCREEN, "Press SPACE or Click to flap and start", SCREEN_HEIGHT * 0.35, font=SMALL_FONT)
            draw_text_center(SCREEN, "Space = flap  |  Avoid pipes", SCREEN_HEIGHT * 0.45, font=SMALL_FONT)
            draw_text_center(SCREEN, f"Score: {score}", SCREEN_HEIGHT * 0.55)
        elif state == "PLAYING":
            score_surf = FONT.render(str(score), True, TEXT_COLOR)
            SCREEN.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 40))
        elif state == "GAMEOVER":
            draw_text_center(SCREEN, "Game Over", SCREEN_HEIGHT * 0.35)
            draw_text_center(SCREEN, f"Score: {score}", SCREEN_HEIGHT * 0.45)
            draw_text_center(SCREEN, "Press SPACE or Click to restart", SCREEN_HEIGHT * 0.55, font=SMALL_FONT)

        # small instruction in corner
        hint = SMALL_FONT.render("Space / Click to flap", True, (60, 60, 60))
        SCREEN.blit(hint, (8, 8))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()