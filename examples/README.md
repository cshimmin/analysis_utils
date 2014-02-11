analysis_utils examples
=======================
Here you can find a collection of example/test programs that help to illustrate the features and common use cases of the analysis_utils package.

Setup
-----
You will need to ensure that the analysis_utils modules are accessible from your `PYTHONPATH`:
```
$ git clone https://github.com/cshimmin/analysis_utils.git
$ export PYTHONPATH=$PYTHONPATH:`pwd`/analysis_utils
$ cd analysis_utils/examples
```
The following examples use the argparse package; if you're using a version of python earlier that 2.7, please make sure this package is installed.

Creating and writing NTuples/TTrees
-----------------------------------
This is dead-easy with the pytree module.
Take a look at the source code and output of the following standalone example:
```
$ ./output_ntuple.py
```
This program creates a ROOT file named "ntuple.root", which contains a TTree named "example".
The TTree is populated with a few branches containing random values of various distributions and types.

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
To run the example variational analysis, first download the test dataset (_see below_) to your example directory:
```
$ curl http://cshimmin.web.cern.ch/cshimmin/analysis_example_data.tgz -o analysis_example_data.tgz
$ tar -xvzf analysis_example_data.tgz
```

Next, run the example on one (or more) of the MC files:
```
$ ./variations.py analysis_example_data/zzllvv.root
```

When the analysis has finished running, the program will print a summary:
```
==== Cutflow: smeared muons ====
2muons: 16767
hardmu: 13237
met80:  3904


==== Cutflow: smeared met ====
2muons: 16767
hardmu: 13841
met80:  4607


==== Cutflow: jets CR ====
2muons: 16767
hardmu: 13841
met80:  3946
3jets:  1347


==== Cutflow: nominal ====
2muons: 16767
hardmu: 13841
met80:  3946


>>>> Calculation stats: <<<<
all_jets:   3946
all_muons:  100000
z_boson:    7850
hard_muons: 33534
met_smeared:    28365
```
The "smear muons" systematic randomly shifts the muon pT from a gaussian with a width about ~20%.
Note that the acceptance at the `hardmu` step is slightly affected by this variation.
Note also that `z_boson` was calculated 7850 times in total.
This is because it was calculated 3946 times for the nominal cutflow (after the MET cut), and an additional 3904 for the shifted variation.
It was not recalculated for any of the other variations.

Datasets
--------
Some of these examples require input data in a specific ntuple format.
You can get a copy of my test dataset at http://cshimmin.web.cern.ch/cshimmin/analysis_example_data.tgz (488Mb).

The test set contains 100,000 Monte Carlo events for each of several physics processes in pp collisions at sqrt(s)=8TeV:
 * `wgamma.root`: W+photon production; W decays leptonically
 * `wwllvv.root`: WW diboson production; both W's decay leptonically
 * `wzlllv.root`: WZ dibison production; both W leptonically, and Z decays to charged leptons
 * `zll.root`: Single Z boson production; Z decays to charged leptons
 * `zzllvv.root`: ZZ diboson production; one Z decays to charged leptons, the other to neutrinos

The event generation and detector simulation was performed with the [MadGraph + Pythia + Delphes3](http://madgraph.hep.uiuc.edu/) toolchain.
Invisible leptonic decays, the tau flavor is excluded.
