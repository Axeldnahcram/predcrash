import asyncio
from predcrash_utils.commons import get_asset_root, get_file_content
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import conda
import os
from logzero import logger as LOGGER

conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl

mpl.rcParams['font.size'] = 10.
mpl.rcParams['font.family'] = 'Comic Sans MS'
mpl.rcParams['axes.labelsize'] = 8.
mpl.rcParams['xtick.labelsize'] = 6.
mpl.rcParams['ytick.labelsize'] = 6.


class Map_france(object):
    def __init__(self, x1=-6., x2=10., y1=41, y2=51.5, figsize=(8, 8)):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.figsize = figsize

    @staticmethod
    async def make_data(datasets:list, years:list):
        cfg = await get_asset_root()
        list_directory = []
        for year in years:
            for dataset in datasets:
                list_directory.append(f'{dataset}_{year}')
        list_df = []
        for directory in list_directory:
            dir = await get_file_content(cfg, directory)
            df = pd.read_csv(dir, encoding='latin1', index_col='Num_Acc')
            list_df.append(df)
        df_total = pd.concat(list_df, axis=1)
        return df_total

    async def plot_data(self, datasets, years, start_date=None, end_date=None, delimitation='gadm36_FRA_2'):
        data = await Map_france.make_data(datasets, years)
        LOGGER.info(data.head())
        lat = data['lat'].values
        lat = [i / 100000 for i in lat]
        lon = data['long'].values
        lon = [i / 100000 for i in lon]
        fig = plt.figure(figsize=self.figsize)
        m = Basemap(resolution='i', projection='merc', llcrnrlat=self.y1, urcrnrlat=self.y2, llcrnrlon=self.x1, urcrnrlon=self.x2,
                    lat_ts=(self.x1 + self.x2) / 2)
        m.drawcountries(linewidth=0.5)
        m.drawcoastlines(linewidth=0.5)
        m.readshapefile(name="France", shapefile="/Users/amarchand/Downloads/gadm36_FRA_shp/{}".format(delimitation))
        m.shadedrelief()
        m.drawcoastlines(color='gray')
        m.drawcountries(color='gray')
        m.drawstates(color='gray')

        # 2. scatter city data, with color reflecting population
        # and size reflecting area
        m.scatter(lon, lat, latlon=True,
                  marker='D', color='m', alpha=0.01)
        plt.show()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    g = Map_france()
    df = loop.run_until_complete(g.plot_data(['caracteristiques'],[str(i) for i in range(2006,2007)]))
    LOGGER.info(df)





