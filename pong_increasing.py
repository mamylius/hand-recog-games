# Multi-Side Pong – Ball acceleration & color shift towards red

import math, random, sys
from typing import List, Tuple
import pygame

# ----------------------------- CONFIG ------------------------------
SCREEN_SIZE          = 1000
FPS                  = 60
ARENA_RADIUS         = 700 // 2         # px – distance from centre to wall

BALL_SPEED           = 1.0          # initial speed
MAX_BALL_SPEED       = BALL_SPEED * 10.0
BALL_SPEED_INCREMENT = 0.0007        # speed increase per frame
BALL_RADIUS          = 10

PADDLE_ARC_FRACTION = 0.25
PADDLE_SPEED_FACTOR = 0.02
SPIN_FACTOR         = 0.1

NUM_ROUNDS    = 10          # total rounds before podium
# Podium visuals
PODIUM_WIDTH  = 140         # px – each block width
PODIUM_GAP    = 60          # px – gap between blocks (centre-to-centre)
PODIUM_HEIGHT = [240, 170, 130]  # heights for 1st, 2nd, 3rd steps

# inflate collision test so ball edge counts
COLLISION_MARGIN = math.asin(BALL_RADIUS / ARENA_RADIUS) + 0.02
# inward nudge after hit to break contact
POST_HIT_INSET    = 1.0      # px

#   full-up , half-up , half-down , full-down
KEY_BINDINGS: List[Tuple[int, int, int, int]] = [
    (pygame.K_1, pygame.K_q, pygame.K_a, pygame.K_z),   # P1
    (pygame.K_2, pygame.K_w, pygame.K_s, pygame.K_x),   # P2
    (pygame.K_3, pygame.K_e, pygame.K_d, pygame.K_c),   # P3
    (pygame.K_4, pygame.K_r, pygame.K_f, pygame.K_v),   # P4
    (pygame.K_5, pygame.K_t, pygame.K_g, pygame.K_b),   # P5
    (pygame.K_6, pygame.K_y, pygame.K_h, pygame.K_n)    # P6
]
PLAYER_COLORS = [
    (64, 128, 255),
    (64, 255, 64),
    (255, 128, 64),
    (64, 255, 255),
    (255, 255, 64),
    (255, 64, 255),
]

# --------------------------- UTILITIES -----------------------------
angle_normalise = lambda r: r % (2 * math.pi)

def angle_between(a, s, e):
    a, s, e = [angle_normalise(x) for x in (a, s, e)]
    return s <= a <= e if s <= e else a >= s or a <= e

# ------------------------------ CLASSES ----------------------------
class Paddle:
    def __init__(self, i: int, n: int):
        self.idx   = i
        self.total = n

        self.base = (2 * math.pi / n) * i + math.pi / n
        self.arc  = (2 * math.pi / n) * PADDLE_ARC_FRACTION
        side      = 2 * math.pi / n
        self.max_off = side / 2 - self.arc / 2

        # speed setup (full and half)
        self.full_speed = PADDLE_SPEED_FACTOR * 2 * self.max_off
        self.half_speed = self.full_speed * 0.5

        # four keys: full-up, half-up, half-down, full-down
        (self.k_full_up,
         self.k_half_up,
         self.k_half_dn,
         self.k_full_dn) = KEY_BINDINGS[i]

        self.color = PLAYER_COLORS[i]
        self.reset()

    # ───── geometry helpers ─────
    @property
    def start(self):
        return angle_normalise(self.base + self.off - self.arc / 2)

    @property
    def end(self):
        return angle_normalise(self.base + self.off + self.arc / 2)

    @property
    def rng0(self):
        return angle_normalise(self.base - self.max_off - self.arc / 2)

    @property
    def rng1(self):
        return angle_normalise(self.base + self.max_off + self.arc / 2)

    # ───── runtime state ─────
    def reset(self):
        self.off = self.prev = self.doff = 0.0

    def update(self, pressed):
        """Move the paddle by half- or full-speed depending on the key."""
        self.prev = self.off

        if pressed[self.k_full_up]:
            self.off -= self.full_speed
        if pressed[self.k_half_up]:
            self.off -= self.half_speed
        if pressed[self.k_half_dn]:
            self.off += self.half_speed
        if pressed[self.k_full_dn]:
            self.off += self.full_speed

        self.off  = max(-self.max_off, min(self.max_off, self.off))
        self.doff = self.off - self.prev

    # ───── drawing helpers (unchanged) ─────
    def _arc(self, surf, a0, a1, r, w, c):
        seg  = 40
        span = (a1 - a0) % (2 * math.pi)
        pts  = [
            (SCREEN_SIZE // 2 + math.cos(a0 + span * i / seg) * r,
             SCREEN_SIZE // 2 + math.sin(a0 + span * i / seg) * r)
            for i in range(seg + 1)
        ]
        pygame.draw.lines(surf, c, False, pts, w)

    def draw(self, surf):
        self._arc(surf, self.rng0,  self.rng1,  ARENA_RADIUS, 3,  self.color)
        self._arc(surf, self.start, self.end,  ARENA_RADIUS, 10, self.color)
        self._arc(surf, self.start, self.end,  ARENA_RADIUS, 4,  (255, 255, 255))


class Ball:
    def __init__(self):
        self.color = (255, 255, 255)
        self.reset()

    def reset(self):
        self.pos  = pygame.math.Vector2(SCREEN_SIZE//2, SCREEN_SIZE//2)
        # --- new: avoid horizontal spawns ±20° ---
        min_deg = 20
        min_rad = math.radians(min_deg)
        # sample until the angle is more than 20° away from 0° or 180°
        ang = random.uniform(0, 2*math.pi)
        # abs(cos(ang)) is 1 at 0/180°, and drops as you move away
        while abs(math.cos(ang)) > math.cos(min_rad):
            ang = random.uniform(0, 2*math.pi)
        self.speed = BALL_SPEED
        self.vel  = pygame.math.Vector2(math.cos(ang), math.sin(ang)) * self.speed


    def update(self):
        # gradually increase speed
        self.speed = min(self.speed + BALL_SPEED_INCREMENT, MAX_BALL_SPEED)
        self.vel.scale_to_length(self.speed)
        self.pos += self.vel

    def draw(self, surf):
        """Draw the ball and return the colour used."""
        # color shifts from white towards red as speed increases
        t = (self.speed - BALL_SPEED) / (MAX_BALL_SPEED - BALL_SPEED) if MAX_BALL_SPEED > BALL_SPEED else 0
        t = max(0.0, min(1.0, t))
        red   = 255
        green = int(255 * (1 - t))
        blue  = int(255 * (1 - t))
        self.color = (red, green, blue)
        pygame.draw.circle(surf, self.color,
                           (int(self.pos.x), int(self.pos.y)),
                           BALL_RADIUS)
        return self.color

# ------------------------- GAME FUNCTIONS --------------------------

def draw_score(surf, scores, pads, count=0, color=(255, 255, 255)):
    """Draw the player scores and the current hit counter."""
    f = pygame.font.SysFont(None, 32)
    x = 20
    for i, s in enumerate(scores):
        t = f.render(f"P{i+1}:{s}", True, pads[i].color)
        surf.blit(t, (x, 10))
        x += t.get_width() + 20

    # counter font size grows gradually with the count
    size = min(32 + count, 120)
    cf = pygame.font.SysFont(None, size)
    ct = cf.render(str(count), True, color)
    surf.blit(ct, (x + 20, 10))

def resolve_paddle_hit(ball, rel, paddle):
    """Reflect ball, add spin, and push it just inside arena to avoid stutter."""
    norm = rel.normalize()
    tan  = pygame.math.Vector2(-norm.y, norm.x)
    # reflect
    ball.vel -= 2 * ball.vel.dot(norm) * norm
    # subtle spin
    ball.vel += tan * (paddle.doff * ARENA_RADIUS * SPIN_FACTOR)
    # clamp speed within bounds
    spd = max(ball.speed * 0.8, min(ball.vel.length(), MAX_BALL_SPEED))
    ball.vel.scale_to_length(spd)
    ball.speed = spd
    # move inward slightly so next frame isn't still colliding
    centre = pygame.math.Vector2(SCREEN_SIZE//2, SCREEN_SIZE//2)
    ball.pos = centre + norm * (ARENA_RADIUS - BALL_RADIUS - POST_HIT_INSET)

# -------------------------------------------------------------------
# NEW – Podium screen
# -------------------------------------------------------------------

def show_podium(screen, scores, pads):
    """Display the final ranking on a three-step podium."""
    pygame.display.set_caption("Results – press <Space> to continue")
    ranking = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
    topN = min(3, len(ranking))
    big_font = pygame.font.SysFont(None, 64)
    small_font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    cx = SCREEN_SIZE // 2
    centres = [cx + (i-1)*(PODIUM_WIDTH+PODIUM_GAP) for i in range(topN)]

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                return

        screen.fill((0,0,0))
        title = big_font.render("Final ranking", True, (255,255,255))
        screen.blit(title, title.get_rect(center=(cx,200)))

        for pos in range(topN):
            p_idx = ranking[pos]
            h     = PODIUM_HEIGHT[pos]
            x     = centres[pos] - PODIUM_WIDTH//2
            y     = SCREEN_SIZE//2 + 200 - h
            pygame.draw.rect(screen, pads[p_idx].color, (x,y,PODIUM_WIDTH,h))
            pygame.draw.rect(screen, (0,0,0), (x,y,PODIUM_WIDTH,10), 1)
            lbl = small_font.render(f"P{p_idx+1}", True, (0,0,0))
            screen.blit(lbl, lbl.get_rect(center=(centres[pos], y-25)))
            scr = small_font.render(str(scores[p_idx]), True, (255,255,255))
            screen.blit(scr, scr.get_rect(center=(centres[pos], y+h/2)))
            rank_txt = big_font.render(str(pos+1), True, (0,0,0))
            screen.blit(rank_txt, rank_txt.get_rect(center=(centres[pos], y+h-40)))

        tip = small_font.render("<Enter> – menu  |  <Esc> – quit", True, (200,200,200))
        screen.blit(tip, tip.get_rect(center=(cx, SCREEN_SIZE-120)))

        pygame.display.flip()
        clock.tick(30)

# -------------------------------------------------------------------
# Training screen
# -------------------------------------------------------------------

def show_training(n):
    """Display player colours and show control arrows until SPACE is pressed."""
    pads = [Paddle(i, n) for i in range(n)]
    pygame.display.set_caption("Training – press <Space> when ready")
    font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()

    def arrow(surf, color, centre, direction, big=False):
        """Draw a small or big left/right arrow next to the centre point."""
        x, y = centre
        size = 30 if big else 18
        if direction == "left":
            pts = [(x - size, y), (x, y - size // 2), (x, y + size // 2)]
        else:
            pts = [(x + size, y), (x, y - size // 2), (x, y + size // 2)]
        pygame.draw.polygon(surf, color, pts)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                running = False

        keys = pygame.key.get_pressed()
        screen.fill((0, 0, 0))
        msg = font.render("Training – press SPACE to start", True, (200,200,200))
        screen.blit(msg, msg.get_rect(center=(SCREEN_SIZE//2, 100)))

        base_y = SCREEN_SIZE//2 - (n-1)*80//2
        for i, p in enumerate(pads):
            y = base_y + i*80
            x = SCREEN_SIZE//2
            pygame.draw.circle(screen, p.color, (x, y), 20)

            if keys[p.k_full_up]:
                arrow(screen, p.color, (x-60, y), "left", True)
            elif keys[p.k_half_up]:
                arrow(screen, p.color, (x-60, y), "left", False)

            if keys[p.k_full_dn]:
                arrow(screen, p.color, (x+60, y), "right", True)
            elif keys[p.k_half_dn]:
                arrow(screen, p.color, (x+60, y), "right", False)

        pygame.display.flip()
        clock.tick(FPS)

# -------------------------------------------------------------------
# Main game loop per player-count selection
# -------------------------------------------------------------------

def run_game(n):
    pads   = [Paddle(i, n) for i in range(n)]
    scores = [0] * n
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont(None, 48)
    rounds = 0

    while rounds < NUM_ROUNDS:
        # ----------------- Round initialisation --------------------
        for p in pads:
            p.reset()
        if rounds > 0:
            ball_speed = max(ball.speed / 3 * 2, BALL_SPEED)
        else:
            ball_speed = BALL_SPEED
        ball = Ball()
        ball.speed = ball_speed
        hit_count = 0
        waiting = True

        # wait for SPACE to serve
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    waiting = False
            screen.fill((0,0,0))
            msg = font.render(f"Round {rounds+1}/{NUM_ROUNDS} – SPACE", True, (200,200,200))
            screen.blit(msg, (SCREEN_SIZE//2-200, SCREEN_SIZE//2-24))
            draw_score(screen, scores, pads, hit_count, ball.color)
            pygame.display.flip()
            clock.tick(FPS)

        # ---------------------- Play round -------------------------
        playing = True
        while playing:
            clock.tick(FPS)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
            pr = pygame.key.get_pressed()
            for p in pads:
                p.update(pr)
            ball.update()

            rel = pygame.math.Vector2(ball.pos.x - SCREEN_SIZE//2,
                                      ball.pos.y - SCREEN_SIZE//2)
            if rel.length() >= ARENA_RADIUS - BALL_RADIUS:
                ang = angle_normalise(math.atan2(rel.y, rel.x))
                hit = None
                for p in pads:
                    if angle_between(ang, p.start - COLLISION_MARGIN, p.end + COLLISION_MARGIN):
                        hit = p
                        break
                if hit:
                    resolve_paddle_hit(ball, rel, hit)
                    hit_count += 1
                else:
                    # Miss – award points
                    side = 2 * math.pi / n
                    loser = int(((ang - 1e-6) // side) % n)
                    for i in range(n):
                        if i != loser:
                            scores[i] += 1
                    rounds += 1
                    # Flash message
                    t0 = pygame.time.get_ticks()
                    miss = font.render(f"P{loser+1} missed", True, PLAYER_COLORS[loser])
                    while pygame.time.get_ticks() - t0 < 1200:
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                pygame.quit(); sys.exit()
                        screen.fill((0,0,0))
                        screen.blit(miss, miss.get_rect(center=(SCREEN_SIZE//2, SCREEN_SIZE//2)))
                        draw_score(screen, scores, pads, hit_count, ball.color)
                        pygame.display.flip()
                        clock.tick(FPS)
                    playing = False

            # draw frame
            screen.fill((0,0,0))
            pygame.draw.circle(screen, (80,80,80),
                               (SCREEN_SIZE//2, SCREEN_SIZE//2),
                               ARENA_RADIUS, 1)
            for p in pads:
                p.draw(screen)
            col = ball.draw(screen)
            draw_score(screen, scores, pads, hit_count, col)
            pygame.display.flip()

    # ---------------- After final round – show podium --------------
    show_podium(screen, scores, pads)

# ------------------------------ MENU -------------------------------

def menu():
    pygame.display.set_caption("Multi-Side Pong")
    font = pygame.font.SysFont(None, 48)
    sel  = 2
    clock= pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_a, pygame.K_DOWN):
                    sel = 4 if sel == 2 else sel - 1
                if e.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_UP):
                    sel = 2 if sel == 4 else sel + 1
                if e.key == pygame.K_SPACE:
                    return sel

        screen.fill((0,0,0))
        screen.blit(font.render("Multi-Side Pong", True, (255,255,255)),
                    (SCREEN_SIZE//2-140, 150))
        screen.blit(font.render(f"Players: {sel}", True, PLAYER_COLORS[sel-1]),
                    (SCREEN_SIZE//2-90, 350))
        pygame.display.flip()
        clock.tick(30)

# ------------------------------ MAIN -------------------------------

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    while True:
        players = menu()
        show_training(players)
        run_game(players)
