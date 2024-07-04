#!/usr/bin/env python3
import sys
import pygame
import pymunk.pygame_util
import time
import random

WIDTH, HEIGHT = 1920, 1080
FPS = 60
BG = 69, 66, 74
OBSTACLE_RAD = int(WIDTH / 240) # 8 on 1920x1080
OBSTACLE_PAD = int(HEIGHT / 19)
OBSTACLE_START = (int((WIDTH / 2) - OBSTACLE_PAD), int((HEIGHT - (HEIGHT * .8)))) # (904, 108) on 1920x1080
OBSTACLE_CATEGORY = 2
OBSTACLE_MASK = pymunk.ShapeFilter.ALL_MASKS()
BALL_CATEGORY = 1
BALL_MASK = pymunk.ShapeFilter.ALL_MASKS() ^ BALL_CATEGORY
NUM_MULTIS = 15
MULTI_HEIGHT = int(HEIGHT / 19) 
MULTI_COLLISION = HEIGHT - (MULTI_HEIGHT * 2) 

balls_used = 0

earned_group = pygame.sprite.Group()
multi_group = pygame.sprite.Group()

multi_rgb = {
    (0, 5): (32, 125, 49),
    (1, 3): (32, 125, 66),
    (2, 2): (32, 125, 96),
    (3, .5): (32, 125, 117),
    (4, -0.25): (32, 105, 125),
    (5, 0.1): (32, 80, 125),
    (6, -0.1): (32, 54, 125),
    (7, 0): (44, 32, 125),
    (8, -0.1): (32, 54, 125),
    (9, 0.1): (32, 80, 125),
    (10, -0.25): (32, 105, 125),
    (11, 0.5): (32, 125, 117),
    (12, 2): (32, 125, 96),
    (13, 3): (32, 125, 66),
    (14, 5): (32, 125, 49),


}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

space = pymunk.Space()
space.gravity = 0, 9999
draw_options = pymunk.pygame_util.DrawOptions(screen)

class Board:
    def __init__(self):
        self.curr_row_count = 3
        self.final_row_count = 14
        self.space = space
        self.obstacles = []
        self.multis = []
        self.segmentA_2 = OBSTACLE_START
        self.updated_coords = OBSTACLE_START

        self.display_surface = pygame.display.get_surface()


        while self.curr_row_count <= self.final_row_count:
            for i in range(self.curr_row_count):
                if self.curr_row_count == 3 and self.updated_coords[0] > OBSTACLE_START[0] + OBSTACLE_PAD:
                    self.segmentB_1 = self.updated_coords
                elif self.curr_row_count == self.final_row_count and i == 0:
                    self.segmentA_1 = self.updated_coords
                elif self.curr_row_count == self.final_row_count and i == self.curr_row_count - 1:
                    self.segmentB_2 = self.updated_coords
                self.obstacles.append(self.spawn_obstacle(self.updated_coords, self.space))
                self.updated_coords = (int(self.updated_coords[0] + OBSTACLE_PAD), self.updated_coords[1])
            self.updated_coords = (((int(WIDTH- self.updated_coords[0] + (0.5*OBSTACLE_PAD)), int(self.updated_coords[1] + OBSTACLE_PAD))))
            self.curr_row_count += 1

        self.multi_x, self.multi_y = self.updated_coords[0], self.updated_coords[1]
        self.spawn_multis()


    def spawn_obstacle(self, pos, space):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = pos
        self.body.friction = 0.6
        self.shape = pymunk.Circle(self.body, OBSTACLE_RAD)
        self.shape.elasticity = 0.4
        self.shape.filter = pymunk.ShapeFilter(categories=OBSTACLE_CATEGORY, mask = OBSTACLE_MASK)
        space.add(self.body, self.shape)
        obstacle = Peg(pos[0], pos[1], OBSTACLE_RAD, space)
        return obstacle

    def visualize(self):
        multi_group.draw(self.display_surface)
        earned_group.draw(self.display_surface)
        multi_group.update()
        for i in self.multis:
            i.check_ball()

        if count.balls == 0 and len(balls) == 0:
            print("OUT OF BALLS")
            earned_group.add(out)
            out.render_out()
        else:
            for i in self.obstacles:
                i.visualize()
            earned_group.remove(out)

    def spawn_multis(self):
        self.multi_amounts = [val[1] for val in multi_rgb.keys()]
        self.rgb_vals = [val for val in multi_rgb.values()]

        for i in range(NUM_MULTIS):
            multi = Multi((self.multi_x, self.multi_y), self.rgb_vals[i], self.multi_amounts[i])
            multi_group.add(multi)
            self.multis.append(multi)
            self.multi_x += OBSTACLE_PAD


class Ball:
    def __init__(self, x, y, radius, mass, color, space):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.color = color
        self.space = space
        self.possible = [-25,25]

        self.body = pymunk.Body(self.mass,1,body_type=pymunk.Body.DYNAMIC)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.filter = pymunk.ShapeFilter(categories=BALL_CATEGORY, mask = BALL_MASK)
        self.space.add(self.body, self.shape)

        self.collided_obstacle = set()

    def check_collision(self, peg):
        dx = self.body.position[0] - peg.body.position[0]
        dy = self.body.position[1] - peg.body.position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance <= self.radius + peg.radius and peg not in self.collided_obstacle:
            self.collided_obstacle.add(peg)

            return True
        return False

    def visualize(self):
        debounce = False
        pygame.draw.circle(screen, self.color, self.body.position, self.radius)
        for obstacle in gameboard.obstacles:
            if self.check_collision(obstacle):
                # if random.randint(0,50) == 2:
                #     balls.append(Ball(OBSTACLE_START[0] + OBSTACLE_PAD,OBSTACLE_START[1]-40, 16, 1, (255,0,0), space))
                
                # self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                # target_peg = pegs[0]
                # direction = target_peg.body.position - self.body.position
                force_magnitude = 1000
                # target = target_peg.body.position[0], target_peg.body.position[1] + 200
                # force = direction.normalized() * force_magnitude
                # self.body.apply_force_at_world_point((random.choice(self.possible), -1000),(self.body.position[0], self.body.position[1]-1000))
                # Apply a constant force in the direction of the target position
                # force = 1000  # adjust this value to control the strength of the force
                #obstacle.body.position.x, obstacle.body.position.y
                #direction[0] * force, direction[1] * force
                # self.body.apply_impulse_at_world_point((-100, -100),(300, 300))
                # print(self.body.force)
                self.snap_to_obstacle(obstacle)
                self.handle_collision()

    def handle_collision(self):
        if random.random() < 0.5:
            self.body.velocity = (self.possible[0], -250)
        else:
            self.body.velocity = (self.possible[1], -250)

    def snap_to_obstacle(self, obstacle):
        self.body.position = (obstacle.body.position[0], obstacle.body.position[1] - self.radius - obstacle.radius)

class Earned(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        position = (400, 400)
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont(None, 26)
        self.rect_width, self.rect_height = 300, 100
        self.image = pygame.Surface((self.rect_width, self.rect_height))
        pygame.draw.rect(self.image, (255,255,255), self.image.get_rect())
        self.rect = self.image.get_rect(center=position)
        self.total = 0

        self.render_earned()

    def render_earned(self):
        self.image.fill((255, 255, 255))
        text_surface = self.font.render("{:.2f}".format(self.total), True, (0,0,0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

class Count(pygame.sprite.Sprite):
    def __init__(self, amnt):
        super().__init__()
        position = (WIDTH-400, 400)
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont(None, 26)
        self.rect_width, self.rect_height = 300, 100
        self.image = pygame.Surface((self.rect_width, self.rect_height))
        pygame.draw.rect(self.image, (255,255,255), self.image.get_rect())
        self.rect = self.image.get_rect(center=position)
        self.balls = amnt

        self.render_count()

    def render_count(self):
        self.image.fill((255, 255, 255))
        text_surface = self.font.render("Balls Left: {}".format(self.balls), True, (0,0,0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

class Out(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        position = (WIDTH/2, HEIGHT/2)
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont(None, 26)
        self.rect_width, self.rect_height = 200, 50
        self.image = pygame.Surface((self.rect_width, self.rect_height))
        self.rect = self.image.get_rect(center = position)

    def render_out(self):
        self.image.fill((200, 50, 20))
        text_surface = self.font.render("Out of balls", True, (0,0,0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)
    
class Multi(pygame.sprite.Sprite):
    def __init__(self, position, color, multi_amt):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont(None, 26)
        self.color = color
        self.border_radius = 10
        self.position = position
        self.rect_width, self.rect_height = OBSTACLE_PAD - (OBSTACLE_PAD/14), MULTI_HEIGHT
        self.image = pygame.Surface((self.rect_width, self.rect_height))
        pygame.draw.rect(self.image, self.color, self.image.get_rect(), border_radius=self.border_radius)
        self.rect = self.image.get_rect(center=position)
        self.multi_amt = multi_amt
        self.prev_multi = int(WIDTH/21.3)

        self.render_multi()
    
    def render_multi(self):
        text_surface = self.font.render(f"{self.multi_amt}", True, (0,0,0))
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

    def check_ball(self):
        for i in balls:
                if self.rect.top <= i.body.position.y + i.radius and i.body.position.x + i.radius <= self.rect.right and i.body.position.x - i.radius >= self.rect.left:
                    balls.remove(i)  
                    total.total += self.multi_amt


class Peg:
    def __init__(self, x, y, radius, space):
        self.x = x
        self.y = y
        self.radius = radius
        self.space = space
        self.color = (0,0,0)

        self.body = pymunk.Body(1, 1, body_type=pymunk.Body.KINEMATIC)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius)
        self.space.add(self.body, self.shape)

    def visualize(self):
        pygame.draw.circle(screen, self.color, self.body.position, self.radius)

def draw_elements(list):
    for i in list:
        i.visualize()

gameboard = Board()
# gameboard.

balls = []
# balls.append(Ball(OBSTACLE_START[0] + OBSTACLE_PAD,OBSTACLE_START[1]-40, 16, 1, (255,0,0), space))
# balls.append(Ball(OBSTACLE_START[0] + OBSTACLE_PAD,OBSTACLE_START[1]-40, 20, 1, (0,255,0), space))


# pegs = []
# pegs.append(Peg(400, 400, 10, space))
# pegs.append(Peg(300, 500, 10, space))

time.sleep(1)

total = Earned()

earned_group.add(total)

count = Count(25)

earned_group.add(count)

out = Out()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == (pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)) and count.balls > 0:
            balls.append(Ball(OBSTACLE_START[0] + OBSTACLE_PAD,OBSTACLE_START[1]-40, 16, 1, (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)), space))
            count.balls -= 1
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and count.balls > 0:
                balls.append(Ball(OBSTACLE_START[0] + OBSTACLE_PAD,OBSTACLE_START[1]-40, 16, 1, (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)), space))
                count.balls -= 1
    total.render_earned()
    count.render_count()
    screen.fill(BG)

    draw_elements(balls)

    gameboard.visualize()

    space.step(1/FPS)
    pygame.display.update()
    clock.tick(FPS)