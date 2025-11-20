#!/usr/bin/env python3
"""
HCW Challenge Solution - Team XX
Family Names: [Your Family Names]
First Names: [Your First Names]
Team Number: XX
"""

import sys
import time
import random
from typing import List, Tuple, Set, Dict

class Painting:
    def __init__(self, pid: int, orientation: str, tags: Set[str]):
        self.id = pid
        self.orientation = orientation
        self.tags = tags
    
    def __repr__(self):
        return f"Painting({self.id}, {self.orientation}, {self.tags})"

class Frameglass:
    def __init__(self, painting_ids: List[int], tags: Set[str]):
        self.painting_ids = painting_ids
        self.tags = tags
    
    def __repr__(self):
        return f"Frameglass({self.painting_ids}, {self.tags})"

def parse_input(filename: str) -> List[Painting]:
    """Parse input file according to page 9 specification"""
    paintings = []
    try:
        with open(filename, 'r') as f:
            n = int(f.readline().strip())
            for i in range(n):
                parts = f.readline().strip().split()
                orientation = parts[0]
                m = int(parts[1])
                tags = set(parts[2:2+m])
                paintings.append(Painting(i, orientation, tags))
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    return paintings

def create_frameglasses(paintings: List[Painting]) -> List[Frameglass]:
    """Create frameglasses from paintings (page 13)"""
    landscapes = [p for p in paintings if p.orientation == 'L']
    portraits = [p for p in paintings if p.orientation == 'P']
    
    frameglasses = []
    
    # Create frameglasses for landscapes (one painting each)
    for landscape in landscapes:
        frameglasses.append(Frameglass([landscape.id], landscape.tags))
    
    # Create frameglasses for portraits (two paintings each)
    if len(portraits) % 2 != 0:
        print(f"Warning: Odd number of portraits ({len(portraits)}). Dropping one.")
        portraits = portraits[:-1]  # Drop last portrait if odd
    
    for i in range(0, len(portraits), 2):
        p1, p2 = portraits[i], portraits[i+1]
        combined_tags = p1.tags.union(p2.tags)
        frameglasses.append(Frameglass([p1.id, p2.id], combined_tags))
    
    return frameglasses

def order_frameglasses_same(frameglasses: List[Frameglass]) -> List[Frameglass]:
    """Strategy 1: Same order as created"""
    return frameglasses.copy()

def order_frameglasses_reverse(frameglasses: List[Frameglass]) -> List[Frameglass]:
    """Strategy 2: Reverse order"""
    return frameglasses[::-1]

def order_frameglasses_random(frameglasses: List[Frameglass]) -> List[Frameglass]:
    """Strategy 3: Random order"""
    shuffled = frameglasses.copy()
    random.shuffle(shuffled)
    return shuffled

def order_frameglasses_by_tag_count(frameglasses: List[Frameglass], ascending: bool = True) -> List[Frameglass]:
    """Strategy 4: Order by number of tags"""
    return sorted(frameglasses, key=lambda fg: len(fg.tags), reverse=not ascending)

def compute_local_score(tags1: Set[str], tags2: Set[str]) -> int:
    """Compute local satisfaction score between two frameglasses (page 19)"""
    common = len(tags1.intersection(tags2))
    only1 = len(tags1 - tags2)
    only2 = len(tags2 - tags1)
    return min(common, only1, only2)

def compute_global_score(ordered_frameglasses: List[Frameglass]) -> int:
    """Compute global satisfaction score for ordered frameglasses (page 19)"""
    if len(ordered_frameglasses) < 2:
        return 0
    
    total_score = 0
    for i in range(len(ordered_frameglasses) - 1):
        score = compute_local_score(
            ordered_frameglasses[i].tags,
            ordered_frameglasses[i+1].tags
        )
        total_score += score
    
    return total_score

def write_output(filename: str, frameglasses: List[Frameglass]):
    """Write output file according to page 29 specification"""
    with open(filename, 'w') as f:
        f.write(f"{len(frameglasses)}\n")
        for fg in frameglasses:
            if len(fg.painting_ids) == 1:
                f.write(f"{fg.painting_ids[0]}\n")
            else:  # portrait pair
                f.write(f"{fg.painting_ids[0]} {fg.painting_ids[1]}\n")

def evaluate_strategy(paintings: List[Painting], strategy_name: str, 
                     order_function, **kwargs) -> Tuple[int, float, List[Frameglass]]:
    """Evaluate a single ordering strategy"""
    start_time = time.time()
    
    # Create frameglasses
    frameglasses = create_frameglasses(paintings)
    
    # Order frameglasses
    ordered_frameglasses = order_function(frameglasses, **kwargs) if kwargs else order_function(frameglasses)
    
    # Compute score
    score = compute_global_score(ordered_frameglasses)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return score, execution_time, ordered_frameglasses

def main():
    if len(sys.argv) != 2:
        print("Usage: python KCW_Team_XX.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = f"output_{input_file.split('/')[-1]}"
    
    print(f"Processing {input_file}...")
    
    # Parse input
    paintings = parse_input(input_file)
    print(f"Parsed {len(paintings)} paintings")
    
    # Define strategies to test (page 45)
    strategies = [
        ("Same order", order_frameglasses_same),
        ("Reverse order", order_frameglasses_reverse),
        ("Random order", order_frameglasses_random),
        ("Ascending tag count", order_frameglasses_by_tag_count, {"ascending": True}),
        ("Descending tag count", order_frameglasses_by_tag_count, {"ascending": False}),
    ]
    
    best_score = -1
    best_strategy = None
    best_ordering = None
    
    print("\nEvaluating strategies:")
    print("-" * 60)
    
    for strategy in strategies:
        strategy_name = strategy[0]
        order_function = strategy[1]
        kwargs = strategy[2] if len(strategy) > 2 else {}
        
        score, exec_time, ordering = evaluate_strategy(
            paintings, strategy_name, order_function, **kwargs
        )
        
        print(f"{strategy_name:20} | Score: {score:4d} | Time: {exec_time:.4f}s")
        
        if score > best_score:
            best_score = score
            best_strategy = strategy_name
            best_ordering = ordering
    
    print("-" * 60)
    print(f"Best strategy: {best_strategy} with score {best_score}")
    
    # Write best output
    write_output(output_file, best_ordering)
    print(f"Output written to {output_file}")
    
    # Additional analysis (pages 46-50)
    print("\n--- Data Analysis ---")
    frameglasses = create_frameglasses(paintings)
    
    num_landscapes = len([p for p in paintings if p.orientation == 'L'])
    num_portraits = len([p for p in paintings if p.orientation == 'P'])
    
    print(f"Landscapes: {num_landscapes}")
    print(f"Portraits: {num_portraits}")
    print(f"Frameglasses created: {len(frameglasses)}")
    
    # Tag statistics
    all_tags = set()
    for painting in paintings:
        all_tags.update(painting.tags)
    
    print(f"Unique tags: {len(all_tags)}")
    
    # Frameglass size distribution
    tag_counts = [len(fg.tags) for fg in frameglasses]
    if tag_counts:
        print(f"Avg tags per frameglass: {sum(tag_counts)/len(tag_counts):.2f}")
        print(f"Min tags: {min(tag_counts)}, Max tags: {max(tag_counts)}")

if __name__ == "__main__":
    main()
