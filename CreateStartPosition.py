#!/usr/bin/env python3
import csv

def print_cube(cube):
    """
    Displays the current cube state in the desired net layout.
    The list 'cube' contains 54 entries (positions 1-54).
    
    The printed layout is as follows:
    
                [19] [20] [21]
                [22] [23] [24]
                [25] [26] [27]
[10] [11] [12]      [1]  [2]  [3]      [28] [29] [30]
[13] [14] [15]      [4]  [5]  [6]      [31] [32] [33]
[16] [17] [18]      [7]  [8]  [9]      [34] [35] [36]
                [37] [38] [39]
                [40] [41] [42]
                [43] [44] [45]
                [46] [47] [48]
                [49] [50] [51]
                [52] [53] [54]
    """
    def line(indices):
        return " ".join(cube[i - 1] for i in indices)
    print("\nCurrent Cube State:")
    # Upper face (Up)
    print("        " + line([19, 20, 21]))
    print("        " + line([22, 23, 24]))
    print("        " + line([25, 26, 27]))
    # Middle zone: Left, Front, Right
    print(line([10, 11, 12]) + "   " + line([1, 2, 3]) + "   " + line([28, 29, 30]))
    print(line([13, 14, 15]) + "   " + line([4, 5, 6]) + "   " + line([31, 32, 33]))
    print(line([16, 17, 18]) + "   " + line([7, 8, 9]) + "   " + line([34, 35, 36]))
    # Lower zone: first lower face (Back)
    print("        " + line([37, 38, 39]))
    print("        " + line([40, 41, 42]))
    print("        " + line([43, 44, 45]))
    # Lower zone: second lower face (Down)
    print("        " + line([46, 47, 48]))
    print("        " + line([49, 50, 51]))
    print("        " + line([52, 53, 54]))
    print()

def save_csv(cube, filename="csv_export-StartPos.csv"):
    """
    Reorders the cube values so that CSV-Feld 1 dem Front Face entspricht
    und anschließend die Werte für Left, Up, Right, Back und Down.
    Die CSV-Datei enthält zwei Zeilen:
      1. Eine Kopfzeile mit den Zahlen 1 bis 54.
      2. Eine Zeile mit den Farbwerten in der neuen Reihenfolge.
    """
    ordered = [
        # Front Face: Positionen 1-9 (Indices 0 bis 8)
        cube[0], cube[1], cube[2],
        cube[3], cube[4], cube[5],
        cube[6], cube[7], cube[8],
        # Left Face: Positionen 10-18 (Indices 9 bis 17)
        cube[9], cube[10], cube[11],
        cube[12], cube[13], cube[14],
        cube[15], cube[16], cube[17],
        # Upper Face: Positionen 19-27 (Indices 18 bis 26)
        cube[18], cube[19], cube[20],
        cube[21], cube[22], cube[23],
        cube[24], cube[25], cube[26],
        # Right Face: Positionen 28-36 (Indices 27 bis 35)
        cube[27], cube[28], cube[29],
        cube[30], cube[31], cube[32],
        cube[33], cube[34], cube[35],
        # Back Face: Positionen 37-45 (Indices 36 bis 44)
        cube[36], cube[37], cube[38],
        cube[39], cube[40], cube[41],
        cube[42], cube[43], cube[44],
        # Down Face: Positionen 46-54 (Indices 45 bis 53)
        cube[45], cube[46], cube[47],
        cube[48], cube[49], cube[50],
        cube[51], cube[52], cube[53],
    ]
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([str(i) for i in range(1, 55)])
        writer.writerow(ordered)
    print(f"Cube configuration saved to {filename}")

def main():
    # Initialize the cube with numbered positions so you see which cell is which.
    cube = [str(i) for i in range(1, 55)]
    print("Initial Cube Configuration (numbered):")
    print_cube(cube)
    
    # Define the input order (list of cell numbers) according to the printed layout.
    input_order = [
        19, 20, 21, 22, 23, 24, 25, 26, 27,    # Upper face (Up)
        10, 11, 12,                             # Left top row of middle zone
        1, 2, 3,                                # Front top row of middle zone
        28, 29, 30,                             # Right top row of middle zone
        13, 14, 15,                             # Left middle row
        4, 5, 6,                                # Front middle row
        31, 32, 33,                             # Right middle row
        16, 17, 18,                             # Left bottom row of middle zone
        7, 8, 9,                                # Front bottom row of middle zone
        34, 35, 36,                             # Right bottom row of middle zone
        37, 38, 39,                             # Lower zone: first block (Back)
        40, 41, 42,
        43, 44, 45,
        46, 47, 48,                             # Lower zone: second block (Down) – first row
        49, 50, 51,                             # second row
        52, 53, 54                              # third row
    ]
    
    print("Now, you will fill in the colors for each cell in the given order.")
    print("Allowed color codes: w, g, r, o, b, y.")
    print("If you make a mistake during sequential input, enter 'k' for correction and specify the cell number to return to.")
    
    i = 0
    while i < len(input_order):
        current_pos = input_order[i]
        prompt = f"Enter color for cell {current_pos} (current value: {cube[current_pos - 1]}): "
        user_input = input(prompt).strip().lower()
        if user_input == "k":
            # Correction during sequential input: ask which cell to return to.
            corr = input("Enter the cell number you wish to correct (must be in the input order): ").strip()
            if not corr.isdigit():
                print("Invalid input. Please enter a number between 1 and 54.")
                continue
            corr_num = int(corr)
            if corr_num not in input_order:
                print(f"Cell {corr_num} is not in the input order. Please enter a valid number.")
                continue
            i = input_order.index(corr_num)
            print(f"Returning to cell {corr_num}.")
        elif user_input in ["w", "g", "r", "o", "b", "y"]:
            cube[current_pos - 1] = user_input
            i += 1  # Move to next position
        else:
            print("Invalid input. Please enter a valid color code or 'k' for correction.")
            continue
        print_cube(cube)
    
    # Final review mode – allow further corrections before saving.
    print("Sequential entry complete.")
    print("You are now in review mode. Enter a cell number (1-54) to correct that position, or type 'save' to save the configuration.")
    while True:
        review_input = input("Review mode: Enter cell number to correct or 'save' to finish: ").strip().lower()
        if review_input == "save":
            break
        elif review_input.isdigit():
            cell_num = int(review_input)
            if not (1 <= cell_num <= 54):
                print("Invalid cell number. Please enter a number between 1 and 54.")
                continue
            new_color = input(f"Enter new color code for cell {cell_num} (allowed: w, g, r, o, b, y): ").strip().lower()
            if new_color not in ["w", "g", "r", "o", "b", "y"]:
                print("Invalid color code. Allowed values: w, g, r, o, b, y.")
                continue
            cube[cell_num - 1] = new_color
            print("Updated Cube:")
            print_cube(cube)
        else:
            print("Invalid command. Please enter a cell number or 'save'.")
    
    # Finally, save the configuration once you're satisfied.
    save_csv(cube)

if __name__ == "__main__":
    main()