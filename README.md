# Fantastats

## What is Fantasy Football

Fantasy football is a game based on the italian football league. Participants in a fantasy league select a list of players at the beginning of the season (no player can be shared between two participants). Every matchday participants select their team out of their list of players. Based on the performance on the field, players are assigned grades from 1 to 10 (10 being the best), plus some bonuses depending on goals and assists scored, cards received, and so on. Each participants is then assigned a number of fantapoints which is just the sum of grades and bonuses of the players on the team. Fantapoints are then converted in "goals". The first goal is assigned when fantapoints are more then 66; another goal is assigned every other 5 fantapoints. If the toal is less then 58, an own-goal is scored, meaning that the opponent gets one extra goal.
Each participant faces another participant on every matchday; looking at how many goals he/she "scored" compared to the opponent, he/she wins, ties or loses that match. Points are assigned every matchday (3 for a win, 1 for a tie, 0 for a loss). The finals classification is based on these points, with fantapoints used as tiebreaker if needed.

## Data collected

In the files .txt some data are collected each matchday; in particular:
- Matchday number (gg)
- Fantapoints (pf)
- Opponent's fantapoints (ps)
- Goals conceded by the goalkeeper (gs)
- Cards (yellow: 1, red: 2) (c)
- Defense bonus modifier (mdif)
Based on these data the results of each matchday are computed. Furthermore an estimate of how lucky each participant has been is computed (Indice Fortuna)

NB: for a missing matchday (games suspended, etc...) simply do not write the corresponding line, or write only the matchday number. The notebook will deal with the situation.

## Luck Index

Since the final classification is based on points scored, and not on the "raw" fantapoints, there is room for luck in this game. For example, a participant winning a matchday 1-0 is considered lucky if all the other participants scored 2 or more goals that same matchday. Furthermore, a difference of, say, 2 fantapoints can result in a win (i.e. 67-65) while a difference of, say, 4 fantapoints can result in a tie (i.e. 70-66). The "Luck Index" (Indice Fortuna) takes into account two factors:
- f_close_games: A close games is a game where the difference in fantapoints is less then the step between two goal marks (in this case it is 5). This factor accounts for point gained/loss w.r.t. the cases where goal marks are different. Example: the two oppontes score 67 and 65 fantapoints respectively, resulting in 3 point for the first person, since a goal mark is present at 66 fantapoints. The same situation is then considered moving the goal marks at 66.5, 67, 67.5, and so on. The average amount of points gained is then computed (assuming a uniform distribution), and then subtracted from the actual amount of points gained, in order to give f_close_games (NB: a positive number here means "luck").
- f_day_average: This factor accounts for luck due to the particular opponent encountered that matchday. The program computes the result of a match againts every other opponenent. The average amount of points gained is then computed (assuming a uniform distribution), and then subtracted from the actual amount of points gained, in order to give f_media_giornata (NB: a positive number here means "luck").

The luck index is then the sum of the two factors.

## Files (example for 2019/20 season)

* Python notebook: Fantastats1920.ipynb
* Configuration data: config.py
* Functions definitions: fanta.py
* Raw data files: .txt

## Website
Final results are published in a simple website, generated with the following tools:
* [nbconvert](https://nbconvert.readthedocs.io) to generate Markdown files from Jupyter Notebooks
* [mkdocs](https://www.mkdocs.org/) to generate a static website out of Markdown files
* [Firebase](https://firebase.google.com/docs/hosting) to host the website

The website is available at [fantaculo.matluca.com](https://fantaculo.matluca.com)

