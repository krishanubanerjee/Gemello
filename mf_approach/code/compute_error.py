import os, glob
import pandas as pd
path = os.path.expanduser('~/collab/')


def compute_prediction(appliance, feature, k):
    files = glob.glob(path+'%s_%d_%s_*.csv' %(appliance, k, feature))
    out = {}
    for e in files:
        out[int(e.split('_')[-1][:-4])] = pd.read_csv(e,index_col=0, header=None).squeeze()
    return pd.DataFrame(out).T

def find_all_error():
    out = {}
    for appliance in ['wm','mw','oven','fridge','hvac','dw']:
        out[appliance]={}
        for feature in ['None', 'occ', 'area','rooms','occ_area','occ_rooms','area_rooms','occ_area_rooms']:
            out[appliance][feature]={}
            for k in range(1, 10):
                try:
                    print feature, k, appliance
                    pred_df = compute_prediction(appliance, feature, k)
                    gt_df = find_gt_df(appliance, pred_df)
                    out[appliance][feature][k] = find_error_df(gt_df, pred_df)
                except:
                    pass
    return out

def find_gt_df(appliance, pred_df):
    import pickle
    out_overall = pickle.load(open('/if6/nb2cz/git/Neighbourhood-NILM/data/input/all_regions.pkl', 'r'))
    region = "Austin"
    df = out_overall[region]
    gt_df = df[pred_df.columns].ix[pred_df.index]
    return gt_df


def find_error_df(gt_df, pred_df):
    return (pred_df-gt_df).abs().div(gt_df).mul(100)

def find_optimal(appliance):
    o = {}
    for feature in ['None', 'occ', 'area','rooms','occ_area','occ_rooms','area_rooms','occ_area_rooms']:
        o[feature]={}
        for k in range(1, 10):
            try:
                print feature, k
                pred_df = compute_prediction(appliance, feature, k)
                gt_df = find_gt_df(appliance, pred_df)
                o[feature][k] = find_error_df(gt_df, pred_df).median().mean()
                print o[feature][k], len(pred_df)
            except Exception, e:
                print e
    return pd.DataFrame(o)