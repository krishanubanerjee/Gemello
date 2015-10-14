__author__ = 'nipunbatra'

import pandas as pd
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor

st = pd.HDFStore(os.path.expanduser("~/Downloads/wiki-temp.h5"))
o = {}

all_keys = st.keys()
for k in all_keys:
    try:
        o[k] = len(st[k]['2013'])
    except:
        pass

s = pd.Series(o)
homes_keys = s[s>505478].index.tolist()
homes_int = map(lambda x: int(x[1:]),homes_keys)


survey_df = pd.read_csv(os.path.expanduser("~/git/nilm-actionable/data/total/survey_2013.csv"))

common_homes = np.intersect1d(survey_df.dataid.values, homes_int)

common_homes_keys = map(lambda x: "/"+str(x), common_homes)

out = {}
for key, int_key in zip(common_homes_keys, common_homes):
    print key
    df = st[key]['2013']
    df_res = df.resample('1M',how="sum")
    df_res_kwh = df_res.mul(0.000017)
    hvac = np.array([np.NaN]*12)
    fridge = np.array([np.NaN]*12)
    wm = np.array([np.NaN]*12)




    if "refrigerator1" in df_res_kwh.columns:
        fridge = df_res_kwh['refrigerator1']


    if 'air1' in df_res_kwh.columns:
        temp = df_res_kwh['air1']
    if 'air2' in df_res_kwh.columns:
        temp = temp + df_res_kwh['air2']

    aggregate = df_res_kwh["use"].values

    hvac = temp

    if "clotheswasher1" in df_res_kwh.columns:
        wm = df_res_kwh['clotheswasher1']
    out[int_key] = np.hstack([aggregate, hvac, fridge, wm])


df = pd.DataFrame(out).T
df.columns = np.hstack([["aggregate_%d" %i for i in range(1,13)],
           ["hvac_%d" %i for i in range(1,13)],
           ["fridge_%d" %i for i in range(1,13)],
           ["wm_%d" %i for i in range(1,13)]
           ])

def create_predictions(appliance="hvac"):
    out_month = {}
    gt_month = {}
    overall_dfs = {}
    for k in range(1, 10):
        out_month[k] = {}
        gt_month[k] = {}
        overall_dfs[k] = {}


        for month in ["%s_%d" %(appliance,i) for i in range(1,13)]:
            #print month
            y = df[month]
            y2 = y.dropna()
            y3 = y2[y2>0].dropna()
            df3 = df.ix[y3.index].dropna()
            y3 = y3.ix[df3.index]
            from sklearn.cross_validation import LeaveOneOut
            clf = KNeighborsRegressor(n_neighbors=k)
            loo = LeaveOneOut(len(df3))
            out_pred = []
            for train, test in loo:
                clf.fit(df3.values[train], y3.values[train])
                out_pred.append(clf.predict(df3.values[test]))

            out_pred = np.hstack(out_pred)
            out_month[k][month] = out_pred
            gt_month[k][month] = y3.values
            overall_dfs[k][month] = pd.DataFrame({"gt":y3.values, "pred":out_pred,
                                                  "gt_total":df3["aggregate_"+str(i-1)].values}, index=y3.index)
    return overall_dfs

def percentage_error(gt, pred):
    return 100*np.abs(gt-pred)/(pred)



def compute_metrics(df):
    temp = df[df.gt_total>0.0]
    temp = temp[temp.gt>temp.gt_total]
    return {"Percentage error in appliance energy":np.median(percentage_error(df["gt"], df["pred"])),
            "Percentage error in fraction energy":((temp['pred']/temp['gt_total'])-((temp['gt']/temp['gt_total']))).abs().mul(100).median()}


from common_functions import *

hvac_fhmm_pred = pd.read_csv("../fhmm_disag.csv", index_col=0)
fridge_fhmm_pred = pd.read_csv("../fridge_fhmm.csv", index_col=0)


"""
FRIDGE
"""

for appliance in ["fridge"]:
    overall_dfs = create_predictions(appliance)
    results = {}
    for month in range(1, 13):
        results[month] = compute_metrics(overall_dfs[4][appliance+"_"+str(month)].ix[fridge_fhmm_pred.index])
    result_df = pd.DataFrame(results).T

results_fridge = {}
for month in range(1,13):
    fhmm_df = pd.DataFrame({"gt":overall_dfs[4]["fridge_"+str(month)].ix[fridge_fhmm_pred.index]["gt"],
                            "pred":fridge_fhmm_pred.values[:,month-1],
                            "gt_total":overall_dfs[4]["fridge_"+str(month)].ix[fridge_fhmm_pred.index]["gt_total"]})
    results_fridge[month] = compute_metrics(fhmm_df)

percentage_fridge = pd.DataFrame({"FHMM":pd.DataFrame(results_fridge).T['Percentage error in appliance energy'],
                                  "Neighbourhood NILM":result_df['Percentage error in appliance energy']})

percentage_pie_fridge = pd.DataFrame({"FHMM":pd.DataFrame(results_fridge).T['Percentage error in fraction energy'],
                                  "Neighbourhood NILM":result_df['Percentage error in fraction energy']})


latexify(columns=2, fig_height=3)
plt.clf()
ax = percentage_fridge.plot(kind="bar", rot=0)
format_axes(ax)
plt.ylabel("Percentage error in fridge energy\n(Lower is better)")
plt.xlabel("Month")
plt.tight_layout()
plt.savefig("../figures/fridge_percentage_energy.pdf", bbox_inches="tight")



latexify(columns=2, fig_height=3)
plt.clf()
ax = percentage_pie_fridge.plot(kind="bar", rot=0)
format_axes(ax)
plt.ylabel("Percentage error in fridge proportion\n(Lower is better)")
plt.xlabel("Month")
plt.tight_layout()
plt.savefig("../figures/fridge_percentage_pie.pdf", bbox_inches="tight")
"""
HVAC
"""


for appliance in ["hvac"]:
    overall_dfs = create_predictions(appliance)
    results = {}
    for month in range(1, 13):
        results[month] = compute_metrics(overall_dfs[4][appliance+"_"+str(month)].ix[fridge_fhmm_pred.index])
    result_df = pd.DataFrame(results).T

results_hvac= {}
for month in range(1,13):
    fhmm_df = pd.DataFrame({"gt":overall_dfs[4]["hvac_"+str(month)].ix[hvac_fhmm_pred.index]["gt"],
                            "pred":hvac_fhmm_pred.values[:,month-1],
                            "gt_total":overall_dfs[4]["hvac_"+str(month)].ix[hvac_fhmm_pred.index]["gt_total"]})
    results_hvac[month] = compute_metrics(fhmm_df)

percentage_hvac = pd.DataFrame({"FHMM":pd.DataFrame(results_hvac).T['Percentage error in appliance energy'],
                                  "Neighbourhood NILM":result_df['Percentage error in appliance energy']})

percentage_pie_hvac = pd.DataFrame({"FHMM":pd.DataFrame(results_hvac).T['Percentage error in fraction energy'],
                                  "Neighbourhood NILM":result_df['Percentage error in fraction energy']})

import seaborn as sns
sns.reset_orig()
latexify(columns=1)
plt.clf()
ax = percentage_hvac.ix[5:10].plot(kind="bar", rot=0)
format_axes(ax)
plt.ylabel("Percentage error in HVAC energy\n(Lower is better)")
plt.xlabel("Month")
plt.tight_layout()
plt.savefig("../figures/hvac_percentage_energy.pdf", bbox_inches="tight")



latexify(columns=2, fig_height=3)
plt.clf()
ax = percentage_pie_hvac.plot(kind="bar", rot=0)
format_axes(ax)
plt.ylabel("Percentage error in HVAC proportion\n(Lower is better)")
plt.xlabel("Month")
plt.tight_layout()
plt.savefig("../figures/hvac_percentage_pie.pdf", bbox_inches="tight")



"""
##################
CODE for sensitivity analysis
##################
"""

sensitivity_k_hvac={}
appliance ="hvac"
overall_dfs = create_predictions(appliance)
results = {}
for k in range(1, 7):
    for month in range(1, 13):
        results[month] = compute_metrics(overall_dfs[k][appliance+"_"+str(month)].ix[hvac_fhmm_pred.index])
    sensitivity_k_hvac[k] = pd.DataFrame(results).T['Percentage error in appliance energy']
hvac_sensitivity_df = pd.DataFrame(sensitivity_k_hvac).ix[5:10]

sns.reset_orig()
latexify(columns=1)
plt.clf()
ax = hvac_sensitivity_df.plot(kind="bar", rot=0)
ax.legend(loc='upper center',title=r'$k$'' neighbours', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True)
format_axes(plt.gca())
plt.xlabel("Month")
plt.ylabel("Percentage error in HVAC energy\n(Lower is better)")
plt.tight_layout()
plt.savefig("../figures/hvac_sensitivity.pdf", bbox_inches="tight")


sensitivity_k_fridge={}
appliance ="fridge"
overall_dfs = create_predictions(appliance)
results = {}
for k in range(1, 7):
    for month in range(1, 13):
        results[month] = compute_metrics(overall_dfs[k][appliance+"_"+str(month)].ix[fridge_fhmm_pred.index])
    sensitivity_k_fridge[k] = pd.DataFrame(results).T['Percentage error in appliance energy']
fridge_sensitivity_df = pd.DataFrame(sensitivity_k_fridge)

sns.reset_orig()
latexify(columns=2, fig_height=3)
plt.clf()
ax = fridge_sensitivity_df.plot(kind="bar", rot=0)
ax.legend(loc='upper center',title=r'$k$'' neighbours', bbox_to_anchor=(0.5, 1.05),
          ncol=6, fancybox=True, shadow=True)
format_axes(plt.gca())
plt.xlabel("Month")
plt.ylabel("Percentage error in fridge energy\n(Lower is better)")
plt.tight_layout()
plt.savefig("../figures/fridge_sensitivity.pdf", bbox_inches="tight")


