#Part 1: reading datasets and plotting stations

import matplotlib.pyplot as plt
import mplleaflet
import pandas as pd

work_hash='fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89'
MetaFileName='data/C2A2_data/BinSize_d{}.csv'.format(400)
WorkFile='data/C2A2_data/BinnedCsvs_d{}/{}.csv'.format(400, work_hash)

def make_dfMeta(hashid):
    df = pd.read_csv(MetaFileName)
    return df[df['hash'] == hashid]

def leaflet_plot_stations(binsize, hashid):
    
    station_locations_by_hash = make_dfMeta(work_hash)

    #print(station_locations_by_hash.head(20))
    
    lons = station_locations_by_hash['LONGITUDE'].tolist()
    lats = station_locations_by_hash['LATITUDE'].tolist()

    plt.figure(figsize=(8,8))

    plt.scatter(lons, lats, c='r', alpha=0.7, s=100)

    return mplleaflet.display()

leaflet_plot_stations(400,work_hash)

#Part 2: tabling 50 data and values from 2005-2014

def make_WorkData():
    MetaCol=['ID', 'NAME']
    
    dfMeta=make_dfMeta(work_hash)
    dfData = pd.read_csv(WorkFile, parse_dates=[0])
    
    dfRet=pd.merge(dfMeta[MetaCol], dfData, how='left', on='ID', sort=False)
    dfRet['Data_Value']=dfRet['Data_Value'].apply(lambda x: x/10)
    return dfRet

print(make_WorkData().head(30))

#Part 3: tabling 30 data and values from record breaking temperatures in 2015

def make_plotting_df():
    
    def group_stations(df_Work, FuncName):
        df=df_Work.groupby(['Date'], as_index=False).agg({'Data_Value':FuncName})
        temp = pd.DatetimeIndex(df['Date'])
        df['Year'], df['Month'], df['Day']=temp.year, temp.month, temp.day
        tmp=df[(df['Month']==2) & (df['Day']==29)] 
        return df.drop(tmp.index).drop('Date', axis=1)

    def group_years_months(df_Work, strFunc):
        return df_Work.groupby(['Month', 'Day'], as_index=False).agg({'Data_Value':strFunc})

    def make_ret_df(dfLeft, dfRight, strLabelMax, strLabelMin):
        dfRet=pd.merge(dfLeft, dfRight, how='inner', on=['Month', 'Day'])
        dfRet.rename(index=str, columns={'Data_Value_x':strLabelMax, 'Data_Value_y':strLabelMin}, inplace=True)
        dfRet.set_index(['Month', 'Day'], inplace=True)
        return dfRet
        
    dfx=make_WorkData()
    
    dfMax=dfx[dfx['Element']=='TMAX'] #make 2 dataframes for 2 lines
    dfMin=dfx[dfx['Element']=='TMIN']

    dfMax=group_stations(dfMax, 'max') # find min-max value for each day by all stations
    dfMin=group_stations(dfMin, 'min')

    df2015Max=dfMax[dfMax['Year']==2015].drop('Year', axis=1) # select 2015 year
    df2015Min=dfMin[dfMin['Year']==2015].drop('Year', axis=1)

    dfMax=dfMax.drop(df2015Max.index) # drop 2015 years data from lines
    dfMin=dfMin.drop(df2015Min.index)

    dfMax=group_years_months(dfMax, 'max') # calc min-max values for each day, year to year
    dfMin=group_years_months(dfMin, 'min')
    
    dfLinesRet=make_ret_df(dfMax, dfMin, 'Max temp, C', 'Min temp, C')
    dfScatRet=make_ret_df(df2015Max, df2015Min, 'Max temp 2015, C', 'Min temp 2015, C')
    
    return (dfLinesRet, dfScatRet)

dfL, dfs=make_plotting_df()

print (dfs.head(30))

#Part 4: Building/Plotting our Chart

%matplotlib notebook
import matplotlib.pyplot as plt
import numpy as np
from calendar import month_abbr
from datetime import date, timedelta

def listdata(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

diap_date=[result.strftime('%b %d') for result in listdata(date(2015, 1, 1), date(2016, 1, 1), timedelta(days=1))]
dfLines, dfScat=make_plotting_df()

def plot2lines(dtf):
    #ax1=dfLines.xs(1).plot.line(figsize=(9, 5), use_index=False) # for one month

    dfx=dtf.reset_index()
    x_val=dfx.index.values
    x_ticks=dfx[dfx['Day']==1].index.tolist()

    ax1=dtf.plot.line(x_val, figsize=(9, 4), xticks=x_ticks) # plot 2 lines
    ax1.fill_between(x_val, dtf['Max temp, C'], dtf['Min temp, C'], facecolor='lightgrey') # fill between 2 lines
    return ax1

def format_plot_area(ax1):
    # format plot area
    ax1.spines['bottom'].set_color('black')
    ax1.spines['left'].set_color('black')

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.set_axis_bgcolor('white')

    h, l = ax1.get_legend_handles_labels()
    lines=(h[0], h[1]) #ax1.get_lines()
    h[0].set_color('darkred')
    h[1].set_color('darkgreen')
    ax1.legend(h, ('Max 2005-2014', 'Min 2005-2014', 
                   '2015 above Max', '2015 below Min'), loc=0, frameon=False)
    plt.setp(lines, linewidth=0.3)
    ax1.set_xticklabels([s for s in month_abbr if s!='']) # set x-labels
    
    ax1.set_xlabel('')
    ax1.set_title('Assignment 2: The interval of minimum and maximum temperatures for 2005-2014 \n and temperatures of 2015')
    ax1.set_ylabel('Temperature, C')

    
def plot_scatter(ax1):
    df=pd.merge(dfLines.reset_index(), dfScat.reset_index(), how='inner')
    df['ind']=df.index
    dfMx=df[df['Max temp 2015, C']>df['Max temp, C']]
    dfMn=df[df['Min temp 2015, C']<df['Min temp, C']]
    
    dfMx.plot.scatter(x='ind', y='Max temp 2015, C', label='a', ax=ax1, 
                      color='red', s=7)
    dfMn.plot.scatter(x='ind', y='Min temp 2015, C', label='b', ax=ax1, 
                      color='green', s=7)
    return ax1

ax1=plot2lines(dfLines)
plot_scatter(ax1)
format_plot_area(ax1)
