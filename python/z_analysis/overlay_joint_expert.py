import pandas as pd
import datashader as ds
import datashader.transfer_functions as tf
from datashader.utils import export_image


def plot_joint_and_expert_overlap(joint_catalog, expert_catalog):

    joint_to_plot = joint_catalog[['ra', 'dec']].to_pandas()
    joint_to_plot['catalog'] = 'joint'
    expert_to_plot = expert_catalog[['_ra', '_de']].to_pandas()
    expert_to_plot.rename(columns={'_ra': 'ra', '_de': 'dec'}, inplace=True)
    expert_to_plot['catalog'] = 'expert'

    df_to_plot = pd.concat([joint_to_plot] + [expert_to_plot for n in range(int(len(joint_to_plot)/len(expert_to_plot)))])
    df_to_plot['catalog'] = df_to_plot['catalog'].astype('category')

    canvas = ds.Canvas(plot_width=300, plot_height=300)
    aggc = canvas.points(df_to_plot, 'ra', 'dec', ds.count_cat('catalog'))
    img = tf.shade(aggc)
    export_image(img, 'locations_datashader_overlaid')
