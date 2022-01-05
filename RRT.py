import pygame
from pygame.event import event_name
from RRTbasePy import RRTGraph
from RRTbasePy import RRTMap
import time
import sys, os
import traceback
import json


def main(datafile= None):
    dimensions = (1024,512)
    start=(50,50)
    goal=(600,300)
    obsdim=30
    obsnum=20
    iteration=0
    t1=0
    input_data = None

    if datafile is not None:
        with open(datafile, 'r') as f:
            input_data = json.load(f)
            f.close()
            print("DATA: ", input_data)

    global map, graph
    map=RRTMap(start,goal,dimensions,obsdim,obsnum)
    graph=RRTGraph(start,goal,dimensions,obsdim,obsnum)

    # if datafile is not None:
    # # obstacles=graph.make_problem_obs()
    #     pass
    # else:
    #     pass

    obstacles=graph.makeobs()
    map.drawMap(obstacles, graph)

    t1=time.time()
    while (not graph.path_to_goal()):
        time.sleep(0.005)
        elapsed=time.time()-t1
        t1=time.time()
        #raise exception if timeout
        # if elapsed > 10:
        #     print('timeout re-initiating the calculations')
        #     raise

        if iteration % 10 == 0:
            X, Y, Parent = graph.bias(goal)
            pygame.draw.circle(map.map, map.grey, (X[-1], Y[-1]), map.nodeRad*2, 0)
            pygame.draw.line(map.map, map.Blue, (X[-1], Y[-1]), (X[Parent[-1]], Y[Parent[-1]]),
                             map.edgeThickness)

        else:
            X, Y, Parent = graph.expand()
            pygame.draw.circle(map.map, map.grey, (X[-1], Y[-1]), map.nodeRad*2, 0)
            pygame.draw.line(map.map, map.Blue, (X[-1], Y[-1]), (X[Parent[-1]], Y[Parent[-1]]),
                             map.edgeThickness)

        if iteration % 5 == 0:
            pygame.display.update()
            # pygame.event.wait(0)
        iteration += 1

        if graph.number_of_nodes() > 50000:
            print("Too many nodes: ", graph.number_of_nodes())
            print("Obs: ", graph.obstacles.copy())
            pygame.event.clear()
            pygame.event.wait(0)
            raise Exception('Too many nodes')
            sys.exit()

    map.drawPath(graph.getPathCoords())
    print("Reached goal. Nodes: ", graph.number_of_nodes())
    pygame.display.update()

def continue_or_exit():
    waiting=True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return True
                if event.key == pygame.K_RETURN:
                    return False
                if event.key == pygame.K_d:
                    obs = []
                    for rect in graph.obstacles.copy():
                        obs.append((rect[0],rect[1]))

                    data = {
                        "objects": obs,
                        "nodes": tuple(zip(graph.x, graph.y)),
                        "path": graph.path,
                    }

                    filename = f"data{os.getpid()}.json"
                    print("filename: ", filename)
                    with open(filename, 'w') as f:
                        json.dump(data, f)
                        f.close()

                    with open(filename, 'r') as f:
                        data2 = json.load(f)
                        f.close()
                        print("DATA: ", data2)

graph = []
map = []

if __name__ == '__main__':
    pygame.init()

    print(f"Arguments: {sys.argv[0:]}")
    print(f"Arguments length: {len(sys.argv)}")

    result=False
    runs=0
    while not result:
        try:
            runs+=1
            main(sys.argv[1] if len(sys.argv) > 1 else None)
            result = continue_or_exit()
            if len(sys.argv) > 1:
                result = True

        except Exception as e:
            # traceback.print_exc(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb)
            # print(exc_type, fname, exc_tb.tb_lineno)
            while not continue_or_exit():
                pass

    
    
    print("Runs: ", runs)
    print("EXIT")
    



























