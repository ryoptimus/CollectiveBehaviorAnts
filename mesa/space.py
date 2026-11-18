"""Minimal MultiGrid implementation for Project 05."""

from __future__ import annotations


class MultiGrid:
    def __init__(self, width, height, torus=False):
        self.width = int(width)
        self.height = int(height)
        self.torus = bool(torus)
        self._grid = [[[] for _ in range(self.height)] for _ in range(self.width)]

    def _normalize_pos(self, pos):
        x, y = pos
        x, y = int(x), int(y)
        if self.torus:
            return (x % self.width, y % self.height)
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise IndexError(f"Position {(x, y)} is outside grid {self.width}x{self.height}")
        return (x, y)

    def out_of_bounds(self, pos):
        x, y = pos
        return x < 0 or y < 0 or x >= self.width or y >= self.height

    def torus_adj(self, pos):
        x, y = pos
        if self.torus:
            return (x % self.width, y % self.height)
        return (x, y)

    def place_agent(self, agent, pos):
        pos = self._normalize_pos(pos)
        # If the agent was already on this grid, remove its previous reference.
        old_pos = getattr(agent, "pos", None)
        if old_pos is not None:
            try:
                old_pos = self._normalize_pos(old_pos)
                if agent in self._grid[old_pos[0]][old_pos[1]]:
                    self._grid[old_pos[0]][old_pos[1]].remove(agent)
            except Exception:
                pass
        self._grid[pos[0]][pos[1]].append(agent)
        agent.pos = pos

    def move_agent(self, agent, pos):
        self.place_agent(agent, pos)

    def remove_agent(self, agent):
        pos = getattr(agent, "pos", None)
        if pos is None:
            return
        pos = self._normalize_pos(pos)
        if agent in self._grid[pos[0]][pos[1]]:
            self._grid[pos[0]][pos[1]].remove(agent)
        agent.pos = None

    def _iter_positions(self, cell_list):
        # Mesa commonly receives [(x, y), ...]. Many notebooks pass a single
        # (x, y) tuple, so support that too.
        if isinstance(cell_list, tuple) and len(cell_list) == 2 and not isinstance(cell_list[0], (tuple, list)):
            yield self._normalize_pos(cell_list)
            return
        for pos in cell_list:
            yield self._normalize_pos(pos)

    def get_cell_list_contents(self, cell_list):
        contents = []
        for x, y in self._iter_positions(cell_list):
            contents.extend(list(self._grid[x][y]))
        return contents

    def get_neighborhood(self, pos, moore=True, include_center=False, radius=1):
        x, y = self._normalize_pos(pos)
        cells = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0 and not include_center:
                    continue
                if not moore and abs(dx) + abs(dy) > radius:
                    continue
                nx, ny = x + dx, y + dy
                if self.torus:
                    cells.append((nx % self.width, ny % self.height))
                elif 0 <= nx < self.width and 0 <= ny < self.height:
                    cells.append((nx, ny))
        return cells

    def get_neighbors(self, pos, moore=True, include_center=False, radius=1):
        return self.get_cell_list_contents(self.get_neighborhood(pos, moore, include_center, radius))

    def iter_neighbors(self, pos, moore=True, include_center=False, radius=1):
        yield from self.get_neighbors(pos, moore, include_center, radius)

    def is_cell_empty(self, pos):
        x, y = self._normalize_pos(pos)
        return len(self._grid[x][y]) == 0

    def coord_iter(self):
        for x in range(self.width):
            for y in range(self.height):
                yield (self._grid[x][y], x, y)
