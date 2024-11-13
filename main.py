"""
Student portion of Zombie Apocalypse mini-project
"""

import random
import poc_grid
import poc_queue
import poc_zombie_gui
from collections import deque

# global constants
EMPTY = 0 
FULL = 1
FOUR_WAY = 0
EIGHT_WAY = 1
OBSTACLE = 5
HUMAN = 6
ZOMBIE = 7


class Apocalypse(poc_grid.Grid):
    """
    Class for simulating zombie pursuit of human on grid with
    obstacles
    """

    def __init__(self, grid_height, grid_width, obstacle_list=None, 
                 zombie_list=None, human_list=None):
        """
        Create a simulation of given size with given obstacles,
        humans, and zombies
        """
        poc_grid.Grid.__init__(self, grid_height, grid_width)
        if obstacle_list is not None:
            for cell in obstacle_list:
                self.set_full(cell[0], cell[1])
        self._zombie_list = list(zombie_list) if zombie_list is not None else []
        self._human_list = list(human_list) if human_list is not None else []
        
    def clear(self):
        """
        Set all cells in the grid to be empty.
        Reset zombie and human lists to be empty.
        """
        for row in range(self.get_grid_height()):
            for col in range(self.get_grid_width()):
                self.set_empty(row, col)

        self._zombie_list = []
        self._human_list = []


        
    def add_zombie(self, row, col):
        """
        Add zombie to the zombie list
        """
        self._zombie_list.append((row, col))
                
    def num_zombies(self):
        """
        Return number of zombies
        """
        return len(self._zombie_list)  
          
    def zombies(self):
        """
        Generator that yields the zombies in the order they were
        added.
        """
        for zombie in self._zombie_list:
            yield zombie

    def add_human(self, row, col):
        """
        Add human to the human list
        """
        self._human_list.append((row, col))
        
    def num_humans(self):
        """
        Return number of humans
        """
        return len(self._human_list)
    
    def humans(self):
        """
        Generator that yields the humans in the order they were added.
        """
        for human in self._human_list:
            yield human

    def compute_distance_field(self, entity_type):
        """
        Computes and returns a 2D distance field.
        Distance at member of entity_list is zero.
        Shortest paths avoid obstacles and use four-way distances.
        """
        distance_field = [[self.get_grid_height() * self.get_grid_width()] * self.get_grid_width()
                          for _ in range(self.get_grid_height())]
        
        visited = [[EMPTY] * self.get_grid_width() for _ in range(self.get_grid_height())]
        
        queue = deque()
        if entity_type == ZOMBIE:
            for zombie in self._zombie_list:
                queue.append(zombie)
                visited[zombie[0]][zombie[1]] = FULL
                distance_field[zombie[0]][zombie[1]] = 0
        elif entity_type == HUMAN:
            for human in self._human_list:
                queue.append(human)
                visited[human[0]][human[1]] = FULL
                distance_field[human[0]][human[1]] = 0
        
        while queue:
            current_cell = queue.popleft()
            current_row, current_col = current_cell
            current_distance = distance_field[current_row][current_col]
            
            for neighbor in self.four_neighbors(current_row, current_col):
                neighbor_row, neighbor_col = neighbor
                if (self.is_empty(neighbor_row, neighbor_col) and
                    visited[neighbor_row][neighbor_col] == EMPTY):
                    visited[neighbor_row][neighbor_col] = FULL
                    distance_field[neighbor_row][neighbor_col] = current_distance + 1
                    queue.append(neighbor)
        
        return distance_field

    
    def move_humans(self, zombie_distance_field):
        """
        Updates the human list to move humans away from zombies.
        Humans move to maximize distance from zombies.
        """
        new_human_positions = []

        for human in self._human_list:
            current_row, current_col = human
            max_distance = zombie_distance_field[current_row][current_col]
            best_position = (current_row, current_col)

            for neighbor in self.eight_neighbors(current_row, current_col):
                neighbor_row, neighbor_col = neighbor
                if (self.is_empty(neighbor_row, neighbor_col) and
                    zombie_distance_field[neighbor_row][neighbor_col] > max_distance):
                    max_distance = zombie_distance_field[neighbor_row][neighbor_col]
                    best_position = neighbor

            new_human_positions.append(best_position)

        self._human_list = new_human_positions

    
    def move_zombies(self, human_distance_field):
        """
        Updates the zombie list to move zombies towards humans.
        Zombies move to minimize distance to humans.
        """
        new_zombie_positions = []

        for zombie in self._zombie_list:
            current_row, current_col = zombie
            min_distance = human_distance_field[current_row][current_col]
            best_position = (current_row, current_col)

            for neighbor in self.four_neighbors(current_row, current_col):
                neighbor_row, neighbor_col = neighbor
                if (self.is_empty(neighbor_row, neighbor_col) and
                    human_distance_field[neighbor_row][neighbor_col] < min_distance):
                    min_distance = human_distance_field[neighbor_row][neighbor_col]
                    best_position = neighbor

            new_zombie_positions.append(best_position)

        self._zombie_list = new_zombie_positions


# Start up GUI for simulation
poc_zombie_gui.run_gui(Apocalypse(30, 40))
