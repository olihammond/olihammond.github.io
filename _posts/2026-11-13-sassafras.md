---
layout: post
title: "Sassafras: a new easy tool for small-angle scattering"
date: 2026-11-13 15:00:00+0100
description: Lightweight browser-based software for fitting your SANS or SAXS data.
tags: sans saxs software sasview
categories: software
---

[Sassafras](https://github.com/SasView/sassafras)(Small Angle Scattering Structure- And Form-factor Rapid ASsessment) is my attempt at a new and very lightweight tool for rapid chi-by-eye and fitting of small-angle data. It is a small Python package that opens a page in your browser, where you drop in reduced 1D data, choose a form factor (and a structure factor if you need one), and drag sliders while the model, residuals and χ² update live. Fundamentally it works in the same way as SasView, but the design philosophy is quite different, and I have found it to be faster, lighter, and more intuitive than the legacy GUI for basic operations.

## sassafras has some cute features:

- **Guess.** The `Guess` button interpolates and compares your curve against ([https://doi.org/10.5281/zenodo.24080759](a simulated library), derived from the original [https://doi.org/10.1039/d3dd00225j](SAS-55M-20k set of Yildirim, Doutch and Cole)) by adding 'strong' and 'weak' HS and RMSA S(Q) to a subset of structures. `Guess` proposes a ranked list of models with starting values. I have found this to work surprisingly well, but it should be used with caution, particularly for datasets which are noisy or which contain multiple P(Q) contributions. 
- **Sliders.** It sounds trite, but these are incredibly helpful for exploring form factors and your fits. 
- **Simultaneous constrained fits with multiple P(Q).** This is a workflow that is possible, but a bit annoying, in SasView. In sassafras you can load multiple datasets (including a whole folder) and enable the `Fit` and `Multi` buttons to model them using simultaneous constraints. Freely set parameters per dataset, and choose whether they are shared, or individually fitted, or fixed. This supports quite complicated modelling too: with `Mix` you can enable up to 4 P(Q), the first of which can also be P(Q) * S(Q).
- **Export to IQuana notebook.** Continue your fitting by directly generating notebooks, rather than in a GUI. We envisage IQuana to be a very useful tool for open scientific publishing, which enables subsequent users to simply follow a jupyter notebook to reproduce your fitting results. Obviously, this also works identically to the much beloved SasView GUI, under the hood. 
- **Themes.** You can pick light/dark mode (obviously), and more importantly a series of gen-Z friendly colour schemes. 


```bash
pip install sassafras
sassafras                                   # or: python -m sassafras

sassafras run_1234.xml run_1235.h5 -m core_shell_sphere -s hardsphere # launch with extra commands
sassafras /data/reduced/                    # every readable file in a folder (≤ 50)
```

## Where it fits

Sassafras is not intended to be a replacement for SasView. I want it to be a tool that users reach for in their first five minutes with a new curve, on a beamline, or at the desk. It naturally hands over to scripting with IQuana, or whatever other analysis, once you know what you are doing. Since version 0.5 it lives under the [SasView organisation on GitHub](https://github.com/SasView/sassafras) alongside sasmodels, IQuana and sasdata, and it is BSD licensed.

It is still in beta (version 0.7.0 at the time of writing), so expect rough edges. Bug reports, feature requests and pull requests are super welcome on GitHub, and if it is useful in your work, in addition to SasView and sasmodels, it can be cited through its [Zenodo DOI](https://doi.org/10.5281/zenodo.24041504).
