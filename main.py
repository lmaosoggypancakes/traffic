"""
traffic simulator with python. simulates cars travelling along a randomly-generated city.
each car travels with a velocity that follows the graph of poisson's integral e**(-x^2)
so it basically speeds up then slows down at a logistic rate.
- red lines are bidirectional (a car can go from a to b and b to a arbitrarily) (a->b and b->a are possible)
- purple lines are unidirectional (either a->b or b->a, but not both) as indicated by the arrow
- "intersection" of diagonals is not yet supported and i'm not sure if i want/need to
- TODO: handle collisions of cars/slowing down to avoid collisions
"""
import pygame
from traffic import *
ARROW_SIZE = 10
NUM_CARS = 512
SIDES = 6

city = City(2 ** SIDES)
city.randomize_connections()

m = CityManager(city)
nodes = m.resolve_points()

cars = []
for i in range(NUM_CARS):
    c = Car(m, random.randrange(0, m.city.num_nodes))
    c.choose_random_road()
    c.go_to(round(random.random()*10, 2))
    cars.append(c)

cf = CarFactory(cars)

pygame.init()
pygame.font.init()

font_norm = pygame.font.SysFont("Noto Sans", 11)
font_xl = pygame.font.SysFont("Noto Sans", 24)
screen = pygame.display.set_mode(m.get_window_dimensions())
clock = pygame.time.Clock()
running = True
cars_enabled = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            print(pygame.K_SPACE)
            if event.key == pygame.K_SPACE:
                cars_enabled = not cars_enabled

    screen.fill("black")
    title = font_xl.render("traffic simulation", False, (255,255,255))
    screen.blit(title, (screen.get_size()[0]/2-75, 30))

    title = font_xl.render(f"cars={NUM_CARS}, roads={2 ** SIDES}", False, (255,255,255))
    screen.blit(title, (screen.get_size()[0]/2-100, 70))
    # draw roads
    connections = m.get_connections()
    for (i, j) in connections:
        if (j, i) in connections: # two-way streets
            pygame.draw.line(screen, (255, 0, 0), m.coord_of(i), m.coord_of(j))
        else: 
            (x_i, y_i) = m.coord_of(i)
            (x_j, y_j) = m.coord_of(j)
            if y_i == y_j:
                angle = 0
            else: 
                angle = round(math.atan2((y_j-y_i), (x_j-x_i)), 2)
            midpoint = ((x_i + x_j)/2, (y_i + y_j)/2)

            if angle == 0 and x_i > x_j:
                left = (midpoint[0]+ARROW_SIZE*math.cos(angle-math.pi/4), midpoint[1]+ARROW_SIZE*math.sin(angle-math.pi/4))     
                right = (midpoint[0]+ARROW_SIZE*math.cos(angle+math.pi/4), midpoint[1]+ARROW_SIZE*math.sin(angle+math.pi/4))
            else: 
                right = (midpoint[0]-ARROW_SIZE*math.cos(angle+math.pi/4), midpoint[1]-ARROW_SIZE*math.sin(angle+math.pi/4))
                left = (midpoint[0]-ARROW_SIZE*math.cos(angle-math.pi/4), midpoint[1]-ARROW_SIZE*math.sin(angle-math.pi/4))
            pygame.draw.polygon(screen, (255, 0, 255), [left, midpoint, right, left])
            pygame.draw.line(screen, (255, 0, 255), (x_i, y_i), (x_j, y_j))
    
    # draw intersections
    for (i, (x, y)) in enumerate(nodes):
        pygame.draw.circle(screen, (255,255,255), (x,y), 5)
        s = font_norm.render(str(i), False, (255, 255, 255))
        screen.blit(s, (x-20, y-20))

    for car in cars:
        pygame.draw.circle(screen, (0, 255, 0), car.pos, 5)
        # if len(car.get_frontier()) != 0 and cars_enabled:
            # car.go()
    if cars_enabled:
        cf.make_cars_go()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()