import pygame

import heapq
import random
import time
from pygame.locals import *

# ---------------------------- Puzzle Solver Implementation ----------------------------
class NPuzzle:
    def __init__(self, size):
        self.size = size
        self.goal = list(range(1, size * size)) + [0]
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.goal_positions = {tile: i for i, tile in enumerate(self.goal)}

    def generate_random_state(self):
        if self.size <= 3:
            state = list(range(self.size * self.size))
            random.shuffle(state)
            while not self.is_solvable(state):
                random.shuffle(state)
            return state
        else:
            state = self.goal.copy()
            moves = self.size * self.size * 3
            for _ in range(moves):
                neighbors = self.get_neighbors(state)
                if neighbors:
                    state = random.choice(neighbors)
            return state

    def is_solvable(self, state):
        inversions = 0
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                    inversions += 1
        if self.size % 2 == 1:
            return inversions % 2 == 0
        else:
            blank_row = state.index(0) // self.size
            return (inversions + blank_row) % 2 == 1

    def get_neighbors(self, state):
        neighbors = []
        blank_index = state.index(0)
        row, col = divmod(blank_index, self.size)
        for dr, dc in self.directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                new_index = new_row * self.size + new_col
                new_state = state[:]
                new_state[blank_index], new_state[new_index] = new_state[new_index], new_state[blank_index]
                neighbors.append(new_state)
        return neighbors

    def manhattan_distance(self, state):
        distance = 0
        for i, tile in enumerate(state):
            if tile != 0:
                goal_pos = self.goal_positions[tile]
                x1, y1 = divmod(i, self.size)
                x2, y2 = divmod(goal_pos, self.size)
                distance += abs(x1 - x2) + abs(y1 - y2)
        return distance

    def best_first_search(self, start, heuristic):
        visited = set()
        queue = [(heuristic(start), 0, start, [])]
        visited.add(tuple(start))
        nodes_expanded = 0
        start_time = time.time()

        while queue:
            _, g_score, current, path = heapq.heappop(queue)
            nodes_expanded += 1

            if current == self.goal:
                return path + [current], nodes_expanded, time.time() - start_time

            for neighbor in self.get_neighbors(current):
                neighbor_tuple = tuple(neighbor)
                if neighbor_tuple not in visited:
                    visited.add(neighbor_tuple)
                    new_g = g_score + 1
                    f = new_g + heuristic(neighbor)
                    heapq.heappush(queue, (f, new_g, neighbor, path + [current]))

        return [], nodes_expanded, time.time() - start_time


# ---------------------------- GUI Setup ----------------------------
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
BUTTON_COLOR = (75, 0, 130)
HOVER_COLOR = (128, 0, 128)
TEXT_COLOR = (255, 255, 255)
TITLE_COLOR = (255, 255, 255)
BG_COLOR = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("N-Puzzle Solver")

font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)

class Button:
    def __init__(self, text, x, y, width=200, height=50, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = BUTTON_COLOR
        self.hover = False

    def draw(self, surface):
        color = HOVER_COLOR if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surf = font_medium.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.action
        return None


# ---------------------------- Screens ----------------------------
def main_menu():
    buttons = [
        Button("Start", SCREEN_WIDTH//2 - 100, 250, action="start"),
        Button("About", SCREEN_WIDTH//2 - 100, 350, action="about"),
        Button("Quit", SCREEN_WIDTH//2 - 100, 450, action="quit")
    ]
    while True:
        screen.fill(BG_COLOR)
        title = font_large.render("N-Puzzle Solver", True, TITLE_COLOR)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            for button in buttons:
                action = button.handle_event(event)
                if action == "start":
                    size_select()
                elif action == "about":
                    about_screen()
                elif action == "quit":
                    pygame.quit()
                    return

def size_select():
    buttons = [
        Button("3x3", SCREEN_WIDTH//2 - 100, 250, action=3),
        Button("4x4", SCREEN_WIDTH//2 - 100, 350, action=4),
        Button("5x5", SCREEN_WIDTH//2 - 100, 450, action=5)
    ]
    while True:
        screen.fill(BG_COLOR)
        title = font_large.render("Select Puzzle Size", True, TITLE_COLOR)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            for button in buttons:
                action = button.handle_event(event)
                if action:
                    heuristic_select(action)
                    return

def heuristic_select(size):
    buttons = [
        Button("Manhattan", SCREEN_WIDTH//2 - 100, 250, action="manhattan"),
        Button("Misplaced", SCREEN_WIDTH//2 - 100, 350, action="misplaced")
    ]
    while True:
        screen.fill(BG_COLOR)
        title = font_large.render("Select Heuristic", True, TITLE_COLOR)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            for button in buttons:
                action = button.handle_event(event)
                if action:
                    puzzle = NPuzzle(size)
                    start_state = puzzle.generate_random_state()
                    if action == "manhattan":
                        heuristic = puzzle.manhattan_distance
                    else:
                        heuristic = puzzle.manhattan_distance
                    solve_puzzle(puzzle, start_state, heuristic)
                    return

def solve_puzzle(puzzle, start_state, heuristic):
    path, expanded, duration = puzzle.best_first_search(start_state, heuristic)
    running = True
    step = 0

    while running:
        screen.fill(BG_COLOR)
        if path:
            state = path[step]
            draw_puzzle(state, puzzle.size)
            info = font_medium.render(f"Steps: {len(path)-1}, Nodes: {expanded}, Time: {duration:.2f}s", True, TEXT_COLOR)
            screen.blit(info, (20, 20))
        else:
            info = font_medium.render("No Solution Found", True, TEXT_COLOR)
            screen.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, SCREEN_HEIGHT//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        if path and step < len(path) - 1:
            pygame.time.delay(500)
            step += 1


def draw_puzzle(state, size):
    tile_size = min(SCREEN_WIDTH, SCREEN_HEIGHT) // (size + 2)
    offset_x = (SCREEN_WIDTH - tile_size * size) // 2
    offset_y = (SCREEN_HEIGHT - tile_size * size) // 2

    for i, tile in enumerate(state):
        if tile != 0:
            row, col = divmod(i, size)
            rect = pygame.Rect(offset_x + col * tile_size, offset_y + row * tile_size, tile_size, tile_size)
            pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=5)
            text = font_medium.render(str(tile), True, TEXT_COLOR)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)


def about_screen():
    running = True
    while running:
        screen.fill(BG_COLOR)
        lines = [
            "N-Puzzle Solver",
            "Developed in Python with Pygame",
            "Algorithms: Best-First Search",
            "Press ESC to return"
        ]
        for i, line in enumerate(lines):
            text = font_medium.render(line, True, TEXT_COLOR)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200 + i*50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False


# ---------------------------- Main ----------------------------
if __name__ == "__main__":
    main_menu()

