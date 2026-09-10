from pathlib import Path
from tempfile import TemporaryDirectory

from solve_maze import Maze, Tile

SQUARE = """\
.....
.S-7.
.|.|.
.L-J.
....."""

SQUARE_WITH_JUNK = """\
-L|F7
7S-7|
L|7||
-L-J|
L|-JF"""

BENT = """\
..F7.
.FJ|.
SJ.L7
|F--J
LJ..."""

BENT_WITH_JUNK = """\
7-F7-
.FJ|7
SJLL7
|F--J
LJ.LJ"""

NEST = """\
...........
.S-------7.
.|F-----7|.
.||.....||.
.||.....||.
.|L-7.F-J|.
.|..|.|..|.
.L--J.L--J.
..........."""

SQUEEZE = """\
..........
.S------7.
.|F----7|.
.||....||.
.||....||.
.|L-7F-J|.
.|..||..|.
.L--JL--J.
.........."""

LARGE = """\
.F----7F7F7F7F-7....
.|F--7||||||||FJ....
.||.FJ||||||||L7....
FJL7L7LJLJ||LJ.L-7..
L--J.L7...LJS7F-7L7.
....F-J..F7FJ|L7L7L7
....L7.F7||L7|.L7L7|
.....|FJLJ|FJ|F7|.LJ
....FJL-7.||.||||...
....L---J.LJ.LJLJ..."""

JUNK = """\
FF7FSF7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJ7F7FJ-
L---JF-JLJ.||-FJLJJ7
|F|F-JF---7F7-L7L|7|
|FFJF7L7F-JF7|JL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJ|||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L"""


def test_start_is_f_on_square() -> None:
    maze = Maze(SQUARE)
    assert maze.start == Tile(1, 1)
    assert maze.start_pipe == "F"


def test_farthest() -> None:
    assert Maze(SQUARE).farthest() == 4
    assert Maze(SQUARE_WITH_JUNK).farthest() == 4
    assert Maze(BENT).farthest() == 8
    assert Maze(BENT_WITH_JUNK).farthest() == 8


def test_enclosed() -> None:
    assert Maze(NEST).enclosed() == 4
    assert Maze(SQUEEZE).enclosed() == 4
    assert Maze(LARGE).enclosed() == 8
    assert Maze(JUNK).enclosed() == 10


def test_svg_marks_route_and_start() -> None:
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "route.svg"
        maze = Maze(SQUARE)
        maze.write_svg(path)
        svg = path.read_text(encoding="utf-8")
    assert "polyline" in svg
    assert "<circle" in svg


if __name__ == "__main__":
    test_start_is_f_on_square()
    test_farthest()
    test_enclosed()
    test_svg_marks_route_and_start()
    print("ok")
