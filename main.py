import pygame
from traffic import *
ARROW_SIZE = 10
NUM_CARS = 15

city = City(25)
city.randomize_connections()

m = CityManager(city)
nodes = m.resolve_points()

cars = []
for i in range(NUM_CARS):
    c = Car(m, random.randrange(0, m.city.num_nodes))
    c.choose_random_road()
    cars.append(c)

pygame.init()
pygame.font.init()

font = pygame.font.SysFont("Noto Sans", 11)
screen = pygame.display.set_mode(m.get_window_dimensions())
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")
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
            # s = font.render(f"({i},{j})", False, (255, 255, 0))
            s = font.render(str(angle), False, (255, 255, 0))
            screen.blit(s, (midpoint[0], midpoint[1]-15))
    
    # draw intersections
    for (i, (x, y)) in enumerate(nodes):
        pygame.draw.circle(screen, (255,255,255), (x,y), 5)
        s = font.render(str(i), False, (255, 255, 255))
        screen.blit(s, (x-20, y-20))
    
    for car in cars:
        pygame.draw.circle(screen, (0, 255, 0), car.pos, 5)
        if len(car.get_frontier()) != 0:
            car.go()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()