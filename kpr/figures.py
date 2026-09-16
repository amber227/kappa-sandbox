"""Build all figures for the kinetic-proofreading report."""
import os, sys, json, glob, subprocess
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
RES = os.environ.get("KPR_RESULTS", os.path.join(ROOT, "results"))
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)

from model import Params, landscape
from theory import self_consistent_eta, stack_gillespie

GIT = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                     capture_output=True, text=True).stdout.strip()

# --- house style -------------------------------------------------------------
plt.rcParams.update({
    "figure.dpi": 160, "savefig.dpi": 300, "font.size": 9,
    "axes.labelsize": 9, "axes.titlesize": 9.5, "legend.fontsize": 8,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
    "legend.frameon": False, "lines.linewidth": 1.4,
    "font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans",
})
C_R, C_W = "#2E7D5B", "#C1443B"          # right / wrong, matching the sketch
C_B, C_C, C_C0 = "#6E7B8B", "#1F4E79", "#D98C1F"   # protocol B / C driven / C undriven
LN10 = np.log(10.0)
ETA_EQ = 1.0 / (1.0 + np.exp(LN10))      # equilibrium bound, 1/(1+e^delta)
FLOOR = ETA_EQ ** 2                      # zero-speed (Hopfield) floor


SSA_CACHE = os.path.join(RES, "_ssa_cache.json")


def ssa(p, n_events, key):
    """stack_gillespie with an on-disk cache (it is slow: pure Python)."""
    try:
        C = json.load(open(SSA_CACHE))
    except Exception:
        C = {}
    if key not in C:
        C[key] = {k: float(v) for k, v in
                  stack_gillespie(p, n_events, seed=abs(hash(key)) % 10**6).items()}
        os.makedirs(RES, exist_ok=True)
        json.dump(C, open(SSA_CACHE, "w"), indent=0)
    return C[key]


def load(pattern):
    out = {}
    for f in sorted(glob.glob(os.path.join(RES, pattern))):
        with open(f) as fh:
            r = json.load(fh)
        if "name" in r:
            out[r["name"]] = r
    return out


def save(fig, stem):
    path = os.path.join(FIG, f"{stem}_{GIT}.pdf")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", os.path.basename(path))
    return path


def _eb(r):
    """Asymmetric 1-sigma error bar on eta."""
    return np.array([[r["eta"] - r["eta_lo"]], [r["eta_hi"] - r["eta"]]])


# =============================================================================
def fig_landscape(tau=1e-5):
    """Fig 1b: the free-energy landscape the model actually implements.

    Barrier levels are B_ij = -T log(w_ij * tau); the time unit tau only shifts
    every barrier by the same constant and is chosen so barriers sit above wells.
    """
    p = Params()
    L = landscape(p)
    B = {k: -np.log(v * tau) for k, v in L["w"].items()}
    d21 = L["delta_21"]
    wells = {0: {"R": 0.0, "W": 0.0}, 1: L["dE"][1], 2: L["dE"][2]}
    xw = {0: 0.0, 1: 3.0, 2: 6.0}

    def arc(x0, y0, xb_, yb_, x1, y1, n=400):
        xa = np.linspace(x0, xb_, n // 2)
        ya = y0 + (yb_ - y0) * (1 - np.cos(np.pi * (xa - x0) / (xb_ - x0))) / 2
        xc = np.linspace(xb_, x1, n // 2)
        yc = yb_ + (y1 - yb_) * (1 - np.cos(np.pi * (xc - xb_) / (x1 - xb_))) / 2
        return np.r_[xa, xc], np.r_[ya, yc]

    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    for nu, col, lab in [("R", C_R, "right (R)"), ("W", C_W, "wrong (W)")]:
        dd = d21 if nu == "R" else 0.0        # delta lowers the right-monomer barrier
        x1, y1 = arc(xw[0], 0.0, 1.5, B["01"], xw[1], wells[1][nu])
        x2, y2 = arc(xw[1], wells[1][nu], 4.5, B["12"] - dd, xw[2], wells[2][nu])
        ax.plot(np.r_[x1, x2], np.r_[y1, y2], color=col, lw=2.0, label=lab, zorder=3)
        xd, yd = arc(xw[0], 0.0, 2.55, B["20"], xw[2], wells[2][nu])
        ax.plot(xd, yd, color=col, lw=1.2, ls=(0, (4, 2)), alpha=0.6, zorder=2)

    def gap(x, ylo, yhi, lab, dx=0.16, ha="left", fs=8.5):
        ax.annotate("", xy=(x, ylo), xytext=(x, yhi),
                    arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color="0.25",
                                    mutation_scale=7, shrinkA=0, shrinkB=0))
        ax.text(x + dx, (ylo + yhi) / 2, lab, va="center", ha=ha, fontsize=fs)

    gap(4.5, B["12"] - d21, B["12"], r"$\delta_{21}=\Delta$", dx=-0.16, ha="right")
    gap(3.0, wells[1]["R"], wells[1]["W"], r"$\Delta_1$")
    gap(6.0, wells[2]["R"], wells[2]["W"], r"$\Delta_2$", dx=-0.16, ha="right")
    ax.annotate("", xy=(2.55, B["20"] - L["mu_02"]), xytext=(2.55, B["20"]),
                arrowprops=dict(arrowstyle="-|>", lw=1.3, color="#B8860B",
                                mutation_scale=9))
    ax.text(2.70, B["20"] - L["mu_02"] / 2, r"$\mu_{02}$" + "\n(fuel)",
            color="#B8860B", fontsize=8.5, va="center", ha="left")
    ax.plot([2.25, 2.85], [B["20"] - L["mu_02"]] * 2, color="#B8860B", lw=1.0, ls=":")
    ax.axhline(0, color="0.85", lw=0.6, ls=":")

    ax.set_xticks([xw[0], xw[1], xw[2]])
    ax.set_xticklabels(["0\nempty site", "1\npaired", "2\ncommitted"])
    ax.set_ylabel(r"free energy  $[k_\mathrm{B}T]$")
    ax.set_ylim(min(wells[2]["R"], 0) - 4, B["20"] + 3)
    ax.set_xlim(-0.35, 6.5)
    ax.grid(False)
    h = [Line2D([], [], color=C_R, lw=2), Line2D([], [], color=C_W, lw=2),
         Line2D([], [], color="0.35", lw=1.4, ls=(0, (4, 2)))]
    ax.legend(h, ["right (R)", "wrong (W)", r"discard path $0\leftrightarrow2$"],
              loc="lower left", ncol=1, handlelength=1.8,
              borderpad=0.2, labelspacing=0.35)
    return save(fig, "fig1_landscape")


# =============================================================================
def fig_main():
    """Fig 2: product accumulation and running error for the three protocols."""
    SHORT = {"main_B": "B\nno discard", "main_C_nodrive": "C\n$\\mu_{02}=0$",
             "main_C_driven": "C\n$\\mu_{02}=20$"}
    runs = [("main_B", "B: no discard", C_B),
            ("main_C_nodrive", r"C: discard, $\mu_{02}=0$", C_C0),
            ("main_C_driven", r"C: discard, $\mu_{02}=20\,k_\mathrm{B}T$", C_C)]
    fig, axs = plt.subplots(1, 3, figsize=(9.6, 2.9))

    # (a) composition of the growing copies
    ax = axs[0]
    ends, tops = [], []
    for name, lab, col in runs:
        f = os.path.join(RES, name + "_traj.csv")
        if not os.path.exists(f):
            continue
        import pandas as pd
        d = pd.read_csv(f)
        ax.plot(d.prod_R + d.prod_W, d.prod_W, color=col, label=lab)
        ends.append(float((d.prod_R + d.prod_W).iloc[-1]))
        if name != "main_C_nodrive":
            tops.append(float(d.prod_W.iloc[-1]))
    lim = min(ends) if ends else ax.get_xlim()[1]
    ax.set_xlim(0, lim)
    if tops:
        ax.set_ylim(0, 1.45 * max(tops))
        r0 = load("main_C_nodrive.json").get("main_C_nodrive")
        if r0:
            ax.annotate(rf"off scale, slope $={r0['eta']:.2f}$",
                        xy=(0.295 * lim, ax.get_ylim()[1] * 0.965),
                        xytext=(0.36 * lim, ax.get_ylim()[1] * 0.60),
                        fontsize=7.5, color=C_C0,
                        arrowprops=dict(arrowstyle="->", color=C_C0, lw=0.8))
    for frac, ls in [(ETA_EQ, (0, (4, 2))), (FLOOR, (0, (1, 1.6)))]:
        ax.plot([0, lim], [0, frac * lim], color="0.35", ls=ls, lw=1.0)
    ax.text(lim * 0.985, ETA_EQ * lim * 1.03, r"$\eta_{\rm eq}$", fontsize=8,
            color="0.35", ha="right", va="bottom")
    ax.text(lim * 0.985, FLOOR * lim * 1.10, r"$\eta_{\rm eq}^2$", fontsize=8,
            color="0.35", ha="right", va="bottom")
    ax.set_xlabel("residues incorporated"); ax.set_ylabel("mismatches incorporated")
    ax.set_title("(a) copy composition", loc="left")
    ax.legend(loc="upper left", fontsize=7.5, borderpad=0.2, labelspacing=0.3)

    # (b) running error fraction
    ax = axs[1]
    for name, lab, col in runs:
        f = os.path.join(RES, name + "_traj.csv")
        if not os.path.exists(f):
            continue
        import pandas as pd
        d = pd.read_csv(f)
        n = d.prod_R + d.prod_W
        m = n > 200
        ax.plot(n[m], (d.prod_W / n)[m], color=col, label=lab)
        r = load(name + ".json").get(name)
        if r:
            ax.axhline(r["eta"], color=col, lw=0.7, ls=":")
    ax.axhline(ETA_EQ, color="0.35", ls=(0, (4, 2)), lw=1.0)
    ax.axhline(FLOOR, color="0.35", ls=(0, (1, 1.6)), lw=1.0)
    ax.text(0.985, ETA_EQ * 1.13, r"$\eta_{\rm eq}$", transform=ax.get_yaxis_transform(),
            ha="right", fontsize=8.5, color="0.35")
    ax.text(0.985, FLOOR * 1.16, r"$\eta_{\rm eq}^2$",
            transform=ax.get_yaxis_transform(), ha="right", fontsize=8.5, color="0.35")
    ax.set_yscale("log"); ax.set_xscale("log")
    ax.set_xlabel("residues incorporated"); ax.set_ylabel(r"running error fraction $\eta$")
    ax.set_title("(b) convergence of the error", loc="left")

    # (c) final error, with theory
    ax = axs[2]
    R = load("main_*.json")
    xs, labs = [], []
    for i, (name, lab, col) in enumerate(runs):
        r = R.get(name)
        if not r:
            continue
        p = Params(**r["params"])
        th = self_consistent_eta(p)
        ax.errorbar(i, r["eta"], yerr=_eb(r), fmt="o", color=col, ms=6, capsize=3)
        ax.plot(i, th["eta"], marker="_", ms=16, color="k", mew=1.4, zorder=5)
        xs.append(i); labs.append(SHORT[name])
    ax.axhline(ETA_EQ, color="0.35", ls=(0, (4, 2)), lw=1.0)
    ax.axhline(FLOOR, color="0.35", ls=(0, (1, 1.6)), lw=1.0)
    ax.set_xticks(xs); ax.set_xticklabels(labs, fontsize=8)
    ax.set_yscale("log"); ax.set_ylabel(r"$\eta$")
    ax.set_xlim(-0.6, len(xs) - 0.4)
    ax.set_title("(c) steady-state error", loc="left")
    ax.legend(handles=[Line2D([], [], marker="_", ls="", color="k", mew=1.4, ms=12,
                              label="self-consistent theory")], loc="lower left")
    fig.tight_layout()
    return save(fig, "fig2_main")


# =============================================================================
def fig_drive():
    """Fig 3: error and speed versus the chemical drive on the discard step."""
    R = load("drive_*.json")
    A = np.array([r["params"]["drive"] for r in R.values()])
    eta = np.array([r["eta"] for r in R.values()])
    lo = np.array([r["eta_lo"] for r in R.values()])
    hi = np.array([r["eta_hi"] for r in R.values()])
    v = np.array([r["velocity"] for r in R.values()])
    o = np.argsort(A); A, eta, lo, hi, v = A[o], eta[o], lo[o], hi[o], v[o]

    Ath = np.linspace(0, 20, 120)
    th = [self_consistent_eta(Params(drive=a)) for a in Ath]
    eth = np.array([t["eta"] for t in th]); vth = np.array([t["velocity"] for t in th])
    b = self_consistent_eta(Params(proofread=False))
    B = load("main_B.json").get("main_B")

    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9))
    ax = axs[0]
    ax.plot(Ath, eth, color=C_C, lw=1.4, label="theory")
    ax.errorbar(A, eta, yerr=[eta - lo, hi - eta], fmt="o", ms=4.5, color=C_C,
                mfc="w", capsize=2.5, lw=1.0, label="Kappa simulation")
    ax.axhline(b["eta"], color=C_B, ls="--", lw=1.1)
    ax.text(19.5, b["eta"] * 1.12, "protocol B (no discard)", ha="right",
            fontsize=7.5, color=C_B)
    if B:
        ax.errorbar([19.5], [B["eta"]], yerr=_eb(B), fmt="s", ms=4, color=C_B, capsize=2.5)
    ax.axhline(FLOOR, color="0.35", ls=(0, (1, 1.6)), lw=1.0)
    ax.text(19.6, FLOOR * 1.16, r"zero-speed floor $\eta_{\rm eq}^2$",
            fontsize=7.5, color="0.35", ha="right")
    ax.axhline(ETA_EQ, color="0.35", ls=(0, (4, 2)), lw=1.0)
    ax.text(0.3, ETA_EQ * 1.14, r"$\eta_{\rm eq}$", fontsize=8, color="0.35")
    ax.set_yscale("log")
    ax.set_xlabel(r"drive on the discard step $\mu_{02}$  $[k_\mathrm{B}T]$")
    ax.set_ylabel(r"error fraction $\eta$")
    ax.set_title("(a) accuracy needs dissipation", loc="left")
    ax.legend(loc="center left", bbox_to_anchor=(0.02, 0.32))

    ax = axs[1]
    ax.plot(Ath, vth, color=C_C, lw=1.4)
    ax.plot(A, v, "o", ms=4.5, color=C_C, mfc="w")
    ax.axhline(b["velocity"], color=C_B, ls="--", lw=1.1)
    ax.text(19.5, b["velocity"] * 1.15, "protocol B", ha="right", fontsize=7.5, color=C_B)
    ax.set_yscale("log")
    ax.set_xlabel(r"$\mu_{02}$  $[k_\mathrm{B}T]$")
    ax.set_ylabel("growth velocity  [residues / chain / time]")
    ax.set_title("(b) and costs speed", loc="left")
    fig.tight_layout()
    return save(fig, "fig3_drive")


# =============================================================================
def fig_square():
    """Fig 4: eta versus the discrimination energy -- the square law."""
    RB = load("delta_B_*.json"); RC = load("delta_C_*.json")
    def arr(R):
        d = np.array([r["params"]["delta"] for r in R.values()])
        e = np.array([r["eta"] for r in R.values()])
        l = np.array([r["eta_lo"] for r in R.values()])
        h = np.array([r["eta_hi"] for r in R.values()])
        o = np.argsort(d); return d[o], e[o], l[o], h[o]
    dB, eB, lB, hB = arr(RB); dC, eC, lC, hC = arr(RC)

    dt = np.linspace(0.6, 3.4, 90)
    eq = np.exp(-dt) / (1 + np.exp(-dt))          # equilibrium bound, Eq. (1)
    tB = np.array([self_consistent_eta(Params(delta=x, proofread=False))["eta"] for x in dt])
    tC = np.array([self_consistent_eta(Params(delta=x))["eta"] for x in dt])

    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0))
    ax = axs[0]
    ax.plot(dt, eq, color="0.35", ls=(0, (4, 2)), lw=1.0, label=r"$\eta_{\rm eq}$")
    ax.plot(dt, eq ** 2, color="0.35", ls=(0, (1, 1.6)), lw=1.0,
            label=r"$\eta_{\rm eq}^2$  (Hopfield floor)")
    ax.plot(dt, tB, color=C_B, lw=1.4); ax.plot(dt, tC, color=C_C, lw=1.4)
    ax.errorbar(dB, eB, yerr=[eB - lB, hB - eB], fmt="s", ms=4.5, color=C_B,
                mfc="w", capsize=2.5, lw=1.0, label="B: no discard (Kappa)")
    ax.errorbar(dC, eC, yerr=[eC - lC, hC - eC], fmt="o", ms=4.5, color=C_C,
                mfc="w", capsize=2.5, lw=1.0, label="C: proofreading (Kappa)")
    ax.set_yscale("log")
    ax.set_xlabel(r"discrimination energy $\delta$  $[k_\mathrm{B}T]$")
    ax.set_ylabel(r"error fraction $\eta$")
    ax.set_title("(a) error versus discrimination", loc="left")
    ax.legend(loc="lower left")
    # fitted slopes
    txt = []
    for d, e, lab, col in [(dB, eB, "B", C_B), (dC, eC, "C", C_C)]:
        if len(d) >= 3 and np.all(e > 0):
            txt.append((lab, np.polyfit(d, np.log(e), 1)[0], col))
    for i, (lab, sl, col) in enumerate(txt):
        ax.text(0.97, 0.95 - 0.085 * i, rf"{lab}: $d\ln\eta/d\delta={sl:.2f}$",
                transform=ax.transAxes, ha="right", color=col, fontsize=8.5)
    if len(txt) == 2:
        ax.text(0.97, 0.95 - 0.085 * 2, rf"ratio $={txt[1][1]/txt[0][1]:.2f}$",
                transform=ax.transAxes, ha="right", color="0.25", fontsize=8.5)

    ax = axs[1]
    ax.plot(tB, tC, color=C_C, lw=1.4, label="theory")
    if len(dB) == len(dC) and len(dB):
        ax.errorbar(eB, eC, xerr=[eB - lB, hB - eB], yerr=[eC - lC, hC - eC],
                    fmt="o", ms=4.5, color=C_C, mfc="w", capsize=2.5, lw=1.0,
                    label="Kappa")
    x = np.logspace(np.log10(max(tB.min(), 1e-3)), np.log10(tB.max()), 50)
    ax.plot(x, x**2, color="0.35", ls=(0, (1, 1.6)), lw=1.0,
            label=r"$\eta_C=\eta_B^2$  (zero-speed floor)")
    ax.plot(x, 2 * x**2, color="0.35", ls=(0, (4, 2)), lw=1.0, label=r"$\eta_C=2\eta_B^2$")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"$\eta$ without proofreading (protocol B)")
    ax.set_ylabel(r"$\eta$ with proofreading (protocol C)")
    ax.set_title("(b) the error is squared", loc="left")
    ax.legend(loc="upper left")
    fig.tight_layout()
    return save(fig, "fig4_squarelaw")


# =============================================================================
def fig_tradeoff():
    """Fig 5: speed / accuracy / cost as the excision rate is varied."""
    R = load("pfr_*.json")
    a = np.array([r["params"]["pf_ratio"] for r in R.values()])
    eta = np.array([r["eta"] for r in R.values()])
    lo = np.array([r["eta_lo"] for r in R.values()])
    hi = np.array([r["eta_hi"] for r in R.values()])
    v = np.array([r["velocity"] for r in R.values()])
    cost = np.array([r["cost"] for r in R.values()])
    o = np.argsort(a); a, eta, lo, hi, v, cost = a[o], eta[o], lo[o], hi[o], v[o], cost[o]
    m = load("main_C_driven.json").get("main_C_driven")
    B = load("main_B.json").get("main_B")
    if m:
        a = np.r_[a, m["params"]["pf_ratio"]]; eta = np.r_[eta, m["eta"]]
        lo = np.r_[lo, m["eta_lo"]]; hi = np.r_[hi, m["eta_hi"]]
        v = np.r_[v, m["velocity"]]; cost = np.r_[cost, m["cost"]]
        o = np.argsort(a); a, eta, lo, hi, v, cost = a[o], eta[o], lo[o], hi[o], v[o], cost[o]

    at = np.linspace(0.0, 0.905, 130)
    th = [self_consistent_eta(Params(pf_ratio=x)) for x in at]
    et = np.array([t["eta"] for t in th]); vt = np.array([t["velocity"] for t in th])
    ok = np.isfinite(et); at, et, vt = at[ok], et[ok], vt[ok]
    b = self_consistent_eta(Params(proofread=False))
    floor = b["eta"] ** 2          # square of the protocol-B error: the zero-speed floor
    a_ssa = [0.85, 0.88, 0.90]
    ssa_pts = [ssa(Params(pf_ratio=x), 900_000, f"pfr{x}") for x in a_ssa]
    v_ssa = [self_consistent_eta(Params(pf_ratio=x))["velocity"] for x in a_ssa]

    fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.0))
    ax = axs[0]
    ax.plot(vt, et, color="0.5", lw=1.2, zorder=1, label="theory")
    sc = ax.scatter(v, eta, c=cost, cmap="viridis", s=42, zorder=3,
                    edgecolor="k", linewidth=0.4)
    ax.errorbar(v, eta, yerr=[eta - lo, hi - eta], fmt="none", ecolor="0.4",
                capsize=2.5, lw=0.9, zorder=2)
    if B:
        ax.errorbar([B["velocity"]], [B["eta"]], yerr=_eb(B), fmt="s", ms=5,
                    color=C_B, capsize=2.5, zorder=4, label="protocol B")
    ax.plot([b["velocity"]], [b["eta"]], "s", ms=5, mfc="none", color=C_B, zorder=4)
    for x, y, lab in zip(v, eta, a):
        ax.annotate(f"{lab:.1f}", (x, y), textcoords="offset points",
                    xytext=(5, 4), fontsize=7, color="0.3")
    _se = np.array([np.sqrt(max(t["eta"], 1e-9) * (1 - t["eta"]) / max(t["n_incorp"], 1))
                    for t in ssa_pts])
    ax.errorbar(v_ssa, [t["eta"] for t in ssa_pts], yerr=_se, fmt="^", ms=5.5,
                color="#8E5BA6", mfc="none", capsize=2.5, lw=0.9, zorder=4,
                label="stack SSA (near stall)")
    ax.axhline(floor, color="0.35", ls=(0, (1, 1.6)), lw=1.0)
    ax.text(0.97, floor * 0.80, r"zero-speed floor $\eta_B^2$", fontsize=7.5,
            color="0.35", transform=ax.get_yaxis_transform(), ha="right", va="top")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("growth velocity  [residues / chain / time]")
    ax.set_ylabel(r"error fraction $\eta$")
    ax.set_title(r"(a) speed-accuracy, labelled by $k^R_{02}/v_{\rm com}$", loc="left")
    cb = fig.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label("excisions per residue kept", fontsize=8)
    ax.legend(loc="upper right")

    ax = axs[1]
    ax.plot(at, et, color=C_C, lw=1.4, label="theory")
    ax.errorbar(a, eta, yerr=[eta - lo, hi - eta], fmt="o", ms=4.5, color=C_C,
                mfc="w", capsize=2.5, lw=1.0, label="Kappa")
    ax.axhline(b["eta"], color=C_B, ls="--", lw=1.1)
    ax.text(0.88, b["eta"] * 1.12, "protocol B", ha="right", fontsize=7.5, color=C_B)
    ax.errorbar(a_ssa, [t["eta"] for t in ssa_pts], yerr=_se, fmt="^", ms=5.5,
                color="#8E5BA6", mfc="none", capsize=2.5, lw=0.9, label="stack SSA")
    ax.axhline(floor, color="0.35", ls=(0, (1, 1.6)), lw=1.0)
    ax.text(0.40, floor * 1.16, r"$\eta_B^2$", fontsize=8.5, color="0.35",
            transform=ax.get_yaxis_transform(), ha="center")
    ax2 = ax.twinx()
    ax2.plot(at, vt, color="0.55", lw=1.1, ls="-.")
    ax2.plot(a, v, ".", color="0.55", ms=6)
    ax2.set_ylabel("velocity", color="0.45", fontsize=8)
    ax2.tick_params(axis="y", colors="0.45"); ax2.grid(False)
    ax.set_yscale("log")
    ax.set_xlabel(r"excision strength  $k^R_{02}/v_{\rm com}$")
    ax.set_ylabel(r"$\eta$")
    ax.set_title("(b) the floor is reached only at stall", loc="left")
    ax.legend(loc="lower left", bbox_to_anchor=(-0.01, -0.02), fontsize=7.5,
              borderpad=0.2, labelspacing=0.3)
    fig.tight_layout()
    return save(fig, "fig5_tradeoff")


# =============================================================================
def fig_validation(n_ssa=700_000):
    """Fig 6: Kappa vs an independent SSA vs the self-consistent theory, and
    the approach to the equilibrium error at stall."""
    R = {}
    for pat in ("main_*.json", "delta_*.json", "drive_*.json", "pfr_*.json"):
        R.update(load(pat))
    R = {k: v for k, v in R.items() if not k.endswith("nodrive")}
    xs, ys, yl, yh, ss, sn = [], [], [], [], [], []
    for name, r in sorted(R.items()):
        p = Params(**r["params"])
        t = self_consistent_eta(p)
        if not np.isfinite(t["eta"]):
            continue
        xs.append(t["eta"]); ys.append(r["eta"]); yl.append(r["eta_lo"]); yh.append(r["eta_hi"])
        g = ssa(p, n_ssa, "val_" + name)
        ss.append(g["eta"]); sn.append(g["n_incorp"])
    xs, ys, yl, yh, ss, sn = map(np.array, (xs, ys, yl, yh, ss, sn))

    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0))
    ax = axs[0]
    lim = [min(xs.min(), ys.min()) * 0.6, max(xs.max(), ys.max()) * 1.6]
    ax.plot(lim, lim, color="0.6", lw=1.0, ls="--")
    ax.errorbar(xs, ys, yerr=[ys - yl, yh - ys], fmt="o", ms=5, color=C_C, mfc="w",
                capsize=2.5, lw=1.0, label="PyKappa")
    se = np.sqrt(np.clip(ss, 1e-9, 1) * (1 - ss) / np.maximum(sn, 1))
    ax.errorbar(xs, ss, yerr=se, fmt="^", ms=5, color="#8E5BA6", mfc="none",
                capsize=2, lw=0.8, label="stack SSA (no Kappa)")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel(r"$\eta$, self-consistent theory")
    ax.set_ylabel(r"$\eta$, simulation")
    ax.set_title("(a) three independent implementations", loc="left")
    ax.legend(loc="upper left")

    # (b) stall check for protocol B
    ax = axs[1]
    kun = np.linspace(0.05, 11.9, 120)
    out = [(Params(k_un_R=k, proofread=False), self_consistent_eta(Params(k_un_R=k, proofread=False)))
           for k in kun]
    vv = np.array([o[1]["velocity"] for o in out])
    ee = np.array([o[1]["eta"] for o in out])
    m = np.isfinite(vv) & (vv > 0)
    ax.plot(vv[m], ee[m], color=C_B, lw=1.5, label="protocol B, theory")
    kk = [0.05, 4.0, 7.0, 9.0, 10.5, 11.5]
    sg = [ssa(Params(k_un_R=k, proofread=False), 2_000_000, f"stall2_{k}") for k in kk]
    tv = [self_consistent_eta(Params(k_un_R=k, proofread=False))["velocity"] for k in kk]
    se = np.array([np.sqrt(max(g["eta"], 1e-9) * (1 - g["eta"]) / max(g["n_incorp"], 1))
                   for g in sg])
    ax.errorbar(tv, [g["eta"] for g in sg], yerr=se, fmt="^", ms=5, color="#8E5BA6",
                mfc="none", capsize=2, lw=0.8, label="stack SSA")
    Bk = load("main_B.json").get("main_B")
    if Bk:
        ax.errorbar([Bk["velocity"]], [Bk["eta"]], yerr=_eb(Bk), fmt="o", ms=5,
                    color=C_C, mfc="w", capsize=2.5, label="PyKappa (base point)")
    ax.axhline(ETA_EQ, color="0.35", ls=(0, (4, 2)), lw=1.0)
    ax.text(0.02, ETA_EQ * 1.06, r"$\eta_{\rm eq}=1/(1+e^{\delta})$",
            transform=ax.get_yaxis_transform(), fontsize=8, color="0.35")
    ax.set_xscale("log")
    ax.set_xlabel("growth velocity  [residues / chain / time]")
    ax.set_ylabel(r"error fraction $\eta$")
    ax.set_title("(b) stall limit recovers the equilibrium error", loc="left")
    ax.legend(loc="upper left")
    fig.tight_layout()
    return save(fig, "fig6_validation")


if __name__ == "__main__":
    which = sys.argv[1:] or ["landscape", "main", "drive", "square", "tradeoff", "validation"]
    for w in which:
        globals()["fig_" + w]()
