# Day 6: all 168 designs, both spans (3 Nov 2026)

ShellBench tag: v0.1.0 (no `floor-r2` or `floor-r3` tag yet, so the pin stays and the `fe.py` cross-check waits). Script: `scripts/day06_all_designs.py`; code: `src/shellform/pipeline.py`, `fe.plan_area`. Results: `results/day06_designs.csv` (168 rows), `results/day06_comparison.csv` (84 rows), `results/day06_tried.json`, `results/day06_meta.json`. Run in the cloud on CalculiX 2.21, 41 x 41 network, about 25 minutes on 4 workers.

**Status: provisional.** The carbon factors in ShellBench are still "author to confirm", and the paper's numbers come from one run after the 10 Nov freeze.

## What changed (pre-registration amendment of 3 Nov, written before this run)

- **D6-1:** carbon and steel per m² now divide by the plan area the shell covers. Corner shells cover 73.39 m² at 10 m and 293.58 m² at 20 m (73.4 % of span², from the D3-1 inset). Edge shells cover span². The Day 5 basis (span²) is kept in the column `carbon_kgco2e_per_span2`.
- **D6-2:** T1 adds the SDL and live mass on the covered plan area, not span². This lowers T1 of the 10 m corner shells by up to 0.012 s. No thickness changes.

## Checks on the 10 m rerun

The 10 m half was resized from scratch. All 84 thicknesses and governing checks equal Day 4's, and carbon per span² equals Day 5's exactly. So the pipeline reproduces Days 4 and 5.

## Results

| Span, supports | Rise | t [mm] | λ min | T1 max [s] | Carbon [kgCO₂e/m²], gravity Sa 0 | Seismic − gravity, range |
|---|---|---|---|---|---|---|
| 10 m corners | 0.10 / 0.15 / 0.20 | 105 / 90 (85) / 75 | 5.01 | 0.184 | 45.5 / 39.8 / 34.3 | −5.8 % to 0 % |
| 10 m edges | all | 50 | 72.8 | 0.045 | 21.6 to 23.4 | 0 to +1.4 % |
| 20 m corners | 0.10 / 0.15 / 0.20 | 265 (260) / 215 / 185 | 5.00 | 0.308 | 116.8 / 96.0 / 85.1 | −2.0 % to 0 % |
| 20 m edges | all | 50 | 15.0 | 0.111 | 21.6 to 23.4 | 0 to +1.4 % |

Figures in brackets are the seismic form's thickness at some Sa.

- **All 168 designs are feasible.** Corner shells are governed by buckling; edge shells sit at the 50 mm minimum.
- **S5 holds for every design:** the largest T1 is 0.308 s (20 m corners, rise 0.10), below Tg = 0.35 s. It is the closest S5 comes; the 20 m corner shells are 12 % below the plateau end.
- **20 m corner shells need steel above the minimum,** unlike the 10 m ones: up to 284 kg of 2953 kg (9.6 %), at the supports. The seismic case adds up to 58 kg (gravity form, rise 0.10, Sa 0.6). The tension demand is still at most 36 % of the minimum steel mass, so the minimum ratio governs most of the shell.
- **Support zones** add up to 1.41 m³ to 80.9 m³ of concrete (1.7 %) at 20 m.
- **Concrete is 80 to 81 % of the carbon** in every design.
- **Cost of resilience:** gravity strategy 1.000 to 1.004; seismic strategy 0.942 to 1.015 (10 m) and 0.983 to 1.015 (20 m).
- **Which strategy is cheaper (5 % rule):** "no meaningful difference" in 78 of 84 cells. The other 6 are the 10 m corners at rise 0.15, Sa 0.1 to 0.6, seismic 5.5 to 5.8 % cheaper: the 85 against 90 mm step already shown to be an artefact of the load basis (D4-5) and the mesh (61 x 61). Every verdict is the same at all four band corners.
- **Headline claim:** not made (`headline_claim_holds: false` in the meta file). At 20 m every cell is "no meaningful difference".
- The 20 m corner seismic form at rise 0.10 drops to 260 mm at Sa 0.5 and 0.6, with λ 5.003 and 5.012, just over the limit. This is the same kind of grid-step effect as the 10 m 85 mm shells [J]; the 61 x 61 sensitivity (8 Nov) should test it. It is worth 2.0 % of carbon, under the 5 % rule either way.

## What this means [J]

Doubling the span does not change the answer. The 20 m corner shells carry real tension at the supports and the seismic case adds steel there, but the added steel is small against the minimum mesh and the concrete. Seismic resilience costs at most 0.4 % carbon for the gravity form and at most 1.5 % for the seismic form, in this model and at these Sa levels. The likely paper result is "no meaningful difference", which the pre-registration requires to be reported as such, with the cases named.

## For the author

- Nothing new to confirm today. The older checks stand: the carbon factor rows (GB/T 51366-2019 Table D.0.1), EN 1992-1-1 Annex F (F.2)/(F.3), GB 50010 Table 8.5.1 note 2.
- D6-1 settles the open "per 100 m² or per covered m²" question from 2 Nov in favour of the covered area, because section 6 says "plan area". If you want the other basis, reverse it with a dated amendment; the span² column is in the results file.
