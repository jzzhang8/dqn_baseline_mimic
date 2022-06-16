
import numpy as np
import sys

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



for host_num in [16, 64, 128]:
	print()
	print("FatTree ", host_num)
	print()

	gt_file = "sim_tcp_ft{}/rtt.dat".format(host_num)
	pred_file = "mimic_tcp_ft{}/rtt.dat".format(host_num)

	gt_flow_data = parse_latency_file(gt_file)
	pred_flow_data = parse_latency_file(pred_file)

	gt_flow_avgRTT = {k: flow_avgRTT(v) for k, v in gt_flow_data.items()}
	gt_flow_p99RTT = {k: flow_p99RTT(v) for k, v in gt_flow_data.items()}

	pred_flow_avgRTT = {k: flow_avgRTT(v) for k, v in pred_flow_data.items()}
	pred_flow_p99RTT = {k: flow_p99RTT(v) for k, v in pred_flow_data.items()}


	print("avg RTT rho:")
	print(flow_corrcoef(gt_flow_avgRTT, pred_flow_avgRTT))

	print("p99 RTT rho:")
	print(flow_corrcoef(gt_flow_p99RTT, pred_flow_p99RTT))

	gt_flow_jitter = {k: flow_jitter(v) for k,v in gt_flow_data.items()}
	pred_flow_jitter = {k : flow_jitter(v) for k,v in pred_flow_data.items()}

	gt_flow_avgjitter = {k: flow_avgjitter(v) for k,v in gt_flow_jitter.items()}
	gt_flow_p99jitter = {k: flow_p99jitter(v) for k,v in gt_flow_jitter.items()}

	# print(gt_flow_avgjitter)
	# sys.exit(0)

	pred_flow_avgjitter = {k: flow_avgjitter(v) for k,v in pred_flow_jitter.items()}
	pred_flow_p99jitter = {k: flow_p99jitter(v) for k,v in pred_flow_jitter.items()}

	print("avg jitter rho:")
	print(flow_corrcoef(gt_flow_avgjitter, pred_flow_avgjitter))

	print("p99 jitter rho:")
	print(flow_corrcoef(gt_flow_p99jitter, pred_flow_p99jitter))


print()




