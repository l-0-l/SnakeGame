# This game uses the pygame library. It may usually be installed
# by running something like "pip install pygame".
# The only controls are:
#   Left arrow: turn left
#   Right arrow: turn right

from random import randint
import pygame


class Direction:
    west = (-1, 0)
    east = (1, 0)
    north = (0, -1)
    south = (0, 1)
    left = {west: south, east: north, north: west, south: east}
    right = {west: north, east: south, north: east, south: west}
    none = {west: west, east: east, north: north, south: south}


class Body:
    """
    The body part has position (x, y) and
    direction (d), where d is a tuple.
    """

    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.d = d

    def move(self):
        self.x += self.d[0]
        self.y += self.d[1]

    def next(self):
        return self.x + self.d[0], self.y + self.d[1]

    def turn(self, direction):
        self.d = direction[self.d]


class Snake:
    """
    The snake consists of body parts. At
    the beginning only one part is there.
    """

    def __init__(self, x, y, d):
        self.body = [Body(x, y, d)]

    def grow(self):
        x = self.body[-1].x
        y = self.body[-1].y
        d = self.body[-1].d
        self.body.append(Body(x, y, d))
        self.body[-1].move()

    def turn(self, direction):
        self.body[-1].turn(direction)

    def move(self):
        for i in range(len(self.body)):
            self.body[i].move()
            if i < len(self.body)-1:
                self.body[i].d = self.body[i+1].d

    def next(self):
        return self.body[-1].next()


class World:
    """
    The world is the place for the snake
    to live in. It consists of borders, a
    snake and an apple.
    """
    def __init__(self, x, y):
        self.max_x = x
        self.max_y = y
        self.snake = Snake(0, y//2, Direction.east)
        self.apple = self.new_apple()
        self.score = 0

    def new_apple(self):
        is_on_snake = True
        x = y = 0
        while is_on_snake:
            is_on_snake = False
            x = randint(0, self.max_x-1)
            y = randint(0, self.max_y-1)
            for part in self.snake.body:
                if part.x == x and part.y == y:
                    is_on_snake = True
                    break
        return x, y

    def bite(self, next_step):
        for part in self.snake.body:
            if part.x == next_step[0] and part.y == next_step[1]:
                return True
        return False

    def step(self, direction):
        self.snake.turn(direction)
        next_step = self.snake.next()
        if next_step == self.apple:
            # If the snake eats an apple
            self.snake.grow()
            self.apple = self.new_apple()
            self.score += 1
        elif not (0 <= next_step[0] < self.max_x) or not (0 <= next_step[1] < self.max_y):
            # If the snake hits a wall
            return False
        elif self.bite(next_step):
            # If the snake bites itself
            return False
        else:
            self.snake.move()
        return True


class Interface:
    """
    The Screen is a place to show the
    world. It may be any type of display,
    now it uses PyGame to show everything.
    """
    def __init__(self, size_x, size_y, dot_size):
        pygame.init()
        self.dot_size = dot_size
        self.window = pygame.display.set_mode((size_x * dot_size, size_y * dot_size))
        pygame.display.set_caption("Snake game, Mor and Noa:)")
        self.snake_color = (0, 255, 0)  # Green
        self.apple_color = (255, 0, 0)  # Red
        self.score_color = (255, 255, 255)  # White
        self.font = pygame.font.SysFont('microsoft new tai lue', 26)
        self.direction = Direction.none

    def resize(self, val):
        return val * self.dot_size + self.dot_size // 2

    def draw_snake_part(self, x, y):
        pygame.draw.circle(self.window, self.snake_color, (self.resize(x), self.resize(y)), self.dot_size // 2)

    def draw_apple(self, x, y):
        pygame.draw.circle(self.window, self.apple_color, (self.resize(x), self.resize(y)), self.dot_size // 2)

    def draw(self, snake, apple, score):
        # Fill the window with black color
        self.window.fill((0, 0, 0))
        # Draw some random lines for background
        w = self.window.get_rect().width
        h = self.window.get_rect().height
        for x in range(100):
            pygame.draw.line(self.window, randint(0, 50), (randint(0, w), randint(0, h)), (randint(0, w), randint(0, h)))
        # Draw the snake
        for part in snake.body:
            self.draw_snake_part(part.x, part.y)
        # Draw the apple
        self.draw_apple(apple[0], apple[1])
        # Print the score
        text = self.font.render("Score: " + str(score), False, self.score_color)
        self.window.blit(text, [0, 0])
        pygame.display.update()
        pygame.time.wait(100)  # 0.1 second

    def check_keys(self):
        self.direction = Direction.none
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            # Respond to keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.left
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.right

    def wait_any_key(self):
        pygame.event.clear()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if event.type == pygame.KEYDOWN:
                    return

    def dead_screen(self, score):
        self.window.fill((0, 0, 0))
        font = pygame.font.SysFont('microsoft new tai lue', 30)
        text = font.render("GOOD JOB! Your score was " + str(score), False, self.score_color)
        text_rect = text.get_rect(center=(self.window.get_rect().width / 2, self.window.get_rect().height / 2))
        self.window.blit(text, text_rect)
        pygame.display.update()


class Game:
    """
    The main class for the game, the
    main loop is here.
    """
    def __init__(self):
        self.world_size_x = 50
        self.world_size_y = 50
        self.world = World(self.world_size_x, self.world_size_y)
        self.direction = Direction.none
        self.running = True
        self.interface = Interface(self.world_size_x, self.world_size_y, 10)

    def run(self):
        # Endless loop
        while True:
            # Main game loop
            while self.running:
                self.interface.draw(self.world.snake, self.world.apple, self.world.score)
                self.interface.check_keys()
                self.running = self.world.step(self.interface.direction)
            # When the game ends, show the score
            self.interface.dead_screen(self.world.score)
            self.interface.wait_any_key()
            # Restart everything
            self.world = World(self.world_size_x, self.world_size_y)
            self.direction = Direction.none
            self.running = True


game = Game()
game.run()
