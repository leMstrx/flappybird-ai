import pygame
import random

#Constants 
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.5
JUMP_STRENGTH = -8
PIPE_SPEED = 3
PIPE_GAP = 130
PIPE_FREQUENCY = 1500

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.velocity = 0

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self):
        #update the bird position
        self.velocity += GRAVITY
        self.y += self.velocity

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.radius, self.radius)
    
class Pipe:
    def __init__(self, x):
        self.x = x 
        self.width = 60
        #random center for the gap
        self.gap_center = random.randint(100, SCREEN_HEIGHT - 100)
        self.gap_size = PIPE_GAP

    def update(self):
        self.x -= PIPE_SPEED

    def off_screen(self):
        return self.x < -self.width
    
    def collides_with(self, bird_rect):
        #top pipe rect
        top_pipe_rect = pygame.Rect(
            self.x,
            0,
            self.width,
            self.gap_center - self.gap_size//2
        )
        #bottom pipe rect
        bottom_pipe_rect = pygame.Rect(
            self.x,
            self.gap_center + self.gap_size//2,
            self.width,
            SCREEN_HEIGHT
        )
        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)
    
def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    bird = Bird(50, SCREEN_HEIGHT//2)
    pipes = []
    last_pipe_time = pygame.time.get_ticks()
    score = 0

    running = True
    while running:
        dt = clock.tick(60) #limit to 60fps
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        #spawn new pipes
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > PIPE_FREQUENCY:
            pipes.append(Pipe(SCREEN_WIDTH))
            last_pipe_time = current_time

        #update bird
        bird.update()

        #check collision with ground or ceiling
        if bird.y < 0 or bird.y > SCREEN_HEIGHT:
            running = False

        #update pipes
        to_remove = []
        for pipe in pipes:
            pipe.update()
            # if collides
            if pipe.collides_with(bird.get_rect()):
                running = False
            # if pipe is off Screen
            if pipe.off_screen():
                to_remove.append(pipe)
                score += 1 # Increase score for passing a pipe

        for r in to_remove:
            pipes.remove(r)

        # render
        screen.fill((135, 206, 250)) # sky blue
        # draw bird
        pygame.draw.circle(screen, (255, 255, 0), (int(bird.x), int(bird.y)), bird.radius)
        # draw pipes
        for pipe in pipes:
            #top pipe
            pygame.draw.rect(screen, (0, 177, 0),
                              (pipe.x, 0, pipe.width, pipe.gap_center - pipe.gap_size//2))
            #bottom pipe
            pygame.draw.rect(screen, (0, 177, 0),
                             (pipe.x, pipe.gap_center + pipe.gap_size//2, pipe.width, SCREEN_HEIGHT))
            
        # draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game_loop()

            