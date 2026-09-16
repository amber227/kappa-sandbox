"""Run the full set of PyKappa proofreading experiments (resumable, 4-way parallel)."""
import os, sys, json, time, math
from dataclasses import asdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "results")
os.makedirs(OUT, exist_ok=True)

from model import Params
from run import simulate, summarise

LN10 = math.log(10.0)


def jobs():
    J = []
    def add(name, n_events, seed, keep_traj=False, **kw):
        J.append(dict(name=name, n_events=n_events, seed=seed,
                      keep_traj=keep_traj, params=kw))

    # --- main comparison ----------------------------------------------------
    add("main_C_driven", 2_600_000, 101, True, proofread=True, drive=20.0)
    add("main_B",          700_000, 102, True, proofread=False)
    add("main_C_nodrive",  400_000, 103, True, proofread=True, drive=0.0)

    # --- discrimination sweep: protocol B vs C ------------------------------
    for d, nC, nB in [(1.05, 300_000, 400_000), (1.40, 450_000, 400_000),
                      (1.75, 700_000, 450_000), (2.10, 1_000_000, 500_000),
                      (2.45, 1_500_000, 600_000)]:
        add(f"delta_B_{d:.2f}", nB, 200 + int(d * 100), proofread=False, delta=d)
        add(f"delta_C_{d:.2f}", nC, 300 + int(d * 100), proofread=True, delta=d, drive=20.0)

    # --- drive sweep --------------------------------------------------------
    for A in [0.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 14.0]:
        add(f"drive_{A:04.1f}", 500_000, 400 + int(A * 10), proofread=True, drive=A)

    # --- proofreading-strength sweep (speed / accuracy / cost) --------------
    for a in [0.1, 0.2, 0.3, 0.4, 0.6, 0.8]:
        add(f"pfr_{a:.2f}", 700_000, 600 + int(a * 100), proofread=True, pf_ratio=a)
    return J


def run_job(j):
    path = os.path.join(OUT, j["name"] + ".json")
    if os.path.exists(path):
        return f"skip {j['name']}"
    p = Params(**j["params"])
    t0 = time.time()
    df, tally = simulate(p, j["n_events"], seed=j["seed"])
    s = summarise(df, p, tally)
    rec = dict(name=j["name"], params=asdict(p), rates=p.rates(),
               n_events=j["n_events"], seed=j["seed"], wall=time.time() - t0,
               tally=tally, **s)
    with open(path, "w") as f:
        json.dump(rec, f, indent=1)
    if j["keep_traj"]:
        df.to_csv(os.path.join(OUT, j["name"] + "_traj.csv"), index=False)
    return (f"{j['name']:20s} eta={s['eta']:.5f} n={s['n_incorp']:.0f} "
            f"v={s['velocity']:.3f} cost={s['cost']:.2f} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    J = jobs()
    print(f"{len(J)} jobs, {sum(x['n_events'] for x in J)/1e6:.1f}M events", flush=True)
    with Pool(4) as pool:
        for msg in pool.imap_unordered(run_job, J):
            print(msg, flush=True)
    print("DONE", flush=True)
