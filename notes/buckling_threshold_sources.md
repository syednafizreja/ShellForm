# Sources behind the buckling threshold λ_LBA ≥ 5 (risk P1)

Written by the assistant on 11 Nov 2026, under the author's standing delegation. Closes the "unopened" part of drafting-kit risk P1. **Author to open both copies and confirm the page numbers before the paper cites them.**

## 1. What was opened

| Source | Copy opened | What was read |
|---|---|---|
| Dulácska E., Kollár L. Design procedure for the buckling analysis of reinforced concrete shells. *Thin-Walled Structures* 23 (1995) 313-321. doi:10.1016/0263-8231(95)00019-A | Author-uploaded copy on academia.edu (https://www.academia.edu/103179107), text layer read 11 Nov | Abstract; pp. 316-319 (imperfection, cracking, plasticity, safety factor) |
| ACI 318.2-14, Building Code Requirements for Concrete Thin Shells, and Commentary ACI 318.2R-14 (ACI, 2014) | Free PDF on concrete.org (`/portals/0/files/pdf/318_2_14.pdf`), all 16 pages read 11 Nov | Cl. 3.1.8 and R3.1.8; reference list |
| IASS Working Group No. 5. Recommendations for Reinforced Concrete Shells and Folded Plates. IASS, Madrid (1979), 66 pp. | **Not opened.** No legal open copy found (a Scribd upload exists; not used). Reference details from ACI 318.2R-14 reference list and Dulácska & Kollár ref. 5 | Nothing first-hand |

## 2. What the sources say

**Dulácska & Kollár (1995).**
- The buckling load is the classical (linear) critical load times a product of reduction factors (p. 318): p_cr,el,rc = p_cr^lin · ρ_imp · ρ_creep · ρ_crack. Plasticity is added with a "semi-quadratic Dunkerley" interaction against the plastic load p_pl (p. 318).
- Imperfection: the eccentricity-to-imperfection ratio e0/w0 is 1.0 for cylinders, 0.67 for domes (positive Gaussian curvature) and 0.50 for hyperbolic shells (pp. 316-317). Accidental imperfection amplitude 1/4 to 3/4 of the wall thickness, or the contractor's guaranteed value (p. 317).
- Creep: modulus of concrete reduced by a creep factor (abstract and section 4).
- Cracking: ρ_crack depends on the steel-to-concrete stiffness ratio, e0/t and e0/w0 (Table 2).
- **Safety factor γ (section 5, Table 3, p. 319):** depends on slenderness p_pl / p_cr^lin. γ = 1.50 at 0, 1.90 at 0.5, 2.35 at 1.0, 2.75 at 2.0 and 3.00 as the ratio tends to infinity (buckling governs). These are minimum values.

**ACI 318.2-14.**
- Cl. 3.1.8: "Shell instability shall be investigated and shown by design to be precluded." No numeric factor.
- R3.1.8 lists eight effects a stability check should consider (as-built geometry, local curvature, large deflections, creep and shrinkage, inelastic material, cracking, reinforcement, support deformation), and says "a procedure for determining critical buckling loads of shells is given in the IASS recommendations (IASS 1979)".

## 3. What this means for λ ≥ 5

- Neither opened source states the number 5. The threshold stays **our judgement [J]**, now with a stated derivation.
- Read with Dulácska & Kollár, a linear buckling factor λ on the factored load must cover γ / (product of the reduction factors). [J] The three thresholds then have a plain meaning:
  - λ ≥ 3: γ = 3.0 (the buckling-governed upper value of Table 3) with no reduction at all. This is a lower bound: every reduction factor is at most 1.
  - λ ≥ 5: γ = 3.0 with combined reductions of 0.6 (3.0 / 5).
  - λ ≥ 8: γ = 3.0 with combined reductions of 0.375 (3.0 / 8).
- ShellForm does not compute ρ_imp, ρ_creep or ρ_crack for its shells. So the paper must present 5 as a stated assumption inside this bracket, and lean on the λ 3 and λ 8 runs (Section 2.9). In the frozen results the headline holds in 0 of 10 scope cells at λ 3, 5 and 8, and the few cells that change verdict are 5 mm thickness-step effects (`paper/11_results_draft.md` Section 3.4, Table 5).

## 4. Changes made on 11 Nov

- `paper/10_methods_draft.md` section 2.5: citations replaced; IASS (1979) cited only through ACI 318.2R-14; the bracket in section 3 written as one sentence.
- `paper/references.md`: rows for Dulácska & Kollár (1995) and ACI 318.2-14; IASS (1979) row marked "not opened, cited via ACI 318.2R-14".
- `docs/preregistration.md`: dated amendment (no threshold changes; the [check] on the source is resolved as above).
- `paper/09_drafting_kit.md` P1: downgraded from high to medium.

## 5. Still open (author)

1. Open the academia.edu PDF and confirm pp. 316-319 and Table 3.
2. If a library can supply IASS (1979), read its buckling section and add a page; otherwise keep the indirect citation.
