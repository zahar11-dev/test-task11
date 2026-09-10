from pathlib import Path
from typing import NamedTuple


class Delta(NamedTuple):
    dr: int
    dc: int

    @property
    def opposite(self) -> "Delta":
        return Delta(-self.dr, -self.dc)


class Tile(NamedTuple):
    row: int
    col: int

    def __add__(self, delta: Delta) -> "Tile":
        return Tile(self.row + delta.dr, self.col + delta.dc)


NORTH = Delta(-1, 0)
SOUTH = Delta(1, 0)
WEST = Delta(0, -1)
EAST = Delta(0, 1)
CARDINALS = (NORTH, SOUTH, WEST, EAST)

PIPES: dict[str, frozenset[Delta]] = {
    "|": frozenset({NORTH, SOUTH}),
    "-": frozenset({WEST, EAST}),
    "L": frozenset({NORTH, EAST}),
    "J": frozenset({NORTH, WEST}),
    "7": frozenset({SOUTH, WEST}),
    "F": frozenset({SOUTH, EAST}),
}
PIPE_FROM_ENDS = {ends: symbol for symbol, ends in PIPES.items()}
NORTH_FACING = frozenset({"|", "L", "J"})


class Maze:
    def __init__(self, sketch: str) -> None:
        self._grid = [line for line in sketch.splitlines() if line]
        self.start = self._locate_start()
        self.start_pipe = self._infer_start_pipe()
        self._loop = self._follow_loop()
        self._interior = self._find_interior()

    def farthest(self) -> int:
        return len(self._loop) // 2

    def enclosed(self) -> int:
        return len(self._interior)

    def write_svg(self, path: Path) -> None:
        path.write_text(self._svg(), encoding="utf-8")

    def _contains(self, tile: Tile) -> bool:
        return 0 <= tile.row < len(self._grid) and 0 <= tile.col < len(self._grid[0])

    def _symbol(self, tile: Tile) -> str:
        return self._grid[tile.row][tile.col]

    def _pipe_at(self, tile: Tile) -> str:
        symbol = self._symbol(tile)
        return self.start_pipe if symbol == "S" else symbol

    def _locate_start(self) -> Tile:
        for row, line in enumerate(self._grid):
            col = line.find("S")
            if col != -1:
                return Tile(row, col)
        raise LookupError("S")

    def _infer_start_pipe(self) -> str:
        openings = []
        for delta in CARDINALS:
            neighbor = self.start + delta
            if not self._contains(neighbor):
                continue
            if delta.opposite in PIPES.get(self._symbol(neighbor), frozenset()):
                openings.append(delta)
        return PIPE_FROM_ENDS[frozenset(openings)]

    def _follow_loop(self) -> list[Tile]:
        heading = next(iter(PIPES[self.start_pipe]))
        tile = self.start + heading
        inbound = heading.opposite
        loop = [self.start]
        while tile != self.start:
            loop.append(tile)
            (heading,) = PIPES[self._pipe_at(tile)] - {inbound}
            tile = tile + heading
            inbound = heading.opposite
        return loop

    def _find_interior(self) -> set[Tile]:
        on_loop = set(self._loop)
        interior: set[Tile] = set()
        for row, raw in enumerate(self._grid):
            inside = False
            for col in range(len(raw)):
                tile = Tile(row, col)
                if tile in on_loop:
                    if self._pipe_at(tile) in NORTH_FACING:
                        inside = not inside
                elif inside:
                    interior.add(tile)
        return interior

    def _svg(self) -> str:
        cell, legend = 8, 28
        bg, loop, inside, route, start, ink = (
            "#16181d",
            "#3d9be9",
            "#3fa66b",
            "#e8f4ff",
            "#ff4d4d",
            "#c8cdd6",
        )
        rows, cols = len(self._grid), len(self._grid[0])
        width, height = cols * cell, rows * cell + legend
        tiles = [
            f'<rect x="{tile.col * cell}" y="{tile.row * cell}" '
            f'width="{cell}" height="{cell}" fill="{inside}"/>'
            for tile in self._interior
        ]
        tiles.extend(
            f'<rect x="{tile.col * cell}" y="{tile.row * cell}" '
            f'width="{cell}" height="{cell}" fill="{loop}"/>'
            for tile in self._loop
        )
        points = " ".join(
            f"{tile.col * cell + cell / 2},{tile.row * cell + cell / 2}"
            for tile in (*self._loop, self._loop[0])
        )
        sx = self.start.col * cell + cell / 2
        sy = self.start.row * cell + cell / 2
        ly = rows * cell + 18
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
            f'<rect width="100%" height="100%" fill="{bg}"/>'
            f"{''.join(tiles)}"
            f'<polyline points="{points}" fill="none" stroke="{route}" '
            f'stroke-width="1.5" stroke-linejoin="round"/>'
            f'<circle cx="{sx}" cy="{sy}" r="4" fill="{start}"/>'
            f'<g font-family="system-ui,sans-serif" font-size="12" fill="{ink}">'
            f'<rect x="8" y="{ly - 10}" width="10" height="10" fill="{loop}"/>'
            f'<text x="22" y="{ly}">loop</text>'
            f'<rect x="68" y="{ly - 10}" width="10" height="10" fill="{inside}"/>'
            f'<text x="82" y="{ly}">inside</text>'
            f'<circle cx="148" cy="{ly - 5}" r="4" fill="{start}"/>'
            f'<text x="158" y="{ly}">start</text>'
            f"</g></svg>\n"
        )


def main() -> None:
    here = Path(__file__).resolve().parent
    maze = Maze((here / "puzzle_input.txt").read_text())
    maze.write_svg(here / "route.svg")
    print(maze.farthest())
    print(maze.enclosed())
    print(here / "route.svg")


if __name__ == "__main__":
    main()
