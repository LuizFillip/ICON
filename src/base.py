import xarray as xr 
import numpy as np 
import datetime as dt
import GEO as gg 
import pandas as pd
import base as b 

cols_to_sel = ['longitude', 
        'latitude',
        'meridional_wind',
       'zonal_wind', 
        'local_solar_time', 
        'magnetic_zonal_wind', 
       'magnetic_meridional_wind', 
        'magnetic_field_aligned_wind', 
       'utc_time', 
       'orbit_number']


def load_data(file, height = 253.714098):
    
    ds = xr.open_dataset(file)
    
    time_msec = np.ma.filled(
        ds.variables['Epoch'][...], np.nan)
    
    ds['Epoch'] = np.array(
        [dt.datetime(1970, 1, 1) + 
         dt.timedelta(seconds=1e-3 * s) 
         for s in time_msec])
    
    
    for name in list(ds.data_vars.keys()):
        new_name = name.replace('ICON_L22_', '').lower()
        ds = ds.rename({name: new_name})
    
    ds = ds.rename({'ICON_L22_Altitude': 'level'})
    
    ds['longitude'] = ds['longitude'] - 180
    
    df = ds.sel(level = height, method = 'nearest')
    
    return df.to_dataframe()

def find_orbit(df, lon_start = -60, lon_end = -30):
    sel_orbit = df.loc[
    ((df['longitude'] > lon_start) & 
     (df['longitude'] < lon_end) )]

    return sel_orbit['orbit_number'].unique()


def filter_by_orbit(df, orbit):
    ds1 = df.loc[df['orbit_number'] == orbit]
    
    ds1.index = pd.to_datetime(ds1.index.get_level_values(0))
    
    ds1.index = ds1.index.map(
        lambda x: dt.datetime(
            x.year,
            x.month, 
            x.day, 
            x.hour, 
            x.minute, 
            x.second)
        )
    
    return ds1[cols_to_sel]


def longitudinal_sector_time(ds1):
    
    sel_time = ds1.loc[
        ((ds1['longitude'] > -50) & 
         (ds1['longitude'] < -40))].index
    
    return sel_time[0], sel_time[-1]

def plot_orbits(
        axes, 
        ax_map, 
        df, 
        orbit, 
        color
        ):
    
    args = dict(
            ncol = 3, 
            loc = "upper center", 
            bbox_to_anchor = (0.5, 1.25), 
            columnspacing = 0.2
        )
    
    ds1 = filter_by_orbit(df, orbit)
    
    
    start, end = longitudinal_sector_time(ds1)
    orbit = int(orbit)
    
    ax_map.axvline(-50)
    ax_map.axvline(-40)
    ax_map.scatter(
        ds1['longitude'], 
        ds1['latitude'],
        c = color, label = orbit)
    
    ax_map.legend(title = 'Orbits',**args )
        

    axes[1].set(ylabel = 'Meridional wind (m/s)')
    
    axes[0].set(
        title = 'Red line Mighti vector wind',
        xticklabels = [], 
        ylabel = 'Zonal (m/s)')
    
    vlz = ['zonal_wind', 'meridional_wind']
    for i, ax in enumerate(axes):
        
        ax.plot(
            ds1[vlz[i]], 
            color = color, label = orbit)
        
        ax.axhline(0, linestyle = '--')
        
        ax.axvspan(
            start, end, 
            ymin = 0, ymax = 1,
            alpha = 0.2, 
            color = 'gray'
            )
        
    axes[1].legend(**args)
    




def plot_orbits_over_map(df, orbits):
    
    lat_lims = dict(min = -20, max = 40, stp = 10)
    
    fig, ax_map, axes = b.multi_layout(
        hspace = 0.2, 
        nrows = 2)
    
    gg.map_attrs(
            ax_map, 2022, 
            lat_lims = lat_lims,
            grid = False,
            degress = None
            )
    
    plot_orbits(axes, ax_map, df, orbits[3], color = 'blue')
    
    plot_orbits(axes, ax_map, df, orbits[4], color = 'green')
    
    plot_orbits(axes, ax_map, df, orbits[5], color = 'magenta')
    
    b.format_time_axes(axes[-1])
    
    return fig 


file = 'ICON/icon_l2-2_mighti_vector-wind-red_20220725_v05r000.nc'

df = load_data(file, height = 253.714098)

orbits = find_orbit(df)

fig = plot_orbits_over_map(df, orbits)


FigureName = 'ICON_winds_mesuarementes'


# fig.savefig(
#       b.LATEX(FigureName, folder = 'paper2'),
#       dpi = 300
#       )
