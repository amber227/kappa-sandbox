"""Emit the Kappa listings and the parameter table used by the report."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE); REP = os.path.join(ROOT, "report")
os.makedirs(REP, exist_ok=True)
from model import Params, kappa, landscape

p = Params()
names = []
src = kappa(p, names).splitlines()

# --- full model -------------------------------------------------------------
open(os.path.join(REP, "model_base.ka"), "w").write(kappa(p) + "\n")

# --- annotated R-half of the rule set ---------------------------------------
DOC = {"add": "0 -> 1   the terminus recruits a free monomer into the active site",
       "reject": "1 -> 0   the monomer leaves again  (discriminating: x e^delta for W)",
       "commit": "1 -> 2   covalent incorporation     (NOT discriminating)",
       "uncommit": "2 -> 1   the reverse of commitment",
       "proofread": "2 -> 0   the terminal residue is excised back to the pool",
       "": ""}
lines, i = [], 0
rule_lines = [l for l in src if l and not l.startswith(("//", "%", " "))]
for nm, rl in zip(names, rule_lines):
    if not nm.endswith("_R"):
        continue
    base = nm[:-2]
    if base == "ligate":
        lines.append("// ligate     0 -> 2   thermodynamic reverse of proofreading;")
        lines.append("//                     its rate is fixed by detailed balance, Eq. (3)")
    elif base == "chemostat":
        lines.append("// chemostat  replenish the free pool towards its set point")
    else:
        lines.append(f"// {base:<10s} {DOC[base]}")
    lines.append(rl)
    lines.append("")
open(os.path.join(REP, "rules_R.ka"), "w").write("\n".join(lines).rstrip() + "\n")

# --- parameter table --------------------------------------------------------
r = p.rates(); L = landscape(p)
rows = [
 (r"$\delta=\Delta_1=\Delta_2$", f"{p.delta:.4g}", r"$\kB T$", "discrimination free energy; $e^{\\delta}=10$"),
 (r"$\mu_{02}$", f"{p.drive:.4g}", r"$\kB T$", "drive on the discard step (fuel)"),
 (r"$k^{\rm add}_{R}=k^{\rm add}_{W}=k_{\rm on}c$", f"{p.assoc:.4g}", "t$^{-1}$", r"$\delta_{01}=0$: association does not discriminate"),
 (r"$k^{\rm rej}_{R}$", f"{r['k_off_R']:.4g}", "t$^{-1}$", "rejection of a cognate monomer"),
 (r"$k^{\rm rej}_{W}$", f"{r['k_off_W']:.4g}", "t$^{-1}$", r"$=e^{\delta}k^{\rm rej}_{R}$"),
 (r"$k^{\rm com}_{R}=k^{\rm com}_{W}$", f"{r['k_cat_R']:.4g}", "t$^{-1}$", r"$\delta_{21}=\Delta$: chemistry does not discriminate"),
 (r"$k^{\rm unc}_{R}=k^{\rm unc}_{W}$", f"{r['k_un_R']:.4g}", "t$^{-1}$", "reverse of commitment"),
 (r"$k^{\rm pf}_{R}$", f"{r['k_pf_R']:.4g}", "t$^{-1}$", rf"$=\,{p.pf_ratio:g}\,v_{{\rm com}}$, $v_{{\rm com}}={r['v_commit']:.4g}$"),
 (r"$k^{\rm pf}_{W}$", f"{r['k_pf_W']:.4g}", "t$^{-1}$", r"$\delta_{02}=0$: $=e^{\delta}k^{\rm pf}_{R}$"),
 (r"$k^{\rm lig}_{R}c=k^{\rm lig}_{W}c$", f"{r['k_lig_R']*p.c:.4g}", "t$^{-1}$", "fixed by detailed balance, Eq.~(3)"),
 (r"$c_R=c_W$", f"{p.c}", "copies", "chemostatted free-monomer pool"),
 (r"$N_{\rm chains}$", f"{p.n_chains}", "copies", "independently growing copies"),
]
land = [
 (r"$\Delta E_1^{R}$", f"{L['dE'][1]['R']:.4g}"), (r"$\Delta E_1^{W}$", f"{L['dE'][1]['W']:.4g}"),
 (r"$\Delta E_2^{R}$", f"{L['dE'][2]['R']:.4g}"), (r"$\Delta E_2^{W}$", f"{L['dE'][2]['W']:.4g}"),
 (r"$\omega_{01}$", f"{L['w']['01']:.4g}"), (r"$\omega_{12}$", f"{L['w']['12']:.4g}"),
 (r"$\omega_{02}$", f"{L['w']['20']:.3g}"), (r"$\delta_{21}$", f"{L['delta_21']:.4g}"),
]
T = [r"\begin{table}[t]\centering\small",
     r"\caption{Base parameter set.  Rates are in an arbitrary time unit fixed by",
     r"$k_{\rm on}c$; energies are in units of $\kB T$.  The lower block is the",
     r"Pigolotti--Sartori landscape of Eq.~(2) recovered from the rate table by",
     r"\texttt{landscape()}, which reproduces every rate to machine precision.}",
     r"\label{tab:params}",
     r"\begin{tabular}{llll}\toprule",
     r"symbol & value & unit & how it was chosen \\ \midrule"]
for a, b, c, d in rows:
    T.append(f"{a} & {b} & {c} & {d} \\\\")
T.append(r"\midrule \multicolumn{4}{l}{\emph{implied landscape}} \\")
for i in range(0, len(land), 2):
    (a, b), (c, d) = land[i], land[i+1]
    T.append(f"{a} & {b} & \\multicolumn{{2}}{{l}}{{ {c} $=$ {d} }} \\\\")
T += [r"\bottomrule\end{tabular}\end{table}"]
open(os.path.join(REP, "partable.tex"), "w").write("\n".join(T) + "\n")
print("wrote rules_R.ka, model_base.ka, partable.tex")
