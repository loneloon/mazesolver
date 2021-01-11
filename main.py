from PIL import Image
import numpy
import random
import sys


class ImageHandler:

    def __init__(self):
        pass

    @staticmethod
    def img_to_matrix(source_path):
        source = Image.open(source_path).convert('L')

        binary = source.point(lambda p: p > 128 and 1)

        matrix = numpy.array(binary)
        return matrix

    @staticmethod
    def matrix_to_img(matrix, file_path):

        for idx, i in enumerate(matrix):
            for idx2, j in enumerate(i):
                if j == 1:
                    matrix[idx][idx2] = 255

        matrix = numpy.asarray(matrix)

        new_im = Image.fromarray(matrix)
        new_im.save(file_path)


class MazePointer:

    def __init__(self):
        pass

    @staticmethod
    def get_endpoints(matrix):
        endpoints = []
        for y, i in enumerate(matrix):
            for x, j in enumerate(i):
                if y == 0 or y == len(matrix) - 1 or x == 0 or x == len(i) - 1:
                    if j == 1:
                        endpoints.append([y, x])
        return endpoints

    @staticmethod
    def draw_pivots(matrix):
        pivots = []

        for y, i in enumerate(matrix):
            for x, j in enumerate(i):
                if not x == 0 and not x == len(i)-1 and not y == 0 and not y == len(matrix)-1:
                    if j > 0:
                        pivot = 0
                        if matrix[y][x-1] and not matrix[y][x+1]:
                            pivot += 1
                        elif matrix[y][x+1] and not matrix[y][x-1]:
                            pivot += 1
                        elif matrix[y+1][x] and not matrix[y-1][x]:
                            pivot += 1
                        elif matrix[y-1][x] and not matrix[y+1][x]:
                            pivot += 1

                        if pivot >= 1:
                            pivots.append([y, x])
        return pivots


class MazeWalk:
    def __init__(self, maze, endpoints, pivots):

        self.maze = maze
        self.start = endpoints[0]
        self.end = endpoints[1]
        self.position = self.start
        self.visited = []
        self.pivots = pivots
        self.pivots.extend(endpoints)
        self.all_nodes = []

        for pivot in self.pivots:
            self.all_nodes.append(self.Node(x=pivot[1], y=pivot[0], maze=self.maze, all_pivots=self.pivots))

        self.start = self.Node(x=self.start[1], y=self.start[0], maze=self.maze, all_pivots=self.pivots)
        self.end = self.Node(x=self.end[1], y=self.end[0], maze=self.maze, all_pivots=self.pivots)

        self.all_nodes.extend([self.start, self.end])

        for node in self.all_nodes:
            for idx, n in enumerate(node.neighbours):
                for second_node in self.all_nodes:
                    if n == [second_node.y, second_node.x]:
                        node.neighbours[idx] = second_node

        self.visited.append(self.start)

    class Node:

        def __init__(self, x, y, all_pivots, maze):

            self.x = x
            self.y = y
            self.neighbours = []

            self.check_for_neighbours(all_pivots, maze)

        def __repr__(self):
            return str([self.y, self.x])

        def check_for_neighbours(self, all_pivots, maze):

            if self.y != 0:
                if maze[self.y - 1][self.x]:
                    possible_neighbours = []
                    for pivot in all_pivots:
                        if pivot[0] in range(0, self.y) and pivot[1] == self.x:
                            possible_neighbours.append(pivot)

                    top_y = 0
                    closest_node = None
                    for node in possible_neighbours:
                        if node[0] >= top_y:
                            top_y = node[0]
                            closest_node = node

                    if closest_node is not None:
                        self.neighbours.append(closest_node)

            if self.y != len(maze) - 1:
                if maze[self.y + 1][self.x]:
                    possible_neighbours = []
                    for pivot in all_pivots:
                        if pivot[0] in range(self.y + 1, len(maze)) and pivot[1] == self.x:
                            possible_neighbours.append(pivot)

                    min_y = len(maze)
                    closest_node = None

                    for node in possible_neighbours:
                        if node[0] < min_y:
                            min_y = node[0]
                            closest_node = node

                    if closest_node is not None:
                        self.neighbours.append(closest_node)

            if self.x != 0:
                if maze[self.y][self.x - 1]:
                    possible_neighbours = []
                    for pivot in all_pivots:
                        if pivot[1] in range(0, self.x) and pivot[0] == self.y:
                            possible_neighbours.append(pivot)

                    top_x = 0
                    closest_node = None
                    for node in possible_neighbours:
                        if node[1] >= top_x:
                            top_x = node[1]
                            closest_node = node

                    if closest_node is not None:
                        self.neighbours.append(closest_node)

            if self.x != len(maze) - 1:
                if maze[self.y][self.x + 1]:
                    possible_neighbours = []
                    for pivot in all_pivots:
                        if pivot[1] in range(self.x + 1, len(maze[0])) and pivot[0] == self.y:
                            possible_neighbours.append(pivot)

                    min_x = len(maze[0])
                    closest_node = None
                    for node in possible_neighbours:
                        if node[0] < min_x:
                            min_x = node[0]
                            closest_node = node

                    if closest_node is not None:
                        self.neighbours.append(closest_node)

    def walk(self, start, end):
        if start.neighbours:
            step = random.choice(start.neighbours)
            start.neighbours.remove(step)

            deadend = False

            if step == end:
                self.visited.append(end)
                return True

            while step in self.visited:
                if start.neighbours:
                    step = random.choice(start.neighbours)
                    start.neighbours.remove(step)
                else:
                    deadend = True
                    break

            if not deadend:
                self.visited.append(step)

                return self.walk(step, end)
            else:
                return False
        else:
            return False


if __name__ == "__main__":

    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print('Please specify input and output files!')
        raise SystemExit

    print(f'Creating binary map from {input_file}...')
    try:
        source_matrix = ImageHandler.img_to_matrix(input_file)
    except Exception as e:
        print(e)
        raise SystemExit

    print('Searching for in and out points...')
    try:
        endpoints = MazePointer.get_endpoints(source_matrix)
    except Exception as e:
        print(e)
        raise SystemExit

    print('Marking pivot points\n')
    try:
        pivots = MazePointer.draw_pivots(source_matrix)
    except Exception as e:
        print(e)
        raise SystemExit

    run = True
    attempts = 0

    while run:
        attempts += 1

        print(f'Initializing nodes... Attempt #{attempts}...')
        maze_nodes = MazeWalk(maze=source_matrix, endpoints=endpoints, pivots=pivots)
        print(f'Building path... {attempts}')
        result = maze_nodes.walk(maze_nodes.start, maze_nodes.end)

        if result:
            print(f'\nSolved! {attempts} attempt(s) elapsed.\n')
            print('Winner path: ')
            for step in maze_nodes.visited:
                print(step)
                source_matrix[step.y][step.x] = 180
            break
        else:
            print("Dead end.")

    print(f'\nSaving path to {output_file}')
    try:
        ImageHandler.matrix_to_img(source_matrix, output_file)
    except Exception as e:
        print(e)
        raise SystemExit
