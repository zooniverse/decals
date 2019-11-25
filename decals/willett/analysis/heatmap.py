# Adapted from https://stanford.edu/~mwaskom/software/seaborn/examples/network_correlations.html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set(context="paper", font="monospace")

# Load the datset of correlations between cortical brain networks
df = pd.read_csv("/Users/willettk/Astronomy/Research/GalaxyZoo/gz_reduction_sandbox/data/full_decals/decals_network.csv",header=[0,1,2],index_col=0)

used_types = ["frac",]
used_columns = (df.columns.get_level_values("answer_type").isin(used_types))

df2 = df.loc[:, used_columns]

corrmat = df2.corr()

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(12, 9))

# Draw the heatmap using seaborn
sns.heatmap(corrmat, vmax=1.0, square=True)

plt.xticks(rotation=90) 
plt.yticks(rotation=0) 
plt.xlabel('')
plt.ylabel('')
plt.title('GZ-DECaLS')

# Use matplotlib directly to emphasize known networks (ie, tasks)
task_numbers = corrmat.columns.get_level_values("task_no")
for i, task_no in enumerate(task_numbers):
    if i and task_no != task_numbers[i - 1]:
        ax.axhline(len(task_numbers) - i, c="k")
        ax.axvline(i, c="k")

f.tight_layout()

plt.savefig('../plots/heatmap.pdf')
