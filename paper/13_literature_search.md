# Documented literature search for the Introduction (13 Nov 2026)

Run by the assistant under the author's standing delegation; closes `01_professor_test.md` section 2 as a first pass. **Leads, not conclusions:** every paper below was read at abstract level only, unless stated. Before a paper is cited for more than its existence, Syed opens the full text and adds the page.

## Protocol

- Database: OpenAlex (via the FastTrack literature service, about 250 M records, paywalled and open access). Search date 13 Nov 2026.
- Window: 2015-2026 for searching (to catch Michiels' work, 2017-2019); the gap claim rests on 2020-2026 papers, as ShellBench's rule asks.
- Inclusion: the paper studies (a) form-finding or shape design of shells or arches with lateral or seismic load, or (b) embodied carbon of concrete shells or shell floors, or (c) the seismic response of concrete shells. Exclusion: retrofit, frames, walls, tanks, piles, masonry infill, unrelated optimisation.
- Snowballing from Michiels & Adriaenssens: backward via the thesis; forward still to do (citations of doi:10.20898/j.iass.2017.194.892 and 10.1016/j.compstruc.2017.10.001) [to do].

| # | Query | Year from | Hits (estimate) | Screened | Included |
|---|---|---|---|---|---|
| Q1 | form finding shell structures seismic lateral loading | 2015 | 5,142 | top 20 | 5 (rows 1-5) |
| Q2 | embodied carbon concrete shell structures form-finding | 2018 | 4,087 | top 20 | 6 (rows 6-11) |
| Q3 | thin concrete shell roof seismic behaviour reinforced concrete earthquake | 2015 | 670 | top 20 | 1 (row 12) |
| Q4 | earthquake response of thin reinforced concrete shell roofs stiffness low mass parametric | 2016 | 293 | top 10 | 2 (rows 13-14) |
| Q5 | concrete shell form finding optimisation material reduction buckling governs thickness | 2018 | 190 | top 10 | 1 (row 15) |
| Q6 | embodied carbon seismic design shell form-found compression-only lateral load material efficiency | 2019 | 175 | top 10 | 0 |

Q6 found no paper that reports the embodied carbon of seismic-aware form-finding. That is the evidence for the gap line, at this depth of search.

## Included papers

| # | Paper | DOI | OA | What it does (abstract) | Use in ShellForm |
|---|---|---|---|---|---|
| 1 | Michiels, Adriaenssens, Jorquera-Lucerga (2017), J. IASS 58(4) 267-275 | 10.20898/j.iass.2017.194.892 | yes | Inverted hanging chain with lateral load in dynamic relaxation; compression-only masonry shells for combined gravity and seismic load; double-layer shells | Method ShellForm extends; masonry setting (opened earlier, Zotero 2EPDR7PB) |
| 2 | Michiels, Adriaenssens, DeJong (2019), Eng. Struct. 181 362-373 | 10.1016/j.engstruct.2018.12.043 | no | Corrugated shells form-found for seismic design, pushover validation | Prior seismic form-finding |
| 3 | Olivieri et al. (2025), Contin. Mech. Thermodyn. | 10.1007/s00161-024-01350-z | yes | Membrane equilibrium with an Airy stress function for compression-only shells under vertical and horizontal body forces; iso-resistant shapes | Recent compression-only seismic shape method |
| 4 | Málaga-Chuquitaype et al. (2022), Earthq. Eng. Struct. Dyn. | 10.1002/eqe.3626 | yes | Optimal arch forms under self-weight and in-plane seismic load; 10-50 % material saving against constant-thickness arches | Material saving claims come from unreinforced settings |
| 5 | Nodargi & Bisegna (2021), Meccanica | 10.1007/s11012-021-01414-3 | yes | Static limit analysis of masonry domes under pseudo-static seismic forces | Masonry seismic capacity |
| 6 | Hawkins, Orr, Shepherd et al. (2018), Structures | 10.1016/j.istruc.2018.10.006 | yes (accepted ms.) | Low-carbon thin-shell concrete floor, designed, built and tested | Carbon motivation for shells |
| 7 | Jayasinghe, Orr, Hawkins et al. (2022), J. Clean. Prod. | 10.1016/j.jclepro.2022.131177 | yes | Floor strategies compared; thin shell floors up to 65 % less cradle-to-gate carbon than flat slabs | Carbon motivation |
| 8 | Oval, Nuh, Castro e Costa et al. (2023), Structures | 10.1016/j.istruc.2023.01.063 | yes | Segmented concrete shell floor prototype; about 50 % less cradle-to-gate carbon than flat slabs | Carbon motivation |
| 9 | Feickert & Mueller (2023), Archit. Struct. Constr. | 10.1007/s44150-023-00101-z | yes | Shell foundations; about half to two-thirds less carbon than spread footings | Shape for carbon, beyond roofs |
| 10 | Leonardi, Ascione, Alraie et al. (2026), Mech. Res. Commun. | 10.1016/j.mechrescom.2026.104851 | yes | Force density form-finding + linear FE + FRP reinforcement design to minimise embodied carbon of RC shells; square and rectangular plans, 4 or 8 columns | Closest carbon study; gravity only (no seismic in abstract) [check] |
| 11 | Nuh, Oval, Orr (2025), Archit. Struct. Constr. | 10.1007/s44150-025-00126-6 | yes | Reconfigurable segmented fan shell floor; carbon saving vs conventional floors | Context |
| 12 | Hammood & Jawad (2023), Open Eng. | 10.1515/eng-2022-0417 | yes | 80 mm cylindrical concrete roof shells; small and midsized shells (span < 30 m) intrinsically earthquake resistant; high frequencies, elastic response | Supports the short-period, plateau-safe finding |
| 13 | Pérez Vega, Susarrey Huerta, Sánchez Sánchez (2026), Res. Eng. Struct. Mater. | 10.17515/resm2026-1812st0804rs | yes | Three force-density RC shells (4, 6, 8 supports); nonlinear multilayer model, imperfections, nonlinear buckling, time histories (Mexico City); imperfections cut ultimate capacity by 45.2 % to 22.1 % | **Closest seismic study.** Shows the gravity form-found RC shell under real seismic analysis; no carbon and no seismic-aware form. Also backs Limitation 1 |
| 14 | Caycedo Garcia, Siqueira, Vieira et al. (2024), Struct. Concr. | 10.1002/suco.202400324 | yes | Fragility of a free-form triangular RC shell; damage near supports; considerable damage likelier above 0.6 g PGA | Seismic behaviour of RC shells; support zones |
| 15 | Fenu, Congiu, Marano et al. (2020), Curved Layer. Struct. | 10.1515/cls-2020-0017 | yes | Shell-supported footbridges; form-finding including horizontal (earthquake) forces | Another lateral-load form-finding use |

## Gap (draft line for `00_core.md` section 1) [J]

Seismic-aware form-finding has been developed for compression-only shells and arches (rows 1-5), and the embodied carbon of reinforced concrete shells has been studied for gravity-designed forms (rows 6-11). The seismic response of form-found reinforced concrete shells has been analysed (rows 12-14). No study found here reports what seismic-aware form-finding costs or saves in embodied carbon for reinforced concrete shells sized to code checks. Gap type: evidence gap.

## Still to do (Syed)

1. Forward snowballing from rows 1 and 2 (Google Scholar "cited by"), and one more database (Scopus or Lens via library).
2. Open rows 10, 12 and 13 in full: they are the three papers a reviewer will compare us with.
3. Add the rows that go into the Introduction to `references.md` with pages.
