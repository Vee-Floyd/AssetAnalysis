import statsmodels
import pandas as pd
import scipy
from scipy.stats import chi2_contingency
from scipy.stats import chi2
import numpy as np
import datetime as dt
from matplotlib import pyplot as plt

#This function finds the first date that a campaign started and the last date it has data for. Subtracting the 2 gives us the total run time in days
#DF input for this should be at the daily data level (straight from the initial export)
def getRunTimes(df,groupings,minDate):
    DFwithRunTimes=df.groupby(groupings).agg({'Date':['min','max']})
    DFwithRunTimes[('Date', 'max')] = pd.to_datetime(DFwithRunTimes[('Date', 'max')], format='%m/%d/%y')
    DFwithRunTimes[('Date', 'min')] = pd.to_datetime(DFwithRunTimes[('Date', 'min')], format='%m/%d/%y')
    DFwithRunTimes['RunTime'] = (DFwithRunTimes[('Date', 'max')] - DFwithRunTimes[('Date', 'min')]).dt.days
    print('made it here')
    DFwithRunTimes.columns = DFwithRunTimes.columns.droplevel(1)
    print('made it here too')
    DFwithRunTimes = DFwithRunTimes.reset_index()
    print('made it here 3')
    finalDfWithRunTimes = df.merge(DFwithRunTimes, how='left',on=groupings)
    print('made it here 4')
    finalDfWithRunTimes = finalDfWithRunTimes[finalDfWithRunTimes.iloc[:,18] >= minDate]
    return finalDfWithRunTimes

#This function runs chi2 tests on the df for each platform and objective. It looks for significant correlation between the metrics and the variables as the level of each grouping
def chiSquareTests(df,objectives,platforms,variables,groups,metrics,significance=.05):
    tests = [['parameters', 'pvalue', 'chisquare']]
    significance = significance
    p = 1 - significance
    for o in objectives:
        objectivedf = df[df['Objective'] == f'{o}']
        print(o)
        # objectivedf.head()
        for p in platforms:
            platformdf = objectivedf[objectivedf['Platform'] == f'{p}']
            print(p)
            # platformdf.head()
            for v in variables:
                for g in groups:
                    for m in metrics:

                        try:
                            chitestdf = platformdf.groupby([f'{v}', f'{g}']).agg({m: metrics[m]}).unstack().dropna(axis=0)
                            chi2_contingency(chitestdf)
                            dof = chi2_contingency(chitestdf)[2]
                            print([p, g, m, metrics[m]])
                            chisquare = chi2_contingency(chitestdf)[0]
                            pvalue = chi2_contingency(chitestdf)[1]
                            # dof=chi2_contingency(chidf)[2]
                            # critialValue=chi2.ppf(p,dof)
                            tests.append([[p, g, v, m, o], pvalue, chisquare])
                            # chitestdf.head()
                        except:
                            pass

    return pd.DataFrame(tests).to_csv('Chi2TestResults.csv')

#This function gives us the median for each metric and the difference from the median
def getMedians(df):
    metrics=['CPC','CPM','CPA','CTR']
    dfMedian= df.groupby(by=['Platform', 'Objective']).agg({
    'CPC':"median",
    'CPM':"median",
    'CPA':"median",
    'CTR':"median"})
    dfMedian=dfMedian.rename(columns={'Spend':'MedianSpend',
                                      'AllSubscriptions':'MedianAllSubscriptions',
                                      'Clicks':'MedianClicks',
                                      'Impressions':'MedianImpressions',
                                      'CPC':'MedianCPC',
                                      'CPM':'MedianCPM',
                                      'CTR':'MedianCTR',
                                      'CPA':'MedianCPA'})
    df=df.merge(dfMedian,how='left',on=['Platform','Objective'])
    for m in metrics:
        df[f'{m}Delta'] = (df[f'{m}'] -df[f'Median{m}']) / df[f'Median{m}']
    df.to_csv('FinalAssetAnalysisResults.csv')
    return df

#This gives us the first and third quartile values for each platform, objective and metric in a specific level of grouping
def getCategorydata(df,Platforms,Objectives,Metrics,Grouping):
    q1=[]
    LowestMetric=pd.DataFrame([])
    HighestMetric = pd.DataFrame([])
    for m in Metrics:
        for o in Objectives:
            for p in Platforms:
                    firstquartile = df[['Platform', 'Objective', m]].loc[df['Platform'].str.contains(p) & df['Objective'].str.contains(o)]
                    firstquartile = firstquartile.quantile([.25, .75])
                    q1.append([m, o, p, firstquartile.iloc[0, 0], firstquartile.iloc[1, 0]])
    pd.DataFrame(q1).to_csv('q1.csv')


    for row in q1:
        df1 = df.loc[(df['Platform'] == f'{row[2]}') & (df['Objective'] == f'{row[1]}') & (df[f'{row[0]}Delta'] <= row[3])]
        to_append = df1[['Objective', 'Platform', 'Creative', Grouping]].groupby(['Objective', 'Platform', Grouping]).count()
        to_append['Metric'] = f'{row[0]}'
        LowestMetric = LowestMetric.append(to_append[['Metric', 'Creative']])

        df2 = df.loc[(df['Platform'] == f'{row[2]}') & (df['Objective'] == f'{row[1]}') & (df[f'{row[0]}Delta'] >= row[4])]
        to_append = df2[['Objective', 'Platform', 'Creative', Grouping]].groupby(['Objective', 'Platform', Grouping]).count()
        to_append['Metric'] = f'{row[0]}'
        HighestMetric = HighestMetric.append(to_append[['Metric', 'Creative']])
    LowestMetric.to_csv(f'LowestMetricby{Grouping}.csv')
    HighestMetric.to_csv(f'HighestMetricby{Grouping}.csv')
    return

