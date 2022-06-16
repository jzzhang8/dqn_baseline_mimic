
import numpy as np
import sys

from scipy.stats import wasserstein_distance as w1

from matplotlib import pyplot as plt

def parse_latency_file(file):
	with open(file, "r") as fp:
		lines = fp.readlines()

	flow_data = dict()

	for line in lines:
		l = line.strip()
		if l == "":
			continue
		else:
			l_split = l.split()
			src, dst, ackno, lat = l_split[0], l_split[1], l_split[2], l_split[3]
			ackno = int(ackno)
			lat = float(lat)
			
			# if src not in flow_data:
			# 	flow_data[src] = dict()
			# if dst not in flow_data[src]:
			# 	flow_data[src][dst] = []
			# flow_data[src][dst].append([ackno, lat])

			if (src, dst) not in flow_data:
				flow_data[(src, dst)] = []
			flow_data[(src, dst)].append([ackno, lat]) 

	# flow_data format:
	# flow_data[(src, dst)] = [[ackno1, latency1], ..., [acknoN, latencyN]]
	# each (src, dst) pair determines a flow
	return flow_data


def flow_avgRTT(flow_list):
	lat_list = [x[-1] for x in flow_list]
	return sum(lat_list) / len(lat_list) 

def flow_p99RTT(flow_list):
	lat_list = [x[-1] for x in flow_list]
	sorted_lat_list = sorted(lat_list)
	return sorted_lat_list[int(0.99 * (len(sorted_lat_list)-1) )]

def flow_avgjitter(flow_list):
	return sum(flow_list) / len(flow_list)

def flow_p99jitter(flow_list):
	sorted_jitter_list = sorted(flow_list)
	return sorted_jitter_list[ int( 0.99 * (len(sorted_jitter_list)-1) ) ]

def flow_jitter(flow_list):
	flow_list = sorted(flow_list, key = lambda x: x[0])
	# print(
	# 	all(flow_list[idx][0] < flow_list[idx+1][0] for idx in range(len(flow_list)-1))
	# 	) # check ascending
	return [flow_list[idx+1][-1] - flow_list[idx][-1] for idx in range(len(flow_list)-1)]


def flow_corrcoef(flow1, flow2):
	keys = list( set(flow1.keys()) & set(flow2.keys()) )
	print("intersection =", len(keys), "; data1, data2 = ", len(flow1), "," ,len(flow2))
	return np.corrcoef(
    [flow1[x] for x in keys],
    [flow2[x] for x in keys])[0, 1]


def plot_cdf(data, data2 = None, label="cdf", label2 = None, savename = "cdf"):
	savename = savename[:savename.rfind(".jpg") if ".jpg" in savename else None]

	count, bins_count = np.histogram(data, bins=100)
	pdf = count / sum(count)
	cdf = np.cumsum(pdf)
	plt.plot(bins_count[1:], cdf, label=label)

	if data2:
		count, bins_count = np.histogram(data2, bins=100)
		pdf = count / sum(count)
		cdf = np.cumsum(pdf)
		plt.plot(bins_count[1:], cdf, label=label2 if label2 else "label2")

	plt.legend()
	plt.savefig("plot/{}.jpg".format(savename))
	plt.clf()


for host_num in [16, 64, 128]:
	print()
	print("FatTree ", host_num)
	print()

	gt_file = "sim_tcp_ft{}/rtt.dat".format(host_num)
	pred_file = "mimic_tcp_ft{}/rtt.dat".format(host_num)

	gt_flow_data = parse_latency_file(gt_file)
	pred_flow_data = parse_latency_file(pred_file)

	gt_latency = []
	for one_flow_data in gt_flow_data.values():
		gt_latency.extend([x[-1] for x in one_flow_data])

	pred_latency = []
	for one_flow_data in pred_flow_data.values():
		pred_latency.extend([x[-1] for x in one_flow_data])

	print("gt latency num:", len(gt_latency) )
	print("pred latency num:", len(pred_latency) )

	print("Normalized W1 value as:")
	print(w1(gt_latency, pred_latency) / w1([0 for _ in range(len(gt_latency))], gt_latency))

	plot_cdf(gt_latency, pred_latency, label="GT", label2="Pred", savename="fattree{}_cdf".format(host_num))


	# sys.exit(0)

print()




