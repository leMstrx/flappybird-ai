import pygame
import random
import sys

from flappy_game import Bird, Pipe, SCREEN_WIDTH, SCREEN_HEIGHT, PIPE_FREQUENCY
from neural_network import NeuralNetwork
from genetic_algorithm import next_generation

###############################
#  HYPERPARAMETERS & SETTINGS
###############################
POP_SIZE = 70      # How many birds (nets) per generation
GENERATIONS = 1000   # How many generations to evolve
INPUT_SIZE = 5     # [bird_y, velocity, top_pipe_y, bottom_pipe_y, x_dist]
HIDDEN_SIZE = 6
OUTPUT_SIZE = 1
UI = True

#####################
#  RUN PARALLEL GEN
#####################
def run_generation_in_parallel(population, draw=False):
    """
    Simulate all birds in the population simultaneously in one environment.
    
    :param population: list of NeuralNetwork objects
    :param draw: bool, whether to render the game visually (True) or run headless (False)
    :return: list of fitness values, one for each bird
    """
    # -- Setup Pygame --
    if draw:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()
    else:
        # "headless" rendering
        pygame.init()
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()

    # -- Create a Bird object for each network in the population --
    birds = [Bird(50, SCREEN_HEIGHT // 2) for _ in population]

    # -- Each bird's score (fitness) --
    #time = [0 for _ in population] #time alive
    scores = [0 for _ in population] #pipes passed

    # -- Track which birds are still alive --
    alive = [True for _ in population]

    # -- List of pipes for this generation --
    pipes = []
    last_pipe_time = pygame.time.get_ticks()

    colors = [
        (random.randint(50, 250), random.randint(50, 255), random.randint(50, 255))
        for _ in range(POP_SIZE)
    ]

    running = True
    while running:
        # If we are not drawing, run faster
        if draw:
            dt = clock.tick(60)
        else:
            dt = clock.tick(300)

        # Handle quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # -- Spawn new pipes --
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > PIPE_FREQUENCY:
            pipes.append(Pipe(SCREEN_WIDTH))
            last_pipe_time = current_time

        # --------------------------------------------------
        # 1) For each *alive* bird, find the closest pipe,
        #    do a forward pass, decide to jump or not.
        # --------------------------------------------------
        for i, nn in enumerate(population):
            if not alive[i]:
                continue  # skip dead birds

            # Find the closest pipe
            closest_pipe = None
            for p in pipes:
                if p.x + p.width > birds[i].x:
                    closest_pipe = p
                    break

            if closest_pipe is None:
                # no pipes ahead
                top_pipe_y = 0
                bottom_pipe_y = SCREEN_HEIGHT
                pipe_x_dist = SCREEN_WIDTH
            else:
                top_pipe_y = closest_pipe.gap_center - closest_pipe.gap_size//2
                bottom_pipe_y = closest_pipe.gap_center + closest_pipe.gap_size//2
                pipe_x_dist = closest_pipe.x - birds[i].x

            # Normalize input
            bird_y = birds[i].y / SCREEN_HEIGHT
            bird_vel = birds[i].velocity / 10.0
            top_y = top_pipe_y / SCREEN_HEIGHT
            bottom_y = bottom_pipe_y / SCREEN_HEIGHT
            x_dist = pipe_x_dist / SCREEN_WIDTH

            inputs = [bird_y, bird_vel, top_y, bottom_y, x_dist]
            output = nn.forward(inputs)[0]
            
            # Decide if we should jump
            if output > 0.5:
                birds[i].jump()

        # -- Update all birds --
        for i in range(len(birds)):
            if not alive[i]:
                continue

            birds[i].update()
            # Check collision with ground or ceiling
            if birds[i].y < 0 or birds[i].y > SCREEN_HEIGHT:
                alive[i] = False

        # -- Update pipes --
        to_remove = []
        for pipe in pipes:
            pipe.update()
            # Check collisions with each bird
            for i in range(len(birds)):
                if alive[i]:
                    if pipe.collides_with(birds[i].get_rect()):
                        alive[i] = False
            # If off screen, we'll remove the pipe
            if pipe.off_screen():
                to_remove.append(pipe)

        # Rewarding Structure
        # Removing pipes that went off screen and awarding score
        
        #for i in range(len(alive)):
        #    if alive[i]:
        #        time[i] += 0.1

        
        # Everyone who is still alive "passed" this pipe
        for r in to_remove:
            pipes.remove(r)
            for i in range(len(alive)):
                if alive[i]:
                    scores[i] += 1
        

        # -- Check if all birds are dead --
        if not any(alive):
            running = False

        # -- Rendering --
        if draw:
            screen.fill((135, 206, 235))  # sky color
            # Draw pipes
            for pipe in pipes:
                pygame.draw.rect(screen, (0, 200, 0),
                    (pipe.x, 0, pipe.width, pipe.gap_center - pipe.gap_size//2))
                pygame.draw.rect(screen, (0, 200, 0),
                    (pipe.x, pipe.gap_center + pipe.gap_size//2,
                     pipe.width, SCREEN_HEIGHT))

            # Draw birds
            for i, bird in enumerate(birds):
                if alive[i]:
                    # Optionally, color them differently:
                    # color = (255, 255, 0)
                    pygame.draw.circle(screen, colors[i], 
                                       (int(bird.x), int(bird.y)), bird.radius)

            # Show how many are alive
            font = pygame.font.SysFont(None, 24)
            alive_count = sum(alive)
            text = font.render(f"Alive: {alive_count}", True, (255, 255, 255))
            screen.blit(text, (10, 10))

            pygame.display.flip()

    return scores


#################
#   MAIN LOGIC  #
#################
def main():
    """
    1) Create initial population of neural networks
    2) For each generation, run the population in parallel, get fitnesses
    3) Print best score, evolve to next generation
    4) After final generation, optionally watch the best
    """
    # -- Initialize population --
    population = []
    for _ in range(POP_SIZE):
        nn = NeuralNetwork(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE)
        population.append(nn)

    # -- Evolve for multiple generations --
    for gen in range(GENERATIONS):
        # Run all birds in parallel (draw=True => real-time visualization)
        fitnesses = run_generation_in_parallel(population, draw=UI)
        
        # Print best score in this generation
        #print(f"Generation {gen} best score: {max(scores)}")
        print(f"Generation {gen} best time alive: {max(fitnesses)}")

        # Evolve next generation
        population = next_generation(population, fitnesses, elite_size=5)

    # -- After final generation, watch the best bird alone if desired --
    #   (Or you can skip and be done)
    fitnesses = run_generation_in_parallel(population, draw=UI)
    best_index = fitnesses.index(max(fitnesses))
    print("Best score after all generations:", max(fitnesses))
    # If you only want to watch the single best, you could write a separate function
    # that runs just one bird (like your old run_game_with_ai).
    # But we'll stop here.

if __name__ == "__main__":
    main()
