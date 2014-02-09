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

