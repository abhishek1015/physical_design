import re
import matplotlib.pyplot as pyplot
import numpy as np
import argparse
from operator import add

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

args = parser.parse_args()

workloadc_throughputs=[]
workloadc_avg_latency=[]
workloadc_max_latency=[]
workloadc_min_latency=[]

cases = args.cases.split(':')

# collecting the workloadc throughputs
for case in cases:
	with open(args.caseresult_dir + '/case' + case + '/workloadc_1.dat', 'r') as file:
		for line in file:
			words = line.split()
			if len(words) == 3:
				if words[0] == '[OVERALL],' and words[1] == 'Throughput(ops/sec),':
					workloadc_throughputs.append(float(words[2]))
				if words[0] == '[UPDATE],' and words[1] == 'AverageLatency(us),':
					workloadc_avg_latency.append(float(words[2]))
				if words[0] == '[UPDATE],' and words[1] == 'MinLatency(us),':
					workloadc_min_latency.append(float(words[2]))
				if words[0] == '[UPDATE],' and words[1] == 'MaxLatency(us),':
					workloadc_max_latency.append(float(words[2]))

print(*workloadc_throughputs, sep=',', end='\n')
print(*workloadc_avg_latency, sep=',', end='\n')
print(*workloadc_max_latency, sep=',', end='\n')
print(*workloadc_min_latency, sep=',', end='\n')

'''def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.itervalues():
        sp.set_visible(False)
'''
fig, ax1 = pyplot.subplots()
fig.subplots_adjust(right=0.75)
p1, = ax1.plot([1,2,3], workloadc_throughputs, color='r', marker='o', label="workloadc throughput", linewidth=1.5)
ax2 = ax1.twinx()
p2, = ax2.plot([1,2,3], workloadc_avg_latency, color='b', marker='o', label="workloadc average latency", linewidth=1.5)
ax3 = ax1.twinx()
p3, = ax3.plot([1,2,3], workloadc_min_latency, color='g', marker='o', label="workloadc min latency", linewidth=1.5)
ax4 = ax1.twinx()
p4, = ax4.plot([1,2,3], workloadc_max_latency, color='k', marker='o', label="workloadc max latency", linewidth=1.5)

ax3.spines["right"].set_position(("axes", 1.2))
ax4.spines["right"].set_position(("axes",  1.4)) 

make_patch_spines_invisible(ax3)
make_patch_spines_invisible(ax4)

ax3.spines["right"].set_visible(True)
ax4.spines["right"].set_visible(True)

ax1.yaxis.label.set_color(p1.get_color())
ax2.yaxis.label.set_color(p2.get_color())
ax3.yaxis.label.set_color(p3.get_color())
ax4.yaxis.label.set_color(p4.get_color())

ax1.set_ylabel('Throughput')
ax2.set_ylabel('Average latency')
ax3.set_ylabel('Min latency')
ax4.set_ylabel('Max latency')

pyplot.xticks([1,2,3],['Default', 'Major Off', 'Major and Minor Off'], rotation=30)


tkw = dict(size=10, width=1.5)
ax1.tick_params(axis='y', colors=p1.get_color(), **tkw)
ax2.tick_params(axis='y', colors=p2.get_color(), **tkw)
ax3.tick_params(axis='y', colors=p3.get_color(), **tkw)
ax4.tick_params(axis='y', colors=p4.get_color(), **tkw)
ax1.tick_params(axis='x', **tkw)


lines = [p1, p2, p3, p4]

ax1.legend(lines, [l.get_label() for l in lines])

pyplot.savefig('workloadc_latency_' + args.cases, bbox_inches='tight', pad_inches=0.2)
#pyplot.show()