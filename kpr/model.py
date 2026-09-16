"""
Minimal Kappa model of kinetic proofreading in template-directed polymerisation,
after Pigolotti & Sartori, J. Stat. Phys. 162:1167 (2016).

One agent type, M, does all the work:

    M(p, n, c{n y}, k{R W S})

    p, n : backbone/template sites of a residue.  A bond p-n means "these two
           residues occupy adjacent template positions".
    c    : {n} the residue merely sits in the active site (paired, not yet
           covalently joined);  {y} the residue has been committed to the copy.
    k    : {R} cognate (right) monomer, {W} non-cognate (wrong) monomer,
           {S} the primer/seed residue that nucleates a copy.

The 3'-terminal residue of a growing copy ("the tip") is the unique
M(c{y}, n[.]) in its component.  Free monomers are M(p[.], n[.], c{n}).

The three reactions of the sketch:

    add       0 -> 1   tip recruits a free monomer into the active site
    commit    1 -> 2   the monomer is covalently incorporated  (c{n} -> c{y})
    proofread 2 -> 0   the terminal committed residue is excised back to the pool

with the reverses reject (1->0), uncommit (2->1) and ligate (0->2).
"""

from math import exp, log
from dataclasses import dataclass, field, asdict


@dataclass
class Params:
    # --- discrimination -----------------------------------------------------
    delta: float = log(10.0)   # discrimination free energy  (k_B T).  f = e^delta
    # --- drive --------------------------------------------------------------
    drive: float = 20.0        # A, chemical drive of the proofreading cycle (k_B T)
    proofread: bool = True     # if False the 2<->0 pathway is deleted entirely
    # --- kinetics -----------------------------------------------------------
    c: int = 1000              # chemostatted copy number of EACH free monomer type
    assoc: float = 100.0       # pseudo-first-order association rate  k_on * c
    k_off_R: float = 900.0     # rejection rate of a cognate monomer from state 1
    k_cat: float = 100.0       # commitment (covalent incorporation) rate
    k_un_R: float = 0.05       # uncommitment rate of a cognate residue
    pf_ratio: float = 0.5      # k_pf_R / v_commit   (dimensionless excision strength)
    # --- system size --------------------------------------------------------
    n_chains: int = 200        # number of independently growing copies
    k_chemo: float = 500.0     # gain of the monomer chemostat

    def rates(self) -> dict:
        f = exp(self.delta)
        k_on = self.assoc / self.c

        k_off_R = self.k_off_R
        k_off_W = f * k_off_R                      # delta_01 = 0: all of Delta_1 in the off-rate
        k_cat_R = k_cat_W = self.k_cat             # delta_12 = Delta_1: commitment does not discriminate
        k_un_R = self.k_un_R
        k_un_W = k_un_R * exp(self.delta - self.delta)  # = k_un_R  (Delta_2 = Delta_1)

        # rate at which a tip in state 0 reaches state 2 through 0->1->2
        v = (self.assoc * self.k_cat / (k_off_R + self.k_cat)
             + self.assoc * self.k_cat / (k_off_W + self.k_cat))

        k_pf_R = self.pf_ratio * v
        k_pf_W = f * k_pf_R                        # delta_20 = 0: all of Delta_2 in the excision rate

        # free energy of state 2 relative to state 0, at the working concentration
        eps2_R = log((self.assoc / k_off_R) * (self.k_cat / k_un_R))
        # detailed balance around 0->1->2->0 with cycle affinity A
        k_lig_R = k_pf_R * exp(eps2_R - self.drive) / self.c   # per free monomer
        eps2_W = eps2_R - self.delta
        k_lig_W = k_pf_W * exp(eps2_W - self.drive) / self.c
        assert abs(k_lig_R - k_lig_W) < 1e-12 * max(k_lig_R, 1e-30), (k_lig_R, k_lig_W)

        return dict(
            f=f, k_on=k_on, v_commit=v,
            k_off_R=k_off_R, k_off_W=k_off_W,
            k_cat_R=k_cat_R, k_cat_W=k_cat_W,
            k_un_R=k_un_R, k_un_W=k_un_W,
            k_pf_R=k_pf_R, k_pf_W=k_pf_W,
            k_lig_R=k_lig_R, k_lig_W=k_lig_W,
            eps2_R=eps2_R, eps2_W=eps2_W,
        )


def kappa(p: Params, names: list | None = None) -> str:
    """Render the model as Kappa source.  If `names` is a list it is filled,
    in order, with a readable name for every rule emitted (PyKappa cannot
    parse quoted rule labels, so the names are carried alongside)."""
    r = p.rates()
    L = []
    A = L.append
    nm = names.append if names is not None else (lambda x: None)

    A("// ---- chemostat set-points (a %var is needed: PyKappa cannot parse |pattern|")
    A("//      directly inside a rule rate, but it can inside a %var) ----")
    A("%var: 'nfree_R' |M(p[.], n[.], c{n}, k{R})|")
    A("%var: 'nfree_W' |M(p[.], n[.], c{n}, k{W})|")
    A("")
    A("// ---- initial state ----")
    A(f"%init: {p.n_chains} M(p[.], n[.], c{{y}}, k{{S}})")
    A(f"%init: {p.c} M(p[.], n[.], c{{n}}, k{{R}})")
    A(f"%init: {p.c} M(p[.], n[.], c{{n}}, k{{W}})")
    A("")

    for nu in ("R", "W"):
        A(f"// ---- {nu} ----")
        # add (0 -> 1): the tip recruits a free monomer into the active site
        A(f"M(c{{y}}, n[.]), M(p[.], n[.], c{{n}}, k{{{nu}}}) -> "
          f"M(c{{y}}, n[1]), M(p[1], n[.], c{{n}}, k{{{nu}}}) @ {r['k_on']:.10g}"); nm(f"add_{nu}")
        # reject (1 -> 0)
        A(f"M(c{{y}}, n[1]), M(p[1], n[.], c{{n}}, k{{{nu}}}) -> "
          f"M(c{{y}}, n[.]), M(p[.], n[.], c{{n}}, k{{{nu}}}) @ {r['k_off_'+nu]:.10g}"); nm(f"reject_{nu}")
        # commit (1 -> 2)
        A(f"M(c{{y}}, n[1]), M(p[1], n[.], c{{n}}, k{{{nu}}}) -> "
          f"M(c{{y}}, n[1]), M(p[1], n[.], c{{y}}, k{{{nu}}}) @ {r['k_cat_'+nu]:.10g}"); nm(f"commit_{nu}")
        # uncommit (2 -> 1)
        A(f"M(c{{y}}, n[1]), M(p[1], n[.], c{{y}}, k{{{nu}}}) -> "
          f"M(c{{y}}, n[1]), M(p[1], n[.], c{{n}}, k{{{nu}}}) @ {r['k_un_'+nu]:.10g}"); nm(f"uncommit_{nu}")
        if p.proofread:
            # proofread / excise (2 -> 0)
            A(f"M(c{{y}}, n[1]), M(p[1], n[.], c{{y}}, k{{{nu}}}) -> "
              f"M(c{{y}}, n[.]), M(p[.], n[.], c{{n}}, k{{{nu}}}) @ {r['k_pf_'+nu]:.10g}"); nm(f"proofread_{nu}")
            # ligate (0 -> 2), the thermodynamic reverse of excision
            if r['k_lig_'+nu] > 0:
                A(f"M(c{{y}}, n[.]), M(p[.], n[.], c{{n}}, k{{{nu}}}) -> "
                  f"M(c{{y}}, n[1]), M(p[1], n[.], c{{y}}, k{{{nu}}}) @ {r['k_lig_'+nu]:.10g}"); nm(f"ligate_{nu}")
        # chemostat: replenish the free pool towards its set point
        A(f". -> M(p[.], n[.], c{{n}}, k{{{nu}}}) @ "
          f"[max] (0) ({p.k_chemo:.10g} * ({p.c} - 'nfree_{nu}'))"); nm(f"chemostat_{nu}")
        A("")

    A("// ---- observables ----")
    A("%obs: 'free_R' |M(p[.], n[.], c{n}, k{R})|")
    A("%obs: 'free_W' |M(p[.], n[.], c{n}, k{W})|")
    A("%obs: 'prod_R' |M(p[_], c{y}, k{R})|")
    A("%obs: 'prod_W' |M(p[_], c{y}, k{W})|")
    return "\n".join(L)


if __name__ == "__main__":
    p = Params()
    import json
    print(json.dumps({k: round(v, 6) for k, v in p.rates().items()}, indent=1))
    print(kappa(p))


def landscape(p: Params) -> dict:
    """Back out the Pigolotti-Sartori energy landscape (Eq. 1) implied by the rates.

    Their parameterisation is  k_{j->i} = w_ij exp[(dE_j + mu_ij + d_ij[right])/T],
    so the well depths dE_i and the barrier prefactors w_ij are fixed by the rates.
    Barrier *levels* are B_ij = -T log w_ij, defined only up to the choice of time
    unit; `tau` rescales every rate by 1/tau and shifts all barriers by +log tau.
    """
    from math import log
    r = p.rates()
    dE0 = 0.0
    dE1 = {nu: log(r["k_off_" + nu] / p.assoc) for nu in "RW"}
    dE2 = {nu: dE1[nu] - log(r["k_cat_" + nu] / r["k_un_" + nu]) for nu in "RW"}
    # prefactors
    from math import exp
    w01 = p.assoc                                    # k_{0->1} = w01 * exp(dE0)
    d21 = dE1["W"] - dE1["R"]                        # delta_21, forced = Delta_1
    w12 = r["k_cat_R"] / exp(dE1["R"] + d21)
    w20 = r["k_pf_R"] / exp(dE2["R"] + p.drive) if r["k_pf_R"] > 0 else float("nan")
    return dict(
        dE={0: {"R": dE0, "W": dE0}, 1: dE1, 2: dE2},
        delta_01=0.0, delta_21=d21, delta_02=0.0,
        Delta_1=dE1["W"] - dE1["R"], Delta_2=dE2["W"] - dE2["R"],
        w={"01": w01, "12": w12, "20": w20},
        mu_02=p.drive,
    )
