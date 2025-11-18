#!/usr/bin/env python3

""" Battle of Heuristics - INTERACTIVE MULTI STRATEGY VERSION 
Team XX - November 2025
Family Names: [Your Names Here]
"""

import sys
import time
import random
import os
from typing import List, Tuple, Set

class Painting:
    __slots__ = ('id', 'orientation', 'tags', 'tag_count')
    def __init__(self, painting_id: int, orientation: str, tags: Set[str]):
        self.id = painting_id
        self.orientation = orientation
        self.tags = tags
        self.tag_count = len(tags)

class Frameglass:
    __slots__ = ('paintings', 'tags', 'tag_count')
    def __init__(self, paintings: List[Painting]):
        self.paintings = paintings
        self.tags = set()
        for p in paintings:
            self.tags.update(p.tags)
        self.tag_count = len(self.tags)
    
    def get_output_line(self) -> str:
        return " ".join(str(p.id) for p in self.paintings)

def parse_input(filename: str) -> Tuple[List[Painting], List[Painting]]:
    landscapes = []
    portraits = []
    with open(filename, 'r', encoding='utf-8') as f:
        n = int(f.readline().strip())
        print(f"Parsing {n} paintings...")

        for i in range(n):
            line = f.readline().strip().split()
            orientation = line[0]
            num_tags = int(line[1])
            tags = set(line[2:2+num_tags])
            painting = Painting(i, orientation, tags)
            if orientation == 'L':
                landscapes.append(painting)
            else:
                portraits.append(painting)

    print(f"  Parsed: {len(landscapes)} landscapes, {len(portraits)} portraits")
    return landscapes, portraits

def create_frameglasses(landscapes: List[Painting], portraits: List[Painting]) -> List[Frameglass]:
    frameglasses = []
    
    print("Creating frameglasses...")
    
    for painting in landscapes:
        frameglasses.append(Frameglass([painting]))

    i = 0
    while i < len(portraits):
        if i + 1 < len(portraits):
            frameglasses.append(Frameglass([portraits[i], portraits[i + 1]]))
            i += 2
        else:
            frameglasses.append(Frameglass([portraits[i]]))
            i += 1

    print(f"  Created {len(frameglasses)} frameglasses")
    return frameglasses

def calculate_local_score(fg1: Frameglass, fg2: Frameglass) -> int:
    common = len(fg1.tags & fg2.tags)
    only_first = len(fg1.tags - fg2.tags)
    only_second = len(fg2.tags - fg1.tags)
    return min(common, only_first, only_second)

def calculate_total_score(frameglasses: List[Frameglass]) -> int:
    total = 0
    for i in range(len(frameglasses) - 1):
        total += calculate_local_score(frameglasses[i], frameglasses[i + 1])
    return total

def order_same(frameglasses: List[Frameglass]) -> List[Frameglass]:
    print("  Using 'same' ordering strategy...")
    return frameglasses[:]

def order_reverse(frameglasses: List[Frameglass]) -> List[Frameglass]:
    print("  Using 'reverse' ordering strategy...")
    return list(reversed(frameglasses))

def order_random(frameglasses: List[Frameglass]) -> List[Frameglass]:
    print("  Using 'random' ordering strategy...")
    result = frameglasses[:]
    random.shuffle(result)
    return result

def order_by_tag_count(frameglasses: List[Frameglass]) -> List[Frameglass]:
    print("  Using 'by_tags' ordering strategy...")
    return sorted(frameglasses, key=lambda fg: -fg.tag_count)

def ensure_output_folder():
    if not os.path.exists("Output"):
        os.makedirs("Output")
        print("Created 'Output' folder")
    return "Output"

def get_output_path(input_file: str) -> str:
    output_folder = ensure_output_folder()
    input_filename = os.path.basename(input_file)
    output_filename = input_filename
    output_path = os.path.join(output_folder, output_filename)
    return output_path

def write_output(filename: str, frameglasses: List[Frameglass]):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{len(frameglasses)}\n")
        for fg in frameglasses:
            f.write(f"{fg.get_output_line()}\n")
    print(f"  Output written: {filename}")

def get_strategy_choice() -> str:
    print("\n" + "="*50)
    print("STRATEGY SELECTION MENU")
    print("="*50)
    print("1. Run ALL strategies (auto-select best)")
    print("2. Use ONLY 'same' strategy")
    print("3. Use ONLY 'reverse' strategy") 
    print("4. Use ONLY 'random' strategy")
    print("5. Use ONLY 'by_tags' strategy")
    print("6. Manual strategy selection for each file")
    print("="*50)
    
    while True:
        choice = input("Enter your choice (1-6): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        else:
            print("Invalid choice! Please enter a number between 1-6.")

def get_manual_strategy() -> str:
    print("\nAvailable strategies:")
    print("1. same")
    print("2. reverse")
    print("3. random")
    print("4. by_tags")
    
    while True:
        choice = input("Select strategy (1-4): ").strip()
        if choice == '1':
            return 'same'
        elif choice == '2':
            return 'reverse'
        elif choice == '3':
            return 'random'
        elif choice == '4':
            return 'by_tags'
        else:
            print("Invalid choice! Please enter 1-4.")

def solve_file_single_strategy(input_file: str, output_file: str, strategy_name: str, verbose: bool = True) -> Tuple[int, float]:
    if verbose:
        print(f"\n{'='*70}")
        print(f"Processing: {input_file}")
        print(f"Strategy: {strategy_name}")
        print(f"{'='*70}")
    
    start_time = time.time()

    landscapes, portraits = parse_input(input_file)
    frameglasses = create_frameglasses(landscapes, portraits)

    strategies = {
        "same": order_same,
        "reverse": order_reverse, 
        "random": order_random,
        "by_tags": order_by_tag_count,
    }
    
    ordered = strategies[strategy_name](frameglasses)
    score = calculate_total_score(ordered)

    write_output(output_file, ordered)

    elapsed = time.time() - start_time
    if verbose:
        print(f"\nScore: {score:,}")
        print(f"Time: {elapsed:.2f}s")
        print(f"Output: {output_file}")
        print(f"{'='*70}\n")
    
    return score, elapsed

def solve_file_all_strategies(input_file: str, output_file: str, verbose: bool = True) -> Tuple[int, float]:
    if verbose:
        print(f"\n{'='*70}")
        print(f"Processing: {input_file}")
        print(f"{'='*70}")
    
    start_time = time.time()

    landscapes, portraits = parse_input(input_file)
    frameglasses = create_frameglasses(landscapes, portraits)

    if verbose:
        print(f"\nTesting all ordering strategies...")

    strategies = {
        "same": order_same,
        "reverse": order_reverse, 
        "random": order_random,
        "by_tags": order_by_tag_count,
    }

    best_score = -1
    best_strategy = None
    best_ordered = None
    strategy_results = []

    for strategy_name, strategy_func in strategies.items():
        strategy_start = time.time()
        
        ordered = strategy_func(frameglasses)
        score = calculate_total_score(ordered)
        
        strategy_elapsed = time.time() - strategy_start
        strategy_results.append((strategy_name, score, strategy_elapsed))
        
        if verbose:
            print(f"  {strategy_name:15s}: Score = {score:>8,} ({strategy_elapsed:6.2f}s)")
        
        if score > best_score:
            best_score = score
            best_strategy = strategy_name
            best_ordered = ordered

    write_output(output_file, best_ordered)

    elapsed = time.time() - start_time
    if verbose:
        print(f"\nBest strategy: {best_strategy}")
        print(f"Best score: {best_score:,}")
        print(f"Total time: {elapsed:.2f}s")
        print(f"Output: {output_file}")
        
        print(f"\nAll strategy results:")
        for name, score, time_taken in strategy_results:
            print(f"   {name:15s}: {score:>8,} ({time_taken:6.2f}s)")
            
        print(f"{'='*70}\n")
    
    return best_score, elapsed

def solve_all_files():
    files = [
        ("0_example.txt", "0_example.txt"),
        ("1_binary_landscapes.txt", "1_binary_landscapes.txt"), 
        ("10_computable_moments.txt", "10_computable_moments.txt"),
        ("11_randomizing_paintings.txt", "11_randomizing_paintings.txt"),
        ("110_oily_portraits.txt", "110_oily_portraits.txt")
    ]

    choice = get_strategy_choice()
    
    print("\n" + "=" * 70)
    print("BATTLE OF HEURISTICS - INTERACTIVE VERSION")
    print("=" * 70)
    print(f"Processing {len(files)} showrooms...")
    print(f"Strategy mode: {['All strategies', 'Same only', 'Reverse only', 'Random only', 'By_tags only', 'Manual selection'][int(choice)-1]}")
    print(f"Output folder: Output/")
    print()

    ensure_output_folder()

    total_score = 0
    total_time = 0
    results = []
    missing = []

    for input_file, output_filename in files:
        if not os.path.exists(input_file):
            print(f"Skipping {input_file} (file not found)")
            missing.append(input_file)
            continue
            
        try:
            output_file = get_output_path(output_filename)
            
            if choice == '1':
                score, elapsed = solve_file_all_strategies(input_file, output_file, verbose=True)
            elif choice == '6':
                print(f"\nFile: {input_file}")
                strategy = get_manual_strategy()
                score, elapsed = solve_file_single_strategy(input_file, output_file, strategy, verbose=True)
            else:
                strategies = ['same', 'reverse', 'random', 'by_tags']
                strategy = strategies[int(choice) - 2]
                score, elapsed = solve_file_single_strategy(input_file, output_file, strategy, verbose=True)
            
            total_score += score
            total_time += elapsed
            results.append((input_file, score, elapsed))
            print(f"Completed: {input_file} -> Score: {score:,}, Time: {elapsed:.2f}s")
            print(f"Saved as: {output_file}")
            
        except Exception as e:
            print(f"Error processing {input_file}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"\n{'File':<35} {'Score':>15} {'Time':>12}")
    print("-" * 70)
    for filename, score, elapsed in results:
        print(f"{filename:<35} {score:>15,} {elapsed:>11.2f}s")
    print("-" * 70)
    print(f"{'TOTAL':<35} {total_score:>15,} {total_time:>11.2f}s")
    print("=" * 70)

    if total_time > 1200:
        print(f"\nWARNING: Exceeded 20-minute limit by {total_time - 1200:.1f}s")
    else:
        print(f"\nWithin time limit! ({1200 - total_time:.1f}s remaining)")

    if results:
        print(f"\nAverage score: {total_score/len(results):,.0f} points/file")
    
    print(f"\nAll output files saved in: Output/ folder")
    print("Output files:")
    for input_file, _, _ in results:
        output_file = get_output_path(os.path.basename(input_file))
        print(f"   {os.path.basename(output_file)}")

    return total_score, total_time

def solve_single_file(input_file: str):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return
    
    output_file = get_output_path(os.path.basename(input_file))
    
    print(f"\n{'='*70}")
    print(f"SINGLE FILE PROCESSING")
    print(f"{'='*70}")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"{'='*70}")
    
    score, elapsed = solve_file_all_strategies(input_file, output_file, verbose=True)
    
    print(f"Final Score: {score:,}")
    print(f"Total Time: {elapsed:.2f}s")
    print(f"Saved as: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        solve_all_files()
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
        solve_single_file(input_file)
    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        custom_output = sys.argv[2]
        output_file = get_output_path(custom_output)
        solve_file_all_strategies(input_file, output_file)
        print(f"Custom output saved as: {output_file}")
    else:
        print("Usage:")
        print("  python KCW_Team_XX.py")
        print("  python KCW_Team_XX.py input.txt")
        print("  python KCW_Team_XX.py input.txt output")
        print("\nAll output files are automatically saved in the 'Output' folder")