import matplotlib.pyplot as plt
from matplotlib import rcParams

# figure size in inches
rcParams['figure.figsize'] = 11.7,8.27
# Set the style globally
plt.style.use('default')
rcParams['font.weight'] = '500'
rcParams['font.size'] = 16
rcParams['axes.labelsize'] = 16
rcParams['axes.labelweight'] = '500'
rcParams['axes.titleweight'] = '600'
rcParams['axes.titlesize'] = 16
rcParams['xtick.labelsize'] = 14
rcParams['ytick.labelsize'] = 14
rcParams['legend.fontsize'] = 12
rcParams['figure.titlesize'] = 18

### Basic parameters ######################################################
parameters = [
    'fantapoints made',         # Fantapoints made
    'fantapoints against',        # Fantapoints against
    'goals against gk',     # Goals conceded by the goalkeeper that contributes to the team
    'cards',          # Cards against players that contribute to the team (yellow=1, red=2)
    'defense modifier',          # Modifier due to the performance of defensive players
]

### List of teams #########################################################
Teams = {'enrico' : ['Gianlucanonpressare', 'darkorange'],
         'fabio' : ['Porti Chiusi Italiani', 'yellowgreen'],
         'gianluca' : ['La mamma di Enrico', 'midnightblue'],
         'giulio' : ['Dinamo Oegia', 'r'],
         'luca' : ['Nottingham Forrest Gump', 'lightskyblue'],
         'riccardo' : ['Laggente','seagreen'],
        }
teams = list(Teams.keys())

### Global setup of the league #############################################
thr_first_goal = 66  # Threshold for first goal
step = 5   # Step between goal marks
thr_own_goal = 58    # Threshold for own goal
n_players = len(Teams)    # Number of players
low_score = 62    # Threshold for defining low scoring games (just for stats)
