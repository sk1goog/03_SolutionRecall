#!/usr/bin/env python3
import json, csv, os

def load_cube():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "csv_export-StartPos.csv")
    cube = list(csv.reader(open(path, newline='', encoding='utf-8'), delimiter=';'))[1]
    if len(cube) != 54:
        raise ValueError("Cube must have 54 colors")
    return cube

def load_mappings():
    return json.load(open("mappings.json", "r", encoding="utf-8"))

def apply_move(cube, move, mapping):
    new_cube = cube.copy()
    for src, tgt in mapping.get(move, {}).items():
        new_cube[int(tgt) - 1] = cube[int(src) - 1]
    return new_cube

def apply_moves(cube, moves, mapping):
    for move in moves:
        cube = apply_move(cube, move, mapping)
    return cube

def cube_to_string(cube_state):
    def col(pos):
        return cube_state[pos - 1]
    lines = [
        f"        {col(19)} {col(20)} {col(21)}",
        f"        {col(22)} {col(23)} {col(24)}",
        f"        {col(25)} {col(26)} {col(27)}",
        f"{col(10)} {col(11)} {col(12)} | {col(1)} {col(2)} {col(3)} | {col(28)} {col(29)} {col(30)}",
        f"{col(13)} {col(14)} {col(15)} | {col(4)} {col(5)} {col(6)} | {col(31)} {col(32)} {col(33)}",
        f"{col(16)} {col(17)} {col(18)} | {col(7)} {col(8)} {col(9)} | {col(34)} {col(35)} {col(36)}",
        f"        {col(37)} {col(38)} {col(39)}",
        f"        {col(40)} {col(41)} {col(42)}",
        f"        {col(43)} {col(44)} {col(45)}",
        f"        {col(46)} {col(47)} {col(48)}",
        f"        {col(49)} {col(50)} {col(51)}",
        f"        {col(52)} {col(53)} {col(54)}"
    ]
    return "\n".join(lines)

def main():
    cube = load_cube()
    mapping = load_mappings()
    
    print("----- Cube Starting Position -----")
    print(cube_to_string(cube))
    
    while True:
        inp = input("\nEnter a sequence of moves (or 'stop'): ").strip()
        if inp.lower() == "stop":
            break
        if inp:
            moves = inp.split()
            cube = apply_moves(cube, moves, mapping)
            print("\n----- Current Cube Position -----")
            print(cube_to_string(cube))
    
    print("\n----- Final Cube Position -----")
    print(cube_to_string(cube))

if __name__ == '__main__':
    main()