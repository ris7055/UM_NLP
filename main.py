import random
import math
import pygame
import csv
import heapq
import ast


def distance(start, goal):
    return math.sqrt((start[0] - goal[0]) ** 2 + (start[1] - goal[1]) ** 2)


# A* pathfinding algorithm
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal):
    global width, height, maze1,TILE_SIZE
    open_set = set()
    closed_set = set()  # Add this line
    open_heap = []
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    heapq.heappush(open_heap, (fscore[start], start))
    open_set.add(start)
    while open_set:
        current = heapq.heappop(open_heap)[1]
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        open_set.remove(current)
        closed_set.add(current)  # Add this line
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = current[0] + dx, current[1] + dy
            if 0 <= neighbor[0] < width/TILE_SIZE and 0 <= neighbor[1] < height/TILE_SIZE:
                if int(maze1[neighbor[1]][neighbor[0]]) != -2 or neighbor in closed_set:
                    continue
                tentative_g_score = gscore[current] + 1
                if neighbor not in open_set or tentative_g_score < gscore[neighbor]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
                        heapq.heappush(open_heap, (fscore[neighbor], neighbor))

    return []


def get_maze(floor):
    floor_map_dict = {
        'agf': 'AGF.csv',
        'af1': 'AF1.csv',
        'af2': 'AF2.csv',
        'bgf': 'BGF.csv',
        'bf1': 'BF1.csv',
        'bf2': 'BF2.csv'
    }
    file = floor_map_dict[floor]
    with open(file, 'r') as f:
        reader = csv.reader(f)
        maze = []
        for line in reader:
            maze.append(line)
        return maze


def read_database():
    with open('Database.csv', 'r') as file:
        # Create a CSV reader
        reader = csv.reader(file)

        room_facilities_dict = {}
        # Loop over each row in the CSV
        next(reader)

        for row in reader:
            # Faculty,Block,Floor,Room/Facilities,Label,Color Code
            # Append each column to the respective list
            temp_dict = {
                'block': row[1],
                'floor': row[2],
                'label': row[4],
                'color code': row[5],
                'coordinate': row[6]
            }
            key = (row[1] + row[2] + " " + row[3]).lower()
            room_facilities_dict[key] = temp_dict
        print(len(room_facilities_dict))
        return room_facilities_dict


def create_tile_map(label_list, color_code_list):
    # Create a dictionary to map tile numbers to colors
    WALL_COLOR = (0, 0, 0)  # Black color
    PATHWAY_COLOR = (255, 255, 255)  # White color
    EMPTY_COLOR = (128, 128, 128)  # Gray color
    tile_map = {
        0: PATHWAY_COLOR,
        1: WALL_COLOR,
        -2: PATHWAY_COLOR,
        -1: EMPTY_COLOR
    }
    for label, color_code in zip(label_list, color_code_list):
        tile_map[int(label)] = ast.literal_eval(color_code)
    return tile_map


def main():
    global width, height, maze1, TILE_SIZE
    pygame.init()
    # Set the dimensions of each tile
    TILE_SIZE = 3
    PATH_COLOR = (255, 0, 0)

    room_facilities_dict = read_database()
    TILE_MAP = create_tile_map([room['label'] for room in room_facilities_dict.values()],
                               [room['color code'] for room in room_facilities_dict.values()])

    destination = input("Destination?['Cancel' to stop]: ").lower()
    while True:
        dest_possible = [key for key in room_facilities_dict if destination in key]
        if destination == 'Cancel':
            return
        if len(dest_possible) == 0:
            print("Invalid Destination")
            destination = input("Destination?['Cancel' to stop]: ").lower()
        elif len(dest_possible) > 1:
            [print(key) for key in dest_possible]
            destination = input("Which location do you mean?")
            if destination in dest_possible:
                break
        else:
            destination = dest_possible[0]
            break

    start = (input("Start Location?: ['Cancel' to stop]")).lower()
    while True:
        start_possible = [key for key in room_facilities_dict if start in key]
        if start == 'Cancel':
            return
        if len(start_possible) == 0:
            print("Invalid Start Position")
            start = (input("Start Location?: ['Cancel' to stop]")).lower()
        elif len(start_possible) > 1:
            [print(key) for key in start_possible]
            start = input("Which location do you mean?")
            if start in start_possible:
                break
        else:
            start = start_possible[0]
            break

    start_floor_plan = start[:3]
    start_coordinate = random.choice(ast.literal_eval(room_facilities_dict[start]['coordinate']))
    destination_floor_plan = destination[:3]
    destination_coordinates = ast.literal_eval(room_facilities_dict[destination]['coordinate'])
    # Calculate distances from start to each goal
    distances = [distance(start_coordinate, goal) for goal in destination_coordinates]
    # Find the goal with the shortest distance
    nearest_goal = destination_coordinates[distances.index(min(distances))]

    maze1 = get_maze(start_floor_plan)
    # Get the width and height of the maze
    width = len(maze1[0]) * TILE_SIZE
    height = len(maze1) * TILE_SIZE
    # Create the Pygame window
    screen = pygame.display.set_mode((width, height))

    if start_floor_plan != destination_floor_plan:
        maze2 = get_maze(destination_floor_plan)

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw the maze
        for y, row in enumerate(maze1):
            for x, tile in enumerate(row):
                pygame.draw.rect(screen, TILE_MAP[int(tile)],
                                 pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # Draw the path
        path = astar(start_coordinate, nearest_goal)
        for node in path:
            pygame.draw.rect(screen, PATH_COLOR,
                             pygame.Rect(node[0] * TILE_SIZE-1, node[1] * TILE_SIZE-1, TILE_SIZE+2, TILE_SIZE+2))

        pygame.display.flip()

    pygame.quit()


main()
