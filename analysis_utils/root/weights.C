#include <map>

std::map<int, double> lumi_weights;
double lumi_scale = 1.0;

void clear_lumi_weights() {
	lumi_weights.clear();
}

void set_lumi_weight(int dsid, double wt) {
	lumi_weights[dsid] = wt;
}

void set_lumi_scale(double scale) {
	lumi_scale = scale;
}

double get_lumi_weight(int dsid) {
	return lumi_scale*lumi_weights[dsid];
}

