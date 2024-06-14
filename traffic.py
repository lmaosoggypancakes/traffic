import random
import math
import uuid
from typing import List
# 60 fps, 5 pts/frame = 120 pts/s
MAX_VEL = 5

class City:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.s = int(math.sqrt(num_nodes))
        self.graph = []
        self.id = uuid.uuid4()
        for i in range(num_nodes):
            self.graph.append([])

        for l in self.graph:
            for j in range(num_nodes):
                l.append(False)
 
    def col_of(self, point):
        return point % self.s

    def row_of(self, point):
        return int(point/self.s)

    def connect(self, a, b):
        self.graph[a][b] = True

    def randomize_connections(self):
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                if random.choice([True, False]) and i != j:
                    # diagonals
                    if abs(self.row_of(i) - self.row_of(j)) == 1 and abs(self.col_of(i) - self.col_of(j)) == 1: 
                        self.connect(i,j) 
                    
                    # left <> right
                    if abs(self.row_of(i) - self.row_of(j)) == 0 and abs(self.col_of(i) - self.col_of(j)) == 1: 
                        self.connect(i,j) 

                    # up <> down
                    if abs(self.row_of(i) - self.row_of(j)) == 1 and abs(self.col_of(i) - self.col_of(j)) == 0: 
                        self.connect(i,j) 
    def can_go_to(self, a):
        """gives a list of all nodes one can travel to from a"""
        if a < 0 or self.num_nodes <= a:
            raise Exception("invalid node")
        n = []
        for i in range(self.num_nodes):
            if self.graph[a][i]:
                n.append(i)
        return n
    
    def has_connection(self, a, b):
        """returns True if one can travel from a->b"""
        return self.graph[a][b]
    
class CityManager:
    def __init__(self, city: City):
        self.city = city

    def resolve_points(self):
        nodes = []
        for i in range(self.city.num_nodes):
            nodes.append((200 + self.city.row_of(i)*100, 200+self.city.col_of(i)*100))
        return nodes
    
    def get_window_dimensions(self):
        return (300+100*self.city.s, 300+100*self.city.s)

    def get_connections(self):
        c = []
        for i in range(self.city.num_nodes):
            for j in range(self.city.num_nodes):
                if self.city.graph[i][j]:
                    c.append((i,j))
        return c
    
    def coord_of(self, point):
        return [200 + self.city.row_of(point) * 100, 200 + self.city.col_of(point)*100]


    
class Car:
    def __init__(self, m: CityManager, start=0):
        self.m = m
        self.last_point=start
        self.vel = 0
        self.pos = m.coord_of(start)
        self.line_along = None
        if 0 > start or m.city.num_nodes <= start:
            raise Exception("invalid starting point")
    
    def go_to(self, dist):
        if self.line_along is None:
            return
        (start, end) = self.line_along
        if start is None or end is None:
            raise Exception("can't travel without a selected start/end")
        (x_i, y_i) = self.m.coord_of(start)
        (x_f, y_f) = self.m.coord_of(end)
        dx = x_f - x_i
        dy = y_f - y_i
        total_dist = math.dist((x_i, y_i), (x_f, y_f))
        if dx == 0:
            if dy > 0:
                angle = -math.pi/2
            else:
                angle = math.pi/2
        else:
            angle = math.atan2(dy, dx)
        
        x = dist * math.cos(angle) + x_i
        y = dist * math.sin(angle) + y_i
        proposed_dist = math.dist((x_i, y_i), (x,y)) 
        if proposed_dist > total_dist:
            raise Exception(f"total_distance is greater than your current path: {proposed_dist}/{total_dist}")
        self.pos = [x,y]
    def get_frontier(self):
        return self.m.city.can_go_to(self.last_point)

    def choose_random_road(self):
        frontier = self.get_frontier()
        if len(frontier) == 0:
            print("DEAD END")
        else: 
            self.line_along = (self.last_point, random.choice(frontier))
    
    def go(self, vel: float):
        self.vel = vel
        if self.line_along == None:
            return
            raise Exception("need to choose a road to follow")
        next_point = self.m.coord_of(self.line_along[1])
        dist = math.dist(self.pos, next_point)
        if dist == 0:
            self.last_point = self.line_along[1]
            self.choose_random_road()
            self.pos = self.m.coord_of(self.last_point)
            return
        if dist < 5:
            self.pos = next_point
            return
        (x_i, y_i) = self.m.coord_of(self.last_point)
        (x_j, y_j) =  next_point
        if x_j-x_i == 0:
            angle = math.pi/2 if y_j-y_i > 0 else -math.pi/2
        else:
            angle = math.atan2((y_j-y_i), (x_j-x_i))
         
        self.pos[0] += vel*math.cos(angle)
        self.pos[1] += vel*math.sin(angle)

    def __repr__(self):
        return f"{self.pos}: {self.line_along[0]} -> {self.line_along[1]}"
class CarFactory:
    def __init__(self, cars: List[Car]):
        self.cars = cars
        pass

    def vel_for(self, car: Car):
        """
        gives the velocity a given car should go at, based on its position,
        distance travelled along its path, and the relative proximity of nearby cars.
        idea: cars should NEVER crash.
        """
        if len(car.get_frontier()) == 0:
            return 0
        next_point = car.m.coord_of(car.line_along[1])
        dist = math.dist(car.pos, next_point)
        total_dist = math.dist(car.m.coord_of(car.last_point), next_point)
        travelled = dist / total_dist
        vel_naive = MAX_VEL * math.e ** (-2*MAX_VEL * ((travelled - 0.5) ** 2))
        neighbors = self.neighbors(car)
        if len(neighbors) == 0:
            return vel_naive
        closest = min(neighbors, key=lambda k:k[0].vel)
        if closest[0].vel < vel_naive:
            return closest[0].vel
        return vel_naive

    def neighbors(self, car: Car):
        """
        fin ds all cars in the city that are 
        - along the same path
        - ahead by a small margin
        to a given car, such that it must "slow" its speed
        """
        res = []
        for c in self.cars:
            if c == car:
                continue
            if c.line_along == car.line_along:
                # travelling in the same road AND direction
                dist = math.dist(c.pos, car.pos)
                # are they close enough together, and is c "ahead" of car?
                start = car.m.coord_of(car.last_point)
                proximity = math.dist(start, c.pos) - math.dist(start, car.pos)
                if 0 <= proximity <= 20:
                    res.append([c, proximity])
        return res
    def make_cars_go(self):
        """
        moves all cars
        """
        for car in self.cars:
            car.go(self.vel_for(car))
    # TODO: handle car crashes (cars waiting at different intersections, starting at different points along
    # a path, etc)