analysis_utils example
===

You can get a test dataset at http://cshimmin.web.cern.ch/cshimmin/analysis_example_data.tgz (488Mb).

The test set contains 100,000 Monte Carlo events for each of several physics processes in pp collisions at sqrt(s)=8TeV:
 * `wgamma.root`: W+photon production; W decays leptonically
 * `wwllvv.root`: WW diboson production; both W's decay leptonically
 * `wzlllv.root`: WZ dibison production; both W leptonically, and Z decays to charged leptons
 * `zll.root`: Single Z boson production; Z decays to charged leptons
 * `zzllvv.root`: ZZ diboson production; one Z decays to charged leptons, the other to neutrinos

The event generation and detector simulation was performed with the [MadGraph + Pythia + Delphes3](http://madgraph.hep.uiuc.edu/) toolchain. In visible leptonic decays, the tau flavor is excluded.

Variational analysis
---
To run the example variational analysis, first download the test dataset to your example directory:
```
$ cd /path/to/analysis_utils/example
$ wget http://cshimmin.web.cern.ch/cshimmin/analysis_example_data.tgz
$ tar -xvzf analysis_example_data.tgz
```

Next, ensure that the analysis_utils modules are accessible from your `PYTHONPATH`:
```
$ export PYTHONPATH=$PYTHONPATH:/path/to/analysis_utils/..
```

Finally, run the example on one (or more) of the MC files:
```
$ ./example/variation_example.py analysis_example_data/zzllvv.root
```

When the analysis has finished running, the program will print a summary:
```
==== Cutflow: shift muon pt ====
2muons:	33471
hardmu:	29771
met80:	7878

==== Cutflow: smeared met ====
2muons:	33471
hardmu:	14170
met80:	7534

==== Cutflow: jets CR ====
2muons:	33471
hardmu:	14170
met80:	6917
3jets:	2317

==== Cutflow: nominal ====
2muons:	33471
hardmu:	14170
met80:	6917

>>>> Calculation stats: <<<<
n_muons:	100000
n_jets:	6917
n_hard_muons:	66942
met_smeared:	43941
```

Note that, for example, the "shift muon pt" systematic has considerably higher acceptance at the `hardmu` step, as one would expect. Note also that `n_hard_muons` was calculated 66942 times in total; this is because it was calculated 33471 times for the nominal cutflow, and additional 33471 for the shifted variation. It was not recalculated for any of the other variations.
