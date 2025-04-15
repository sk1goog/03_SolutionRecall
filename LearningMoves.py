#!/usr/bin/env python3
import csv
import json
import random
import time
import os
import copy

# Globales Skriptverzeichnis
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ======================================================================
# Parameter-, Startpositions- und Mapping-Funktionen
# ======================================================================
def load_parameters_from_csv(filename="parameter_csv-Parameter.csv"):
    """
    Liest Parameter aus der CSV-Datei im Skriptverzeichnis.
    Es wird eine zufällige Parametergruppe ausgewählt.
    Liefert ein Tupel (parameters, chosen_set).
    """
    filepath = os.path.join(SCRIPT_DIR, filename)
    with open(filepath, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        rows = list(reader)
    if not rows:
        raise ValueError("Die CSV-Datei ist leer.")
    header = rows[0]
    num_sets = len(header) - 1  # Erste Spalte sind Parameternamen
    chosen_index = random.randint(1, num_sets)
    chosen_set = header[chosen_index].strip()
    parameters = {}
    for row in rows[1:]:
        if not row or len(row) < chosen_index + 1:
            continue
        key = row[0].strip()
        value_str = row[chosen_index].strip()
        value_str_clean = value_str.replace(".", "")
        try:
            value = int(value_str_clean)
        except ValueError:
            try:
                value = float(value_str_clean)
            except ValueError:
                value = value_str
        if " " in key:
            main_key, sub_key = key.split(" ", 1)
            if main_key not in parameters:
                parameters[main_key] = {}
            parameters[main_key][sub_key] = value
        else:
            parameters[key] = value
    return parameters, chosen_set

def load_cube_from_csv():
    """
    Liest die Startposition des Würfels aus der CSV-Datei (csv_export-StartPos.csv).
    Erwartet mindestens zwei Zeilen, wobei die zweite Zeile die 54 Farbcodes enthält.
    """
    csv_path = os.path.join(SCRIPT_DIR, "csv_export-StartPos.csv")
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        rows = list(reader)
    if len(rows) < 2:
        raise ValueError("CSV-Datei muss mindestens zwei Zeilen enthalten.")
    colors = rows[1]
    if len(colors) != 54:
        raise ValueError(f"Erwartet 54 Farbcodes, gefunden: {len(colors)}")
    return colors

def load_mappings(filename="mappings.json"):
    """
    Liest die Mappings (Rotationstransformationen) aus einer JSON-Datei.
    """
    filepath = os.path.join(SCRIPT_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# ======================================================================
# Funktionen zur Würfeltransformation
# ======================================================================
def apply_move(cube_state, move, moves_mapping):
    """
    Wendet einen einzelnen Zug (move) auf den cube_state an.
    moves_mapping enthält Quell-/Zielpositionen als Strings (Positionen 1–54).
    """
    new_state = cube_state.copy()
    for src_str, tgt in moves_mapping.get(move, {}).items():
        new_state[int(tgt) - 1] = cube_state[int(src_str) - 1]
    return new_state

def apply_sequence(cube_state, sequence, moves_mapping):
    """
    Wendet eine Sequenz von Zügen (Liste von Moves) nacheinander an.
    """
    for move in sequence:
        cube_state = apply_move(cube_state, move, moves_mapping)
    return cube_state

def cube_to_string(cube_state):
    """
    Gibt eine formatierte Darstellung des Würfelzustands zurück.
    """
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

# ======================================================================
# Funktionen zur Zustandsbewertung (20 bewegliche Steine)
# ======================================================================
def get_correct_pieces(cube_state, target_pieces):
    """
    Bestimmt anhand des aktuellen Zustands, welche beweglichen Steine (Ecken und Kanten)
    korrekt positioniert und orientiert sind. target_pieces ist ein Dictionary, z. B.:
       "E1": ((1, 12, 25), ('w', 'r', 'g'))
    """
    return {
        piece for piece, (positions, colors) in target_pieces.items()
        if all(cube_state[pos - 1] == col for pos, col in zip(positions, colors))
    }

def count_correct_pieces(cube_state, target_pieces):
    """
    Zählt die Anzahl der beweglichen Steine, die korrekt positioniert sind.
    Der Würfel gilt als gelöst, wenn 20 Steine korrekt sind.
    """
    return len(get_correct_pieces(cube_state, target_pieces))

# ======================================================================
# Globale Definitionen: Zielzustände, Ebenen und erlaubte Moves
# ======================================================================
pieces_level1 = {
    "E1": ((1, 12, 25), ('w', 'r', 'g')),
    "E2": ((3, 27, 28), ('w', 'g', 'o')),
    "E3": ((9, 34, 39), ('w', 'o', 'b')),
    "E4": ((7, 18, 37), ('w', 'r', 'b')),
    "K1": ((4, 15),    ('w', 'r')),
    "K2": ((2, 26),    ('w', 'g')),
    "K3": ((6, 31),    ('w', 'o')),
    "K4": ((8, 38),    ('w', 'b')),
}
pieces_level2 = {
    "K5": ((17, 40), ('r', 'b')),
    "K6": ((11, 22), ('r', 'g')),
    "K7": ((24, 29), ('g', 'o')),
    "K8": ((35, 42), ('o', 'b')),
}
pieces_level3 = {
    "E5":  ((10, 19, 52), ('r', 'g', 'y')),
    "E6":  ((21, 30, 54), ('g', 'o', 'y')),
    "E7":  ((36, 45, 48), ('o', 'b', 'y')),
    "E8":  ((16, 43, 46), ('r', 'b', 'y')),
    "K9":  ((13, 49),     ('r', 'y')),
    "K10": ((20, 53),     ('g', 'y')),
    "K11": ((33, 51),     ('o', 'y')),
    "K12": ((44, 47),     ('b', 'y')),
}
levels = {
    "E1": {**pieces_level1},
    "E2": {**pieces_level1, **pieces_level2},
    "E3": {**pieces_level1, **pieces_level2, **pieces_level3},
}
TARGET_CORRECT = 20  # Gelöst: 20 korrekt positionierte bewegliche Steine
allowed_moves_global = ["F", "Fb", "U", "Ub", "L", "Lb", "R", "Rb", "B", "Bb", "D", "Db"]

# ======================================================================
# Laden der gelernten Zugfolgen aus Improvements.csv
# ======================================================================
def load_learned_moves(filename):
    learned = []
    filepath = os.path.join(SCRIPT_DIR, filename)
    if not os.path.exists(filepath):
        return learned
    with open(filepath, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            if "Move Sequence" not in row or not row["Move Sequence"]:
                continue
            try:
                row["Start Count"] = int(row["Start Count"])
                row["End Count"] = int(row["End Count"])
                row["Improvement Count"] = int(row["Improvement Count"])
                row["Move Count"] = int(row["Move Count"])
                row["Value"] = float(row["Value"])
            except Exception:
                pass
            learned.append(row)
    return learned

# ======================================================================
# Optimierungsalgorithmus (neue Version)
# ======================================================================
def optimize_cube(params, starting_state, moves_mapping, learned_moves):
    """
    Optimiert den Würfel, indem Zugfolgen (aus Improvements.csv) so angewendet werden, dass die 
    Anzahl korrekt positionierter beweglicher Steine steigt.
    
    Vorgehen:
      - Vom (eventuell gemischten) Ausgangszustand wird iterativ ein Kandidat gesucht,
        der durch Anwendung einer Zugfolge zu einem Anstieg der korrekt positionierten Steine führt.
      - Falls in der aktuellen Kombination keine Verbesserung erzielt wird, wird diese Kombination
        intern gesperrt und der Zustand auf den ursprünglichen Ausgangszustand zurückgesetzt.
    """
    # Zustandsbewertung auf Basis von Level "E3" (alle 20 Steine)
    level_targets = levels["E3"]
    current_state = starting_state.copy()
    starting_state_saved = starting_state.copy()
    print("Startzahl korrekt positionierter Steine:", count_correct_pieces(current_state, level_targets))
    
    combination_history = set()  # Gesperrte Kombinationen (als Tuple)
    current_combination = []      # Aktuell angewandte Zugfolgen (Liste von Strings)
    
    # Hier holen wir den Wert für MAX_ITERATIONS aus den Parametern für Level "E3" (als Integer)
    max_iterations = params["MAX_ITERATIONS"]["E3"]
    
    iteration = 0
    while count_correct_pieces(current_state, level_targets) < TARGET_CORRECT and iteration < max_iterations:
        improvement_found = False
        random.shuffle(learned_moves)
        for candidate in learned_moves:
            candidate_sequence = candidate["Move Sequence"]  # z. B. "R Fb"
            candidate_key = tuple(current_combination + [candidate_sequence])
            if candidate_key in combination_history:
                continue
            
            # Falls in "Starting Positions" Bedingungen definiert sind, diese prüfen:
            start_positions = candidate.get("Starting Positions", "").strip()
            if start_positions:
                required_pieces = start_positions.split("-")
                current_correct = get_correct_pieces(current_state, level_targets)
                if not all(piece in current_correct for piece in required_pieces):
                    continue
            candidate_moves = candidate_sequence.split()
            candidate_state = apply_sequence(current_state.copy(), candidate_moves, moves_mapping)
            current_count = count_correct_pieces(current_state, level_targets)
            candidate_count = count_correct_pieces(candidate_state, level_targets)
            if candidate_count > current_count:
                current_state = candidate_state
                current_combination.append(candidate_sequence)
                improvement_found = True
                if iteration % 100 == 0:
                    print(f"Iteration {iteration}: Verbesserung erzielt, korrekt: {candidate_count}")
                break
        
        if not improvement_found:
            combination_history.add(tuple(current_combination))
            if iteration % 100 == 0:
                print(f"Iteration {iteration}: Keine Verbesserung, Kombination zurückgesetzt.")
            current_state = starting_state_saved.copy()
            current_combination = []
        iteration += 1
    
    solved = (count_correct_pieces(current_state, level_targets) == TARGET_CORRECT)
    return current_state, current_combination, solved, iteration

# ======================================================================
# Hauptprogramm
# ======================================================================
def main():
    # Parameter einlesen
    params, chosen_set = load_parameters_from_csv()
    print("Verwendete Parametergruppe:", chosen_set)
    
    # Startposition laden
    try:
        starting_state = load_cube_from_csv()  # Liste mit 54 Farbcodes
    except Exception as e:
        print("Fehler beim Laden der Startposition:", e)
        return
    print("Ausgangszustand des Würfels:")
    print(cube_to_string(starting_state))
    print("Anzahl korrekt positionierter Steine (Level E1):", count_correct_pieces(starting_state, levels["E1"]))
    
    # Mappings laden
    try:
        moves_mapping = load_mappings("mappings.json")
    except Exception as e:
        print("Fehler beim Laden der Mappings:", e)
        return
    
    # Mischen, falls NO_MOVES_TO_SHUFFLE > 0
    no_moves_to_shuffle = params.get("NO_MOVES_TO_SHUFFLE", 0)
    if no_moves_to_shuffle > 0:
        shuffle_sequence = [random.choice(allowed_moves_global) for _ in range(no_moves_to_shuffle)]
        original_state = starting_state.copy()
        starting_state = apply_sequence(starting_state, shuffle_sequence, moves_mapping)
        print("Nach dem Mischen:")
        print(cube_to_string(starting_state))
        print("Mischzugfolge:", " ".join(shuffle_sequence))
    
    # Gelernte Zugfolgen aus Improvements.csv laden
    improvements_filename = os.path.join(SCRIPT_DIR, "Improvements.csv")
    learned_moves = load_learned_moves(improvements_filename)
    if not learned_moves:
        print("Keine gelernten Zugfolgen in", improvements_filename, "gefunden.")
        return
    
    # Optimierungsphase: Anwenden gelernter Zugfolgen
    final_state, combination, solved, iterations = optimize_cube(params, starting_state, moves_mapping, learned_moves)
    
    print("\nFinaler Würfelzustand:")
    print(cube_to_string(final_state))
    print("Iterationen:", iterations)
    
    # Gesamte Zugfolge als Konkatenation aller angewandten Zugfolgen
    total_moves_list = []
    for seq in combination:
        total_moves_list.extend(seq.split())
    total_moves = len(total_moves_list)
    
    if solved:
        print(f"\nWürfel gelöst! Gesamtanzahl an Zügen: {total_moves}")
    else:
        print("\nWürfel nicht vollständig gelöst.")
    
    # Ausgabe der einzelnen angewandten Zugfolgen
    print("\nEinzelne angewandte Zugfolgen (in Reihenfolge):")
    for idx, seq in enumerate(combination, start=1):
        print(f"{idx}: {seq}")
    
    # Ausgabe der gesamten Zugfolge (als verketteter String)
    print("\nGesamte Zugfolge (verkettet):")
    print(" ".join(total_moves_list))

if __name__ == '__main__':
    main()