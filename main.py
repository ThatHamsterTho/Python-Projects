from random import randint
import sys
import pygame
from pynput.keyboard import Key, Controller

# setting up input
keyboard = Controller()

# setting up screen
pygame.init()
pygame.font.init()

size = 700

screen = pygame.display.set_mode((size + 100, size + 100))
pygame.display.set_caption("snake")

screen.fill((170, 170, 170))

MainFrame = pygame.Surface((size, size))
MainFrame.fill((219, 216, 138))

pygame.display.flip()


# Functions

def draw_border_rect(surface, fill_color, outline_color, rect, border=1):
    surface.fill(outline_color, rect)
    surface.fill(fill_color, rect.inflate(-border * 2, -border * 2))


def redraw_surface():
    MainFrame.fill((219, 216, 138))
    screen.fill((170, 170, 170))
    snake.draw()
    food.draw()

    textsurface = myfont.render(f"your score is {snake.score}", False, (0, 0, 0))
    screen.blit(textsurface, (0, 0))

    screen.blit(MainFrame, (50, 50))


# classes

class SnakeBody:
    size = 20

    def __init__(self, x, y, num):
        self.x, self.y = x, y
        self.body_num = num
        self.body = pygame.rect.Rect(self.x, self.y, self.size, self.size)
        self.att_body = None
        self.dirs = []
        self.colour = (255, 0, 0)

    def move(self):
        # movement
        self.dirs.reverse()
        try:
            if self.dirs[0] == "left":
                self.body.move_ip(-self.size, 0)
                self.x = self.x - self.size
            if self.dirs[0] == "right":
                self.body.move_ip(self.size, 0)
                self.x = self.x + self.size
            if self.dirs[0] == "up":
                self.body.move_ip(0, -self.size)
                self.y = self.y - self.size
            if self.dirs[0] == "down":
                self.body.move_ip(0, self.size)
                self.y = self.y + self.size

            self.body.clamp_ip(MainFrame.get_rect())
        except IndexError:
            self.body.clamp_ip(MainFrame.get_rect())
        if self.x > size:
            self.x = size - self.size
        if self.y > size:
            self.y = size - self.size
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        self.dirs.reverse()
        # keep the array at length 2
        if len(self.dirs) > 2:
            self.dirs.pop(0)

        # pass movement to next body if there is one
        try:
            if len(self.dirs) > 0:
                self.att_body.dirs.append(self.dirs[0])
            self.att_body.move()
        except AttributeError:
            pass

        #
        # point scoring ( eating the food )
        if self.body.colliderect(food.body):
            snake.add_body()
            food.gen_pos()

        global pause
        #
        # self collision
        if self.body_num == 0:
            for snakeBody in snake.bodies:
                if self.body.colliderect(snakeBody.body) and self.body_num != snakeBody.body_num and not pause:
                    pause = True

    def draw(self):
        if self.body_num == 0:
            self.colour = (0, 0, 255)
        pygame.draw.rect(MainFrame, (0, 0, 0), self.body)
        pygame.draw.rect(MainFrame, self.colour, self.body.inflate(-3 * 2, -3 * 2))


class Snake:
    size = SnakeBody.size

    def __init__(self):
        self.score = 0
        self.bodies = []
        bodies = 10
        for i in range(bodies):
            self.bodies.append(SnakeBody((bodies - 2 - i) * self.size, 300, i))
        for idx, body in enumerate(self.bodies):
            try:
                body.att_body = self.bodies[idx + 1]
            except IndexError:
                body.att_body = None

    def add_body(self):
        self.bodies.reverse()
        dir_ = self.bodies[0].dirs[1]
        body = self.bodies[0]
        self.bodies.reverse()

        if dir_ == "left":
            self.bodies.append(SnakeBody(body.x + self.size, body.y, len(self.bodies)))
        if dir_ == "right":
            self.bodies.append(SnakeBody(body.x - self.size, body.y, len(self.bodies)))
        if dir_ == "up":
            self.bodies.append(SnakeBody(body.x, body.y + self.size, len(self.bodies)))
        if dir_ == "down":
            self.bodies.append(SnakeBody(body.x, body.y - self.size, len(self.bodies)))
        self.bodies[-2].att_body = self.bodies[-1]
        self.bodies[-1].colour = (0, 255, 0)
        self.score += 1

    def move(self, key):
        try:
            dir_ = self.bodies[0].dirs[1]
        except IndexError:
            dir_ = "right"
        try:
            if key[pygame.K_LEFT]:
                dir_ = "left"
            if key[pygame.K_RIGHT]:
                dir_ = "right"
            if key[pygame.K_UP]:
                dir_ = "up"
            if key[pygame.K_DOWN]:
                dir_ = "down"
        except IndexError:
            if key == "start":
                dir_ = "right"
        if dir_ is not None:
            try:
                prev_dir = self.bodies[0].dirs[-1]
                if prev_dir == "left" and dir_ == "right":
                    dir_ = "left"
                if prev_dir == "right" and dir_ == "left":
                    dir_ = "right"
                if prev_dir == "up" and dir_ == "down":
                    dir_ = "up"
                if prev_dir == "down" and dir_ == "up":
                    dir_ = "down"
            except IndexError:
                pass

            self.bodies[0].dirs.append(dir_)
            self.bodies[0].move()

    def draw(self):
        self.bodies.reverse()
        for body in self.bodies:
            body.draw()
        self.bodies.reverse()


class Food:
    size = SnakeBody.size
    colour = (198, 39, 55)

    def __init__(self):
        self.x, self.y = 0, 0
        self.body = pygame.rect.Rect(self.x, self.y, self.size, self.size)
        self.gen_pos()

    def gen_pos(self):
        x = randint(0, size / self.size) * self.size
        y = randint(0, size / self.size) * self.size
        x2 = x - self.x
        y2 = y - self.y
        self.body.move_ip(x2, y2)
        self.body.clamp_ip(MainFrame.get_rect())
        self.x = x
        self.y = y
        self.colour = (198, 39, 55)

    def draw(self):
        pygame.draw.rect(MainFrame, self.colour, self.body)


class Player:

    def __init__(self):
        self.moved = False
        self.pressed_key = None

    def move(self, direction):
        if direction == 0:
            keyboard.press(Key.left)
            self.pressed_key = Key.left
        elif direction == 1:
            keyboard.press(Key.right)
            self.pressed_key = Key.right
        elif direction == 2:
            keyboard.press(Key.up)
            self.pressed_key = Key.up
        elif direction == 3:
            keyboard.press(Key.down)
            self.pressed_key = Key.down

        self.moved = True

    def release_key(self):
        keyboard.release(self.pressed_key)


# main variables
myfont = pygame.font.SysFont('Comic Sans MS', 30)
clock = pygame.time.Clock()
fps = 60

snake = Snake()
food = Food()

player = Player()

pause = False


def main():
    snake.move("start")
    running = True
    global pause

    while running:
        redraw_surface()

        # resetting auto move value
        moved = False

        if not player.moved:
            player.move(2)

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause = not pause

                snake.move(pygame.key.get_pressed())
                moved = True
                pause = False

        # auto move snake if not moved
        if not moved and not pause:
            snake.move("")

        player.release_key()

        # finish drawing screen
        pygame.display.update()
        clock.tick(fps)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
