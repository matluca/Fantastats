import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import seaborn as sns
from functools import reduce

def all_time_luck():
    #read dataframes
    luck1 = pd.read_csv('2018-2019/luck.csv')
    luck1['year'] = 2019
    luck2 = pd.read_csv('2019-2020/luck.csv')
    luck2['year'] = 2020
    luck3 = pd.read_csv('2020-2021/luck.csv')
    luck3['year'] = 2021
    luck4 = pd.read_csv('2021-2022/luck.csv')
    luck4['year'] = 2022
    luck5 = pd.read_csv('2022-2023/luck.csv')
    luck5['year'] = 2023
    luck = pd.concat([luck1, luck2, luck3, luck4, luck5])
    
    #fill dataframe
    players = luck['team'].unique()
    years = luck['year'].unique()
    for year in years:
        luck_by_year = luck.loc[luck['year'] == year]
        year_players = luck_by_year['team'].unique()
        games = luck_by_year['Game'].unique()
        for player in players:
            if player not in year_players:
                for game in games:
                    to_append = pd.DataFrame([[game, 0.0, player, year]], columns=luck.columns)
                    #luck = luck.append(to_append, ignore_index=True)
                    luck = pd.concat([luck, to_append], ignore_index=True)
    luck['new_index'] = luck['Game'] + 35 * (luck['year'] - 2019)
    games = max(luck['new_index'].unique())
    luck = luck.set_index('new_index')
    luck.index.name = 'index'
    
    colors = ['darkorange', 'yellowgreen', 'r', 'midnightblue', 'lightskyblue', 'seagreen', 'grey', 'purple', 'firebrick', 'hotpink']
    teamColors = {}
    for i in range(len(players)):
        teamColors[players[i]] = colors[i]
    
    #plot
    luck_index_plot(luck, games, players, games)
    evo_plot(games, luck, teamColors, players, par='Luck Index', title='Luck Index Evolution', ylabel='Luck Index', threshold=5)
        
def evo_plot(games, df_final, teamColors, players, par, title, ylabel, threshold):
    '''Evolution plots'''
    gms = np.arange(0, games+1)
    fig = plt.figure(figsize=(games*0.6,6))
    data = []
    for team in players:
        df = df_final[df_final['team']==team].copy()
        df['cumsum'] = np.cumsum(df[par])
        score = df['cumsum'].loc[games]
        df['score'] = score
        data.append(df)
    data = sorted(data, key=lambda x: x['score'].unique().min(axis=0), reverse=True)
    for df in data:
        team = df['team'].unique()[0]
        color = teamColors[team]
        df = df.reindex(gms, fill_value=0) #Adding zeroes for missing games and for game number 0
        df['cumsum'] = round(np.cumsum(df[par]), 3)
        values = df['cumsum']
        score = values.loc[games]
        score_prev = values.loc[games-1]
        diff = round(score - score_prev,3)
        if diff >= 0:
            sign = '+'
        else:
            sign = ''
        p = plt.plot(gms, values, color=color, ls='-', lw=2,
                     label=str(score)+' ('+ sign + str(diff)+') | '+str(team))
        # Labels for games over threshold
        gm = df[(df[par]>threshold)|(df[par]<-threshold)].index
        dd = df[df.index.isin(gm)]
        marks = dd['cumsum']
        plt.scatter(gm, marks, edgecolor=color, facecolor=color, s=400+20*dd[par], label='')
        for x, y, text in zip(gm, marks, dd[par]):
            plt.text(x, y, text, horizontalalignment='center', verticalalignment='center', color='white')
    plt.xticks(np.arange(0, games+1))
    plt.xlim((-0.5, games+0.5))
    plt.grid(axis='x', linestyle='-', linewidth=5, alpha=0.2)
    plt.grid(axis='y', alpha=0.2)
    plt.xlabel('Matchday')
    plt.ylabel(ylabel)
    plt.title(title, fontsize=20)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()

def luck_index_plot(df, games, players, games_completed):
    df_total = total_df(df)
    avg = df_total['Luck Index'].mean()

    fig = plt.figure(figsize=(8,5))
    plt.grid(which='major', axis='y', ls='-', alpha=0.25)
    xlabels = sorted(players)
    plt.xticks(np.arange(len(players)), xlabels, rotation=45, ha='right')
    plt.axhline(y=0, xmin=-100, xmax=100, color='grey', ls='-')
    plt.bar(np.arange(len(players)), df_total['Luck Index'], color='lightblue', lw=0, alpha=0.99, width=0.9, label='Luck Index')
    plt.legend()
    for i, f in enumerate(list(np.round(df_total['Luck Index'], decimals=2))):
        if f<0:
            va = 'top'
            offset = -0.7
        else: 
            va = 'bottom'
            offset = 0.7
        plt.annotate(f, (i, f+offset), horizontalalignment='center', verticalalignment=va)
    plt.ylim(min(df_total['Luck Index'])-3, max(df_total['Luck Index'])+3)
    plt.ylabel('Luck Index (points)')
    title = 'Luck Index (' + str(games) + ' games)'
    plt.title(title)
    plt.axhline(avg, -100, 100, color='red', linewidth=1, ls='-', label='Average: ' + str(format(avg, '.1f')))
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    
def total_df(df_final):
    df_total = df_final.groupby(['team']).apply(lambda x: x.sum())
    return df_total