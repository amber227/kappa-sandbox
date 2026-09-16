"""Emit report/macros.tex so every number quoted in the report comes from the data."""
import os, sys, json, glob, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE); RES = os.path.join(ROOT, "results")
from model import Params, landscape
from theory import self_consistent_eta

def load(pat):
    out = {}
    for f in sorted(glob.glob(os.path.join(RES, pat))):
        r = json.load(open(f))
        if "name" in r: out[r["name"]] = r
    return out

DEFINED = set()


def fmt(x, n=3):
    if x is None or not np.isfinite(x): return "--"
    return f"{x:.{n}g}"

L = []
def m(name, val):
    DEFINED.add(name)
    L.append(rf"\providecommand{{\{name}}}{{}}\renewcommand{{\{name}}}{{{val}}}")

POSSIBLE = set("""githash pardelta parfdisc parassoc parkoffR parkoffW parkcat parkunR
parkpfR parkpfW parkligc parvcom pardrive parconc parnchains parpfratio parkon parkchemo
lsdEoneR lsdEoneW lsdEtwoR lsdEtwoW lswomegazeroone lswomegaonetwo lswomegatwozero
lsdeltatwoone etaeq etahop etairr etaB etaloB etahiB nB vB costB evB thB etaC etaloC
etahiC nC vC costC evC thC etaCz etaloCz etahiCz nCz vCz costCz evCz thCz gain slowdown
slopeB slopethB slopeC slopethC prefac drivecross etaCtheory etaBtheory vCtheory
vBtheory njobs nevents sloperatio etafloor etaBsq astall etaCstall stallratio
vstall""".split())

git = subprocess.run(["git","-C",ROOT,"rev-parse","--short","HEAD"],
                     capture_output=True, text=True).stdout.strip()
m("githash", git)

p = Params(); r = p.rates(); ls = landscape(p)
for k, v in [("delta", p.delta), ("fdisc", r["f"]), ("assoc", p.assoc),
             ("koffR", r["k_off_R"]), ("koffW", r["k_off_W"]), ("kcat", r["k_cat_R"]),
             ("kunR", r["k_un_R"]), ("kpfR", r["k_pf_R"]), ("kpfW", r["k_pf_W"]),
             ("kligc", r["k_lig_R"] * p.c), ("vcom", r["v_commit"]),
             ("drive", p.drive), ("conc", p.c), ("nchains", p.n_chains),
             ("pfratio", p.pf_ratio), ("kon", r["k_on"]), ("kchemo", p.k_chemo)]:
    m("par" + k.replace("_", ""), fmt(v, 4))
for k, v in [("dEoneR", ls["dE"][1]["R"]), ("dEoneW", ls["dE"][1]["W"]),
             ("dEtwoR", ls["dE"][2]["R"]), ("dEtwoW", ls["dE"][2]["W"]),
             ("womegazeroone", ls["w"]["01"]), ("womegaonetwo", ls["w"]["12"]),
             ("womegatwozero", ls["w"]["20"]), ("deltatwoone", ls["delta_21"])]:
    m("ls" + k, fmt(v, 4))
m("etaeq", fmt(1/(1+np.exp(p.delta)), 4))
m("etahop", fmt(np.exp(-2*p.delta), 3))
m("etairr", fmt(np.exp(-p.delta)/(1+np.exp(-p.delta)), 4))

R = load("*.json")
for nm, key in [("main_B", "B"), ("main_C_driven", "C"), ("main_C_nodrive", "Cz")]:
    rr = R.get(nm)
    if not rr: continue
    m(f"eta{key}", fmt(rr["eta"], 3))
    m(f"etalo{key}", fmt(rr["eta_lo"], 3)); m(f"etahi{key}", fmt(rr["eta_hi"], 3))
    m(f"n{key}", f"{int(rr['n_incorp']):,}".replace(",", r"\,"))
    m(f"v{key}", fmt(rr["velocity"], 3))
    m(f"cost{key}", fmt(rr["cost"], 3))
    m(f"ev{key}", f"{rr['n_events']//1000}")
    m(f"th{key}", fmt(self_consistent_eta(Params(**rr["params"]))["eta"], 3))
if "main_B" in R and "main_C_driven" in R:
    m("gain", fmt(R["main_B"]["eta"] / R["main_C_driven"]["eta"], 3))
    m("slowdown", fmt(R["main_B"]["velocity"] / R["main_C_driven"]["velocity"], 3))

# fitted slopes of the delta sweep
for tag, key in [("B", "delta_B_*.json"), ("C", "delta_C_*.json")]:
    S = load(key)
    if len(S) >= 3:
        d = np.array([v["params"]["delta"] for v in S.values()])
        e = np.array([v["eta"] for v in S.values()])
        ok = e > 0
        m(f"slope{tag}", fmt(np.polyfit(d[ok], np.log(e[ok]), 1)[0], 3))
        th = np.array([self_consistent_eta(Params(**v["params"]))["eta"] for v in S.values()])
        m(f"slopeth{tag}", fmt(np.polyfit(d, np.log(th), 1)[0], 3))
SB, SC = load("delta_B_*.json"), load("delta_C_*.json")
if SB and SC:
    ds = sorted(set(round(v["params"]["delta"], 2) for v in SB.values())
                & set(round(v["params"]["delta"], 2) for v in SC.values()))
    rat = []
    for d in ds:
        b = [v for v in SB.values() if round(v["params"]["delta"], 2) == d][0]
        c = [v for v in SC.values() if round(v["params"]["delta"], 2) == d][0]
        if c["eta"] > 0: rat.append(c["eta"] / b["eta"] ** 2)
    if rat: m("prefac", fmt(float(np.mean(rat)), 3))

# drive at which protocol C overtakes protocol B
A = np.linspace(0, 20, 801)
et = np.array([self_consistent_eta(Params(drive=a))["eta"] for a in A])
eb = self_consistent_eta(Params(proofread=False))["eta"]
cross = A[np.argmax(et < eb)] if np.any(et < eb) else np.nan
m("drivecross", fmt(cross, 3))
m("etaCtheory", fmt(self_consistent_eta(Params())["eta"], 3))
m("etaBtheory", fmt(eb, 3))
m("vCtheory", fmt(self_consistent_eta(Params())["velocity"], 3))
m("vBtheory", fmt(self_consistent_eta(Params(proofread=False))["velocity"], 3))
# slope ratio, stall point, zero-speed floor
SB2, SC2 = load("delta_B_*.json"), load("delta_C_*.json")
if len(SB2) >= 3 and len(SC2) >= 3:
    def _sl(S):
        d = np.array([v["params"]["delta"] for v in S.values()])
        e = np.array([v["eta"] for v in S.values()]); ok = e > 0
        return np.polyfit(d[ok], np.log(e[ok]), 1)[0]
    m("sloperatio", fmt(_sl(SC2) / _sl(SB2), 3))
eq = 1 / (1 + np.exp(p.delta))
m("etafloor", fmt(eq**2, 3))
_eB = self_consistent_eta(Params(proofread=False))["eta"]
m("etaBsq", fmt(_eB**2, 3))
astar, prev = np.nan, None
for a in np.arange(0.40, 0.99, 0.005):
    t = self_consistent_eta(Params(pf_ratio=float(a)))
    if np.isfinite(t["eta"]) and t["velocity"] > 0:
        prev = (float(a), t)
    else:
        break
if prev:
    astar = prev[0]
    m("astall", fmt(astar, 3))
    m("etaCstall", fmt(prev[1]["eta"], 3))
    m("stallratio", fmt(prev[1]["eta"] / _eB**2, 3))
    m("vstall", fmt(prev[1]["velocity"], 2))
m("njobs", str(len(glob.glob(os.path.join(RES, "*.json")))))
m("nevents", fmt(sum(v["n_events"] for v in R.values())/1e6, 3))

# any macro the text uses but the data does not yet provide gets a loud placeholder,
# so a missing run shows up in the PDF instead of breaking the build
import re
REP = os.path.join(ROOT, "report")
used = set()
for f in ("body.tex", "abstract.tex"):
    try:
        used |= set(re.findall(r"\\([a-z][a-zA-Z]*)\b", open(os.path.join(REP, f)).read()))
    except FileNotFoundError:
        pass
missing = sorted((used & POSSIBLE) - DEFINED)
head = [rf"\providecommand{{\{n}}}{{\textbf{{[no data]}}}}" for n in missing]
os.makedirs(REP, exist_ok=True)
open(os.path.join(REP, "macros.tex"), "w").write("\n".join(head + L) + "\n")
print(f"wrote {len(DEFINED)} macros; placeholders for {missing}")
