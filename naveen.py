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
    __slots__ = ('paintings', 'tags', 'tag_count', 'sig')
    def __init__(self, paintings: List[Painting]):
        self.paintings = paintings
        self.tags = set()
        for p in paintings:
            self.tags.update(p.tags)
        self.tag_count = len(self.tags)
        self.sig = 0  # for ultra-fast greedy


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
# Optimal Portrait Pairing
# -------------------------------------------------------------

def pair_portraits_optimal(portraits: List[Painting]) -> List[Frameglass]:
    """
    Pair vertical paintings to maximize tag diversity.
    Heuristic: pair least overlapping tags first.
    """
    paired = []
    used = set()
    sorted_portraits = sorted(portraits, key=lambda p: -p.tag_count)

    for i, p1 in enumerate(sorted_portraits):
        if p1.id in used:
            continue
        best_score = -1
        best_j = None
        for j, p2 in enumerate(sorted_portraits[i+1:], start=i+1):
            if p2.id in used:
                continue
            overlap = len(p1.tags & p2.tags)
            score = -(overlap)  # smaller overlap better
            if score > best_score:
                best_score = score
                best_j = j
        if best_j is not None:
            p2 = sorted_portraits[best_j]
            paired.append(Frameglass([p1, p2]))
            used.add(p1.id)
            used.add(p2.id)
        else:
            # single portrait left
            paired.append(Frameglass([p1]))
            used.add(p1.id)
    return paired


# -------------------------------------------------------------
# Create Frameglasses
# -------------------------------------------------------------

def create_frameglasses(landscapes: List[Painting], portraits: List[Painting]) -> List[Frameglass]:
    frameglasses = [Frameglass([p]) for p in landscapes]
    frameglasses += pair_portraits_optimal(portraits)
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
# Ultra-Fast Greedy Strategy
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
    all_tags = list({t for fg in frameglasses for t in fg.tags})
    tag_to_bit = {tag: i for i, tag in enumerate(all_tags)}

    for fg in frameglasses:
        fg.sig = build_signature(fg.tags, tag_to_bit)

    remaining = sorted(frameglasses, key=lambda fg: len(fg.tags))
    n = len(remaining)
    idx = n // 2
    curr = remaining.pop(idx)
    result = [curr]

    BUCKET_SIZE = 250

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
        idx = best_i

    return result


# -------------------------------------------------------------
# Post-processing / Hill-Climbing
# -------------------------------------------------------------

def optimize_order_hillclimb(frameglasses: List[Frameglass], iterations: int = 5) -> List[Frameglass]:
    """
    Swap neighboring slides if it increases total score.
    Run multiple iterations to improve score.
    """
    n = len(frameglasses)
    for it in range(iterations):
        improved = False
        for i in range(n-1):
            score_before = calculate_local_score(frameglasses[i], frameglasses[i+1])
            # Swap neighbors
            frameglasses[i], frameglasses[i+1] = frameglasses[i+1], frameglasses[i]
            score_after = calculate_local_score(frameglasses[i], frameglasses[i+1])
            if score_after <= score_before:
                # Revert if not better
                frameglasses[i], frameglasses[i+1] = frameglasses[i+1], frameglasses[i]
            else:
                improved = True
        if not improved:
            break
    return frameglasses


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
        "greedy_similarity": order_greedy_ultrafast,
    }

    ordered = strategies[strategy_name](frameglasses)
    ordered = optimize_order_hillclimb(ordered, iterations=5)  # post-processing hill-climb
    score = calculate_total_score(ordered)
    write_output(output_file, ordered)

    elapsed = time.time() - start_time
    print(f"Score: {score:,}")
    print(f"Time: {elapsed:.2f}s")
    return score, elapsed


# -------------------------------------------------------------
# Main
# -------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) == 1:
        input_file = "0_example.txt"  # default file
        output_file = get_output_path(os.path.basename(input_file))
        solve_file_single_strategy(input_file, output_file, "greedy_similarity")
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
        print("  python finalall.py input.txt")
        print("  python finalall.py input.txt strategy")
