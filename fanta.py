import config
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import seaborn as sns
from functools import reduce

### Configure database ####################################################
def configure_db():
    df_list = list()
    for team in config.teams:
        df_result = pd.read_csv(f'{team}.txt', sep=' ', names=config.parameters, skiprows=1)
        df_result.dropna(axis=0, inplace=True)
        df_result['team'] = team
        df_list.append(df_result)
    df_final = reduce(lambda a, b : a.append(b), df_list)
    df_final.index.name = 'Game'
    # Adding columns to the dataframe
    df_final['GM'] = df_final.apply(lambda x: get_goal(x['fantapoints made'], x['fantapoints against']), axis=1)
    df_final['GA'] = df_final.apply(lambda x: get_goal(x['fantapoints against'], x['fantapoints made']), axis=1)
    df_final['result'] = df_final.apply(lambda x: result(x['GM'], x['GA']), axis=1)
    df_final['points'] = df_final.apply(lambda x: points(x['result']), axis=1)
    df_final['f_close_games'] = round(
        df_final.apply(lambda x: points_gaines_diff(x['fantapoints made'], x['fantapoints against'], x['points']), axis=1), 3)
    df_final['f_day_average'] = round(df_final.apply(
        lambda x: points_gained_day(x['GM'], x['points'], x.name, config.teams, df_final), axis=1), 3)
    df_final['Luck Index'] = round(df_final['f_close_games'] + df_final['f_day_average'], 3)
    return df_final

### Total dataframe ##################################################
def total_df(df_final):
    df_total = df_final.groupby(['team']).apply(lambda x: x.sum())
    df_total['results'] = df_total.apply(lambda x: compact_res(x['result']), axis=1)
    # Order by points (and then fantapoints) -> Build classification
    cols = ['points', 'fantapoints made']
    tups = df_total[cols].sort_values(cols, ascending=False).apply(tuple, 1)
    f, i = pd.factorize(tups)
    factorized = pd.Series(f + 1, tups.index)
    df_total['pos'] = factorized
    df_total['rank'] = df_total['fantapoints made'].rank(ascending=False, method='first').astype(int)
    df_total['distance'] = np.max(df_total['points']) - df_total['points']
    return df_total

### Utility functions ################################################
def get_goal(fp_made, fp_against):
    '''Return number of goals given fantapoints'''
    goal_counter = 0
    if fp_against < config.thr_own_goal: goal_counter = goal_counter + 1
    if fp_made >= config.thr_first_goal: goal_counter = goal_counter + math.floor((fp_made-config.thr_first_goal)/config.step) + 1
    return goal_counter

def result(gf, gs):
    '''Return match result (W,T,L) given goal scored and conceded'''
    if gf > gs:
        return 'W'
    elif gf < gs:
        return 'L'
    else:
        return 'T'
    
def points(result):
    '''Return standing points given match result'''
    if result == 'W':
        return 3
    elif result == 'L':
        return 0
    elif result == 'T':
        return 1
    else:
        print('Non valid result')

def get_team_colors():
    '''Return list of team colors by default order'''
    colors = [config.Teams[key][1] for key in config.Teams.keys()]
    return colors

def points_gaines_diff(fp_made, fp_against, pts):
    '''Returns points gained wrt the expected value given the difference in fantapoints'''
    diff = fp_made - fp_against
    if diff < -config.step:
        exp_points = 0
    elif diff >= config.step:
        exp_points = 3
    elif diff >= -config.step and diff < 0:
        exp_points = 1 + diff/config.step
    elif diff >= 0 and diff < config.step:
        exp_points = 1 + 2*diff/config.step
    return pts - exp_points

def points_gained_day(gf, pts, matchday, teams, df_final):
    '''Returns points gained wrt expected value considering fantapoints made by other players that matchday'''
    exp_points = 0
    for team in teams:
        exp_points = exp_points + points(result(gf,df_final[df_final['team']==team].at[matchday,'GM']))
    return pts - (exp_points-1) / (config.n_players-1)  # -1 to eliminate the case when a player is against him/herself

def compact_res(res_str):
    '''Returns something of the form 3W,1T,2L from a string of the form WLTLWWL'''
    n_w, n_t, n_l = 0, 0, 0
    for c in res_str:
        if (c == 'W'):
            n_w = n_w + 1
        elif (c == 'T'):
            n_t = n_t + 1
        elif (c == 'L'):
            n_l = n_l + 1
        else:
            print('Non valid result')
    return f'{n_w}W,{n_t}T,{n_l}L'

def evo_plot(games, df_final, par, title, ylabel, threshold):
    '''Evolution plots'''
    gms = np.arange(0, games+1)
    fig = plt.figure(figsize=(games*0.6,6))
    data = []
    for team in config.teams:
        df = df_final[df_final['team']==team].copy()
        df['cumsum'] = np.cumsum(df[par])
        score = df['cumsum'].loc[games]
        df['score'] = score
        data.append(df)
    data = sorted(data, key=lambda x: x['score'].unique().min(axis=0), reverse=True)
    for df in data:
        team = df['team'].unique()[0]
        color = config.Teams[team][1]
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

### Melt dataframe with variables of interest ######################
def melt_df(df_final, variables = ['fantapoints against', 'fantapoints made']):
    data = []
    for team in config.teams:
        df=df_final[df_final['team']==team].copy()
        dd = pd.DataFrame()
        dd['Team'] = df_final[df_final['team']==team]['team']
        for key in variables:
            dd[key] = df[key]
        data.append(dd)
    cdf = pd.concat(data)    
    mdf = pd.melt(cdf, id_vars=['Team'], var_name=['Variable'])
    return mdf

### Expected value of goals against, facing all other opponents ##############################
def exp_goal_plot(df_total, games, games_completed):
    df_total['x_GA'] = (df_total['GM'].sum()-df_total['GM']) / (config.n_players-1)
    fig = plt.figure(figsize=(8,5))
    colors = get_team_colors()
    plt.bar(np.arange(0, config.n_players), df_total['x_GA'], color=colors, alpha=0.2, label='Exp GA')
    plt.bar(np.arange(0, config.n_players), df_total['GA'], color=colors, alpha=0.99, width=0.5, label='GA')
    xlabels = config.teams
    plt.xticks(np.arange(config.n_players), config.teams, rotation=45, ha='right')
    plt.grid(which='both', axis='y', alpha=0.25)
    plt.ylim(bottom = min(df_total['GA']-1))
    plt.ylabel('Goals Against')
    title = 'Exp Goals Against (Matchday ' + str(games) + ', ' + str(games_completed) + ' completed)'
    plt.title(title)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()
    
### Fantapoints made vs classification ###############
def fantap_vs_class(df_total, games, games_completed):
    fig = plt.figure(figsize=(8,5))
    colors = get_team_colors()
    plt.bar(np.arange(0, config.n_players), df_total['fantapoints made'], color=colors, alpha=0.99, label='Fantapoints')
    plt.ylabel('Fantapoints')
    plt.ylim(np.min(df_total['fantapoints made'])-10, np.max(df_total['fantapoints made'])+10)
    xlabels = config.teams
    plt.xticks(np.arange(config.n_players), xlabels, rotation=45, ha='right')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    # secondary y axis
    ax2 = plt.twinx()
    ax2.set_ylabel('Points')
    ax2.tick_params(axis='y', colors='grey', length=0)
    ax2.yaxis.label.set_color('grey')
    ax2.plot([],[])
    plt.bar(np.arange(0, config.n_players), df_total['points'], color='black', alpha=0.5, width=0.35, label='Points')
    plt.grid(which='both', axis='y', alpha=0.25)
    title = 'Points vs Fantapoints Made (Matchday ' + str(games) + ', ' + str(games_completed) + ' completed)'
    plt.title(title)
    ax2.legend(bbox_to_anchor=(1.05, 0.9), loc=2, borderaxespad=0.)
    plt.show()

### Luck Index plot ###########################################
def luck_index_plot(df_total, games, games_completed):
    keys = ('f_close_games', 'f_day_average')  # Factors contributing to Luck Index
    cols = ['dodgerblue', 'purple']

    fig = plt.figure(figsize=(8,5))
    plt.grid(which='major', axis='y', ls='-', alpha=0.25)
    xlabels = config.teams
    plt.xticks(np.arange(config.n_players), xlabels, rotation=45, ha='right')
    plt.axhline(y=0, xmin=-100, xmax=100, color='grey', ls='-')
    plt.bar(np.arange(config.n_players), df_total['Luck Index'], color='black', lw=0, alpha=0.15, width=0.9, label='Luck Index')
    plt.bar(np.arange(config.n_players), df_total[keys[0]], color=cols[0] ,alpha=0.99, width=0.5, label=keys[0])
    plt.bar(np.arange(config.n_players), df_total[keys[1]],
            bottom=np.heaviside(df_total[keys[1]]*df_total[keys[0]],0.5)*df_total[keys[0]],
            color=cols[1] ,alpha=0.99, width=0.5, label=keys[1])  # Bottom different from 0 for piling up bars in a proper way
    plt.legend()
    for i, f in enumerate(list(np.round(df_total['Luck Index'], decimals=2))):
        if f<0:
            va = 'top'
            offset = -0.7
        else: 
            va = 'bottom'
            offset = 0.7
        plt.annotate(f, (i, f+offset), horizontalalignment='center', verticalalignment=va)
    plt.ylim(min(df_total['Luck Index'])-2, max(df_total['Luck Index'])+2)
    plt.ylabel('Luck Index (points)')
    title = 'Luck Index (Matchday ' + str(games) + ', ' + str(games_completed) + ' completed)'
    plt.title(title)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()
    
### Box Plots #################################################
def box_plot(df_final, fp_med, par, label, title, col, pal):
    data = melt_df(df_final, [par])
    # Box plot
    ax = sns.boxplot(x="Team", y="value", hue="Variable", data=data, color=col, whis=1.5, width=0.5)    
    # Draw single datapoints
    ax = sns.swarmplot(x="Team", y="value", hue="Variable", data=data, palette=pal)    
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ymin, ymax = ax.get_ylim()
    goal_marks = np.array([config.thr_own_goal])
    goal_numb = np.array([0])
    for i in range(0, math.floor((ymax-config.thr_first_goal) / config.step) + 2):
            goal_marks = np.append(goal_marks, [config.thr_first_goal + i*config.step])
            goal_numb = np.append(goal_numb, i+1)
    goal_numb = np.insert(goal_numb, 0, -1)
    ax.grid(axis='x', linestyle='-', linewidth=5, alpha=0.2)
    ax.hlines(goal_marks, -1000, 1000, 'grey', '-', linewidth=1, alpha=0.5)
    ax.hlines(fp_med, -100, 100, colors='red', linewidth=1, linestyles='--', alpha=0.5, label='Median')
    ax.set_ylabel(label)
    ax.set_xlabel('')
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    # Secondary y axis
    ax2 = ax.twinx()
    goal = lambda fp_made: (fp_made-66) / config.step + 0.5
    ax2.set_ylim((goal(ymin), goal(ymax)))
    ax2.set_yticks(goal_numb)
    yticks = goal_numb.tolist()
    yticks[0] = 'Own goal\nthreshold'
    ax2.set_yticklabels(yticks)
    ax2.set_ylabel('Goals')
    ax2.tick_params(axis='y', colors='grey', length=0)
    ax2.yaxis.label.set_color('grey')
    ax2.plot([],[])
    plt.title(title, fontsize=20)
    plt.show()

### Graphical display of results ######################################################
def graphical_results(df_final, games, fp_med):
    for team in config.teams: 
        data_team = df_final[df_final['team']==team].copy()  
        fig = plt.figure(figsize=(games*0.5, 4))
        # Losses
        data = data_team[data_team.result == 'L']
        ax = plt.scatter(data.index, data['fantapoints made'], c='black', edgecolor='r',
                         linewidth=2, s=data['fantapoints made']*2, label='')
        ax = plt.scatter(data.index, data['fantapoints against'], c='black', edgecolor='none',
                         s=data['fantapoints against']*2, alpha=0.25, label='')
        # Ties
        data = data_team[data_team.result == 'T']
        ax = plt.scatter(data.index, data['fantapoints made'], c='black', edgecolor='grey',
                         linewidth=2, s=data['fantapoints made']*2, label='')
        ax = plt.scatter(data.index, data['fantapoints against'], c='black', edgecolor='none',
                         s=data['fantapoints against']*2, alpha=0.25, label='')
        # Wins
        data = data_team[data_team.result == 'W']
        ax = plt.scatter(data.index, data['fantapoints made'], c='black', edgecolor='g',
                         linewidth=2, s=data['fantapoints made']*2, label='')
        ax = plt.scatter(data.index, data['fantapoints against'], c='black', edgecolor='none',
                         s=data['fantapoints against']*2, alpha=0.25, label='')
        # Setting limits y-axis and adding line for goal marks and median
        ymin = min(df_final['fantapoints made'].min(), df_final['fantapoints against'].min()) - 3
        ymax = max(df_final['fantapoints made'].max(), df_final['fantapoints against'].max()) + 3
        goal_marks = np.array([config.thr_own_goal])
        goal_numb = np.array([0])
        for i in range(0, math.floor((ymax-config.thr_first_goal) / config.step) + 2):
            goal_marks = np.append(goal_marks,[config.thr_first_goal + i*config.step])
            goal_numb = np.append(goal_numb, i + 1)
        goal_numb = np.insert(goal_numb, 0, -1)
        plt.hlines(goal_marks, -1000, 1000, 'grey', '-', linewidth=1, alpha=0.5)
        plt.hlines(fp_med, 0, 40, colors='blue', linewidth=2, linestyles='--', alpha=0.5, label='Median')
        plt.xlabel('Matchday')
        plt.ylabel('Fantapoints')
        plt.title(team)
        plt.xlim(0, games + 1)
        plt.ylim(ymin, ymax)
        plt.xticks(np.arange(0, games + 1))
        plt.grid(axis='x', linestyle='-', linewidth=5, alpha=0.2)
        # Secondary y axis
        ax2 = plt.twinx()  
        goal = lambda fp_made: (fp_made-config.thr_first_goal) / config.step + 0.5 
        ax2.set_yticks(goal_numb)
        yticks = goal_numb.tolist()
        yticks[0] = 'Own goal\nthreshold'
        ax2.set_yticklabels( yticks)
        ax2.set_ylabel('Goals')
        ax2.set_ylim((goal(ymin), goal(ymax)))
        ax2.tick_params(axis='y', colors='grey', length=0)
        ax2.yaxis.label.set_color('grey')
        ax2.plot([],[])
        plt.show()