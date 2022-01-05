import random
import math
import sys
import pygame


class RRTMap:
    def __init__(self, start, goal, MapDimensions, obsdim, obsnum):
        self.start = start
        self.goal = goal
        self.MapDimensions = MapDimensions
        self.Mapw, self.Maph = self.MapDimensions

        # window settings
        self.MapWindowName = 'RRT path planning'
        pygame.display.set_caption(self.MapWindowName)
        self.map = pygame.display.set_mode((self.Mapw, self.Maph))
        self.map.fill((255, 255, 255))
        self.nodeRad = 2
        self.nodeThickness = 0
        self.edgeThickness = 1

        self.obstacles = []
        self.obsdim = obsdim
        self.obsNumber = obsnum

        # Colors
        self.grey = (70, 70, 70)
        self.Blue = (0, 0, 255)
        self.Green = (0, 255, 0)
        self.Red = (255, 0, 0)
        self.white = (255, 255, 255)

    def drawMap(self, obstacles, graph):
        pygame.draw.circle(self.map, self.Green, self.start, self.nodeRad + 5, 0)
        pygame.draw.circle(self.map, self.Green, self.goal, self.nodeRad + 20, 1)
        self.drawObs(obstacles, graph)

    def drawPath(self, path):
        for node in path:
            pygame.draw.circle(self.map, self.Red, node, 3, 0)

    def drawObs(self, obstacles, graph):
        num=0
        obstaclesList = obstacles.copy()
        minDist = 1000
        closest = False
        while (len(obstaclesList) > 0):
            obstacle = obstaclesList.pop(0)
            dist = graph.distance2((obstacle[0], obstacle[1]), self.goal)
            if dist < minDist:
                minDist = dist
                closest = obstacle
            # print("OB ", obstacle[0], obstacle[1], dist)
            pygame.draw.rect(self.map, self.grey, obstacle)
        # pygame.draw.rect(self.map, self.Red, closest)


class RRTGraph:
    def __init__(self, start, goal, MapDimensions, obsdim, obsnum):
        (x, y) = start
        self.start = start
        self.goal = goal
        self.goalFlag = False
        self.mapw, self.maph = MapDimensions
        self.x = []
        self.y = []
        self.parent = []
        # initialize the tree
        self.x.append(x)
        self.y.append(y)
        self.parent.append(0)
        # the obstacles
        self.obstacles = []
        self.obsDim = obsdim
        self.obsNum = obsnum
        # path
        self.goalstate = None
        self.path = []

    def makeRandomRect(self):
        uppercornerx = int(random.uniform(0, self.mapw - self.obsDim))
        uppercornery = int(random.uniform(0, self.maph - self.obsDim))

        return (uppercornerx, uppercornery)

    def makeobs(self):
        obs = []
        for i in range(0, self.obsNum):
            rectang = None
            startgoalcol = True
            while startgoalcol:
                upper = self.makeRandomRect()
                rectang = pygame.Rect(upper, (self.obsDim, self.obsDim))
                if rectang.collidepoint(self.start) or rectang.collidepoint(self.goal):
                    startgoalcol = True
                else:
                    startgoalcol = False
            obs.append(rectang)
        self.obstacles = obs.copy()
        return obs
    
    def make_problem_obs(self):
        obs = [(166, 66, 30, 30), (444, 4, 30, 30), (196, 392, 30, 30), (99, 364, 30, 30), (378, 329, 30, 30), (69, 222, 30, 30), (480, 81, 30, 30), (269, 282, 30, 30), (177, 103, 30, 30), (151, 207, 30, 30), (221, 321, 30, 30), (154, 147, 30, 30), (83, 97, 30, 30), (364, 413, 30, 30), (160, 413, 30, 30), (441, 227, 30, 30), (143, 410, 30, 30), (222, 328, 30, 30), (104, 88, 30, 30), (445, 79, 30, 30)]
        rects = []
        for obj in obs:
            rect = pygame.Rect(obj)
            rects.append(rect)
        self.obstacles = rects.copy()
        return rects
    
    def nearest_ob_to_goal(self):
        pass

    def add_node(self, n, x, y):
        self.x.insert(n, x)
        self.y.append(y)

    def remove_node(self, n):
        self.x.pop(n)
        self.y.pop(n)

    def add_edge(self, parent, child):
        self.parent.insert(child, parent)

    def remove_edge(self, n):
        self.parent.pop(n)

    def number_of_nodes(self):
        return len(self.x)

    def distance2(self, a, b):
        px = (float(a[0]) - float(b[0])) ** 2
        py = (float(a[1]) - float(b[1])) ** 2
        return (px + py) ** (0.5)

    def distance(self, n1, n2):
        (x1, y1) = (self.x[n1], self.y[n1])
        (x2, y2) = (self.x[n2], self.y[n2])
        px = (float(x1) - float(x2)) ** 2
        py = (float(y1) - float(y2)) ** 2
        return (px + py) ** (0.5)

    def sample_envir(self):
        x = int(random.uniform(0, self.mapw))
        y = int(random.uniform(0, self.maph))
        return x, y

    def nearest(self, n):
        dmin = self.distance(0, n)
        nnear = 0
        for i in range(0, n):
            if self.distance(i, n) < dmin:
                dmin = self.distance(i, n)
                nnear = i
        return nnear

    def isFree(self):
        n = self.number_of_nodes() - 1
        (x, y) = (self.x[n], self.y[n])
        obs = self.obstacles.copy()
        while len(obs) > 0:
            rectang = obs.pop(0)
            if rectang.collidepoint(x, y):
                self.remove_node(n)
                return False
        return True

    def crossObstacle(self, x1, x2, y1, y2):
        obs = self.obstacles.copy()
        while (len(obs) > 0):
            rectang = obs.pop(0)
            for i in range(0, 101):
                u = i / 100
                x = x1 * u + x2 * (1 - u)
                y = y1 * u + y2 * (1 - u)
                if rectang.collidepoint(x, y):
                    if self.goalFlag:
                        print("Hit object: ", rectang, x, y)
                    return True
        return False

    def connect(self, n1, n2):
        (x1, y1) = (self.x[n1], self.y[n1])
        (x2, y2) = (self.x[n2], self.y[n2])
        if self.crossObstacle(x1, x2, y1, y2):
            self.remove_node(n2)
            # if self.goalFlag:
                # print("Edge to goal crosses obstacle, removing node: ", n2)
                # print("Nodes: ", self.number_of_nodes())
            self.goalFlag = False
            return False
        else:
            self.add_edge(n1, n2)
            return True

    def step(self, nnear, nrand, dmax=25):
        d = self.distance(nnear, nrand)
        distance_to_goal = self.distance2((self.x[nrand], self.y[nrand]), self.goal)
        if distance_to_goal < 1:
            # print("Distance random sample to nearest node: ", d, self.x[nnear], self.y[nnear])
            # print("Distance random sample to goal: ", distance_to_goal)
            # print(self.x[nrand], self.y[nrand], self.goal)
            if d < dmax:
                self.goalstate = nrand
                self.goalFlag = True
        if d > dmax:
            u = dmax / d
            (xnear, ynear) = (self.x[nnear], self.y[nnear])
            (xrand, yrand) = (self.x[nrand], self.y[nrand])
            (px, py) = (xrand - xnear, yrand - ynear)
            theta = math.atan2(py, px)
            (x, y) = (int(xnear + dmax * math.cos(theta)),
                      int(ynear + dmax * math.sin(theta)))
            self.remove_node(nrand)
            if abs(x - self.goal[0]) <= dmax and abs(y - self.goal[1]) <= dmax:
                self.add_node(nrand, self.goal[0], self.goal[1])
                self.goalstate = nrand
                self.goalFlag = True
            else:
                self.add_node(nrand, x, y)

    def bias(self, ngoal):
        n = self.number_of_nodes()
        self.add_node(n, ngoal[0], ngoal[1])
        nnear = self.nearest(n)
        self.step(nnear, n)
        self.connect(nnear, n)
        return self.x, self.y, self.parent

    def expand(self):
        n = self.number_of_nodes()
        x, y = self.sample_envir()
        self.add_node(n, x, y)
        if self.isFree():
            xnearest = self.nearest(n)
            self.step(xnearest, n)
            self.connect(xnearest, n)
        return self.x, self.y, self.parent

    def path_to_goal(self):
        if self.goalFlag:
            self.path = []
            self.path.append(self.goalstate)
            newpos = self.parent[self.goalstate]
            while (newpos != 0):
                self.path.append(newpos)
                newpos = self.parent[newpos]
            self.path.append(0)
        return self.goalFlag

    def getPathCoords(self):
        pathCoords = []
        for node in self.path:
            x, y = (self.x[node], self.y[node])
            pathCoords.append((x, y))
        return pathCoords

    def cost(self, n):
        ninit = 0
        n = n
        parent = self.parent[n]
        c = 0
        while n is not ninit:
            c = c + self.distance(n, parent)
            n = parent
            if n is not ninit:
                parent = self.parent[n]
        return c

    def getTrueObs(self, obs):
        TOBS = []
        for ob in obs:
            TOBS.append(ob.inflate(-50, -50))
        return TOBS

    def waypoints2path(self):
        oldpath = self.getPathCoords()
        path = []
        for i in range(0, len(self.path) - 1):
            print(i)
            if i >= len(self.path):
                break
            x1, y1 = oldpath[i]
            x2, y2 = oldpath[i + 1]
            print('---------')
            print((x1, y1), (x2, y2))
            for i in range(0, 5):
                u = i / 5
                x = int(x2 * u + x1 * (1 - u))
                y = int(y2 * u + y1 * (1 - u))
                path.append((x, y))
                print((x, y))

        return path



def makeRandomRect(self):
    uppercornerx = int(random.uniform(0, self.mapw - self.obsDim))
    uppercornery = int(random.uniform(0, self.maph - self.obsDim))
    return (uppercornerx, uppercornery)

def makeobs(self):
    obs = []
    for i in range(0, self.obsNum):
        rectang = None
        startgoalcol = True
        while startgoalcol:
            upper = self.makeRandomRect()
            rectang = pygame.Rect(upper, (self.obsDim, self.obsDim))
            if rectang.collidepoint(self.start) or rectang.collidepoint(self.goal):
                startgoalcol = True
            else:
                startgoalcol = False
            obs.append(rectang)
        self.obstacles = obs.copy()
    return obs








































