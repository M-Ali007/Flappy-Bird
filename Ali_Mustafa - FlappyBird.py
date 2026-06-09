# Mustafa Ali
# Course End Project - Flappy Bird
# Block 5
# 30th May
# This program is my own work - MA

# Consider any possible problems or limitations pertaining to this program.
# What are they? Make the necessary modifications.
#
# A problem that I came across was getting the bird to animate properly. Initially
# I used a single static image for the bird, but it looked wrong. I fixed this by
# loading three separate frames (upflap, midflap, downflap) into a list and cycling
# through them using a timer event (BIRDFLAP) every 200ms.
#
# Another problem was the scoring system. At first I incremented the score by a small
# amount every frame, which meant the score depended on how fast the game ran rather
# than how many pipes the player passed. I fixed this by counting how many bottom pipes
# have moved past the bird's position, so the player earns exactly one point per pair.
#
# A limitation of this program is that there is no audio - the original Flappy Bird had
# sound effects for flapping, scoring, and dying. Another limitation is that the pipe
# list is never cleaned up, so pipes that have scrolled off screen stay in memory for
# the entire session.

import pygame, sys, random
import os
import platform

# Fix to make sure the game renders properly on Linux
if platform.system() == 'Linux':
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    os.environ['SDL_VIDEO_HIGHDPI_ENABLED'] = '0'


# Draws two copies of the floor side by side to create a seamless scrolling loop
def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, 900))
    screen.blit(floor_surface, (floor_x_pos + 576, 900))

# Picks a random height and returns a bottom and top pipe as a pair of rects
def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop = (700, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom = (700, random_pipe_pos - 300))
    return bottom_pipe, top_pipe

# Moves all pipes 5 pixels to the left each frame
def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes

# Draws bottom pipes normally and flips the top pipes upside down
def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 1024:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

# Returns False (game over) if the bird hits a pipe or flies out of bounds
def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False

    if bird_rect.top <= -100 or bird_rect.bottom >= 900: # inequalities used because pixel measurements are never exact
        return False

    return True

# Tilts the bird based on its vertical speed — noses down when falling, up when jumping
def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
    return new_bird

# Returns the current animation frame and a rect centered on the bird's position
def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center = (100, bird_rect.centery))
    return new_bird, new_bird_rect

# Returns the medal name and display colour based on final score
# No medal: 0-9 | Bronze: 10-19 | Silver: 20-29 | Gold: 30-39 | Platinum: 40+
def get_medal(score):
    if score >= 40:
        return "Platinum", (180, 210, 255)
    elif score >= 30:
        return "Gold", (255, 215, 0)
    elif score >= 20:
        return "Silver", (192, 192, 192)
    elif score >= 10:
        return "Bronze", (205, 127, 50)
    else:
        return None, None

# Shows score during gameplay; on game over shows score, high score, and medal
def score_display(game_state):
    if game_state == "main_game":
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center = (288, 100))
        screen.blit(score_surface, score_rect)
    if game_state == "game_over":
        score_surface = game_font.render(f"Score: {int(score)}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center = (288, 100))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f"High Score: {int(highscore)}", True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center = (288, 850))
        screen.blit(high_score_surface, high_score_rect)

        medal_name, medal_color = get_medal(int(score))
        if medal_name:
            medal_surface = game_font.render(f"Medal: {medal_name}", True, medal_color)
            medal_rect = medal_surface.get_rect(center = (288, 775))
            screen.blit(medal_surface, medal_rect)

# Updates and returns the high score if the current score is higher
def update_score(score, highscore):
    if score > highscore:
        highscore = score
    return highscore


# --- Setup ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((576, 1024))
clock = pygame.time.Clock()
pygame.display.set_caption("Flappy Mustafa")
game_font = pygame.font.Font('04B_19.TTF', 40)

# Sound effects
sound_wing      = pygame.mixer.Sound('sound/sfx_wing.wav')
sound_hit       = pygame.mixer.Sound('sound/sfx_hit.wav')
sound_die       = pygame.mixer.Sound('sound/sfx_die.wav')
sound_point     = pygame.mixer.Sound('sound/sfx_point.wav')
sound_swooshing = pygame.mixer.Sound('sound/sfx_swooshing.wav')

# Game state variables
gravity = 0.25
bird_movement = 0
game_active = True
score = 0
highscore = 0

# Splash / game over image
game_over_surface = pygame.transform.scale2x(pygame.image.load("assets/message.png").convert_alpha())
game_over_rect = game_over_surface.get_rect(center = (288, 450))

# Background and scrolling floor
bg_surface = pygame.transform.scale2x(pygame.image.load('assets/background-day.png').convert())
floor_surface = pygame.transform.scale2x(pygame.image.load('assets/base.png').convert())
floor_x_pos = 0

# Load three bird animation frames into a list
bird_downflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-downflap.png').convert_alpha())
bird_midflap  = pygame.transform.scale2x(pygame.image.load('assets/bluebird-midflap.png').convert_alpha())
bird_upflap   = pygame.transform.scale2x(pygame.image.load('assets/bluebird-upflap.png').convert_alpha())
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 2
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center = (100, 512))

# Custom event that cycles the bird animation every 200ms
BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

# Pipes — a new pair spawns every 1.2 seconds
pipe_surface = pygame.transform.scale2x(pygame.image.load("assets/pipe-green.png").convert())
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)
pipe_height = [400, 600, 800]


# --- Main Game Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                # Jump — reset vertical speed then apply upward force
                bird_movement = 0
                bird_movement -= 8
                sound_wing.play()
            if event.key == pygame.K_SPACE and not game_active:
                # Restart — reset all game state
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100, 512)
                bird_movement = 0
                score = 0
                sound_swooshing.play()

        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())

        if event.type == BIRDFLAP:
            # Advance to next animation frame, wrap back to 0 after frame 2
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0
            bird_surface, bird_rect = bird_animation()

    # Draw background first so everything else renders on top
    screen.blit(bg_surface, (0, 0))

    if game_active:
        # Bird — apply gravity, move, rotate, and draw
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)
        still_alive = check_collision(pipe_list)
        if not still_alive:
            sound_hit.play()
            sound_die.play()
        game_active = still_alive

        # Pipes — scroll left and draw
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Score — count how many bottom pipes have passed the bird
        new_score = sum(1 for pipe in pipe_list if pipe.bottom >= 1024 and pipe.right < bird_rect.left)
        if new_score > score:
            sound_point.play()
        score = new_score
        score_display("main_game")

    else:
        # Game over — show splash image, update high score, show all text
        screen.blit(game_over_surface, game_over_rect)
        highscore = update_score(score, highscore)
        score_display("game_over")

    # Scroll the floor and wrap it when it's moved a full tile width
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -576:
        floor_x_pos = 0

    pygame.display.update()
    clock.tick(120)
