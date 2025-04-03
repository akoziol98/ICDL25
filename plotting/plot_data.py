import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams.update({'font.size': 18})

def make_boxplots(df, x_var, y_var, times, x_ticks, colors):

    manual_timepoint_mdn = df.groupby(['id', x_var])[y_var].median().reset_index(drop=False)
    df_mdn = manual_timepoint_mdn[manual_timepoint_mdn[x_var].isin(times)].sort_values(by=x_var).reset_index(drop=False)

    fig = plt.figure(figsize=(12, 8))

    ax = sns.boxplot(
        data=df_mdn, x=x_var, y=y_var, hue=x_var,
        fliersize=0,
        boxprops=dict(alpha=.5),
        linewidth=1,
        notch=True,
        medianprops={"color": "grey", "linewidth": 2},
        hue_order=times,
        order=times,
        legend=0,
        dodge=False,
        palette=colors,
    )

    sns.swarmplot(
        data=df_mdn, x=x_var, y=y_var, hue=x_var,
        size=6,
        hue_order=times,
        order=times,
        edgecolor='black',
        linewidth=1,
        legend=0,
        palette = colors,
    )

    for label in times:
        x_pos = times.index(label)
        counts = df_mdn[x_var].value_counts()[label]
        plt.text(x_pos, df_mdn[y_var].min() - 1.3, f'n = {counts}', ha='center', va='bottom')
    locs, labels = plt.xticks()
    plt.xticks(locs, x_ticks)
    sns.despine(trim=True)
    plt.xlabel('')
    plt.ylabel('Duration of a manual sampling episode [s]', fontsize=22)
    plt.tight_layout()

    plt.show()