import AssetHelper
import pandas as pd

#Read looker export
df=pd.read_csv('[PATH_TO_RAW_DATA_FILE]')
#Make column names more friendly
Assetdf=df.rename(columns={DICTIONARY_TO_RENAME_COLUMNS})

#Define the asset groupings
Assetgroupings=['Platform','Creative Campaign','Objective','Creative','Asset Type','Genre','Show']
#Get All campaigns after start date that have been running for at least 14 days
finalDfWithRunTimes=AssetHelper.getRunTimes(Assetdf,Assetgroupings,'2020-12-01')
EligibleCampaigns=finalDfWithRunTimes.loc[finalDfWithRunTimes['RunTime']>=14]
#Output = Vee to Remove after demo EligibleCampaigns.to_csv('_EligibleCampaignsInitial.csv')

#Aggregate data at the creative level and add calculated metrics
EligibleCampaigns=EligibleCampaigns.groupby(by=['Creative','Platform','Objective','Asset Type','Genre','Show','RunTime'],as_index=False).agg({'Spend':'sum','Impressions':'sum','Clicks':'sum','AllSubscriptions':'sum'})
EligibleCampaigns['CPA']=EligibleCampaigns['Spend']/EligibleCampaigns['AllSubscriptions']
EligibleCampaigns['CPM']=1000*EligibleCampaigns['Spend']/EligibleCampaigns['Impressions']
EligibleCampaigns['CPC']=EligibleCampaigns['Spend']/EligibleCampaigns['Clicks']
EligibleCampaigns['CTR']=EligibleCampaigns['Clicks']/EligibleCampaigns['Impressions']
#Output = Vee to Remove after demo EligibleCampaigns.to_csv('_EligibleCampaignsAggregated.csv')


 #Loop through chisuared test for each platform and objective. Variables are the categories we want to test for an effect, groups is the category we are testing for an effect in
platforms=['Snapchat', 'DV360', 'The Trade Desk','Facebook', 'Twitter', 'Pinterest', 'Reddit', 'TikTok','Audiomatic', 'Pandora']
objectives=['Acquisition', 'Retention', 'Awareness', 'Engagement']
groups=['Genre','Show','Creative Campaign']
variables=['Asset Type','AssetSize','Show']
metrics={'AllSubscriptions':"sum",'Clicks':"sum",'Impressions':"sum"}
AssetHelper.chiSquareTests(EligibleCampaigns,objectives,platforms,variables,groups,metrics)
#VOutput = ee to Remove after demo  look at Chi2TestResults.csv

#GetMedianValues and variance from the median value for each calculated metric at the platform & objective level
EligibleCampaignsWithMedians=AssetHelper.getMedians(EligibleCampaigns)
#Output = Vee to Remove after demo EligibleCampaigns.to_csv('_EligibleCampaignsFinal.csv')

#Define the metrics we'd like to analyze in our final output comparing top and bottom quartile creatives
Metrics=['CPC','CPA']
Grouping='Show'
AssetHelper.getCategorydata(EligibleCampaignsWithMedians.reset_index(),platforms,objectives,Metrics,Grouping)
#Output = Vee to Remove after demo  look at HighestMetricbyShow and LowestMetricbyShow
