#!/usr/bin/env python3

import sys
import time
import random
import os
from typing import List, Tuple, Set

# -------------------------------------------------------------
# Classes
# -------------------------------------------------------------

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


# -------------------------------------------------------------
# Input Parsing
# -------------------------------------------------------------

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


# -------------------------------------------------------------
# Create Frameglasses
# -------------------------------------------------------------

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


# -------------------------------------------------------------
# Score Calculations
# -------------------------------------------------------------

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


# -------------------------------------------------------------
# Basic Strategies
# -------------------------------------------------------------

def order_same(frameglasses: List[Frameglass]) -> List[Frameglass]:
    return frameglasses[:]

def order_reverse(frameglasses: List[Frameglass]) -> List[Frameglass]:
    return list(reversed(frameglasses))

def order_random(frameglasses: List[Frameglass]) -> List[Frameglass]:
    result = frameglasses[:]
    random.shuffle(result)
    return result

def order_by_tag_count(frameglasses: List[Frameglass]) -> List[Frameglass]:
    return sorted(frameglasses, key=lambda fg: -fg.tag_count)


# -------------------------------------------------------------
# Ultra-Fast Greedy Strategy (optimized)
# -------------------------------------------------------------

def build_signature(tags, tag_to_bit):
    sig = 0
    for tag in tags:
        sig |= 1 << tag_to_bit[tag]
    return sig

def calc_score_sig(sig1, sig2):
    common = (sig1 & sig2).bit_count()
    only1 = (sig1 & ~sig2).bit_count()
    only2 = (sig2 & ~sig1).bit_count()
    return min(common, only1, only2)

def order_greedy_ultrafast(frameglasses):
    # Map tags → bit indices
    all_tags = list({t for fg in frameglasses for t in fg.tags})
    tag_to_bit = {tag: i for i, tag in enumerate(all_tags)}

    # Precompute signatures
    for fg in frameglasses:
        fg.sig = build_signature(fg.tags, tag_to_bit)

    # Sort by number of tags once
    remaining = sorted(frameglasses, key=lambda fg: len(fg.tags))
    n = len(remaining)

    # Start in the middle
    idx = n // 2
    curr = remaining.pop(idx)
    result = [curr]

    WINDOW = 120        # adjustable for speed/quality tradeoff
    BUCKET_SIZE = 250   # cluster frames

    while remaining:
        lo = max(0, idx - BUCKET_SIZE)
        hi = min(len(remaining), idx + BUCKET_SIZE)

        best_score = -1
        best_i = lo

        for i in range(lo, hi):
            sc = calc_score_sig(curr.sig, remaining[i].sig)
            if sc > best_score:
                best_score = sc
                best_i = i

        curr = remaining.pop(best_i)
        result.append(curr)
        idx = best_i  # stay near same tag count region

    return result


# -------------------------------------------------------------
# Output
# -------------------------------------------------------------

def ensure_output_folder():
    if not os.path.exists("Output"):
        os.makedirs("Output")
    return "Output"

def get_output_path(input_file: str) -> str:
    output_folder = ensure_output_folder()
    input_filename = os.path.basename(input_file)
    return os.path.join(output_folder, input_filename)

def write_output(filename: str, frameglasses: List[Frameglass]):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{len(frameglasses)}\n")
        for fg in frameglasses:
            f.write(f"{fg.get_output_line()}\n")
    print(f"  Output written: {filename}")


# -------------------------------------------------------------
# Strategy Menus
# -------------------------------------------------------------

def get_strategy_choice() -> str:
    print("\n" + "="*50)
    print("STRATEGY SELECTION MENU")
    print("="*50)
    print("1. Run ALL strategies")
    print("2. same")
    print("3. reverse")
    print("4. random")
    print("5. by_tags")
    print("6. greedy_similarity   <-- optimized")
    print("="*50)
    
    while True:
        choice = input("Enter your choice (1-6): ").strip()
        if choice in ['1','2','3','4','5','6']:
            return choice
        print("Invalid choice")


# -------------------------------------------------------------
# Solve One File
# -------------------------------------------------------------

def solve_file_single_strategy(input_file: str, output_file: str, strategy_name: str) -> Tuple[int, float]:
    print(f"\nProcessing: {input_file}")
    print(f"Strategy: {strategy_name}")

    start_time = time.time()

    landscapes, portraits = parse_input(input_file)
    frameglasses = create_frameglasses(landscapes, portraits)

    strategies = {
        "same": order_same,
        "reverse": order_reverse,
        "random": order_random,
        "by_tags": order_by_tag_count,
        "greedy_similarity": order_greedy_ultrafast,  # use ultrafast greedy
    }
    
    ordered = strategies[strategy_name](frameglasses)
    score = calculate_total_score(ordered)

    write_output(output_file, ordered)

    elapsed = time.time() - start_time
    print(f"Score: {score:,}")
    print(f"Time: {elapsed:.2f}s")

    return score, elapsed


# -------------------------------------------------------------
# Solve All Showroom Files
# -------------------------------------------------------------

def solve_all_files():
    files = [
        ("0_example.txt", "0_example.txt"),
        ("1_binary_landscapes.txt", "1_binary_landscapes.txt"),
        ("10_computable_moments.txt", "10_computable_moments.txt"),
        ("11_randomizing_paintings.txt", "11_randomizing_paintings.txt"),
        ("110_oily_portraits.txt", "110_oily_portraits.txt")
    ]

    choice = get_strategy_choice()
    strategies = ['same', 'reverse', 'random', 'by_tags', 'greedy_similarity']

    total_score = 0
    total_time = 0

    for input_file, output_file in files:
        if not os.path.exists(input_file):
            print(f"Missing file: {input_file}")
            continue

        out_path = get_output_path(output_file)

        if choice == '1':
            # Run all and pick best
            best_score = -1
            file_time = 0
            for sname in strategies:
                score, t = solve_file_single_strategy(input_file, out_path, sname)
                file_time += t
                if score > best_score:
                    best_score = score
            total_score += best_score
            total_time += file_time
        else:
            strategy = strategies[int(choice)-2]
            score, elapsed = solve_file_single_strategy(input_file, out_path, strategy)
            total_score += score
            total_time += elapsed

    mins = int(total_time // 60)
    secs = int(total_time % 60)

    print("\n======= FINAL RESULTS =======")
    print(f"Total Score: {total_score:,}")
    print(f"Total Time: {mins} min {secs} sec")
    print("=============================\n")


# -------------------------------------------------------------
# Main
# -------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) == 1:
        solve_all_files()
    elif len(sys.argv) == 2:
        input_file = sys.argv[1]
        output_file = get_output_path(os.path.basename(input_file))
        solve_file_single_strategy(input_file, output_file, "greedy_similarity")
    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        strategy = sys.argv[2]
        output_file = get_output_path(os.path.basename(input_file))
        solve_file_single_strategy(input_file, output_file, strategy)
    else:
        print("Usage:")
        print("  python finalall.py")
        print("  python finalall.py input.txt")
        print("  python finalall.py input.txt strategy")
