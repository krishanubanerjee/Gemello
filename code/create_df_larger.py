__author__ = 'nipunbatra'

import numpy as np
import pandas as pd
import  pickle
APPLIANCES=["dw",'hvac','fridge','wm','mw','ec','wh','oven']
def read_df_larger():
    out_overall = pickle.load(open('../data/input/all_regions.pkl','r'))



    df=out_overall['Austin'].query('full_agg_available>0 & md_available>0')
    dfc = df.copy()
    features_individual = {'fraction':["fraction_%d" % i for i in range(1, 25)],
                           'area': 'area',
                           'autocorr':'autocorr',
                           'month': ["aggregate_%d" % i for i in range(1, 13)],
                           'occupants': 'total_occupants',
                           'rooms': 'num_rooms',
                           'seasonal_12':['stdev_seasonal_12','max_seasonal_12'],
                           'trend_12':['stdev_trend_12','max_trend_12'],

                           'seasonal_daily':['stdev_seasonal_daily','max_seasonal_daily'],
                           'trend_daily':['stdev_trend_daily','max_trend_daily'],
                           'seasonal_weekly':['stdev_seasonal_weekly','max_seasonal_weekly'],
                           'trend_weekly':['stdev_trend_weekly','max_trend_weekly'],
                           'cluster_big':'cluster_big',
                           'cluster_small':'cluster_small',
                           'diff':['lt_500','bet_500_1000','gt_1000'],
                           'temp':'temperature_corr',
                           'week':["fraction_%d" % i for i in range(1, 8)],
                           #'disag_fridge':'disag_fridge'}
                           'mins_hvac':'mins_hvac',
                           'month_extract':['variance','ratio_min_max', 'difference_min_max',
                                            'ratio_difference_min_max']}

    all_homes = {}
    for appliance in APPLIANCES:
        all_homes[appliance] = df[['%s_%d' %(appliance, month) for month in range(1,13)]].dropna().index


    appliance_min=None
    national_average = None

    return df, dfc, all_homes, appliance_min, national_average