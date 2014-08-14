import re
import matplotlib.pyplot as pyplot
import numpy as np
import argparse
from operator import add
from operator import sub

def make_patch_spines_invisible(ax):
  ax.set_frame_on(True)
  ax.patch.set_visible(False)
    #for sp in ax.spines.itervalues():
    #    sp.set_visible(False)
  for k in ax.spines.keys():
        ax.spines[k].set_visible(False)

parser = argparse.ArgumentParser()

parser.add_argument("-caseresult_dir", "--caseresult_dir", help="Result Dir")
parser.add_argument("-cases", "--cases", help="Cases")
parser.add_argument("-loc", "--loc", help="loc")
parser.add_argument("-title", "--title", help="title")
parser.add_argument("-plot_dir", "--plot_dir", help="plot directory")
parser.add_argument("-workload", "--workload", help="Workload type")

args = parser.parse_args()

workloadc_throughputs = []
number_bytes_written_master = []
number_bytes_written_slave1 = []
number_of_compaction = []
number_of_storeFiles = []
number_bytes_read_master=[]
number_bytes_read_slave1=[]
number_bytes_read=[]

cases = args.cases.split(':')

# collecting the load throughputs

for case in cases:
	if args.workload == 'load':
		ycsb_log = args.caseresult_dir + '/case' + case + '/load_1.dat'
	elif args.workload == 'workloada':
		ycsb_log = args.caseresult_dir + '/case' + case + '/workloada_1.dat'
	elif args.workload == 'workloadb':
		ycsb_log = args.caseresult_dir + '/case' + case + '/workloadb_1.dat'
	elif args.workload == 'workloadc':
		ycsb_log = args.caseresult_dir + '/case' + case + '/workloadc_1.dat'
	with open(ycsb_log, 'r') as file:
		for line in file:
			words = line.split()
			if len(words) == 3:
				if words[0] == '[OVERALL],' and words[1] == 'Throughput(ops/sec),':
					workloadc_throughputs.append(float(words[2]))

# collecting metrics
def metricstats(file_name, master, metric):
	metric_val_list=[]
	metric_end_val_list=[]
	metric_start_val_list=[]
	casecount=-1
	for case in cases:
		if master:
			filename = args.caseresult_dir +  '/case'+ case + '/master/' + file_name
		else:
			filename = args.caseresult_dir + '/case' + case + '/slave1/' + file_name
		casecount=casecount+1
		
		with open(filename, 'r') as file:
			for line in file:
				tokens = line.split()
				for token in tokens:
					words=token.strip(',').split('=')
					if re.match(metric, words[0]):
						metric_val = int(words[1])
			metric_val_list.append(metric_val)
	return(metric_val_list)

def compactionstats(file_name, master, metric):
	metric_val_list=[]
	casecount=-1
	for case in cases:
		if master:
			filename = args.caseresult_dir +  '/case'+ case + '/master/' + file_name
		else:
			filename = args.caseresult_dir + '/case' + case + '/slave1/' + file_name
		casecount=casecount+1
		
		with open(filename, 'r') as file:
			count=0
			for line in file:
				words=line.split()
				for word in words:
					kv = word.strip(',').split('=')
					p = re.compile('namespace_default_table_usertable_region_\w*_metric_numFilesCompactedCount')
					if p.match(kv[0]):
						count = count + int(kv[1])
			metric_val_list.append(count)
	return(metric_val_list)


number_bytes_written_master = metricstats( 'datanode-metrics.out', True, 'bytes_written')
number_bytes_written_slave1 = metricstats( 'datanode-metrics.out', False, 'bytes_written')
number_bytes_written = list(map(add, number_bytes_written_master, number_bytes_written_slave1))

number_bytes_read_master = metricstats('datanode-metrics.out', True, 'bytes_read')
number_bytes_read_slave1 = metricstats('datanode-metrics.out', False, 'bytes_read')
number_bytes_read = list(map(add, number_bytes_read_master, number_bytes_read_slave1))

number_storeFiles_master = metricstats('all.metrics', True, 'storeFileCount')
number_storeFiles_slave1 = metricstats('all.metrics', False, 'storeFileCount')
number_storeFiles = list(map(add, number_storeFiles_master, number_storeFiles_slave1))

# collecting the compaction counts

master_number_compaction= compactionstats('all.metrics', True, 'namespace_default_table_usertable_region_\w*_metric_numFilesCompactedCount')
slave_number_compaction= compactionstats('all.metrics', False, 'namespace_default_table_usertable_region_\w*_metric_numberFilesCompactedCount')
number_of_compaction = list(map(add, master_number_compaction, slave_number_compaction))

print(*workloadc_throughputs, sep=',', end='\n')
print(*number_bytes_written, sep=',', end='\n')
#print(*master_number_compaction, sep=',', end='\n')
print(*number_of_compaction, sep=',', end='\n')
print(*number_storeFiles, sep=',', end='\n')
print(*number_bytes_read, sep=',', end='\n')

fig, ax1 = pyplot.subplots()
fig.subplots_adjust(right=0.75)
p1, = ax1.plot([1,2,3], workloadc_throughputs, color='r', marker='o', label= args.workload +  " throughput", linewidth=1.5)
ax2 = ax1.twinx()
p2, = ax2.plot([1,2,3], number_bytes_written, color='b', marker='o', label="byte written", linewidth=1.5)
ax3 = ax1.twinx()
p3, = ax3.plot([1,2,3], number_of_compaction, color='g', marker='o', label="number of compaction", linewidth=1.5)
ax4 = ax1.twinx()
p4, = ax4.plot([1,2,3], number_storeFiles, color='k', marker='o', label="number of storeFiles")
ax5 = ax1.twinx()
p5, = ax5.plot([1,2,3], number_bytes_read, color='c', marker='o', label="byte read", linewidth=1.5)

ax3.spines["right"].set_position(("axes", 1.2))
ax4.spines["right"].set_position(("axes",  1.4)) 
ax5.spines["right"].set_position(("axes", 1.6))

make_patch_spines_invisible(ax3)
make_patch_spines_invisible(ax4)
make_patch_spines_invisible(ax5)

ax3.spines["right"].set_visible(True)
ax4.spines["right"].set_visible(True)
ax5.spines["right"].set_visible(True)

ax1.yaxis.label.set_color(p1.get_color())
ax2.yaxis.label.set_color(p2.get_color())
ax3.yaxis.label.set_color(p3.get_color())
ax4.yaxis.label.set_color(p4.get_color())
ax5.yaxis.label.set_color(p5.get_color())

ax1.set_ylabel('Throughput')
ax2.set_ylabel('byte written')
ax3.set_ylabel('number of compaction')
ax4.set_ylabel('number of storeFiles')
ax5.set_ylabel('byte read')

pyplot.xticks([1,2,3],['Default', 'Major Off', 'Major and Minor Off'], rotation=30)


tkw = dict(size=10, width=1.5)
ax1.tick_params(axis='y', colors=p1.get_color(), **tkw)
ax2.tick_params(axis='y', colors=p2.get_color(), **tkw)
ax3.tick_params(axis='y', colors=p3.get_color(), **tkw)
ax4.tick_params(axis='y', colors=p4.get_color(), **tkw)
ax5.tick_params(axis='y', colors=p5.get_color(), **tkw)
ax1.tick_params(axis='x', **tkw)


lines = [p1, p2, p3, p4, p5]
#lines = [p1, p2, p3,  p5]

ax1.legend(lines, [l.get_label() for l in lines])

pyplot.title(args.title)
pyplot.savefig(args.plot_dir + args.workload + '_' + args.cases, bbox_inches='tight', pad_inches=0.2)
#pyplot.show()