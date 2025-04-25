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
def load_parameters_from_csv(filename="Parameter.csv"):
    """
    Liest Parameter aus der CSV-Datei.
    Erwartete Schlüssel:
      - NO_MOVES_TO_SHUFFLE
      - MAX_ITERATIONS E3
      - TOTAL_RUNS
      - SOLUTIONS_PER_RUN
    Liefert ein Dictionary.
    """
    filepath = os.path.join(SCRIPT_DIR, filename)
    parameters = {}
    with open(filepath, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        header = next(reader)  # Überschrift überspringen
        for row in reader:
            if not row or len(row) < 2:
                continue
            key = row[0].strip()
            value_str = row[1].strip()
            value_str_clean = value_str.replace(".", "")
            try:
                value = int(value_str_clean)
            except ValueError:
                try:
                    value = float(value_str_clean)
                except ValueError:
                    value = value_str
            parameters[key] = value
    return parameters

def load_cube_from_csv():
    """
    Liest die Startposition (54 Farbcodes) aus der CSV-Datei (csv_export-StartPos.csv).
    """
    csv_path = os.path.join(SCRIPT_DIR, "csv_export-StartPos.csv")
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        rows = list(reader)
    if len(rows) < 2:
        raise ValueError("CSV file must contain at least two rows.")
    colors = rows[1]
    if len(colors) != 54:
        raise ValueError(f"Expected 54 color codes, found: {len(colors)}")
    return colors

def load_mappings(filename="mappings.json"):
    """
    Liest die Mappings (Rotationstransformationen) aus der JSON-Datei.
    """
    filepath = os.path.join(SCRIPT_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# ======================================================================
# Funktionen zur Würfeltransformation
# ======================================================================
def apply_move(cube_state, move, moves_mapping):
    """
    Wendet einen Zug an. moves_mapping enthält die Transformationen.
    """
    new_state = cube_state.copy()
    for src_str, tgt in moves_mapping.get(move, {}).items():
        new_state[int(tgt) - 1] = cube_state[int(src_str) - 1]
    return new_state

def apply_sequence(cube_state, sequence, moves_mapping):
    """
    Wendet eine Liste von Zügen (Sequenz) nacheinander an.
    """
    for move in sequence:
        cube_state = apply_move(cube_state, move, moves_mapping)
    return cube_state

def cube_to_string(cube_state):
    """
    Gibt den Würfelzustand formatiert zurück.
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
    Gibt die Menge der korrekt positionierten beweglichen Steine zurück.
    """
    return {piece for piece, (positions, colors) in target_pieces.items()
            if all(cube_state[pos - 1] == col for pos, col in zip(positions, colors))}

def count_correct_pieces(cube_state, target_pieces):
    """
    Zählt, wie viele bewegliche Steine korrekt positioniert sind.
    """
    return len(get_correct_pieces(cube_state, target_pieces))


# ======================================================================
# Globale Definitionen: Ebenen und erlaubte Moves
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
TARGET_CORRECT = 20  # Cube gelöst, wenn 20 Steine korrekt sind.
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
# Optimierungsalgorithmus (ohne parallele Suche)
# ======================================================================
def optimize_cube(params, starting_state, moves_mapping, learned_moves, combination_history):
    """
    Optimiert den Würfel vom gegebenen Ausgangszustand, indem Zugfolgen iterativ angewendet werden,
    bis der Cube gelöst ist oder die maximale Iterationszahl erreicht wird.
    
    "Kombination" := Verkettung mehrerer Zugfolgen.
    Eine Kombination wird als "erschöpft" markiert (und in combination_history gespeichert),
    wenn alle möglichen Erweiterungen für diese Kombination ausprobiert wurden oder sie bereits zur Lösung geführt hat.
    
    Die combination_history gilt für den gesamten Run (oder Versuch) und wird nicht zurückgesetzt.
    
    Rückgabe: finaler Zustand, die aktuell angewandte (unvollständige) Kombination, ob der Cube gelöst ist,
    und die Anzahl der Iterationen.
    """
    level_targets = levels["E3"]
    current_state = starting_state.copy()
    starting_state_saved = starting_state.copy()
    print("Startzahl korrekt positionierter Steine:", count_correct_pieces(current_state, level_targets))
    
    current_combination = []  # Aktuelle Verkettung von Zugfolgen
    max_iterations = params["MAX_ITERATIONS E3"]
    iteration = 0
    while count_correct_pieces(current_state, level_targets) < TARGET_CORRECT and iteration < max_iterations:
        improvement_found = False
        
        # Erstelle Liste der Kandidaten, deren Erweiterung (als Kombination) noch nicht erschöpft ist.
        viable_candidates = []
        for candidate in learned_moves:
            candidate_sequence = candidate["Move Sequence"]
            candidate_key = tuple(current_combination + [candidate_sequence])
            if candidate_key not in combination_history:
                viable_candidates.append(candidate)
                
        # Wenn keine viable Kandidaten mehr vorhanden sind, gilt die aktuelle Kombination als erschöpft.
        if not viable_candidates:
            if current_combination:
                combination_history.add(tuple(current_combination))
            current_state = starting_state_saved.copy()
            current_combination = []
            iteration += 1
            if iteration % 1000 == 0:
                print(iteration)
            continue
        
        # Versuche, die aktuelle Kombination zu erweitern.
        for candidate in viable_candidates:
            candidate_sequence = candidate["Move Sequence"]
            candidate_key = tuple(current_combination + [candidate_sequence])
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
                # Wenn der Cube gelöst ist, markiere diese Kombination als erschöpft.
                if count_correct_pieces(current_state, level_targets) == TARGET_CORRECT:
                    combination_history.add(tuple(current_combination))
                improvement_found = True
                break
        
        if not improvement_found:
            if current_combination:
                combination_history.add(tuple(current_combination))
            current_state = starting_state_saved.copy()
            current_combination = []
        iteration += 1
        if iteration % 1000 == 0:
            print(iteration)
    
    solved = (count_correct_pieces(current_state, level_targets) == TARGET_CORRECT)
    return current_state, current_combination, solved, iteration


# ======================================================================
# Funktion zum sofortigen Abspeichern jeder Lösung in "Results.csv"
# Spalten:
#   - RunID (fortlaufende Nummer)
#   - RunDateTime (Zeitpunkt des Run-Beginns)
#   - Start State (gemischter Ausgangszustand)
#   - Solution Time (elapsed time seit Run-Beginn, hh:mm:ss)
#   - Solution Iterations (Iteration, in der diese Lösung erzielt wurde)
#   - Solution Move Sequence (verkettete Zugfolge)
#   - Total Moves (Anzahl der Züge)
# ======================================================================
def save_results(run_id, run_datetime, start_state_str, solution_time, solution_iterations, solution_move_sequence, total_moves, results_filename="Results.csv"):
    header = ["RunID", "RunDateTime", "Start State", "Solution Time", "Solution Iterations", "Solution Move Sequence", "Total Moves"]
    filepath = os.path.join(SCRIPT_DIR, results_filename)
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        if not file_exists:
            writer.writerow(header)
        writer.writerow([run_id, run_datetime, start_state_str, solution_time, solution_iterations, solution_move_sequence, total_moves])


# ======================================================================
# Hauptprogramm: Wiederholte Runs mit konstanter Startposition pro Run.
# Das combination_history-Sperrset gilt für alle Versuche in einem Run.
# ======================================================================
def main():
    params = load_parameters_from_csv()
    total_runs = params["TOTAL_RUNS"]
    solutions_per_run = params["SOLUTIONS_PER_RUN"]
    
    print("Verwendete Parameter:", params)
    
    # Ursprüngliche Startposition laden (unverändert)
    try:
        original_state = load_cube_from_csv()
    except Exception as e:
        print("Fehler beim Laden der Startposition:", e)
        return
    print("Ausgangszustand des Würfels:")
    print(cube_to_string(original_state))
    print("Anzahl korrekt positionierter Steine (Level E1):", count_correct_pieces(original_state, levels["E1"]))
    
    # Mappings laden
    try:
        moves_mapping = load_mappings("mappings.json")
    except Exception as e:
        print("Fehler beim Laden der Mappings:", e)
        return
    
    # Gelernte Zugfolgen laden
    improvements_filename = os.path.join(SCRIPT_DIR, "Improvements.csv")
    learned_moves = load_learned_moves(improvements_filename)
    if not learned_moves:
        print("Keine gelernten Zugfolgen in", improvements_filename, "gefunden.")
        return

    overall_start_time = time.time()
    
    # Pro Run: Eine neue Startposition wird einmal gemischt und danach beibehalten.
    for run_number in range(1, total_runs + 1):
        print(f"\n=== Starting Run {run_number} ===")
        run_start_time = time.time()
        # Erzeuge eine Startposition für diesen Run (einmaliges Mischen)
        current_state = original_state.copy()
        no_moves_to_shuffle = params.get("NO_MOVES_TO_SHUFFLE", 0)
        if no_moves_to_shuffle > 0:
            shuffle_sequence = [random.choice(allowed_moves_global) for _ in range(no_moves_to_shuffle)]
            current_state = apply_sequence(current_state, shuffle_sequence, moves_mapping)
        run_start_state_str = ";".join(current_state)
        
        # Kombinationen (erschöpfte Kombinationen) werden pro Run in combination_history gespeichert
        combination_history = set()
        run_iterations = 0
        run_solutions = []  # Liste der gefundenen Lösungen in diesem Run
        # Suche im Run: Verwende denselben gemischten Startzustand für alle Versuche.
        while run_iterations < params["MAX_ITERATIONS E3"] and len(run_solutions) < solutions_per_run:
            final_state, combination, solved, iter_run = optimize_cube(params, current_state, moves_mapping, learned_moves, combination_history)
            run_iterations += iter_run
            if solved:
                sol_time = time.time() - run_start_time
                solution_time_str = time.strftime("%H:%M:%S", time.gmtime(sol_time))
                total_moves_list = []
                for seq in combination:
                    total_moves_list.extend(seq.split())
                total_move_sequence = " ".join(total_moves_list)
                total_moves = len(total_moves_list)
                # Pro Run wird die Lösung einmalig gespeichert (Duplikate innerhalb des Runs verhindern)
                if total_move_sequence not in [sol["move_sequence"] for sol in run_solutions]:
                    solution = {
                        "iterations": run_iterations,
                        "time": solution_time_str,
                        "move_sequence": total_move_sequence,
                        "total_moves": total_moves,
                        "start_state": run_start_state_str
                    }
                    run_solutions.append(solution)
                    run_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(run_start_time))
                    save_results(run_number, run_datetime, run_start_state_str, solution_time_str, run_iterations, total_move_sequence, total_moves)
                    print(f"Run {run_number}: Lösung gefunden bei Iteration {run_iterations}, Zeit {solution_time_str}, Total moves: {total_moves}")
                else:
                    print(f"Run {run_number}: Duplikat-Lösung ignoriert")
            else:
                # Wenn keine Verbesserung mehr möglich ist, beenden wir den Run.
                break
            if run_iterations % 1000 == 0:
                print(run_iterations)
        print(f"Run {run_number} abgeschlossen. Gefundene Lösungen: {len(run_solutions)}")
    
    overall_elapsed = time.time() - overall_start_time
    overall_runtime_str = time.strftime("%H:%M:%S", time.gmtime(overall_elapsed))
    print("\nAlle Runs abgeschlossen.")
    print(f"Gesamtlaufzeit: {overall_runtime_str}")
    print("\nErgebnisse wurden in Results.csv gespeichert.")

if __name__ == '__main__':
    main()