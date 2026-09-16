"""Re-run the high-flux (low-drive) conditions with a stiffer monomer chemostat.

At mu_02 = 0 the futile ligation/excision cycle consumes monomers ~200x faster than
at the working point, and the default chemostat gain (k_chemo = 500) lets the free
pool fall ~30% below its set point.  Raising the gain costs nothing in events --- the
number of replenishment events equals the number of monomers consumed either way ---
so these conditions are repeated with k_chemo = 1e5, which holds the pool to <1%.
"""
import os, sys, json, time
from dataclasses import asdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE); OUT = os.path.join(ROOT, "results")
from model import Params
from run import simulate, summarise
from experiments import jobs, run_job

STIFF = 1e5
REDO = {"main_C_nodrive", "drive_00.0", "drive_02.0", "drive_03.0", "drive_04.0"}

if __name__ == "__main__":
    J = []
    for j in jobs():
        if j["name"] in REDO:
            j = dict(j); j["params"] = dict(j["params"], k_chemo=STIFF)
            p = os.path.join(OUT, j["name"] + ".json")
            if os.path.exists(p):
                old = json.load(open(p))
                if old["params"].get("k_chemo") == STIFF:
                    continue
                os.rename(p, p + ".lowgain")
            J.append(j)
    print(f"{len(J)} re-runs: {[x['name'] for x in J]}", flush=True)
    with Pool(4) as pool:
        for msg in pool.imap_unordered(run_job, J):
            print(msg, flush=True)
    print("FOLLOWUP DONE", flush=True)
