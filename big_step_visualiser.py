from pygame.math import Vector2 
from connorama import Back
import random
import time
import os

class Node:
    """individual peice of the map that can be traversed"""
    def __init__(self, pos: tuple[int, int]):
        self.pos = Vector2(pos)                 # position of node on the map list (not true game pos)
        self.visited = False                    # whether the node's been visited
        self.distance_from_start = float("inf") # 'steps' from start node
        self.total_distance = float("inf")      # 'steps' + heuristic distance
        self.previous_node = None               # node that leads to this node
    
    def calculate_heuristic(self, target_node_pos: Vector2) -> None:
        """manhattan distance to target node"""
        self.heuristic = abs(self.pos.x-target_node_pos.x) + abs(self.pos.y-target_node_pos.y)
    
    def show_table(self) -> None:
        """displays useful info about each node (for testing)"""
        try: print(self.pos, "|", self.visited, "|", self.distance_from_start, "|", self.heuristic, "|", 
         self.total_distance, "|", self.previous_node.pos)
        except AttributeError: print(self.pos, "|", self.visited, "|", self.distance_from_start, "|", self.heuristic,
         "|", self.total_distance, "|")

def main():
    rows = 20
    cols = 50

    map_list = []
    for row in range(rows):
        map_list.append([random.choice([1,1,0]) for i in range(cols)])

    nodes = [] # CREATES ALL AVAILABLE NODES TO PATHFIND TO 
    for i, row in enumerate(map_list):
        for j, col in enumerate(row):
            if col == 1: 
                nodes.append(Node((j,i)))

    # GET THE CURRENT AND TARGET NODES
    current_map_pos = Vector2(random.randint(0,cols-1),random.randint(0,rows-1)) # will be converted from enemy pos
    for node in nodes: # find the current map node
        if node.pos == current_map_pos: 
            current_map_node = node
            break
    else: 
        current_map_node = Node(current_map_pos) # make sure the current position is a node even if it's not traversable
        nodes.append(current_map_node)
    target_node_pos = Vector2(random.randint(0,cols-1),random.randint(0,rows-1)) # will be converted from player pos
    for node in nodes: # find the target node
        if node.pos == target_node_pos:
            target_node = node
            break
    else: 
        target_node = Node(target_node_pos) # make sure the target position is a node even if it's not traversable
        nodes.append(target_node)

    for node in nodes: # calculate the heuristics for all the nodes
        node.calculate_heuristic(target_node.pos)

    def print_map(show_path: bool = False):
        total_string = "" # string to print
        for i, row in enumerate(map_list):
            row_string = "" # string for the row
            for j, col in enumerate(row):
                if col == 0: row_string += Back.white                   # colour obstacles white
                elif col == 1:
                    if show_path and (j,i) in path: row_string += Back.green # colour path green
                    else: 
                        for node in nodes:
                            if node.pos == Vector2(j,i):
                                current_node = node                    # colour traversable + calculated magenta
                                break
                        if current_node.previous_node != None: row_string += Back.light_magenta
                        else: row_string += Back.RESET                 # colour traversable black(trasparent)
                        if current_node.visited: row_string += Back.light_red
                if (j,i) == current_map_pos: row_string += Back.yellow # colour current pos yellow
                elif (j,i) == target_node_pos: row_string += Back.cyan # colour target cyan
                row_string += "  " # space to be coloured
            total_string += row_string + Back.RESET + "\n" # add row string to total
        print("\033[H\033[J", end='')
        print(total_string)

    # set up the current node to start pathfinding
    current_map_node.distance_from_start = 0
    current_map_node.total_distance = 0
    pathfind_node = current_map_node # current node which paths are being calculated
    calculated_nodes = [] # holds a list of nodes calculated but not visited

    while 1: # continue until pathfinding is complete
        pathfind_node.visited = True
        # GET THE NODES NEXT TO THE CURRENT ONE
        up = pathfind_node.pos - Vector2(0,1)
        down = pathfind_node.pos + Vector2(0,1)
        left = pathfind_node.pos - Vector2(1,0)
        right = pathfind_node.pos + Vector2(1,0)
        neighbours = [up, down, left, right]

        for neighbour in neighbours: # check+update neighbouts if the neighbours get closer to the target
            # linear search get the node of the neighbour
            for node in nodes:
                if node.pos == neighbour:
                    neighbour_node = node
                    break
            else: continue # neighbour isn't traversable (out of map/obstacle)

            if neighbour_node.visited: continue # don't recalculate visited nodes
            if neighbour_node not in calculated_nodes: calculated_nodes.append(neighbour_node) # add neighbour to calculated nodes

            new_distance = pathfind_node.distance_from_start + 1 # new distance is 1 more than the previous node
            new_total = neighbour_node.heuristic + new_distance  # add heuristic for total distance
            if new_total < neighbour_node.total_distance: # make sure this is the most optimal path
                neighbour_node.distance_from_start = new_distance
                neighbour_node.total_distance = new_total
                neighbour_node.previous_node = pathfind_node

        # get the closest node to the target to visit next
        min_node_distance = float("inf") 
        min_node = None
        for node in calculated_nodes: # linear search to find the closest next node
            if node.total_distance < min_node_distance: # current closest path searched
                min_node_distance = node.total_distance
                min_node = node
            elif node.total_distance == min_node_distance and min_node_distance != float("inf"):
                if node.heuristic < min_node.heuristic:
                    min_node = node
        if min_node == None: # all possible nodes visited (and no target found)
            # get visited node with smallest heuristic
            min_heuristic = float("inf")
            min_heuristic_node = None
            for node in nodes: # linear search to find visited node with smallest heurstic
                if not node.visited: continue
                if node.heuristic < min_heuristic:
                    min_heuristic = node.heuristic
                    min_heuristic_node = node
            # make new target
            if min_heuristic_node != None: target_node = min_heuristic_node
            break # pathfinding done - get path to new target
        
        if min_node == target_node: break # finish when reached the target

        pathfind_node = min_node # go to next node
        calculated_nodes.remove(min_node) # remove from calculated as it's going to be visted

        print_map()

    # print("pos | visited | distance | heuristic | total | previous node")
    # for node in nodes:
    #     node.show_table()

    def get_path(current_end: Node) -> list:
        """recursively goes back through previous nodes until it reaches the start\n
        returns the shortest path to the start node"""
        previous = current_end.previous_node
        if previous == None: return [current_end.pos] # previous is the start node
        else: return [current_end.pos] + get_path(previous) # add the next nodes

    path = get_path(target_node)
    print_map(True)
    input("press [ENTER] To Continue: ")

if __name__ == "__main__":
    while 1:
        main()