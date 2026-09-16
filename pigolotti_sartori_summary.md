# Pigolotti & Sartori (2016) — "Protocols for Copying and Proofreading in Template-Assisted Polymerization"

J. Stat. Phys. 162, 1167–1182 (2016), DOI 10.1007/s10955-015-1399-2. arXiv:1601.06940 [q-bio.SC].

## Sources

- **Retrieved full text from**: `https://arxiv.org/html/1601.06940v1` (LaTeXML-rendered HTML, fetched and parsed directly via `curl` — this is the primary source for every equation/quote below).
- Confirmed identity/metadata at `https://arxiv.org/abs/1601.06940` and PDF link `https://arxiv.org/pdf/1601.06940`.
- **Springer page** `https://link.springer.com/article/10.1007/s10955-015-1399-2` redirected to an IdP login wall (303 → `idp.springer.com/authorize...`) and could **not** be fetched — the published (2016) version content is assumed identical to arXiv v1 (submitted Jan 26 2016, same title/authors), but this was **not independently verified**. Treat any Springer-specific pagination/equation numbers as unconfirmed; all equation numbers below are from the arXiv HTML version.
- No Kappa/PyKappa documentation or pykappa.org content was consulted, per task constraint.

---

## 1. Full reaction scheme

The paper's general framework (Sec. 2) describes a copying machine cycling through **main states** (rectangles, polymer-committed) and **intermediate states** (circles, conformational states of the machine while processing one candidate monomer). Four specific protocols (Fig. 2, A–D) are built from this framework. All rate constants below are reproduced **exactly as named in the paper**; `k_{ij}` denotes the rate of the transition **from state j to state i**.

### General rate parameterization (Eq. 1) — applies to every protocol

$$k_{ij}^{r} = \omega_{ij}\exp\!\big[(\Delta E_j^{r}+\mu_{ij}+\delta_{ij})/T\big]$$
$$k_{ij}^{w} = \omega_{ij}\exp\!\big[(\Delta E_j^{w}+\mu_{ij})/T\big]$$
$$k_{ji}^{r} = \omega_{ij}\exp\!\big[(\Delta E_i^{r}+\delta_{ij})/T\big]$$
$$k_{ji}^{w} = \omega_{ij}\exp\!\big[(\Delta E_i^{w})/T\big]$$

Reference state: $\Delta E_0^w=\Delta E_0^r=0$ (initial main state).

### Protocol A — single-step copolymerization (Bennett's model; Sec. 3)

No intermediate. States: `…` (pre-incorporation main state) ⇄ `…r` / `…w` (post-incorporation main states, right/wrong).

- $0 \to 1$-type binding/incorporation directly: rate $k_{10}^r$ (right), $k_{10}^w$ (wrong)
- Reverse (excision): rate $k_{01}^r$, $k_{01}^w$

Master equations, Eq. (2):
$$\dot P(\dots r)=k^{r}_{10}P(\dots)+k^{r}_{01}P(\dots rr)+k^{w}_{01}P(\dots rw)-(k^{r}_{10}+k^{w}_{10}+k^{r}_{01})P(\dots r)$$
$$\dot P(\dots w)=k^{w}_{10}P(\dots)+k^{r}_{01}P(\dots wr)+k^{w}_{01}P(\dots ww)-(k^{r}_{10}+k^{w}_{10}+k^{w}_{01})P(\dots w)$$

### Protocol B — double-step copying (Sec. 5; the "Michaelis–Menten-like" scheme)

Three states 0 (unbound main) → 1 (intermediate, bound complex) → 2 (main, product/incorporated). **No discard pathway back from state 2.**

- $0\leftrightarrow1$: $k_{10}^{r/w}$ (forward binding), $k_{01}^{r/w}$ (reverse/unbinding)
- $1\leftrightarrow2$: $k_{21}^{r/w}$ (forward accommodation/catalysis), $k_{12}^{r/w}$ (reverse of catalysis)

Occupancy of intermediate (analogous to Eq. 9's $p_1$):
$$p_1^{r}=\frac{k_{10}^{r}+(1-\eta)k_{12}^{r}}{k_{01}^{r}+k_{21}^{r}}, \qquad p_1^{w}=\frac{k_{10}^{w}+\eta k_{12}^{w}}{k_{01}^{w}+k_{21}^{w}}$$

Error condition, Eq. (9):
$$\frac{\eta}{1-\eta}=\frac{p_{1}^{w}k_{21}^{w}-k_{12}^{w}\eta}{p_{1}^{r}k_{21}^{r}-k_{12}^{r}(1-\eta)}$$

### Protocol C — Kinetic Proofreading (Sec. 6; "in the spirit of Hopfield's model") — THE core proofreading scheme

Same three states 0, 1, 2 as Protocol B, **plus an added reaction $2\to0$** ("driven backward", i.e. hydrolysis-fueled) that discards/corrects an already-incorporated monomer:

- $0\leftrightarrow1$: **binding** — $k_{10}^{r/w}$ (fwd), $k_{01}^{r/w}$ (rev)
- $1\leftrightarrow2$: **accommodation/incorporation** — $k_{21}^{r/w}$ (fwd), $k_{12}^{r/w}$ (rev)
- $2\leftrightarrow0$: **proofreading (discard/reset)** — $k_{02}^{r/w}$ (fwd, i.e. the 2→0 discard), $k_{20}^{r/w}$ (rev)

Exact error equation, Eq. (11):
$$\frac{\eta}{1-\eta}=\frac{p_{1}^{w}k_{21}^{w}+k_{20}^{w}-(k_{12}^{w}+k_{02}^{w})\eta}{p_{1}^{r}k_{21}^{r}+k_{20}^{r}-(k_{12}^{r}+k_{02}^{w})(1-\eta)}$$
(Note: the last term of the denominator is printed as $k_{02}^{w}$ in the arXiv HTML — this is almost certainly a **typesetting typo** for $k_{02}^{r}$, given the pattern of every other term; flagged, not silently corrected.)

**Irreversibility approximation used for the whole rest of Sec. 6** (explicitly stated, "the same assumptions used to simplify the reaction scheme in Hopfield's original model"):
> "the second step and the proofreading reaction are irreversible, so that $k_{12}^{r}$, $k_{12}^{w}$, $k_{20}^{r}$, and $k_{20}^{w}$ can be neglected."

I.e., in the working (Hopfield-style) version of Protocol C, the scheme is a **unidirectional 3-state cycle**:
$$0 \xrightarrow{k_{10}^{r/w}} 1 \xrightarrow{k_{21}^{r/w}} 2 \xrightarrow{k_{02}^{r/w}} 0 \to \dots$$
with only $k_{01}^{r/w}$ (reversal of initial binding, before commitment) kept as a genuine reverse rate.

Simplified error equation, Eq. (12), with $r=\omega_{21}/\omega_{10}$ and $K=(\omega_{21}/\omega_{02})e^{(\mu_{10}+\mu_{21}-\mu_{02})/T}$:
$$\frac{\eta}{1-\eta}=\frac{e^{\delta_{10}/T}+re^{(\delta_{21}+\mu_{21})/T}}{1+re^{\mu_{21}/T}}\cdot\frac{K-\eta e^{\Delta E_2^w/T}(1+r)}{Ke^{(\delta_{21}+\delta_{10})/T}-(1-\eta)e^{(\Delta E_2^r+\delta_{02})/T}\left(e^{\delta_{10}/T}+re^{\delta_{21}/T}\right)}$$

Full (unapproximated) exact expression is given in the Appendix, Eq. (19), with $r_p=\omega_{02}/\omega_{10}$.

### Protocol D — Proofreading/accommodation (Sec. 7)

Same topology as C, but the discard pathway acts **from the intermediate state 1** rather than from the final state 2. There are now **two parallel sets of rates between states 0 and 1**: the ordinary copying rates $k_{10}^{r/w}$, $k_{01}^{r/w}$, and a second, barred set $\bar k_{10}^{r/w}$, $\bar k_{01}^{r/w}$ for the proofreading branch. $k_{21}^{r/w}$, $k_{12}^{r/w}$ remain the 1↔2 accommodation rates (no separate discard from 2 in this protocol). Error equation, Eq. (14), formally identical to Eq. (9) but with modified occupancies:
$$p_1^{r}=\frac{k_{10}^{r}+\bar k_{10}^{r}+(1-\eta)k_{12}^{r}}{k_{01}^{r}+\bar k_{01}^{r}+k_{21}^{r}}, \qquad p_1^{w}=\frac{k_{10}^{w}+\bar k_{10}^{w}+\eta k_{12}^{w}}{k_{01}^{w}+\bar k_{01}^{w}+k_{21}^{w}}$$

---

## 2. Energy landscape / thermodynamic parameterization

- $\Delta E_i^{r}$, $\Delta E_i^{w}$: state energies of state $i$ for right/wrong candidate ($\Delta E_0^{r}=\Delta E_0^{w}=0$ by convention).
- $\delta_{ij}$: **kinetic** (activation-barrier) discrimination parameter attached to the unordered pair of states $\{i,j\}$ — it enters **both** $k_{ij}^{r}$ (the $j\to i$ forward rate) **and** $k_{ji}^{r}$ (the $i\to j$ reverse rate) identically, per Eq. (1); it never appears in any wrong-monomer rate ($k^{w}$ never contains a $\delta$). "A positive value of $\delta_{ij}$ means that the corresponding transition is kinetically facilitated for right monomers with respect to wrong ones."
- $\mu_{ij}$: chemical driving favoring $j\to i$ regardless of right/wrong (this is the non-conservative, detailed-balance-breaking "fuel" term — physically, NTP/ATP/GTP hydrolysis free energy channeled into a specific transition). $\mu_{ij}>0$.
- $\omega_{ij}$: inverse characteristic timescale (prefactor) of the $i\leftrightarrow j$ transition.
- $T$: temperature, $k_B=1$.

**Detailed balance / equilibrium limit.** A copying step is quasi-static (net speed $v=0$) when both $v^r=0$ and $v^w=0$ simultaneously — this fixes the driving to its **stall value**:
$$\mu_{\rm st}\equiv -T\log\!\big(e^{-\Delta E_1^{w}/T}+e^{-\Delta E_1^{r}/T}\big)$$
"the stall chemical driving is negative, since to arrest polymerization it needs to oppose the entropic force driving growth of the chain" (an entropic effect: exponentially many chain continuations). At stall, the error reaches its **equilibrium value** (Protocol A):
$$\eta_{\rm eq}=\frac{1}{1+e^{(\Delta E_1^{w}-\Delta E_1^{r})/T}}$$
which depends **only on the energy difference**, not on any $\delta$.

**Irreversible (large-driving) limit** (Protocol A): as $\mu_{10}\to\infty$,
$$\eta_{\rm irr}=\frac{e^{-\delta_{10}/T}}{1+e^{-\delta_{10}/T}}$$
which depends **only on $\delta_{10}$**, not on the energy difference.

**Which rate constants depend on $\delta$, which on the driving $\mu$:**
- $\delta_{ij}$ appears **only inside the right-monomer rates** ($k_{ij}^r$ and $k_{ji}^r$), in **both** the forward and backward direction of a given transition pair — i.e. $\delta$ modifies a **barrier height common to both directions** of one step, not a single on/off rate in isolation. It never appears in $k^w$.
- $\mu_{ij}$ appears in **both** $k_{ij}^{r}$ **and** $k_{ij}^{w}$ (i.e. in the forward rate regardless of match), but **not** in the corresponding backward rates $k_{ji}^{r}$, $k_{ji}^{w}$. This is what breaks detailed balance / drives net flux: $\mu_{ij}$ raises the forward rate of a transition without raising its reverse, for both right and wrong candidates equally.
- Net effect: setting all $\mu_{ij}=\mu_{\rm st}$ (equivalently zero net driving/dissipation) restores detailed balance and $\eta\to\eta_{\rm eq}$, which is governed purely by $\Delta E^w-\Delta E^r$ and is **independent of any $\delta$**. Non-zero (positive) $\mu$ is exactly the fuel/hydrolysis term; larger $\mu_{ij}$ (esp. $\mu_{02}$ for the discard reaction in Protocol C) drives the system away from equilibrium and lets $\delta$-type (kinetic) discrimination be expressed.

**Does $\delta$ appear once or twice in the full proofreading scheme (Hopfield square-law question)?**

In the fully general Protocol C, there are **three distinct $\delta$ parameters**, one per transition: $\delta_{10}$ (binding step), $\delta_{21}$ (accommodation step), $\delta_{02}$ (proofreading/discard step, "$\delta_{02}<0$" by construction — favors wrong-monomer discard). The general minimum-error formula, Eq. (13):
$$\eta_{\rm min}(v\to0)\approx e^{\frac{\Delta E_2^r-\Delta E_2^w+\delta_{02}}{T}}\cdot\frac{e^{\delta_{10}/T}+re^{\delta_{21}/T}}{(1+r)e^{(\delta_{21}+\delta_{10})/T}}, \qquad r=\omega_{21}/\omega_{10}$$
mixes all three $\delta$'s plus the energy gap $\Delta E_2^w-\Delta E_2^r$; in general the exponent is **not simply $-2\delta$**.

The **classic Hopfield square-law is recovered only under a specific parameter choice** stated explicitly by the authors:
> "Hopfield's model corresponds to the choice of $\delta_{10}=\delta_{02}=0$, $\Delta E_2^w=\Delta E_1^w$ and $\Delta E_2^w=\Delta E_1^r$ [sic, presumably meaning the energy of state 1 equals that of state 2 for each of right/wrong]. Moreover, as the forward rates of the second reaction are equal for right and wrong incorporations, one should fix $\delta_{21}=\Delta E_2^w-\Delta E_2^r$. With this choice, the minimum error in Eq. (13) correctly becomes $\eta_{\rm min}\approx\exp[-2(\Delta E_2^w-\Delta E_2^r)/T]$, i.e. the square of the equilibrium error."

So: **two of the three $\delta$'s ($\delta_{10}$, $\delta_{02}$) are set to zero**, and the single surviving discrimination quantity — the energy gap $\Delta=\Delta E_2^w-\Delta E_2^r$ — is forced (via $\delta_{21}=\Delta$) to appear **twice** in the exponent: once directly as the equilibrium-type energy term, once via the kinetic barrier $\delta_{21}$ that is tied to it. This is the origin of the $e^{-2\Delta/T}$ (square-of-equilibrium-error) signature. **Flagged interpretive point**: the paper's own $\delta_{ij}$ notation is therefore not literally "the discrimination energy appearing once vs. twice" in the generic model — genericaly there are three independent $\delta$'s each entering once in their own step; the "squaring" is a special-case consequence of Hopfield's assumption that forces one physical energy gap to double-count across the accommodation step and the (implicit) equilibrium/energetic contribution. For a **general driven, kinetic-lock, or induced-fit regime** (not Hopfield's specific choice), $\eta_{\rm min}$ instead reduces to a **single** barrier, $e^{-\delta_{10}/T}$ or $e^{-\delta_{21}/T}$ (see Sec. 4 below) — i.e. **linear**, not squared, in the barrier. Bennett's proofreading limit (no energy differences at all, $E_2^w=E_2^r$) gives $\eta_{\rm min}\approx\exp[-(\delta_{21}-\delta_{02})/T]$ — again the two proofreading-relevant barriers appear once each, additively, not squared.

---

## 3. Numerical values

**The paper reports no dimensioned numerical values anywhere** (no rate constants in s⁻¹, no concentrations, no kcal/mol free energies). Every quantity is dimensionless, expressed in units of $T$ (with $k_B=1$), and $\omega_{ij}$ (a rate) is used only as a unit in which speeds are measured (e.g. "speed is measured in units of $\omega_{10}$", Fig. 4C, 5C captions). There are **no tables** in the paper; the only numeric content is a handful of illustrative parameter choices used to generate heatmaps (Figs. 5–7). Reproduced exactly:

| Figure | Fixed parameters (illustrative only) |
|---|---|
| Fig. 4B (Protocol A) | Heat map axes: $\delta_{10}$ vs. $\Delta E_1^w-\Delta E_1^r$ (no numeric bounds given in extracted text) |
| Fig. 5B (Protocol B) | $\Delta E_2^r=\Delta E_1^r=0$; $\Delta E_2^w=\Delta E_1^w=3T$; chemical drivings & timescale ratios numerically optimized (values not tabulated) |
| Fig. 6B (Protocol C) | $\Delta E_2^r=\Delta E_1^r=0$; $\Delta E_2^w=\Delta E_1^w=3T$; $\delta_{02}=-2T$ fixed; axes over $\delta_{21}$ (and presumably $\delta_{10}$) |
| Fig. 6C (Protocol C) | Same energies; $\delta_{10}=2T$ fixed; axes over $\delta_{21}$, $\delta_{02}$ |
| Fig. 7 (Protocol D) | $\Delta E_2^r=\Delta E_1^r=0$; $\Delta E_2^w=\Delta E_1^w=3T$; a barrier printed as "$\delta_{01}=2T$" — **flag**: given the paper's own notation uses a **barred** symbol $\bar\delta_{10}$ for the proofreading/accommodation barrier in this protocol, and no $\delta_{01}$ is defined anywhere else in the text, this is almost certainly a rendering artifact where the diacritic (bar) over $\delta_{10}$ was dropped by the HTML converter — most likely means $\bar\delta_{10}=2T$. Treat with caution; not independently confirmed against the PDF. |

All other "numbers" in the paper are symbolic relations (Sections 4–5 below), not tabulated constants.

---

## 4. Key quantitative results

**Error fraction definition** (general, Eq. 3, "ansatz of uncorrelated errors"):
$$P(\dots)\propto(1-\eta)^{N^r}\eta^{N^w}$$
where $N^r$, $N^w$ are the number of right/wrong matches in an arbitrary copy sequence, and $\eta$ is determined self-consistently at steady state — i.e. $\eta$ is literally the **per-monomer probability that an incorporated unit is a mismatch**, assumed uncorrelated between positions along the copy.

General steady-state closure condition:
$$\frac{\eta}{1-\eta}=\frac{v^w(\eta)}{v^r(\eta)}$$
where $v^{r/w}$ are net per-step incorporation speeds of right/wrong monomers (Protocol A: $v^w=k_{10}^w-k_{01}^w\eta$, $v^r=k_{10}^r-k_{01}^r(1-\eta)$; general speed $v=\eta v^w+(1-\eta)v^r$).

**Protocol A (no intermediate; the introductory/simplest scheme) — regimes** (Fig. 4B/4C):
- **Energetic region** ($\delta_{10}<\Delta E_1^w-\Delta E_1^r$): minimum error is $\eta_{\rm eq}$ (achieved at $\mu_{10}\to\mu_{\rm st}$); error is an **increasing** function of driving/speed.
- **Kinetic region** ($\delta_{10}>\Delta E_1^w-\Delta E_1^r$): minimum error is $\eta_{\rm irr}$ (achieved as $\mu_{10}\to\infty$); error is a **decreasing** function of driving/speed.
- Energetic and kinetic discrimination are **mutually exclusive** in this protocol — can't combine.

**Protocol B (double-step, no proofreading — "MM-like") regimes** (Fig. 5B/5C), each exploiting **only one** discrimination mechanism:
- **Energetic region** ($\Delta E_2^w-\Delta E_2^r>\delta_{10}$ and $>\delta_{21}$): $\eta_{\rm min}=\eta_{\rm eq}=e^{-\Delta E_2^w/T}/(e^{-\Delta E_2^w/T}+e^{\Delta E_2^r/T})$, at stall.
- **Kinetic Lock** ($\delta_{10}>\Delta E_2^w-\Delta E_2^r$, $\delta_{10}>\delta_{21}$): $\eta_{\rm min}=\eta_{\rm irr}=e^{-\delta_{10}/T}/(1+e^{-\delta_{10}/T})$ — "the system is thus kinetically locked after the first step"; **only the first barrier matters**, second barrier is irrelevant once the first step is strongly driven.
- **Induced Fit** ($\delta_{21}>\Delta E_2^w-\Delta E_2^r$, $\delta_{21}>\delta_{10}$): $\eta_{\rm min}\approx e^{-\delta_{21}/T}$ (obtained as $r\to0$ then $\mu\to\infty$).
- Explicit statement: **"it is impossible to exploit both kinetic barriers"** in Protocol B — no square-law improvement is possible without the discard/proofreading pathway.

**Protocol C (Kinetic Proofreading) — the improvement over B:**
General minimum error, Eq. (13) (already given in Sec. 2 above):
$$\eta_{\rm min}(v\to0)\approx e^{\frac{\Delta E_2^r-\Delta E_2^w+\delta_{02}}{T}}\cdot\frac{e^{\delta_{10}/T}+re^{\delta_{21}/T}}{(1+r)e^{(\delta_{21}+\delta_{10})/T}}$$
- Two regimes distinguished by which of $\delta_{10}$/$\delta_{21}$ dominates (paper proves the expression is monotonic in $r=\omega_{21}/\omega_{10}$):
  - **Kinetic Lock + Proofreading** ($\delta_{10}>\delta_{21}$): as $r\gg1$, the copying-discrimination factor $\to \exp(-\delta_{10}/T)$.
  - **Induced Fit + Proofreading** ($\delta_{21}>\delta_{10}$): as $r\ll1$, the copying-discrimination factor $\to \exp(-\delta_{21}/T)$.
- "The minimum error always decreases exponentially with $\delta_{02}$" (the proofreading barrier) — this is the direct, always-present benefit of adding the discard pathway, independent of regime.
- Under **Hopfield's specific parameter choice** ($\delta_{10}=\delta_{02}=0$, $\delta_{21}=\Delta E_2^w-\Delta E_2^r$): $\eta_{\rm min}\approx\exp[-2(\Delta E_2^w-\Delta E_2^r)/T] = \eta_{\rm eq}^{2}$ (to leading exponential order) — **the "Hopfield limit."**
- Under **Bennett's proofreading choice** (kinetic lock, no energy differences, $E_2^w=E_2^r$): $\eta_{\rm min}\approx\exp[-(\delta_{21}-\delta_{02})/T]$.

**Protocol D (proofreading/accommodation) — richer regime structure:**
- $v\to0$ limit: $\eta_{\rm min}(v\to0)\approx\exp[(-\delta_{10}+E_2^r-E_2^w+\bar\delta_{10})/T]$ (Eq. 15) — "the minimum error associated to the first barrier, times the proofreading error reduction factor."
- $v\to\infty$ limit: Eq. (16), more complex expression involving $\delta_{10}$, $\delta_{21}$, $\bar\delta_{10}$, $\mu_{21}$, $r=\omega_{21}/\omega_{10}$, $\bar r=\bar\omega_{01}/\omega_{10}$.
- **Kinetic Lock + Proofreading** region ($\delta_{21}<\Delta E_2^w-\Delta E_2^r$): error given by Eq. (15).
- **Mixed Region** ($\delta_{21}>\Delta E_2^w-\Delta E_2^r$): $\eta_{\rm min}=\exp[(\bar\delta_{10}-\delta_{10}-\delta_{21})/T]$ — **all three kinetic barriers combine additively** in the exponent. Explicit contrast: "This is at variance with models B and C where only one barrier... affects the minimum error in each region" — i.e. Protocol D is strictly more powerful than B or C because proofreading acting from the intermediate state lets all three barriers stack, whereas B/C only ever get to use one barrier (per regime) plus (in C) the separate proofreading factor.

**Speed–accuracy–dissipation tradeoff, as framed by the paper:** There is no single universal tradeoff sign. In the **kinetic region/regime**, increasing driving (dissipation) **decreases** error and **increases** speed (positive, "good" tradeoff — you get both for free). In the **energetic region/regime**, increasing driving **increases** error while increasing speed (negative tradeoff — genuine speed/accuracy conflict). Because each multi-step protocol partitions into several such regimes, "one can find negative and positive speed-error relations depending on which parameter is altered... and in which region the model is operating" (stated for Protocol B, Sec. 5, and shown in Fig. 5C for two example points; analogous statement/figure for Protocol A in Fig. 4C).

**Figures referencing error vs. driving/dissipation (as described in text; exact pixel-level trends not independently re-derived by us beyond the text descriptions):**
- **Fig. 4B**: heat map of $\eta_{\rm min}$ over axes ($\delta_{10}$, $\Delta E_1^w-\Delta E_1^r$) for Protocol A, dashed line separating kinetic/energetic regions.
- **Fig. 4C**: speed–error tradeoff curves for the energetic vs. kinetic regimes (opposite-sign slopes), speed in units of $\omega_{10}$.
- **Fig. 5B**: heat map of $\eta_{\rm min}$ over ($\delta_{10}$, $\delta_{21}$) for Protocol B, three regions (energetic/kinetic-lock/induced-fit).
- **Fig. 5C**: speed–error tradeoff, points chosen from induced-fit and kinetic-lock regimes of Fig. 5B.
- **Fig. 6A**: energy-landscape schematic for Protocol C showing the $\delta_{02}<0$ proofreading barrier.
- **Fig. 6B**: $\eta_{\rm min}$ heat map at fixed $\delta_{02}=-2T$, varying (presumably) $\delta_{10}$, $\delta_{21}$ — shows the Kinetic-Lock-vs-Induced-Fit-plus-Proofreading boundary.
- **Fig. 6C**: $\eta_{\rm min}$ heat map at fixed $\delta_{10}=2T$, varying $\delta_{21}$, $\delta_{02}$ — error decays exponentially with $\delta_{02}$ throughout, and depends on $\delta_{21}$ only once $\delta_{21}>\delta_{10}$.
- **Fig. 7A–C**: analogous energy landscape and region/heat-map plots for Protocol D.

---

## 5. Notation table

| Symbol | Meaning | Units / range |
|---|---|---|
| $i,j$ | State indices; $0$=initial main state, $n{+}1$=main state after incorporation, $1\ldots n$=intermediate states | integers |
| $k_{ij}^{r}$, $k_{ij}^{w}$ | Transition rate from state $j$ to state $i$, for a right/wrong candidate monomer | rate (arbitrary units, set by $\omega_{ij}$) |
| $\Delta E_i^{r}$, $\Delta E_i^{w}$ | Free energy of state $i$ for right/wrong match (relative to $\Delta E_0=0$) | energy, units of $T$ |
| $\mu_{ij}$ | Chemical driving force favoring transition $j\to i$ (same for right & wrong); the non-equilibrium "fuel" term (e.g. NTP/ATP/GTP hydrolysis) | energy, units of $T$; $\mu_{ij}>0$ favors $j\to i$ |
| $\mu_{\rm st}$ | Stall value of the (total) chemical driving at which net speed $v=0$ | energy, units of $T$; $\mu_{\rm st}<0$ |
| $\delta_{ij}$ | Kinetic discrimination: activation-barrier difference between right and wrong monomer for the $i\leftrightarrow j$ transition pair (enters both directions identically); appears only in $k^{r}$, never in $k^{w}$ | energy, units of $T$; $\delta_{ij}>0$ favors right |
| $\omega_{ij}$ | Inverse characteristic timescale (prefactor / attempt rate) of transition $i\leftrightarrow j$ | rate (1/time) |
| $T$ | Temperature ($k_B\equiv1$) | energy unit; all $\delta$, $\Delta E$, $\mu$ reported in multiples of $T$ |
| $\eta$ | Error fraction: steady-state probability that an incorporated monomer is a mismatch | dimensionless, $0\le\eta\le1$ |
| $\eta_{\rm eq}$ | Equilibrium (quasi-static, detailed-balance) error, achieved at $\mu=\mu_{\rm st}$ | dimensionless |
| $\eta_{\rm irr}$ | Irreversible (large-driving) error limit, Protocol A | dimensionless |
| $\eta_{\rm min}(v\to0)$ / $\eta_{\rm min}(v\to\infty)$ | Minimum achievable error in the vanishing-speed / diverging-speed limit for multi-step protocols | dimensionless |
| $v$, $v^r$, $v^w$ | Net copying speed, and its right/wrong-monomer components | rate (1/time), units of $\omega_{10}$ in figures |
| $p_i^{r}$, $p_i^{w}$ | Steady-state occupancy of intermediate state $i$ relative to the preceding main state | dimensionless |
| $N^r$, $N^w$ | Number of right/wrong matches in an (arbitrary) copy sequence | integer counts |
| $r$ | $\omega_{21}/\omega_{10}$ — ratio of timescales of accommodation vs. binding steps | dimensionless |
| $r_p$ | $\omega_{02}/\omega_{10}$ — ratio of timescale of proofreading discard vs. binding | dimensionless |
| $\bar r$ | $\bar\omega_{01}/\omega_{10}$ — ratio of timescales, Protocol D proofreading branch | dimensionless |
| $K$ | $(\omega_{21}/\omega_{02})\,e^{(\mu_{10}+\mu_{21}-\mu_{02})/T}$ — lumped parameter controlling Protocol C's proofreading strength | dimensionless |
| $\bar k_{10}^{r/w}$, $\bar k_{01}^{r/w}$, $\bar\delta_{10}$, $\bar\omega_{01}$, $\bar\mu_{10}$ | Barred quantities = the second (proofreading-branch) set of $0\leftrightarrow1$ rates/parameters unique to Protocol D | same units as unbarred counterparts |
| $\mathcal{N}$ | Normalization factor for occupancies in speed formulas, $\mathcal{N}=(1+p_1^w+p_1^r)^{-1}$ | dimensionless |
| $\mathcal{J}_{ij}^{r/w}$ | Probability flux between states $i,j$ for right/wrong: $\mathcal{J}_{ij}^{r}=k_{ij}^{r}P(\dots r_j)-k_{ji}^{r}P(\dots r_i)$ | probability/time |

---

## 6. Essential vs. elaborative model components

### Non-proofreading vs. proofreading schemes, side by side

| | Protocol B (no proofreading, "MM-like") | Protocol C (Kinetic Proofreading) |
|---|---|---|
| States | 0 (unbound) → 1 (intermediate/bound) → 2 (product) | Same 0→1→2, **plus** irreversible discard arc $2\to0$ |
| Reactions | $0\leftrightarrow1$ ($k_{10}$,$k_{01}$), $1\leftrightarrow2$ ($k_{21}$,$k_{12}$) | Same, plus $2\leftrightarrow0$ ($k_{02}$,$k_{20}$); in working (irreversible) form, $k_{12}$ and $k_{20}$ are dropped, leaving a driven 3-cycle $0\to1\to2\to0$ |
| Best achievable error | $\eta_{\rm eq}$ (energetic), $\eta_{\rm irr}\!=\!e^{-\delta_{10}/T}/(1+e^{-\delta_{10}/T})$ (kinetic lock), or $\approx e^{-\delta_{21}/T}$ (induced fit) — **only one discrimination mechanism usable at a time**; linear in whichever single barrier is exploited | $\eta_{\rm min}\approx e^{(\Delta E_2^r-\Delta E_2^w+\delta_{02})/T}\cdot(\ldots)$, decreasing **exponentially in $\delta_{02}$ always**, and under Hopfield's specific parameter choice collapsing to $\eta_{\rm min}\approx\exp[-2(\Delta E_2^w-\Delta E_2^r)/T]=\eta_{\rm eq}^2$ — **strictly better than any Protocol B regime** |
| Essential extra ingredient | — | The discard reaction $2\to0$ **must be driven** by a nonzero, dissipative $\mu_{02}$ (fuel/hydrolysis term) to be effectively irreversible; without it ($\mu_{02}\to$ its own stall value) the discard step re-equilibrates and the advantage vanishes. |

### What a minimal single-monomer-incorporation Kappa model needs (essential) vs. can drop (elaborative)

**Essential — must be in the Kappa model to reproduce the core KPR phenomenon:**
1. Exactly the three-state cycle of Protocol C: a template/enzyme-site state (call it `0`), a bound-intermediate state (`1`), and a post-catalysis/incorporated state (`2`), with **two monomer species**, right (`R`) and wrong (`W`).
2. All six directed rates in the general (non-approximated) scheme — $k_{10}^{r/w}$, $k_{01}^{r/w}$, $k_{21}^{r/w}$, $k_{02}^{r/w}$ — with $k_{12}^{r/w}$ and $k_{20}^{r/w}$ droppable (set to ~0) **only if** the goal is to reproduce the paper's simplified/Hopfield-style irreversible limit; keep them if you want the general (Eq. 11/12) behavior.
3. The Eq. (1) rate parameterization: each rate must be built from $\Delta E_j^{r/w}$, $\mu_{ij}$, $\delta_{ij}$, $\omega_{ij}$, $T$ exactly as specified — in particular, $\delta$ terms enter **only** right-monomer rates ($k^r$), and a given $\delta_{ij}$ affects **both directions** of its transition pair equally.
4. A genuinely dissipative driving term on the discard step ($\mu_{02}>0$, i.e. hydrolysis-fueled) — this is what makes $2\to0$ effectively irreversible and is the source of the whole effect; setting $\mu_{02}=0$ (or to its stall value) must reproduce $\eta\to\eta_{\rm eq}$ as a sanity check.
5. The three discrimination barriers $\delta_{10}$ (binding), $\delta_{21}$ (accommodation), $\delta_{02}$ (discard) as **independently tunable** parameters — this is required to reproduce the paper's regime structure (Kinetic-Lock-vs-Induced-Fit-plus-Proofreading) and, in the Hopfield special case ($\delta_{10}=\delta_{02}=0$, $\delta_{21}=\Delta E_2^w-\Delta E_2^r$), the square-law result.
6. The energy gap $\Delta E_2^w-\Delta E_2^r$ (equivalently $\Delta E_1^w-\Delta E_1^r$ if state-1 energy differences are also wanted) as an independent parameter, to be able to dial between "energetic," "kinetic," and Hopfield-mixed regimes.

**Elaborative — explicitly droppable for a single-monomer-incorporation model, per the paper's own reasoning:**
1. **Copolymer/sequence growth.** The paper's whole multi-monomer treatment rests on the "uncorrelated errors" ansatz (Eq. 3): $P(\dots)\propto(1-\eta)^{N^r}\eta^{N^w}$, i.e. the steady-state statistics of the full growing copolymer are assumed (and, self-consistently, shown) to factorize into **independent, identically-distributed single-monomer incorporation events**. This directly licenses a minimal model that simulates just one incorporation cycle (or a Markov chain repeating it) — the paper itself treats this as equivalent to the full sequence-copying process for computing $\eta$ and $v$.
2. **Multiple/varied monomer identities** ("full gray"/"full white"/"half-half" combinatorics in Fig. 2). The physics depends only on the binary right/wrong classification, never on which specific monomer type; a Kappa model needs only two monomer agents (`R`, `W`), not four combinatorial pairings.
3. **Protocol D's second (barred) rate branch and its more complex regime algebra** — this is a variant elaboration (proofreading acting from the intermediate rather than the final state) that demonstrates all three barriers can be combined, but it is not needed to demonstrate the basic KPR phenomenon; Protocol C alone suffices as the canonical Hopfield-style scheme.
4. **Spatial/steric effects** — the paper never models these at all (pure well-mixed CTMC over discrete states); nothing to drop, but also nothing to add.
5. **Backtracking / sub-network switching** — explicitly flagged by the authors themselves as a *future generalization*, not part of the core model ("A possible further generalization would be to include the possibility of performing stochastic transitions among different sub-networks... to study backtracking" — Conclusions).

### Caveat on which "non-proofreading" reference scheme to use

The task prompt describes a reference "Michaelis–Menten-like, single intermediate, one committed step" scheme. In this paper that maps cleanly onto **Protocol B** (0↔1↔2, no discard arc) rather than Protocol A (which has zero intermediates and is Bennett's model). Protocol A is the simplest scheme in the paper but has **no intermediate state at all**; Protocol B is the closer MM analog (bound complex 1 ~ "ES", catalytic step 1→2 ~ $k_{\rm cat}$). Protocol C = Protocol B + discard arc is the right "add a proofreading branch to the MM scheme" comparison for a minimal Kappa build.
