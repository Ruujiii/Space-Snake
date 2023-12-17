import pygame
from pygame.locals import USEREVENT
import sys
import random
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 1500, 600
FPS = 60
SNAKE_SIZE = 80
STAR_SIZE = 40
DEBRIS_SIZE = 70
OBSTACLE_SIZE = 100
GRAVITY_CONSTANT = 0
FAKE_TIME = 0
REAL_TIME = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2      
GAME_STATE_DIFFICULTY_SELECTION = 3
GAME_STATE_MENU = 0

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Background music files
music_files = ["bgm/BlueFlame.mp3", "bgm/FireintheBelly.mp3", "bgm/PerfectNight.mp3", "bgm/StrawberryMoon.mp3", "bgm/EvePsyche&theBluebeard'sWife.mp3"]
current_music = None

# Lagrange Interpolation function
def lagrange_interpolation(x, points):
    result = 0
    if game_state == GAME_STATE_PLAYING:
        for i, (x_i, y_i) in enumerate(points):
            find = y_i
            for j, (x_j, _) in enumerate(points):
                if i != j and x_i != x_j:
                    find *= (x - x_j) / (x_i - x_j)
            result += find
    else: 
        result = 0
    return result

#Timer function
def timer():
    global FAKE_TIME
    global REAL_TIME

    if game_state == GAME_STATE_PLAYING:
        FAKE_TIME += 1
        if FAKE_TIME > 100:
            REAL_TIME = FAKE_TIME // 100
    else: 
        FAKE_TIME = 0

#Music shuffler function
def play_random_music():
    new_music = random.choice(music_files)
    pygame.mixer.music.load(new_music)
    pygame.mixer.music.play()

#Difficulty selection function
def get_gravity_constant(selected_difficulty):
    difficulty_constants = {
        "easy":     0.000000000000001,
        "normal":   0.0000000001,
        "hard":     0.000001,
    }
    return difficulty_constants.get(selected_difficulty, 0.00000000000001)

# Snake class
class Snake(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("img/snake.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (SNAKE_SIZE, SNAKE_SIZE))
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = SNAKE_SIZE // 2
        self.vel_x = 0
        self.vel_y = 0

    def update(self):
        # Update position within screen bounds
        self.rect.x = max(0, min(WIDTH - SNAKE_SIZE, self.rect.x + self.vel_x))
        self.rect.y = max(0, min(HEIGHT - SNAKE_SIZE, self.rect.y + self.vel_y))
    
# Star class
class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("img/star.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (STAR_SIZE, STAR_SIZE))
        self.rect = self.image.get_rect()

    def reset_position(self):
        self.rect.center = (random.randint(WIDTH, WIDTH + STAR_SIZE), random.randint(0, HEIGHT - STAR_SIZE))

    def update(self):
        self.rect.x -= 5  # Move to the left
        if self.rect.right < 0:
            self.reset_position()

#Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("img/obstacle1_l.png").convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rotation_speed = random.uniform(-0.1, 0.1)  # Random rotation speed
        self.radius = OBSTACLE_SIZE // 2
        self.reset_position()

    def reset_position(self):
        # Start from the right side
        self.rect.x = WIDTH
        # Random height, avoiding overlap with stars
        valid_y_range = list(range(0, HEIGHT - SNAKE_SIZE))
        for star in stars:
            # Remove the y-range where a star is located
            valid_y_range = [y for y in valid_y_range if not (star.rect.y < y < star.rect.y + STAR_SIZE)]
        if valid_y_range:
            self.rect.y = random.choice(valid_y_range)
        else:
            # If there's no valid y-range (stars cover the entire height), choose a random position
            self.rect.y = random.randint(0, HEIGHT - SNAKE_SIZE)
        # Reset rotation angle
        self.angle = 0

    def update(self):
        self.rect.x -= 5  # Move to the left
        self.angle += self.rotation_speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.rect.right < 0:
            self.reset_position()

#Debris class  
class Debris(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("img/debris.png").convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.radius = DEBRIS_SIZE // 2
        self.reset_position()
    
    def reset_position(self):
        self.rect.center = (random.randint(WIDTH, WIDTH + DEBRIS_SIZE), random.randint(0, HEIGHT - DEBRIS_SIZE))

    def update(self):
        self.rect.x -= 5  # Move to the left
        if self.rect.right < 0:
            self.reset_position()

#Game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Snake")

#Sprite groups
all_sprites = pygame.sprite.Group()
stars = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
debris = pygame.sprite.Group()

#Snake object
snake = Snake(WIDTH // 2, HEIGHT // 2)

#Initial score
score = 0
font = pygame.font.Font(None, 36)

#Background image
bg = pygame.image.load("img/bg2.png").convert()
bg_width = bg.get_width()
bg_rect = bg.get_rect()
scroll = 0
tiles = math.ceil(WIDTH / bg_width) + 1

#Main menu buttons
start_button = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 20, 160, 40)
exit_button = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 80, 160, 40)

#Difficulty selection buttons
easy_button = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 150, 160, 40)
normal_button = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 100, 160, 40)
hard_button = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 50, 160, 40)

#Loading music file
pygame.mixer.music.load(random.choice(music_files))
pygame.mixer.music.set_endevent(USEREVENT + 1)

#Playing music
pygame.mixer.music.play(-1)  # -1 means loop indefinitely
current_music = pygame.mixer.music.get_busy()

#Difficulty buttons
difficulty_buttons = {
    "easy": easy_button,
    "normal": normal_button,
    "hard": hard_button,
}

# Main game loop
clock = pygame.time.Clock()
game_state = GAME_STATE_MENU
running = True

#Initializing obstacles
obstacles_counter = 1
obstacles_list = []

#Initializing debris
debris_counter = 1
debris_list = []

#Initializing selected difficulty
selected_difficulty = None

#Initializing boolean for increasing number of stars
increase_stars = False

while running:
    
    #Background scrolling
    for i in range(0, tiles):
        screen.blit(bg, (i * bg_width + scroll, 0))

    scroll -= 5

    if abs(scroll) > bg_width:
        scroll = 0

    #Keyboard/Mouse inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                snake.vel_y = -2 
                result_x = lagrange_interpolation(snake.rect.x, points)
                result_y = lagrange_interpolation(snake.rect.y, points)
                print("Datapoints = ", points)
                print("Lagrange Result X = ", result_x)
                print("Lagrange Result Y = ", result_y)
                print("Applied Gravity to X = ", gravitational_force_x)
                print("Applied Gravity to Y = ", gravitational_force_y)
                
            elif event.key == pygame.K_s:
                snake.vel_y = 2
                result_x = lagrange_interpolation(snake.rect.x, points)
                result_y = lagrange_interpolation(snake.rect.y, points)
                print("Datapoints = ", points)
                print("Lagrange Result X = ", result_x)
                print("Lagrange Result Y = ", result_y)
                print("Applied Gravity to X = ", gravitational_force_x)
                print("Applied Gravity to Y = ", gravitational_force_y)

            elif event.key == pygame.K_a:
                snake.vel_x = -4 
                result_x = lagrange_interpolation(snake.rect.x, points)
                result_y = lagrange_interpolation(snake.rect.y, points)
                print("Datapoints = ", points)
                print("Lagrange Result X = ", result_x)
                print("Lagrange Result Y = ", result_y)
                print("Applied Gravity to X = ", gravitational_force_x)
                print("Applied Gravity to Y = ", gravitational_force_y)

            elif event.key == pygame.K_d:
                snake.vel_x = 4
                result_x = lagrange_interpolation(snake.rect.x, points)
                result_y = lagrange_interpolation(snake.rect.y, points)
                print("Datapoints = ", points)
                print("Lagrange Result X = ", result_x)
                print("Lagrange Result Y = ", result_y)
                print("Applied Gravity to X = ", gravitational_force_x)
                print("Applied Gravity to Y = ", gravitational_force_y)
  
        elif event.type == pygame.KEYUP:
            # Stop the snake when the arrow keys are released
            if event.key in [pygame.K_w, pygame.K_s]:
                snake.vel_y = 0
  
            elif event.key in [pygame.K_a, pygame.K_d]:
                snake.vel_x = 0
                # Handle button clicks in the main menu
        
        elif event.type == pygame.USEREVENT + 1:
            # Music has ended, play a new random song
            play_random_music()
        
        elif game_state == GAME_STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    # Start the game
                    game_state = GAME_STATE_DIFFICULTY_SELECTION
                elif exit_button.collidepoint(event.pos):
                    running = False
                    pygame.mixer.music.stop()
        
        elif game_state == GAME_STATE_DIFFICULTY_SELECTION:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for difficulty, button_rect in difficulty_buttons.items():
                    if button_rect.collidepoint(event.pos):
                        #Set everything back to initial values
                        debris_counter = 1
                        debris_list = []
                        obstacles_counter = 1
                        obstacles_list = []

                        selected_difficulty = difficulty
                        GRAVITY_CONSTANT = get_gravity_constant(selected_difficulty)
                        # Start the game
                        snake = Snake(WIDTH // 2, HEIGHT // 2)
                        all_sprites.add(snake)
                        score = 0
                        FAKE_TIME = 0
                        REAL_TIME = 0
                        # Create initial stars
                        stars.empty()
                        for _ in range(5):
                            star = Star()
                            star.reset_position()
                            stars.add(star)
                            all_sprites.add(star)
                        # Create initial obstacles
                        obstacles.empty()
                        obstacles_list = [Obstacle() for _ in range(obstacles_counter)]
                        obstacles.add(*obstacles_list)
                        all_sprites.add(*obstacles_list)
                        # Create initial debris
                        debris.empty()
                        debris_list = [Debris() for _ in range(debris_counter)]
                        debris.add(*debris_list)
                        all_sprites.add(*debris_list)

                        game_state = GAME_STATE_PLAYING
                        # Change background music when starting the game
                        new_music = random.choice(music_files)
                        while new_music == current_music:
                            new_music = random.choice(music_files)
                        current_music = new_music
                        pygame.mixer.music.load(new_music)
                        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                        break           
    # Update
    if game_state == GAME_STATE_PLAYING:
        #Initial data points (7)
        points = [(snake.rect.x, snake.rect.y)]
        points += [(star.rect.x, star.rect.y) for star in stars]

        #appends new data points after every set interval

        #Lagrange implementation where gravity is influenced by data points
        gravitational_force_x = GRAVITY_CONSTANT * lagrange_interpolation(snake.rect.x, points)
        gravitational_force_y = GRAVITY_CONSTANT * lagrange_interpolation(snake.rect.y, points)

        #Apply gravitational force to the snake
        snake.vel_x += gravitational_force_x
        snake.vel_y += gravitational_force_y

        #Check for collisions with stars
        collisions = pygame.sprite.spritecollide(snake, stars, True)
        if collisions:
            #Increment the score
            score += 1

            #Check if the score is a multiple of 30
            if score % 30 == 0:
                increase_stars = True
            
            if increase_stars:
                #Add 3 new stars as data points for Lagrange interpolation when increase_stars = true
                new_stars = [Star() for _ in range(3)]
                stars.add(*new_stars)
                all_sprites.add(*new_stars)

                #Reset flag
                increase_stars = False

                #Update the points with the new stars
                points += [(star.rect.x, star.rect.y) for star in new_stars]

                #Update the Lagrange interpolation function with the new points
                lagrange_interpolation(snake.rect.x, points)
                lagrange_interpolation(snake.rect.y, points)

            star = Star()
            star.reset_position()
            stars.add(star)
            all_sprites.add(star)
            star.update()

            #Check if the score is a multiple of 25
            if score % 25 == 0:
                obstacles_counter += 1
                new_obstacle = Obstacle()
                obstacles_list.append(new_obstacle)
                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle)

                #Adjust the position of the new obstacle to avoid collisions with stars
                for obstacle in obstacles_list:
                    valid_y_range = list(range(0, HEIGHT - SNAKE_SIZE))
                    for star in stars:
                        valid_y_range = [y for y in valid_y_range if not (star.rect.y < y < star.rect.y + STAR_SIZE)]
                    if valid_y_range:
                        obstacle.rect.y = random.choice(valid_y_range)
                    else:
                        obstacle.rect.y = random.randint(0, HEIGHT - SNAKE_SIZE)
            
            #Check if the score is a multiple of 20
            if score % 20 == 0 and score != 0:
                debris_counter += 1
                new_debris = Debris()
                debris_list.append(new_debris)
                debris.add(new_debris)
                all_sprites.add(new_debris)
       
        #Check for collisions with obstacles
        obstacle_collisions = pygame.sprite.spritecollide(snake, obstacles, False, pygame.sprite.collide_circle)
        if obstacle_collisions:
            #If player touches an obstacle, move to game over screen
            game_state = GAME_STATE_GAME_OVER

        #Check for collisions with debris
        debris_collisions = pygame.sprite.spritecollide(snake, debris, False, pygame.sprite.collide_circle)
        if debris_collisions:
            #Player touched debris, deduct a point
            score -= 1
            #If the score is less than 0, move to game over screen
            if (score < 0):
                game_state = GAME_STATE_GAME_OVER

            for debris_item in debris_collisions:
                debris_item.reset_position()
        
        #Update the timer during gameplay
        timer()

    elif game_state == GAME_STATE_GAME_OVER:

        #Get rid of all sprites
        stars.empty()
        obstacles.empty()
        obstacles_list = []
        debris.empty()
        debris_list = []
        all_sprites.empty()

        for i in range(0, tiles):
            screen.blit(bg, (i * bg_width + scroll, 0))

        scroll -= 5

        if abs(scroll) > bg_width:
            scroll = 0

        #Display game over image
        game_over_orig_img = pygame.image.load("img/gameover.png").convert_alpha()
        game_over_img = game_over_orig_img
        game_over_rect = game_over_img.get_rect()
        screen.blit(game_over_img, (550, 200))

        #Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - 60, HEIGHT // 2))

        #Retry, main menu, and exit buttons
        retry_button = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 50, 150, 40)
        menu_button = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 100, 150, 40)
        exit_game_button = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 150, 150, 40)

        pygame.draw.rect(screen, WHITE, retry_button)
        pygame.draw.rect(screen, WHITE, menu_button)
        pygame.draw.rect(screen, WHITE, exit_game_button)
        
        retry_text = font.render("Retry", True, BLACK)
        menu_text = font.render("Main Menu", True, BLACK)
        exit_game_text = font.render("Exit", True, BLACK)

        screen.blit(retry_text, (WIDTH // 2 - 35, HEIGHT // 2 + 60))
        screen.blit(menu_text, (WIDTH // 2 - 70, HEIGHT // 2 + 110))
        screen.blit(exit_game_text, (WIDTH // 2 - 30, HEIGHT // 2 + 160))

        #Check for mouse click on the buttons
        mouse_x, mouse_y = pygame.mouse.get_pos()
        click, _, _ = pygame.mouse.get_pressed()
        if retry_button.collidepoint(mouse_x, mouse_y) and click:
            #Reset the game state and clear sprites
            all_sprites.empty()
            snake = Snake(WIDTH // 2, HEIGHT // 2)
            all_sprites.add(snake)
            stars.empty()
            obstacles.empty()
            obstacles_list = []
            debris.empty()
            debris_list = []
            #Generate initial stars, obstacles, and debris
            for _ in range(5):
                star = Star()
                star.reset_position()
                stars.add(star)
                all_sprites.add(star)

            obstacles_counter = 1
            obstacles_list = [Obstacle() for _ in range(obstacles_counter)]
            obstacles.add(*obstacles_list)
            all_sprites.add(*obstacles_list)

            debris_counter = 1
            debris_list = [Debris() for _ in range(debris_counter)]
            debris.add(*debris_list)
            all_sprites.add(*debris_list)

            #Initialize timer
            FAKE_TIME = 0
            REAL_TIME = 0
            score = 0
            game_state = GAME_STATE_PLAYING

        elif menu_button.collidepoint(mouse_x, mouse_y) and click:
            #Go back to the main menu
            game_state = GAME_STATE_MENU
        elif exit_game_button.collidepoint(mouse_x, mouse_y) and click:
            #Closes the application
            running = False
    
    elif game_state == GAME_STATE_DIFFICULTY_SELECTION:
        #Generate difficulty selection buttons
        for difficulty, button_rect in difficulty_buttons.items():
            pygame.draw.rect(screen, WHITE, button_rect)
            difficulty_text = font.render(difficulty.capitalize(), True, BLACK)
            screen.blit(difficulty_text, (button_rect.x + 40, button_rect.y + 10))

    elif game_state == GAME_STATE_MENU:
        #Generate buttons in the main menu
        title_orig_img = pygame.image.load("img/title.png").convert_alpha()
        title_img = title_orig_img
        title_rect = title_img.get_rect()
        screen.blit(title_img, (350, 200))
        
        pygame.draw.rect(screen, WHITE, start_button)
        pygame.draw.rect(screen, WHITE, exit_button)

        #Generate text on buttons
        start_text = font.render("Start", True, BLACK)
        exit_text = font.render("Exit", True, BLACK)

        screen.blit(start_text, (WIDTH // 2 - 28, HEIGHT // 2 + 30, 160, 40))
        screen.blit(exit_text, (WIDTH // 2 - 27, HEIGHT // 2 + 90, 160, 40))

    #Update
    all_sprites.update()

    #Render
    all_sprites.draw(screen)

    #Display the score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    #Display the timer
    time_text = font.render(f"Time: {REAL_TIME}", True, WHITE)
    screen.blit(time_text, (10, 40))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()