#!/usr/bin/env python3
"""
HCW Challenge Solution - Team XX
Family Names: [Your Family Names]
First Names: [Your First Names]
Team Number: XX
"""

import sys
import os
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
                if not parts:  # Skip empty lines
                    continue
                orientation = parts[0]
                m = int(parts[1])
                tags = set(parts[2:2+m])
                paintings.append(Painting(i, orientation, tags))
    except Exception as e:
        print(f"Error reading input file {filename}: {e}")
        return []
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
    try:
        with open(filename, 'w') as f:
            f.write(f"{len(frameglasses)}\n")
            for fg in frameglasses:
                if len(fg.painting_ids) == 1:
                    f.write(f"{fg.painting_ids[0]}\n")
                else:  # portrait pair
                    f.write(f"{fg.painting_ids[0]} {fg.painting_ids[1]}\n")
        return True
    except Exception as e:
        print(f"✗ Error writing output file {filename}: {e}")
        return False

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

def find_input_files():
    """Automatically find all input files in current directory and Data folder"""
    input_files = []
    
    # Check current directory
    current_dir_files = [f for f in os.listdir('.') 
                        if f.endswith('.txt') and not f.startswith('output_') and not f.startswith('KCW_')]
    input_files.extend(current_dir_files)
    
    # Check Data folder if it exists
    if os.path.exists('Data'):
        data_files = [os.path.join('Data', f) for f in os.listdir('Data') 
                     if f.endswith('.txt') and not f.startswith('output_')]
        input_files.extend(data_files)
    
    # Remove duplicates and sort
    input_files = sorted(list(set(input_files)))
    return input_files

def display_progress(current, total, message=""):
    """Display a progress bar"""
    bar_length = 30
    progress = float(current) / total
    block = int(round(bar_length * progress))
    text = f"\r[{'█' * block}{'░' * (bar_length - block)}] {current}/{total} {message}"
    sys.stdout.write(text)
    sys.stdout.flush()

def process_single_file_live(input_file: str, file_index: int, total_files: int):
    """Process a single input file with live progress"""
    print(f"\n\n{'='*70}")
    print(f"📁 FILE {file_index}/{total_files}: {input_file}")
    print(f"{'='*70}")
    
    # Parse input
    display_progress(0, 5, "Parsing input file...")
    paintings = parse_input(input_file)
    if not paintings:
        print(f"\n❌ No paintings found in {input_file}")
        return None, -1, {}
    
    display_progress(1, 5, f"Parsed {len(paintings)} paintings")
    time.sleep(0.5)  # Small delay for better visualization
    
    # Define strategies to test (page 45)
    strategies = [
        ("Same order", order_frameglasses_same),
        ("Reverse order", order_frameglasses_reverse),
        ("Random order", order_frameglasses_random),
        ("Ascending tag count", order_frameglasses_by_tag_count, {"ascending": True}),
        ("Descending tag count", order_frameglasses_by_tag_count, {"ascending": False}),
    ]
    
    strategy_scores = {}
    best_score = -1
    best_strategy = None
    best_ordering = None
    
    display_progress(2, 5, "Evaluating strategies...")
    
    print(f"\n\n📊 STRATEGY EVALUATION:")
    print("-" * 60)
    
    # Run multiple random trials for better results
    random_trials = 3  # Reduced for faster live feedback
    
    for i, strategy in enumerate(strategies):
        strategy_name = strategy[0]
        order_function = strategy[1]
        kwargs = strategy[2] if len(strategy) > 2 else {}
        
        if strategy_name == "Random order":
            # Run multiple random trials and take the best
            best_random_score = -1
            best_random_ordering = None
            for trial in range(random_trials):
                score, exec_time, ordering = evaluate_strategy(
                    paintings, f"{strategy_name} (trial {trial+1})", order_function, **kwargs
                )
                if score > best_random_score:
                    best_random_score = score
                    best_random_ordering = ordering
            score = best_random_score
            ordering = best_random_ordering
            exec_time = 0.001
        else:
            score, exec_time, ordering = evaluate_strategy(
                paintings, strategy_name, order_function, **kwargs
            )
        
        strategy_scores[strategy_name] = score
        
        # Visual indicator for current best
        best_indicator = " 🏆" if score == best_score else " ★" if score > best_score else ""
        if score > best_score:
            best_score = score
            best_strategy = strategy_name
            best_ordering = ordering
        
        print(f"  {i+1}. {strategy_name:25} | Score: {score:4d} | Time: {exec_time:.4f}s{best_indicator}")
    
    display_progress(4, 5, "Writing output files...")
    
    # Write best output
    output_file = f"output_{os.path.basename(input_file)}"
    success = write_output(output_file, best_ordering)
    
    if success:
        print(f"\n✅ Output written to: {output_file}")
    else:
        print(f"\n❌ Failed to write output file")
    
    display_progress(5, 5, "Complete!")
    
    # Data analysis
    print(f"\n📈 DATA ANALYSIS:")
    print("-" * 40)
    frameglasses = create_frameglasses(paintings)
    
    num_landscapes = len([p for p in paintings if p.orientation == 'L'])
    num_portraits = len([p for p in paintings if p.orientation == 'P'])
    
    print(f"  • Landscapes: {num_landscapes}")
    print(f"  • Portraits: {num_portraits}")
    print(f"  • Frameglasses: {len(frameglasses)}")
    
    # Tag statistics
    all_tags = set()
    for painting in paintings:
        all_tags.update(painting.tags)
    
    print(f"  • Unique tags: {len(all_tags)}")
    
    # Frameglass size distribution
    tag_counts = [len(fg.tags) for fg in frameglasses]
    if tag_counts:
        print(f"  • Avg tags/frameglass: {sum(tag_counts)/len(tag_counts):.2f}")
    
    print(f"\n🎯 BEST STRATEGY: {best_strategy} with score {best_score}")
    
    return output_file, best_score, strategy_scores

def main():
    print("🎨 HCW CHALLENGE - AUTOMATIC PROCESSOR")
    print("=" * 70)
    
    # Find all input files automatically
    input_files = find_input_files()
    
    if not input_files:
        print("❌ No input files found!")
        print("Please make sure you have .txt files in the current directory or in a 'Data' folder.")
        print("Looking for files like: example.txt, showroom1.txt, etc.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print(f"📂 Found {len(input_files)} input files:")
    for i, file in enumerate(input_files, 1):
        print(f"  {i}. {file}")
    
    print(f"\n🚀 Starting processing of {len(input_files)} files...")
    print("   Each file will be processed with 5 different ordering strategies.")
    print("   Live progress will be shown below.\n")
    
    input("Press Enter to start processing...")
    
    results = []
    total_score = 0
    all_strategy_scores = {}
    
    # Initialize strategy totals
    strategies = ["Same order", "Reverse order", "Random order", "Ascending tag count", "Descending tag count"]
    strategy_totals = {strategy: 0 for strategy in strategies}
    
    start_time = time.time()
    
    for i, input_file in enumerate(input_files, 1):
        output_file, score, strategy_scores = process_single_file_live(input_file, i, len(input_files))
        
        if output_file and score >= 0:
            results.append((os.path.basename(input_file), output_file, score, strategy_scores))
            total_score += score
            
            # Accumulate strategy scores
            for strategy, strat_score in strategy_scores.items():
                strategy_totals[strategy] += strat_score
            
            # Add a small delay between files for better readability
            if i < len(input_files):
                print(f"\n⏳ Preparing next file...")
                time.sleep(1)
    
    total_time = time.time() - start_time
    
    # Print final summary
    print(f"\n\n{'='*70}")
    print("🏆 FINAL RESULTS SUMMARY")
    print(f"{'='*70}")
    
    print(f"\n📊 INDIVIDUAL FILE RESULTS:")
    print("-" * 70)
    for input_file, output_file, score, strategy_scores in results:
        best_strat = max(strategy_scores.items(), key=lambda x: x[1])
        print(f"  {input_file:25} → Score: {score:4d} | Best: {best_strat[0]}")
    
    print(f"\n📈 STRATEGY PERFORMANCE SUMMARY:")
    print("-" * 70)
    for strategy in strategies:
        print(f"  {strategy:25} | Total Score: {strategy_totals[strategy]:4d}")
    
    best_overall_strategy = max(strategy_totals.items(), key=lambda x: x[1])
    
    print(f"\n{'='*70}")
    print(f"📋 TOTAL FILES PROCESSED : {len(results)}")
    print(f"⏱️  TOTAL PROCESSING TIME : {total_time:.2f} seconds")
    print(f"🏆 OVERALL TOTAL SCORE   : {total_score}")
    print(f"🎯 BEST OVERALL STRATEGY : {best_overall_strategy[0]} (Score: {best_overall_strategy[1]})")
    print(f"{'='*70}")
    
    # Save results to file
    with open("KCW_final_results.txt", "w") as f:
        f.write("HCW Challenge - Final Results\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Files Processed: {len(results)}\n")
        f.write(f"Total Processing Time: {total_time:.2f} seconds\n")
        f.write(f"Overall Total Score: {total_score}\n\n")
        
        f.write("Individual File Results:\n")
        f.write("-" * 40 + "\n")
        for input_file, output_file, score, strategy_scores in results:
            f.write(f"{input_file} -> {output_file} : {score}\n")
        
        f.write("\nStrategy Performance:\n")
        f.write("-" * 40 + "\n")
        for strategy in strategies:
            f.write(f"{strategy}: {strategy_totals[strategy]}\n")
        
        f.write(f"\nBest Overall Strategy: {best_overall_strategy[0]} (Score: {best_overall_strategy[1]})\n")
    
    print(f"\n💾 Detailed results saved to: KCW_final_results.txt")
    
    # Wait for user input before closing
    input(f"\n🎉 Processing complete! Press Enter to exit...")

if __name__ == "__main__":
    main()
