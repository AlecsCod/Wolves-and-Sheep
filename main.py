import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
marginSize = 200
leftMargin, rightMargin, topMargin, bottomMargin = marginSize, WIDTH - marginSize, marginSize, HEIGHT - marginSize
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wolves and Sheep")

image_files = ["wolf.png", "wolf_fed.png", "sheep.png", "sheep_fed.png", "grass.png"]
images = [pygame.image.load("assets/" + img).convert_alpha() for img in image_files]
pygame.display.set_icon(images[4])

sheep = []
wolves = []
grass = []

turnfactor = 0.2
visualRange = 40
protectedRange = 8
centeringfactor = 0.0005
avoidfactor = 0.05
matchingfactor = 0.05
maxspeed = 4
minspeed = 2
hungerLevel = 300

protected_range_squared = 500
visual_range_squared = 20000

def clamp(n, min, max):
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n

class Grass:
    def __init__(self):
        self.image = images[4]
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(self.rect.width, WIDTH-self.rect.width)
        self.rect.centery = random.randint(self.rect.height, HEIGHT-self.rect.height)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Boid:
    def __init__(boid, image, x = None, y = None):
        boid.image = image
        boid.rect = boid.image[0].get_rect()

        boid.rect.centerx = x if x != None else random.randint(boid.rect.width, WIDTH-boid.rect.width)
        boid.rect.centery = y if y != None else random.randint(boid.rect.height, HEIGHT-boid.rect.height)

        boid.vx = random.uniform(-2, 2)
        boid.vy = random.uniform(-2, 2)
        boid.hunger = hungerLevel

        boid.fleeStrength = 0.3 #random.randint(2, 4) / 10 #more unbalanced

    def update(boid, group, food = grass, avoid = wolves):
        xpos_avg, ypos_avg, xvel_avg, yvel_avg, neighboring_boids, close_dx, close_dy = (0,) * 7

        ##### STARVING #####
        boid.hunger -= 1
        if (boid.hunger <= 0):
            group.remove(boid)

        ##### SEEKING FOOD #####
        if(boid.hunger <= hungerLevel):
            for foodItem in food:
                dx = boid.rect.centerx - foodItem.rect.centerx
                dy = boid.rect.centery - foodItem.rect.centery

                squared_distance = dx*dx + dy*dy

                if squared_distance < visual_range_squared and squared_distance > 0:
                    distance = math.sqrt(squared_distance)

                    dx /= -distance
                    dy /= -distance

                    boid.vx += dx
                    boid.vy += dy

                if (squared_distance <= protected_range_squared):
                    food.remove(foodItem)
                    boid.hunger = hungerLevel * 2
        ##### SEEKING MATE #####
        else: 
            for otherboid in group:
                if otherboid != boid and otherboid.hunger > hungerLevel:
                    dx = boid.rect.centerx - otherboid.rect.centerx
                    dy = boid.rect.centery - otherboid.rect.centery

                    squared_distance = dx*dx + dy*dy

                    if squared_distance < visual_range_squared and squared_distance > 0:
                        distance = math.sqrt(squared_distance)

                        dx /= -distance
                        dy /= -distance

                        boid.vx += dx
                        boid.vy += dy

                    ##### GENERATE NEW BOID #####
                    if (squared_distance <= protected_range_squared): 
                        boid.hunger = hungerLevel
                        otherboid.hunger = hungerLevel
                        group.append(Boid([boid.image[0], boid.image[1]], boid.rect.centerx, boid.rect.centery))

        ##### SHEEP ONLY #####
        if avoid != None: 
            for runFrom in avoid: ##### RUN FROM WOLVES #####
                dx = boid.rect.centerx - runFrom.rect.centerx
                dy = boid.rect.centery - runFrom.rect.centery

                squared_distance = dx*dx + dy*dy

                if squared_distance < visual_range_squared and squared_distance > 0:
                    distance = math.sqrt(squared_distance)

                    dx /= distance
                    dy /= distance

                    boid.vx += dx * boid.fleeStrength
                    boid.vy += dy * boid.fleeStrength

        ##### FLOCKING #####
        for otherboid in group:
            if otherboid != boid:
                dx = boid.rect.centerx - otherboid.rect.centerx
                dy = boid.rect.centery - otherboid.rect.centery

                if (abs(dx)<visualRange and abs(dy)<visualRange):
                    squared_distance = dx*dx + dy*dy

                    if (squared_distance < protected_range_squared):
                        close_dx += boid.rect.centerx - otherboid.rect.centerx
                        close_dy += boid.rect.centery - otherboid.rect.centery

                    elif (squared_distance < visual_range_squared):
                        xpos_avg += otherboid.rect.centerx
                        ypos_avg += otherboid.rect.centery 
                        xvel_avg += otherboid.vx
                        yvel_avg += otherboid.vy

                        neighboring_boids += 1

        if (neighboring_boids > 0): 
            xpos_avg = xpos_avg/neighboring_boids 
            ypos_avg = ypos_avg/neighboring_boids
            xvel_avg = xvel_avg/neighboring_boids
            yvel_avg = yvel_avg/neighboring_boids

            boid.vx = (boid.vx + 
                (xpos_avg - boid.rect.centerx)*centeringfactor + 
                (xvel_avg - boid.vx)*matchingfactor)

            boid.vy = (boid.vy + 
                (ypos_avg - boid.rect.centery)*centeringfactor + 
                (yvel_avg - boid.vy)*matchingfactor)

        boid.vx += close_dx*avoidfactor
        boid.vy += close_dy*avoidfactor

        if boid.rect.centery < topMargin:
            boid.vy += turnfactor
        if boid.rect.centerx > rightMargin:
            boid.vx -= turnfactor
        if boid.rect.centerx < leftMargin:
            boid.vx += turnfactor
        if boid.rect.centery > bottomMargin:
            boid.vy -= turnfactor

        speed = math.sqrt(boid.vx*boid.vx + boid.vy*boid.vy)

        if speed < minspeed:
            boid.vx = (boid.vx/speed)*minspeed
            boid.vy = (boid.vy/speed)*minspeed
        if speed > maxspeed:
            boid.vx = (boid.vx/speed)*maxspeed
            boid.vy = (boid.vy/speed)*maxspeed

        boid.rect.centerx = clamp(boid.rect.centerx + boid.vx, boid.rect.width/2, WIDTH - boid.rect.width/2)
        boid.rect.centery = clamp(boid.rect.centery + boid.vy, boid.rect.height/2, HEIGHT - boid.rect.height/2)

    def draw(boid, surface):
        ##### CHANGE SPRITE #####
        if (boid.hunger <= hungerLevel):
            surface.blit(boid.image[0], boid.rect)
        else:
            surface.blit(boid.image[1], boid.rect)

grass = [Grass() for _ in range(30)]
sheep = [Boid([images[2], images[3]]) for _ in range(20)]
wolves = [Boid([images[0], images[1]]) for _ in range(4)]

SPAWN_GRASS = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_GRASS, 300)

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == SPAWN_GRASS and len(grass) < 50:
            grass.append(Grass())

    for obj in sheep:
        obj.update(sheep, grass, wolves)

    for obj in wolves:
        obj.update(wolves, sheep, None)

    screen.fill((30, 30, 30))

    for obj in grass:
        obj.draw(screen)

    for obj in sheep:
        obj.draw(screen)

    for obj in wolves:
        obj.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
