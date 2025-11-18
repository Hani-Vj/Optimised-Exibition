#!/usr/bin/env python3
"""
Battle of Heuristics Challenge Week - Exhibition Opening Optimizer
Complete Standalone Solution - NO EXTERNAL DEPENDENCIES
Team XX
November 2025

USAGE:
  python hcw_solution.py                        # Process all 5 files
  python hcw_solution.py 0_example.txt          # Process single file
  python hcw_solution.py 0_example.txt output.txt  # Custom output name
"""

import sys
import time
import random
from typing import List, Tuple, Set


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class Painting:
    """Represents a single painting with orientation and tags."""
    
    def __init__(self, painting_id: int, orientation: str, tags: Set[str]):
        self.id = painting_id
        self.orientation = orientation
        self.tags = tags
        self.tag_count = len(tags)
    
    def __repr__(self):
        return f"P{self.id}({self.orientation},{self.tag_count}t)"


class Frameglass:
    """Represents a frameglass containing 1 landscape or 2 portraits."""
    
    def __init__(self, paintings: List[Painting]):
        self.paintings = paintings
        self.tags = set()
        for p in paintings:
            self.tags.update(p.tags)
        self.tag_count = len(self.tags)
    
    def get_output_line(self) -> str:
        """Return output format: 'id' for landscape, 'id1 id2' for portrait pair."""
        return " ".join(str(p.id) for p in self.paintings)
    
    def __repr__(self):
        ids = " ".join(map(str, [p.id for p in self.paintings]))
        return f"FG[{ids}]({self.tag_count}t)"


# ============================================================================
# TASK 1: READ AND PARSE INPUT FILE
# ============================================================================

def parse_input(filename: str) -> Tuple[List[Painting], List[Painting]]:
    """
    Parse input file and return separate lists of landscape and portrait paintings.
    
    Input format:
    Line 1: N (number of paintings)
    Lines 2-N+1: <orientation> <num_tags> <tag1> <tag2> ... <tagN>
    
    Returns:
        (landscapes, portraits)
    """
    landscapes = []
    portraits = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        n = int(f.readline().strip())
        
        for i in range(n):
            line = f.readline().strip().split()
            orientation = line[0]  # 'L' or 'P'
            num_tags = int(line[1])
            tags = set(line[2:2+num_tags])  # Extract tag set
            
            painting = Painting(i, orientation, tags)
            
            if orientation == 'L':
                landscapes.append(painting)
            else:
                portraits.append(painting)
    
    return landscapes, portraits


# ============================================================================
# TASK 2: CREATE FRAMEGLASSES FROM INPUT DATA
# ============================================================================

def create_frameglasses(landscapes: List[Painting], 
                       portraits: List[Painting]) -> List[Frameglass]:
    """
    Create frameglasses with greedy pairing to maximize tag diversity.
    
    Rules:
    - Each landscape = 1 frameglass (single painting)
    - Portraits must be paired = 1 frameglass (2 paintings)
    - Frameglass tags = union of all paintings' tags
    """
    frameglasses = []
    
    # Each landscape becomes its own frameglass
    for painting in landscapes:
        frameglasses.append(Frameglass([painting]))
    
    # Pair portraits greedily to maximize diversity
    if not portraits:
        return frameglasses
    
    used = set()
    portraits_sorted = sorted(portraits, key=lambda p: p.tag_count, reverse=True)
    
    for i, p1 in enumerate(portraits_sorted):
        if p1.id in used:
            continue
        
        best_pair = None
        best_score = -1
        
        # Find best partner (maximize total unique tags)
        for p2 in portraits_sorted[i+1:]:
            if p2.id in used:
                continue
            
            total_tags = len(p1.tags | p2.tags)
            overlap = len(p1.tags & p2.tags)
            score = total_tags - overlap * 0.3  # Penalize overlap
            
            if score > best_score:
                best_score = score
                best_pair = p2
        
        if best_pair:
            frameglasses.append(Frameglass([p1, best_pair]))
            used.add(p1.id)
            used.add(best_pair.id)
    
    # Handle remaining unpaired portrait (if odd number)
    unpaired = [p for p in portraits if p.id not in used]
    if unpaired:
        # Pair with any already paired portrait (or create single-portrait frameglass)
        frameglasses.append(Frameglass([unpaired[0]]))
    
    return frameglasses


# ============================================================================
# TASK 3: ORDER THE FRAMEGLASSES
# ============================================================================

def calculate_local_score(fg1: Frameglass, fg2: Frameglass) -> int:
    """
    Calculate satisfaction score between two consecutive frameglasses.
    
    Score = min(common_tags, only_in_first, only_in_second)
    """
    common = len(fg1.tags & fg2.tags)
    only_first = len(fg1.tags - fg2.tags)
    only_second = len(fg2.tags - fg1.tags)
    return min(common, only_first, only_second)


def calculate_total_score(frameglasses: List[Frameglass]) -> int:
    """Calculate total score for a sequence of frameglasses."""
    total = 0
    for i in range(len(frameglasses) - 1):
        total += calculate_local_score(frameglasses[i], frameglasses[i+1])
    return total


# 3.1: Using same order
def order_same(frameglasses: List[Frameglass]) -> List[Frameglass]:
    """Keep original order."""
    return frameglasses[:]


# 3.2: Using reverse order
def order_reverse(frameglasses: List[Frameglass]) -> List[Frameglass]:
    """Reverse the order."""
    return list(reversed(frameglasses))


# 3.3: Using random order
def order_random(frameglasses: List[Frameglass]) -> List[Frameglass]:
    """Random shuffle."""
    result = frameglasses[:]
    random.shuffle(result)
    return result


# 3.4: Ordered according to the number of tags
def order_by_tag_count(frameglasses: List[Frameglass]) -> List[Frameglass]:
    """Order by number of tags (descending)."""
    return sorted(frameglasses, key=lambda fg: fg.tag_count, reverse=True)


# Advanced: Greedy nearest-neighbor (bonus strategy)
def order_greedy(frameglasses: List[Frameglass]) -> List[Frameglass]:
    """
    Greedy ordering: always pick next frameglass that maximizes local score.
    """
    if not frameglasses:
        return []
    
    # Start with frameglass that has most tags
    start_idx = max(range(len(frameglasses)), key=lambda i: frameglasses[i].tag_count)
    
    ordered = [frameglasses[start_idx]]
    remaining = set(range(len(frameglasses)))
    remaining.remove(start_idx)
    
    while remaining:
        current = ordered[-1]
        best_idx = None
        best_score = -1
        
        for idx in remaining:
            score = calculate_local_score(current, frameglasses[idx])
            if score > best_score:
                best_score = score
                best_idx = idx
        
        if best_idx is not None:
            ordered.append(frameglasses[best_idx])
            remaining.remove(best_idx)
    
    return ordered


# ============================================================================
# TASK 4: WRITE OUTPUT FILE
# ============================================================================

def write_output(filename: str, frameglasses: List[Frameglass]):
    """
    Write solution to output file.
    
    Output format:
    Line 1: F (number of frameglasses)
    Lines 2-F+1: For each frameglass:
      - Landscape: single painting ID
      - Portrait pair: two painting IDs separated by space
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{len(frameglasses)}\n")
        for fg in frameglasses:
            f.write(f"{fg.get_output_line()}\n")


# ============================================================================
# TASK 5: ADD EXECUTION TIME EVALUATION
# ============================================================================

def solve_file(input_file: str, output_file: str, verbose: bool = True):
    """
    Main function to solve a single file with all strategies.
    
    Returns:
        (best_score, elapsed_time)
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"Processing: {input_file}")
        print(f"{'='*70}")
    
    start_time = time.time()
    
    # Step 1: Parse input
    landscapes, portraits = parse_input(input_file)
    if verbose:
        print(f"  ✓ Parsed: {len(landscapes)} landscapes, {len(portraits)} portraits")
    
    # Step 2: Create frameglasses
    frameglasses = create_frameglasses(landscapes, portraits)
    if verbose:
        print(f"  ✓ Created {len(frameglasses)} frameglasses")
    
    # Step 3: Test all ordering strategies
    strategies = {
        "same": order_same,
        "reverse": order_reverse,
        "random": order_random,
        "by_tags": order_by_tag_count,
        "greedy": order_greedy
    }
    
    best_score = -1
    best_strategy = None
    best_ordered = None
    
    if verbose:
        print(f"\n  Testing strategies:")
    
    for strategy_name, strategy_func in strategies.items():
        ordered = strategy_func(frameglasses)
        score = calculate_total_score(ordered)
        
        if verbose:
            print(f"    • {strategy_name:12s}: Score = {score:,}")
        
        if score > best_score:
            best_score = score
            best_strategy = strategy_name
            best_ordered = ordered
    
    # Step 4: Write output
    write_output(output_file, best_ordered)
    
    elapsed = time.time() - start_time
    
    if verbose:
        print(f"\n  🏆 Best strategy: {best_strategy}")
        print(f"  📊 Best score: {best_score:,}")
        print(f"  ⏱️  Time: {elapsed:.3f}s")
        print(f"  ✓ Output: {output_file}")
        print(f"{'='*70}\n")
    
    return best_score, elapsed


# ============================================================================
# TASK 7: PROCESS ALL SHOWROOMS
# ============================================================================

def solve_all_files():
    """Process all 5 showroom files sequentially."""
    import os
    
    # File mappings for all 5 showrooms
    files = [
        ("0_example.txt", "0_output.txt"),
        ("1_binary_landscapes.txt", "1_output.txt"),
        ("10_computable_moments.txt", "10_output.txt"),
        ("11_randomizing_paintings.txt", "11_output.txt"),
        ("110_oily_portraits.txt", "110_output.txt")
    ]
    
    print("=" * 70)
    print(" BATTLE OF HEURISTICS - EXHIBITION OPENING CHALLENGE")
    print("=" * 70)
    print(f" Processing {len(files)} showrooms...\n")
    
    total_score = 0
    total_time = 0
    results = []
    missing_files = []
    
    for input_file, output_file in files:
        if not os.path.exists(input_file):
            print(f"⚠️  Skipping {input_file} (file not found)")
            missing_files.append(input_file)
            continue
        
        try:
            score, elapsed = solve_file(input_file, output_file, verbose=True)
            total_score += score
            total_time += elapsed
            results.append((input_file, score, elapsed))
        except Exception as e:
            print(f"❌ Error processing {input_file}: {e}")
            import traceback
            traceback.print_exc()
    
    # Final summary
    print("\n" + "=" * 70)
    print(" FINAL RESULTS SUMMARY")
    print("=" * 70)
    print(f"\n{'File Name':<35} {'Score':>15} {'Time':>12}")
    print("-" * 70)
    
    for filename, score, elapsed in results:
        print(f"{filename:<35} {score:>15,} {elapsed:>11.3f}s")
    
    print("-" * 70)
    print(f"{'TOTAL (' + str(len(results)) + ' files)':<35} {total_score:>15,} {total_time:>11.3f}s")
    print("=" * 70)
    
    # Time limit check (20 minutes = 1200 seconds)
    if total_time > 1200:
        print(f"\n⚠️  WARNING: Exceeded 20-minute limit by {total_time - 1200:.1f}s!")
    else:
        print(f"\n✅ Within time limit! ({1200 - total_time:.1f}s remaining)")
    
    if missing_files:
        print(f"\n⚠️  Missing files ({len(missing_files)}):")
        for f in missing_files:
            print(f"   • {f}")
    
    print(f"\n✅ Successfully processed {len(results)}/{len(files)} files")
    
    return total_score, total_time


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments: process all files
        print("\n🚀 Running in batch mode (all files)...\n")
        solve_all_files()
        
    elif len(sys.argv) == 2:
        # Single argument: process one file, auto-generate output name
        input_file = sys.argv[1]
        output_file = input_file.replace('.txt', '_output.txt')
        
        try:
            score, elapsed = solve_file(input_file, output_file)
            print(f"\n✅ SUCCESS! Score: {score:,} | Time: {elapsed:.3f}s")
        except FileNotFoundError:
            print(f"\n❌ Error: File '{input_file}' not found!")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
            
    elif len(sys.argv) == 3:
        # Two arguments: input and output files specified
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
        try:
            score, elapsed = solve_file(input_file, output_file)
            print(f"\n✅ SUCCESS! Score: {score:,} | Time: {elapsed:.3f}s")
        except FileNotFoundError:
            print(f"\n❌ Error: File '{input_file}' not found!")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
            
    else:
        print("\n📖 USAGE:")
        print("  python hcw_solution.py                      # Process all 5 files")
        print("  python hcw_solution.py <input_file>         # Process one file")
        print("  python hcw_solution.py <input> <output>     # Specify both files")
        print("\n📝 EXAMPLES:")
        print("  python hcw_solution.py")
        print("  python hcw_solution.py 0_example.txt")
        print("  python hcw_solution.py 0_example.txt my_output.txt")
        sys.exit(1)
