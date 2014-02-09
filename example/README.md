analysis_utils examples
=======================
Here you can find a collection of example/test programs that help to illustrate the features and common use cases of the analysis_utils package.

Setup
-----
You will need to ensure that the analysis_utils modules are accessible from your `PYTHONPATH`:
```
$ export PYTHONPATH=$PYTHONPATH:/path/to/analysis_utils/..
```

(note that the directory _containing_ your copy of analysis_utils is added to the path)

Datasets
--------
Some of these examples require input data in a specific ntuple format. You can get a copy of my test dataset at http://cshimmin.web.cern.ch/cshimmin/analysis_example_data.tgz (488Mb).

The test set contains 100,000 Monte Carlo events for each of several physics processes in pp collisions at sqrt(s)=8TeV:
 * `wgamma.root`: W+photon production; W decays leptonically
 * `wwllvv.root`: WW diboson production; both W's decay leptonically
 * `wzlllv.root`: WZ dibison production; both W leptonically, and Z decays to charged leptons
 * `zll.root`: Single Z boson production; Z decays to charged leptons
 * `zzllvv.root`: ZZ diboson production; one Z decays to charged leptons, the other to neutrinos

The event generation and detector simulation was performed with the [MadGraph + Pythia + Delphes3](http://madgraph.hep.uiuc.edu/) toolchain. In visible leptonic decays, the tau flavor is excluded.

Creating and writing NTuples/TTrees
-----------------------------------
This is dead-easy with the pytree module. Take a look at the source code and output of the following standalone example:
```
$ cd /path/to/analysis_utils/example
$ ./output_ntup.py
```
This program creates a ROOT file named "ntuple.root", which contains a TTree named "example". The TTree is populated with a few branches containing random values of various distributions and types.

Note also that one of the branches ("late_branch") contains the event number, but is only written _after_ the first ~20 events; pytree handles this seamlessly, backfilling the previous entries with 0. After 21 events, the two branches agree:
```
$ python
>>> import ROOT as r
>>> f = r.TFile("ntuple.root")
>>> ntup = f.Get("example")
>>> ntup.Scan('event_number:late_branch')
************************************
*    Row   * event_num * late_bran *
************************************
                ...
*       16 *        16 *         0 *
*       17 *        17 *         0 *
*       18 *        18 *         0 *
*       19 *        19 *         0 *
*       20 *        20 *         0 *
*       21 *        21 *        21 *
*       22 *        22 *        22 *
*       23 *        23 *        23 *
*       24 *        24 *        24 *
                ...
```

Variational analysis
--------------------
To run the example variational analysis, first download the test dataset to your example directory:
```
$ cd /path/to/analysis_utils/example
$ wget http://cshimmin.web.cern.ch/cshimmin/analysis_example_data.tgz
$ tar -xvzf analysis_example_data.tgz
```

Next, run the example on one (or more) of the MC files:
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

Note that for example, the "shift muon pt" systematic (which adds a constant value to all muon momenta) has considerably higher acceptance at the `hardmu` step, as one would expect. Note also that `n_hard_muons` was calculated 66942 times in total; this is because it was calculated 33471 times for the nominal cutflow, and additional 33471 for the shifted variation. It was not recalculated for any of the other variations.
