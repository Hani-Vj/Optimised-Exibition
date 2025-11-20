#!/usr/bin/env python3
import os, time, random
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict

# --------------------------- Data Structures ---------------------------
class Painting:
    __slots__ = ('id','orientation','tag_ids','tag_count')
    def __init__(self,pid,ori,tag_ids):
        self.id = pid
        self.orientation = ori
        self.tag_ids = tag_ids
        self.tag_count = len(tag_ids)

class Frame:
    __slots__ = ('paintings','tag_ids_set','tag_count')
    def __init__(self,paintings):
        self.paintings = paintings
        tag_ids = set()
        for p in paintings:
            tag_ids |= p.tag_ids
        self.tag_ids_set = tag_ids
        self.tag_count = len(tag_ids)
    def get_line(self):
        return ' '.join(str(p.id) for p in self.paintings)

# --------------------------- Input Parsing ---------------------------
def parse_input(fname, tag2id):
    with open(fname,'r') as f:
        n = int(f.readline().strip())
        landscapes, portraits = [], []
        for pid in range(n):
            parts = f.readline().split()
            ori = parts[0]
            tags = parts[2:]
            tag_ids = set()
            for t in tags:
                if t not in tag2id:
                    tag2id[t] = len(tag2id)
                tag_ids.add(tag2id[t])
            p = Painting(pid, ori, tag_ids)
            if ori=='L':
                landscapes.append(p)
            else:
                portraits.append(p)
    return landscapes, portraits

# --------------------------- Frame Creation ---------------------------
def create_frames(landscapes, portraits):
    frames = [Frame([p]) for p in landscapes]
    portraits.sort(key=lambda p: p.tag_count)
    i,j = 0,len(portraits)-1
    while i<j:
        frames.append(Frame([portraits[i], portraits[j]]))
        i+=1
        j-=1
    if i==j:
        frames.append(Frame([portraits[i]]))
    return frames

# --------------------------- Scoring ---------------------------
def local_score(f1,f2):
    c = len(f1.tag_ids_set & f2.tag_ids_set)
    o1 = f1.tag_count - c
    o2 = f2.tag_count - c
    return min(c,o1,o2)

def total_score(frames):
    score = 0
    for i in range(len(frames)-1):
        score += local_score(frames[i], frames[i+1])
    return score

# --------------------------- Strategies ---------------------------
def strat_same(frames): return frames[:]
def strat_reverse(frames): return list(reversed(frames))
def strat_random(frames):
    arr = frames[:]
    random.shuffle(arr)
    return arr
def strat_by_tags(frames): return sorted(frames, key=lambda f: f.tag_count)

# --------------------------- Candidate-limited Greedy ---------------------------
def strat_greedy_fast(frames):
    if not frames: return []
    remaining = frames[:]
    result = []

    idx = max(range(len(remaining)), key=lambda i: remaining[i].tag_count)
    current = remaining.pop(idx)
    result.append(current)

    LIMIT_CANDIDATES = 1000
    while remaining:
        sample = remaining[:LIMIT_CANDIDATES] if len(remaining)>LIMIT_CANDIDATES else remaining
        next_frame = max(sample, key=lambda f: local_score(current,f))
        remaining.remove(next_frame)
        result.append(next_frame)
        current = next_frame
    return result

# --------------------------- Output ---------------------------
def write_output(fname, frames):
    os.makedirs('Output', exist_ok=True)
    with open(f'Output/{fname}','w') as f:
        f.write(str(len(frames))+'\n')
        for fr in frames:
            f.write(fr.get_line()+'\n')

# --------------------------- Process Single File ---------------------------
def process_file_worker(args):
    fname, strategy, tag2id = args
    start = time.time()
    landscapes, portraits = parse_input(fname, tag2id)
    frames = create_frames(landscapes, portraits)

    strategies_dict = {
        "same": strat_same,
        "reverse": strat_reverse,
        "random": strat_random,
        "by_tags": strat_by_tags,
        "greedy": strat_greedy_fast
    }

    if strategy=="1":  # run all strategies
        best_score = -1
        best_result = None
        for name,func in strategies_dict.items():
            arr = func(frames)
            sc = total_score(arr)
            if sc>best_score:
                best_score = sc
                best_result = arr
        write_output(fname,best_result)
        elapsed = time.time()-start
        return (fname,best_score,elapsed)
    else:
        sname = {"2":"same","3":"reverse","4":"random","5":"by_tags","6":"greedy"}[strategy]
        arr = strategies_dict[sname](frames)
        sc = total_score(arr)
        write_output(fname,arr)
        elapsed = time.time()-start
        return (fname,sc,elapsed)

# --------------------------- Progress Bar ---------------------------
def update_progress(completed,total,start,scores_times):
    elapsed = time.time()-start
    speed = completed/elapsed if elapsed>0 else 0.0001
    remaining = (total-completed)/speed
    percent = completed/total
    bar_len = 40
    filled = int(percent*bar_len)
    bar = '█'*filled + '░'*(bar_len-filled)
    spinner = ['|','/','-','\\']
    spin = spinner[completed%4]
    print(f"\r{spin} [{bar}] {percent*100:5.1f}% ({completed}/{total}) | Elapsed: {int(elapsed)}s | ETA: {int(remaining)}s | Speed: {speed:.2f} files/s",end='',flush=True)

# --------------------------- Main ---------------------------
def main():
    input_files = sorted([f for f in os.listdir('.') if f.endswith('.txt')])
    if not input_files:
        print("No input files found.")
        return

    choice = input("\nStrategy Menu:\n1-Run ALL\n2-same\n3-reverse\n4-random\n5-by_tags\n6-greedy\nEnter choice (1-6): ").strip()
    total_files = len(input_files)
    tag2id = dict()
    total_score_sum = 0
    total_time_sum = 0
    completed = 0
    start_global = time.time()

    args_list = [(f,choice,tag2id) for f in input_files]

    scores_times = {}

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_file_worker,args): args[0] for args in args_list}
        for future in as_completed(futures):
            fname, score, t = future.result()
            scores_times[fname] = (score,t)
            completed += 1
            update_progress(completed,total_files,start_global,scores_times)
            print(f"\n  Finished {fname} | Score: {score} | Time: {t:.2f}s")

    # Total summary
    total_score_sum = sum(s for s,t in scores_times.values())
    total_time_sum = sum(t for s,t in scores_times.values())
    print("\n\n============== SUMMARY ==============")
    print(f"Total files processed: {total_files}")
    print(f"Total score: {total_score_sum:,}")
    print(f"Total time: {total_time_sum:.2f}s")
    print("=====================================")

if __name__=="__main__":
    main()
