########## IMPORTS ########## 

import pandas as pd
import numpy as np
import requests
import time
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from datetime import datetime as dt
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

########## FUNCTIONS ##########

def scrape_matchups():

    # Instantiating stuff

    def remove_numbers(input_string):
        result = ""
        for char in input_string:
            if not char.isdigit():
                result += char
        return result

    date_format = "%d %b %Y"
    driver = webdriver.Safari()
    driver.get('https://matchstat.com/tennis/all-upcoming-matches')
    data_dict = {
        'date' : [],
        'player_1' : [],
        'player_2' : [],
        'current_rank_1' : [],
        'current_rank_2' : [],
        'best_rank_1' : [],
        'best_rank_2' : [],
        'time_elapsed_best_rank_1' : [],
        'time_elapsed_best_rank_2' : [],
        'titles_1' : [],
        'titles_2' : [],
        'slams_1' : [],
        'slams_2' : [],
        'tour_titles_1' : [],
        'tour_titles_2' : [],
        'masters_1' : [],
        'masters_2' : [],
        'challengers_1' : [],
        'challengers_2' : [],
        'futures_1' : [],
        'futures_2' : [],
        'age_1' : [],
        'age_2' : [],
        'rank_win_pct_1' : [],
        'rank_win_pct_2' : [],
        'rank_matches_1' : [],
        'rank_matches_2' : [],
        'aces_per_game_1' : [],
        'aces_per_game_2' : [],
        'dfs_per_game_1' : [],
        'dfs_per_game_2' : [],
        'first_serve_pct_1' : [],
        'first_serve_pct_2' : [],
        'first_serve_win_pct_1' : [],
        'first_serve_win_pct_2' : [],
        'second_serve_win_pct_1' : [],
        'second_serve_win_pct_2' : [],
        'serve_win_pct_1' : [],
        'serve_win_pct_2' : [],
        'bp_saved_1' : [],
        'bp_saved_2' : [],
        'bp_faced_1' : [],
        'bp_faced_2' : [],
        'bp_saved_pct_1' : [],
        'bp_saved_pct_2' : [],
        'serve_hold_pct_1' : [],
        'serve_hold_pct_2' : [],
        'bp_won_pg_1' : [],
        'bp_won_pg_2' : [],
        'bp_opps_1' : [],
        'bp_opps_2' : [],
        'bp_won_pct_1' : [],
        'bp_won_pct_2' : [],
        'bp_opp_hold_pct_1' : [],
        'bp_opp_hold_pct_2' : [],
        'career_win_pct_1' : [],
        'career_win_pct_2' : [],
        'career_matches_1' : [],
        'career_matches_2' : [],
        'ytd_win_pct_1' : [],
        'ytd_win_pct_2' : [],
        'ytd_matches_1' : [],
        'ytd_matches_2' : [],
        'ytd_titles_1' : [],
        'ytd_titles_2' : [],
        'h2h_matches' : [],
        'h2h_win_pct_1' : [],
        'h2h_win_pct_2' : [],
        'h2h_win_pct_length_1' : [],
        'h2h_win_pct_length_2' : [],
        'career_win_pct_surface_1' : [],
        'career_win_pct_surface_2' : [],
        'aces_pg_surface_1' : [],
        'aces_pg_surface_2' : [],
        'first_serve_pct_surface_1' : [],
        'first_serve_pct_surface_2' : [],
        'first_serve_win_pct_surface_1' : [],
        'first_serve_win_pct_surface_2' : [],
        'second_serve_win_pct_surface_1' : [],
        'second_serve_win_pct_surface_2' : [],
        'bp_win_pct_surface_1' : [],
        'bp_win_pct_surface_2' : [],
        'return_win_pct_surface_1' : [],
        'return_win_pct_surface_2' : [],
        'slam_win_pct_surface_1' : [],
        'slam_win_pct_surface_2' : [],
        'slam_matches_surface_1' : [],
        'slam_matches_surface_2' : [],
        
    }

    # Iterating through matchups

    # Instantiating stuff
    players = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="profile-link"]')))
    players = driver.find_elements(By.CSS_SELECTOR, '[class*="m-0 link ms-0 profile-link ms-md-2"]')
    all_links = []
    player_1_links = []
    player_2_links = []
    matchup_links = []

    # Getting a list set of all the links
    for i in range(len(players)):
        href = players[i].get_attribute('href')
        all_links.append(href)
    # Removing duplicates
    indices_to_remove = list(range(2, len(all_links), 3))
    for index in reversed(indices_to_remove):
        del all_links[index]
    players_links = all_links.copy()

    # Getting individual player links & names
    for i in range(len(players_links)):
        if i%2 == 0:
            player_1_links.append(players_links[i])
            player_2_links.append(players_links[i+1])
            
    # Getting player and matchup stats
    for href_1, href_2 in zip(player_1_links, player_2_links):
            
        # Getting individual player stats


        dfs_indy_1 = pd.read_html(href_1)
        dfs_indy_2 = pd.read_html(href_2)
        time.sleep(2)

        # Player 1

        # Basics
        # Case of player with no individual data
        try:
            df_1_basics = dfs_indy_1[0]
            df_1_basics.columns = ['Stat', 'Value']
        except:
            continue
        # Case of player with no rank
        try:
            current_rank_1 = float(df_1_basics.loc[df_1_basics.Stat == 'Current Rank', 'Value'].values[0])
        except:
            continue
        best_rank_info_1 = df_1_basics.loc[df_1_basics.Stat == 'Best Rank', 'Value'].values[0].strip(' ').split('(')
        best_rank_1 = float(best_rank_info_1[0])
        best_rank_date_1 = best_rank_info_1[1].strip(')')
        best_rank_date_1 = dt.strptime(best_rank_date_1, date_format)
        time_elapsed_best_rank_1 = (dt.now() - best_rank_date_1).days
        titles_1 = float(df_1_basics.loc[df_1_basics.Stat == 'Titles', 'Value'].values[0])
        slams_1 = float(df_1_basics.loc[df_1_basics.Stat == 'Grand Slams', 'Value'].values[0])
        tour_titles_1 = float(df_1_basics.loc[df_1_basics.Stat == 'Main Tour', 'Value'].values[0])
        masters_1 = float(df_1_basics.loc[df_1_basics.Stat == 'Masters', 'Value'].values[0])
        challengers_1 = float(df_1_basics.loc[df_1_basics.Stat == 'Challengers', 'Value'].values[0])
        futures_1 = float(df_1_basics.loc[df_1_basics.Stat == 'Futures', 'Value'].values[0])
        # Demographic
        df_1_demographic = dfs_indy_1[1]
        df_1_demographic.columns = ['Stat', 'Value']
        age_1 = float(df_1_demographic.loc[df_1_demographic.Stat == 'Age', 'Value'].values[0][:2])
        # Performance by surface
        df_1_surface_perf = dfs_indy_1[3]
        df_1_surface_perf.columns = ['Surface', 'Win_Pct', 'Breakdown']
        overall_win_pct_1 = float(df_1_surface_perf.loc[df_1_surface_perf.Surface == 'Overall', 'Win_Pct'].values[0].strip('%'))
        overall_matches_1 = df_1_surface_perf.loc[df_1_surface_perf.Surface == 'Overall', 'Breakdown'].values[0].strip(' ').split('/')
        overall_matches_1 = float(overall_matches_1[0]) + float(overall_matches_1[1])
        hard_win_pct_1 = float(df_1_surface_perf.loc[df_1_surface_perf.Surface == 'Hard', 'Win_Pct'].values[0].strip('%'))
        hard_matches_1 = df_1_surface_perf.loc[df_1_surface_perf.Surface == 'Hard', 'Breakdown'].values[0].strip(' ').split('/')
        hard_matches_1 = float(hard_matches_1[0]) + float(hard_matches_1[1])
        clay_win_pct_1 = float(df_1_surface_perf.loc[df_1_surface_perf.Surface == 'Clay', 'Win_Pct'].values[0].strip('%'))
        clay_matches_1 = df_1_surface_perf.loc[df_1_surface_perf.Surface == 'Clay', 'Breakdown'].values[0].strip(' ').split('/')
        clay_matches_1 = float(clay_matches_1[0]) + float(clay_matches_1[1])
        grass_win_pct_1 = float(df_1_surface_perf.loc[df_1_surface_perf.Surface == 'Grass', 'Win_Pct'].values[0].strip('%'))
        grass_matches_1 = df_1_surface_perf.loc[df_1_surface_perf.Surface == 'Grass', 'Breakdown'].values[0].strip(' ').split('/')
        grass_matches_1 = float(grass_matches_1[0]) + float(grass_matches_1[1])
        # Performance by level
        df_1_level_perf = dfs_indy_1[6]
        df_1_level_perf.columns = ['Level', 'Win_Pct', 'Breakdown']
        top_1_win_pct_1 = float(df_1_level_perf.loc[df_1_level_perf.Level == 'Vs No.1', 'Win_Pct'].values[0].strip('%'))
        top_1_matches_1 = df_1_level_perf.loc[df_1_level_perf.Level == 'Vs No.1', 'Breakdown'].values[0].strip(' ').split('/')
        top_1_matches_1 = float(top_1_matches_1[0]) + float(top_1_matches_1[1])
        top_5_win_pct_1 = float(df_1_level_perf.loc[df_1_level_perf.Level == 'Vs Top.5', 'Win_Pct'].values[0].strip('%'))
        top_5_matches_1 = df_1_level_perf.loc[df_1_level_perf.Level == 'Vs Top.5', 'Breakdown'].values[0].strip(' ').split('/')
        top_5_matches_1 = float(top_5_matches_1[0]) + float(top_5_matches_1[1])
        top_10_win_pct_1 = float(df_1_level_perf.loc[df_1_level_perf.Level == 'Vs Top.10', 'Win_Pct'].values[0].strip('%'))
        top_10_matches_1 = df_1_level_perf.loc[df_1_level_perf.Level == 'Vs Top.10', 'Breakdown'].values[0].strip(' ').split('/')
        top_10_matches_1 = float(top_10_matches_1[0]) + float(top_10_matches_1[1])
        top_20_win_pct_1 = float(df_1_level_perf.loc[df_1_level_perf.Level == 'Vs Top.20', 'Win_Pct'].values[0].strip('%'))
        top_20_matches_1 = df_1_level_perf.loc[df_1_level_perf.Level == 'Vs Top.20', 'Breakdown'].values[0].strip(' ').split('/')
        top_20_matches_1 = float(top_20_matches_1[0]) + float(top_20_matches_1[1])
        top_50_win_pct_1 = float(df_1_level_perf.loc[df_1_level_perf.Level == 'Vs Top.50', 'Win_Pct'].values[0].strip('%'))
        top_50_matches_1 = df_1_level_perf.loc[df_1_level_perf.Level == 'Vs Top.50', 'Breakdown'].values[0].strip(' ').split('/')
        top_50_matches_1 = float(top_50_matches_1[0]) + float(top_50_matches_1[1])
        top_100_win_pct_1 = float(df_1_level_perf.loc[df_1_level_perf.Level == 'Vs Top.100', 'Win_Pct'].values[0].strip('%'))
        top_100_matches_1 = df_1_level_perf.loc[df_1_level_perf.Level == 'Vs Top.100', 'Breakdown'].values[0].strip(' ').split('/')
        top_100_matches_1 = float(top_100_matches_1[0]) + float(top_100_matches_1[1])
        # Serve stats
        serve_stats_1 = dfs_indy_1[8]
        serve_stats_1.columns = ['Stat', 'Value', 'Breakdown']
        aces_per_game_1 = float(serve_stats_1.loc[serve_stats_1.Stat == 'Aces per Game', 'Value'].values[0])
        dfs_per_game_1 = float(serve_stats_1.loc[serve_stats_1.Stat == 'DFs per Game', 'Value'].values[0])
        first_serve_pct_1 = float(serve_stats_1.loc[serve_stats_1.Stat == '1st Serve %', 'Value'].values[0].strip('%'))
        first_serve_win_pct_1 = float(serve_stats_1.loc[serve_stats_1.Stat == '1st Serve Win%', 'Value'].values[0].strip('%'))
        second_serve_win_pct_1 = float(serve_stats_1.loc[serve_stats_1.Stat == '2nd Serve Win%', 'Value'].values[0].strip('%'))
        serve_win_pct_1 = float(serve_stats_1.loc[serve_stats_1.Stat == 'Serve Pts Win%', 'Value'].values[0].strip('%'))
        # Opponent serve stats
        opp_stats_1 = dfs_indy_1[9]
        opp_stats_1.columns = ['Stat', 'Value', 'Breakdown']
        opp_aces_per_game_1 = float(opp_stats_1.loc[opp_stats_1.Stat == 'Opp Aces per Game', 'Value'].values[0])
        opp_dfs_per_game_1 = float(opp_stats_1.loc[opp_stats_1.Stat == 'Opp DFs per Game', 'Value'].values[0])
        first_rtn_win_pct_1 = float(opp_stats_1.loc[opp_stats_1.Stat == '1st Rtn Win%', 'Value'].values[0].strip('%'))
        second_rtn_win_pct_1 = float(opp_stats_1.loc[opp_stats_1.Stat == '2nd Rtn Win%', 'Value'].values[0].strip('%'))
        rtn_win_pct_1 = float(opp_stats_1.loc[opp_stats_1.Stat == 'Rtn Pts Win%', 'Value'].values[0].strip('%'))
        # Break points faced stats
        bp_stats_1 = dfs_indy_1[10]
        bp_stats_1.columns = ['Stat', 'Value', 'Breakdown']
        bp_saved_1 = float(bp_stats_1.loc[bp_stats_1.Stat == 'BPs Saved per game', 'Value'].values[0])
        bp_faced_1 = float(bp_stats_1.loc[bp_stats_1.Stat == 'BPs Faced per game', 'Value'].values[0])
        bp_saved_pct_1 = float(bp_stats_1.loc[bp_stats_1.Stat == 'BP Save %', 'Value'].values[0].strip('%'))
        serve_hold_pct_1 = float(bp_stats_1.loc[bp_stats_1.Stat == 'Service Hold %', 'Value'].values[0].strip('%'))
        # Break points in favor stats
        bp_stats_1 = dfs_indy_1[11]
        bp_stats_1.columns = ['Stat', 'Value', 'Breakdown']
        bp_won_pg_1 = float(bp_stats_1.loc[bp_stats_1.Stat == 'BPs Won per game', 'Value'].values[0])
        bp_opps_1 = float(bp_stats_1.loc[bp_stats_1.Stat == 'BPs Opps per game', 'Value'].values[0])
        bp_won_pct_1 = float(bp_stats_1.loc[bp_stats_1.Stat == 'BP Won %', 'Value'].values[0].strip('%'))
        bp_opp_hold_pct_1 = float(bp_stats_1.loc[bp_stats_1.Stat == 'Opp Hold %', 'Value'].values[0].strip('%'))
        # Yearly results by surface
        yearly_results_1 = dfs_indy_1[14]
        try:
            this_year_win_pct_df_1 = yearly_results_1.loc[yearly_results_1.year == float(dt.now().year), 'sum.'].values[0].split('/')
            this_year_win_pct_1 = float(this_year_win_pct_df_1[0])/(float(this_year_win_pct_df_1[0]) + float(this_year_win_pct_df_1[1]))
            this_year_matches_1 = (float(this_year_win_pct_df_1[0]) + float(this_year_win_pct_df_1[1]))
            this_year_win_pct_hard_df_1 = yearly_results_1.loc[yearly_results_1.year == float(dt.now().year), 'hard'].values[0].split('/')
            this_year_win_pct_hard_1 = float(this_year_win_pct_hard_df_1[0])/(float(this_year_win_pct_hard_df_1[0]) + float(this_year_win_pct_hard_df_1[1]))
            this_year_matches_hard_1 = (float(this_year_win_pct_hard_df_1[0]) + float(this_year_win_pct_hard_df_1[1]))
            this_year_win_pct_clay_df_1 = yearly_results_1.loc[yearly_results_1.year == float(dt.now().year), 'clay'].values[0].split('/')
            this_year_win_pct_clay_1 = float(this_year_win_pct_clay_df_1[0])/(float(this_year_win_pct_clay_df_1[0]) + float(this_year_win_pct_clay_df_1[1]))
            this_year_matches_clay_1 = (float(this_year_win_pct_clay_df_1[0]) + float(this_year_win_pct_clay_df_1[1]))
            this_year_win_pct_grass_df_1 = yearly_results_1.loc[yearly_results_1.year == float(dt.now().year), 'grass'].values[0].split('/')
            this_year_win_pct_grass_1 = float(this_year_win_pct_grass_df_1[0])/(float(this_year_win_pct_grass_df_1[0]) + float(this_year_win_pct_grass_df_1[1]))
            this_year_matches_grass_1 = (float(this_year_win_pct_grass_df_1[0]) + float(this_year_win_pct_grass_df_1[1]))
        except:
            this_year_win_pct_1 = None
            this_year_matches_1 = None
            this_year_win_pct_hard_1 = None
            this_year_matches_hard_1 = None
            this_year_win_pct_clay_1 = None
            this_year_matches_clay_1 = None
            this_year_win_pct_grass_1 = None
            this_year_matches_grass_1 = None
        try:
            last_year_win_pct_df_1 = yearly_results_1.loc[yearly_results_1.year == (float(dt.now().year) - 1), 'sum.'].values[0].split('/')
            last_year_win_pct_1 = float(last_year_win_pct_df_1[0])/(float(last_year_win_pct_df_1[0]) + float(last_year_win_pct_df_1[1]))
            last_year_matches_1 = (float(last_year_win_pct_df_1[0]) + float(last_year_win_pct_df_1[1]))
            last_year_win_pct_df_hard_1 = yearly_results_1.loc[yearly_results_1.year == (float(dt.now().year) - 1), 'hard'].values[0].split('/')
            last_year_win_pct_hard_1 = float(last_year_win_pct_df_hard_1[0])/(float(last_year_win_pct_df_hard_1[0]) + float(last_year_win_pct_df_hard_1[1]))
            last_year_matches_hard_1 = (float(last_year_win_pct_df_hard_1[0]) + float(last_year_win_pct_df_hard_1[1]))
            last_year_win_pct_df_clay_1 = yearly_results_1.loc[yearly_results_1.year == (float(dt.now().year) - 1), 'clay'].values[0].split('/')
            last_year_win_pct_clay_1 = float(last_year_win_pct_df_clay_1[0])/(float(last_year_win_pct_df_clay_1[0]) + float(last_year_win_pct_df_clay_1[1]))
            last_year_matches_clay_1 = (float(last_year_win_pct_df_clay_1[0]) + float(last_year_win_pct_df_clay_1[1]))
            last_year_win_pct_df_grass_1 = yearly_results_1.loc[yearly_results_1.year == (float(dt.now().year) - 1), 'grass'].values[0].split('/')
            last_year_win_pct_grass_1 = float(last_year_win_pct_df_grass_1[0])/(float(last_year_win_pct_df_grass_1[0]) + float(last_year_win_pct_df_grass_1[1]))
            last_year_matches_grass_1 = (float(last_year_win_pct_df_grass_1[0]) + float(last_year_win_pct_df_grass_1[1]))
        except:
            last_year_win_pct_1 = None
            last_year_matches_1 = None
            last_year_win_pct_hard_1 = None
            last_year_matches_hard_1 = None
            last_year_win_pct_clay_1 = None
            last_year_matches_clay_1 = None
            last_year_win_pct_grass_1 = None
            last_year_matches_grass_1 = None
            last_year_matches_grass_1 = None

        # Player 2

        # Basics
        # Case of player with no data
        try:
            df_2_basics = dfs_indy_2[0]
            df_2_basics.columns = ['Stat', 'Value']
        except:
            continue
        # Case of player with no rank
        try:
            current_rank_2 = float(df_2_basics.loc[df_2_basics.Stat == 'Current Rank', 'Value'].values[0])
        except:
            continue
        best_rank_info_2 = df_2_basics.loc[df_2_basics.Stat == 'Best Rank', 'Value'].values[0].strip(' ').split('(')
        best_rank_2 = float(best_rank_info_2[0])
        best_rank_date_2 = best_rank_info_2[1].strip(')')
        best_rank_date_2 = dt.strptime(best_rank_date_2, date_format)
        time_elapsed_best_rank_2 = (dt.now() - best_rank_date_2).days
        titles_2 = float(df_2_basics.loc[df_2_basics.Stat == 'Titles', 'Value'].values[0])
        slams_2 = float(df_2_basics.loc[df_2_basics.Stat == 'Grand Slams', 'Value'].values[0])
        tour_titles_2 = float(df_2_basics.loc[df_2_basics.Stat == 'Main Tour', 'Value'].values[0])
        masters_2 = float(df_2_basics.loc[df_2_basics.Stat == 'Masters', 'Value'].values[0])
        challengers_2 = float(df_2_basics.loc[df_2_basics.Stat == 'Challengers', 'Value'].values[0])
        futures_2 = float(df_2_basics.loc[df_2_basics.Stat == 'Futures', 'Value'].values[0])
        # Demographic
        df_2_demographic = dfs_indy_2[1]
        df_2_demographic.columns = ['Stat', 'Value']
        age_2 = float(df_2_demographic.loc[df_2_demographic.Stat == 'Age', 'Value'].values[0][:2])
        # Performance by surface
        # Case where no such data exists
        try:
            df_2_surface_perf = dfs_indy_2[3]
            df_2_surface_perf.columns = ['Surface', 'Win_Pct', 'Breakdown']
        except:
            continue
        overall_win_pct_2 = float(df_2_surface_perf.loc[df_2_surface_perf.Surface == 'Overall', 'Win_Pct'].values[0].strip('%'))
        overall_matches_2 = df_2_surface_perf.loc[df_2_surface_perf.Surface == 'Overall', 'Breakdown'].values[0].strip(' ').split('/')
        overall_matches_2 = float(overall_matches_2[0]) + float(overall_matches_2[1])
        hard_win_pct_2 = float(df_2_surface_perf.loc[df_2_surface_perf.Surface == 'Hard', 'Win_Pct'].values[0].strip('%'))
        hard_matches_2 = df_2_surface_perf.loc[df_2_surface_perf.Surface == 'Hard', 'Breakdown'].values[0].strip(' ').split('/')
        hard_matches_2 = float(hard_matches_2[0]) + float(hard_matches_2[1])
        clay_win_pct_2 = float(df_2_surface_perf.loc[df_2_surface_perf.Surface == 'Clay', 'Win_Pct'].values[0].strip('%'))
        clay_matches_2 = df_2_surface_perf.loc[df_2_surface_perf.Surface == 'Clay', 'Breakdown'].values[0].strip(' ').split('/')
        clay_matches_2 = float(clay_matches_2[0]) + float(clay_matches_2[1])
        grass_win_pct_2 = float(df_2_surface_perf.loc[df_2_surface_perf.Surface == 'Grass', 'Win_Pct'].values[0].strip('%'))
        grass_matches_2 = df_2_surface_perf.loc[df_2_surface_perf.Surface == 'Grass', 'Breakdown'].values[0].strip(' ').split('/')
        grass_matches_2 = float(grass_matches_2[0]) + float(grass_matches_2[1])
        # Performance by level
        df_2_level_perf = dfs_indy_2[6]
        df_2_level_perf.columns = ['Level', 'Win_Pct', 'Breakdown']
        top_1_win_pct_2 = float(df_2_level_perf.loc[df_2_level_perf.Level == 'Vs No.1', 'Win_Pct'].values[0].strip('%'))
        top_1_matches_2 = df_2_level_perf.loc[df_2_level_perf.Level == 'Vs No.1', 'Breakdown'].values[0].strip(' ').split('/')
        top_1_matches_2 = float(top_1_matches_2[0]) + float(top_1_matches_2[1])
        top_5_win_pct_2 = float(df_2_level_perf.loc[df_2_level_perf.Level == 'Vs Top.5', 'Win_Pct'].values[0].strip('%'))
        top_5_matches_2 = df_2_level_perf.loc[df_2_level_perf.Level == 'Vs Top.5', 'Breakdown'].values[0].strip(' ').split('/')
        top_5_matches_2 = float(top_5_matches_2[0]) + float(top_5_matches_2[1])
        top_10_win_pct_2 = float(df_2_level_perf.loc[df_2_level_perf.Level == 'Vs Top.10', 'Win_Pct'].values[0].strip('%'))
        top_10_matches_2 = df_2_level_perf.loc[df_2_level_perf.Level == 'Vs Top.10', 'Breakdown'].values[0].strip(' ').split('/')
        top_10_matches_2 = float(top_10_matches_2[0]) + float(top_10_matches_2[1])
        top_20_win_pct_2 = float(df_2_level_perf.loc[df_2_level_perf.Level == 'Vs Top.20', 'Win_Pct'].values[0].strip('%'))
        top_20_matches_2 = df_2_level_perf.loc[df_2_level_perf.Level == 'Vs Top.20', 'Breakdown'].values[0].strip(' ').split('/')
        top_20_matches_2 = float(top_20_matches_2[0]) + float(top_20_matches_2[1])
        top_50_win_pct_2 = float(df_2_level_perf.loc[df_2_level_perf.Level == 'Vs Top.50', 'Win_Pct'].values[0].strip('%'))
        top_50_matches_2 = df_2_level_perf.loc[df_2_level_perf.Level == 'Vs Top.50', 'Breakdown'].values[0].strip(' ').split('/')
        top_50_matches_2 = float(top_50_matches_2[0]) + float(top_50_matches_2[1])
        top_100_win_pct_2 = float(df_2_level_perf.loc[df_2_level_perf.Level == 'Vs Top.100', 'Win_Pct'].values[0].strip('%'))
        top_100_matches_2 = df_2_level_perf.loc[df_2_level_perf.Level == 'Vs Top.100', 'Breakdown'].values[0].strip(' ').split('/')
        top_100_matches_2 = float(top_100_matches_2[0]) + float(top_100_matches_2[1])
        # Serve stats
        serve_stats_2 = dfs_indy_2[8]
        serve_stats_2.columns = ['Stat', 'Value', 'Breakdown']
        aces_per_game_2 = float(serve_stats_2.loc[serve_stats_2.Stat == 'Aces per Game', 'Value'].values[0])
        dfs_per_game_2 = float(serve_stats_2.loc[serve_stats_2.Stat == 'DFs per Game', 'Value'].values[0])
        first_serve_pct_2 = float(serve_stats_2.loc[serve_stats_2.Stat == '1st Serve %', 'Value'].values[0].strip('%'))
        first_serve_win_pct_2 = float(serve_stats_2.loc[serve_stats_2.Stat == '1st Serve Win%', 'Value'].values[0].strip('%'))
        second_serve_win_pct_2 = float(serve_stats_2.loc[serve_stats_2.Stat == '2nd Serve Win%', 'Value'].values[0].strip('%'))
        serve_win_pct_2 = float(serve_stats_2.loc[serve_stats_2.Stat == 'Serve Pts Win%', 'Value'].values[0].strip('%'))
        # Opponent serve stats
        opp_stats_2 = dfs_indy_2[9]
        opp_stats_2.columns = ['Stat', 'Value', 'Breakdown']
        opp_aces_per_game_2 = float(opp_stats_2.loc[opp_stats_2.Stat == 'Opp Aces per Game', 'Value'].values[0])
        opp_dfs_per_game_2 = float(opp_stats_2.loc[opp_stats_2.Stat == 'Opp DFs per Game', 'Value'].values[0])
        first_rtn_win_pct_2 = float(opp_stats_2.loc[opp_stats_2.Stat == '1st Rtn Win%', 'Value'].values[0].strip('%'))
        second_rtn_win_pct_2 = float(opp_stats_2.loc[opp_stats_2.Stat == '2nd Rtn Win%', 'Value'].values[0].strip('%'))
        rtn_win_pct_2 = float(opp_stats_2.loc[opp_stats_2.Stat == 'Rtn Pts Win%', 'Value'].values[0].strip('%'))
        # Break points faced stats
        bp_stats_2 = dfs_indy_2[10]
        bp_stats_2.columns = ['Stat', 'Value', 'Breakdown']
        bp_saved_2 = float(bp_stats_2.loc[bp_stats_2.Stat == 'BPs Saved per game', 'Value'].values[0])
        bp_faced_2 = float(bp_stats_2.loc[bp_stats_2.Stat == 'BPs Faced per game', 'Value'].values[0])
        bp_saved_pct_2 = float(bp_stats_2.loc[bp_stats_2.Stat == 'BP Save %', 'Value'].values[0].strip('%'))
        serve_hold_pct_2 = float(bp_stats_2.loc[bp_stats_2.Stat == 'Service Hold %', 'Value'].values[0].strip('%'))
        # Break points in favor stats
        bp_stats_2 = dfs_indy_2[11]
        bp_stats_2.columns = ['Stat', 'Value', 'Breakdown']
        bp_won_pg_2 = float(bp_stats_2.loc[bp_stats_2.Stat == 'BPs Won per game', 'Value'].values[0])
        bp_opps_2 = float(bp_stats_2.loc[bp_stats_2.Stat == 'BPs Opps per game', 'Value'].values[0])
        bp_won_pct_2 = float(bp_stats_2.loc[bp_stats_2.Stat == 'BP Won %', 'Value'].values[0].strip('%'))
        bp_opp_hold_pct_2 = float(bp_stats_2.loc[bp_stats_2.Stat == 'Opp Hold %', 'Value'].values[0].strip('%'))
        # Yearly results by surface
        yearly_results_2 = dfs_indy_2[14]
        try:
            this_year_win_pct_df_2 = yearly_results_2.loc[yearly_results_2.year == float(dt.now().year), 'sum.'].values[0].split('/')
            this_year_win_pct_2 = float(this_year_win_pct_df_2[0])/(float(this_year_win_pct_df_2[0]) + float(this_year_win_pct_df_2[1]))
            this_year_matches_2 = (float(this_year_win_pct_df_2[0]) + float(this_year_win_pct_df_2[1]))
            this_year_win_pct_hard_df_2 = yearly_results_2.loc[yearly_results_2.year == float(dt.now().year), 'hard'].values[0].split('/')
            this_year_win_pct_hard_2 = float(this_year_win_pct_hard_df_2[0])/(float(this_year_win_pct_hard_df_2[0]) + float(this_year_win_pct_hard_df_2[1]))
            this_year_matches_hard_2 = (float(this_year_win_pct_hard_df_2[0]) + float(this_year_win_pct_hard_df_2[1]))
            this_year_win_pct_clay_df_2 = yearly_results_2.loc[yearly_results_2.year == float(dt.now().year), 'clay'].values[0].split('/')
            this_year_win_pct_clay_2 = float(this_year_win_pct_clay_df_2[0])/(float(this_year_win_pct_clay_df_2[0]) + float(this_year_win_pct_clay_df_2[1]))
            this_year_matches_clay_2 = (float(this_year_win_pct_clay_df_2[0]) + float(this_year_win_pct_clay_df_2[1]))
            this_year_win_pct_grass_df_2 = yearly_results_2.loc[yearly_results_2.year == float(dt.now().year), 'grass'].values[0].split('/')
            this_year_win_pct_grass_2 = float(this_year_win_pct_grass_df_2[0])/(float(this_year_win_pct_grass_df_2[0]) + float(this_year_win_pct_grass_df_2[1]))
            this_year_matches_grass_2 = (float(this_year_win_pct_grass_df_2[0]) + float(this_year_win_pct_grass_df_2[1]))
        except:
            this_year_win_pct_2 = None
            this_year_matches_2 = None
            this_year_win_pct_hard_2 = None
            this_year_matches_hard_2 = None
            this_year_win_pct_clay_2 = None
            this_year_matches_clay_2 = None
            this_year_win_pct_grass_2 = None
            this_year_matches_grass_2 = None
        try:
            last_year_win_pct_df_2 = yearly_results_2.loc[yearly_results_2.year == (float(dt.now().year) - 1), 'sum.'].values[0].split('/')
            last_year_win_pct_2 = float(last_year_win_pct_df_2[0])/(float(last_year_win_pct_df_2[0]) + float(last_year_win_pct_df_2[1]))
            last_year_matches_2 = (float(last_year_win_pct_df_2[0]) + float(last_year_win_pct_df_2[1]))
            last_year_win_pct_df_hard_2 = yearly_results_2.loc[yearly_results_2.year == (float(dt.now().year) - 1), 'hard'].values[0].split('/')
            last_year_win_pct_hard_2 = float(last_year_win_pct_df_hard_2[0])/(float(last_year_win_pct_df_hard_2[0]) + float(last_year_win_pct_df_hard_2[1]))
            last_year_matches_hard_2 = (float(last_year_win_pct_df_hard_2[0]) + float(last_year_win_pct_df_hard_2[1]))
            last_year_win_pct_df_clay_2 = yearly_results_2.loc[yearly_results_2.year == (float(dt.now().year) - 1), 'clay'].values[0].split('/')
            last_year_win_pct_clay_2 = float(last_year_win_pct_df_clay_2[0])/(float(last_year_win_pct_df_clay_2[0]) + float(last_year_win_pct_df_clay_2[1]))
            last_year_matches_clay_2 = (float(last_year_win_pct_df_clay_2[0]) + float(last_year_win_pct_df_clay_2[1]))
            last_year_win_pct_df_grass_2 = yearly_results_2.loc[yearly_results_2.year == (float(dt.now().year) - 1), 'grass'].values[0].split('/')
            last_year_win_pct_grass_2 = float(last_year_win_pct_df_grass_2[0])/(float(last_year_win_pct_df_grass_2[0]) + float(last_year_win_pct_df_grass_2[1]))
            last_year_matches_grass_2 = (float(last_year_win_pct_df_grass_2[0]) + float(last_year_win_pct_df_grass_2[1]))
        except:
            last_year_win_pct_2 = None
            last_year_matches_2 = None
            last_year_win_pct_hard_2 = None
            last_year_matches_hard_2 = None
            last_year_win_pct_clay_2 = None
            last_year_matches_clay_2 = None
            last_year_win_pct_grass_2 = None
            last_year_matches_grass_2 = None
            last_year_matches_grass_2 = None



        # Getting matchup data & surface



        # Obtaining data
        player_1_sub_link = href_1.split('/')[-1]
        player_2_sub_link = href_2.split('/')[-1]
        matchup_link = 'https://matchstat.com/tennis/h2h-odds-bets/' + player_1_sub_link + '/' + player_2_sub_link
        # Getting names
        names = matchup_link.split('/')[-2:]
        player_1_list = names[0].split('%')
        player_1 = ''
        for name in player_1_list:
            player_1 = player_1 + ' ' + remove_numbers(name)
        player_1 = player_1[1:]
        player_1
        player_2_list = names[1].split('%')
        player_2 = ''
        for name in player_2_list:
            player_2 = player_2 + ' ' + remove_numbers(name)
        player_2 = player_2[1:]
        player_2
        matchup_links.append(matchup_link)
        driver.get(matchup_link)
        time.sleep(5)
        html = driver.page_source
        try:
            dfs_matchup = pd.read_html(html)
        except:
            continue
        # Getting correct dfs based on matchup
        if len(dfs_matchup) == 9:
            if len(dfs_matchup[0]) == 5:
                df_ytd = dfs_matchup[0]
                df_ytd.columns = ['Player_1', 'Stat', 'Player_2']
                df_h2h = dfs_matchup[2]
                df_h2h.columns = ['Stat', 'Player_1', 'Player_2']
                df_career_surface = dfs_matchup[4]
                df_career_surface.columns = ['Stat', 'Player_1', 'Player_2']
            else:
                df_ytd = dfs_matchup[1]
                df_ytd.columns = ['Player_1', 'Stat', 'Player_2']
                df_career_surface = dfs_matchup[4]
                df_career_surface.columns = ['Stat', 'Player_1', 'Player_2']
        elif len(dfs_matchup) == 7:
            df_ytd = dfs_matchup[0]
            df_ytd.columns = ['Player_1', 'Stat', 'Player_2']
            # Case of no surface data
            try:
                df_career_surface = dfs_matchup[2]
                df_career_surface.columns = ['Stat', 'Player_1', 'Player_2']
            except:
                pass
        elif len(dfs_matchup) == 8:
            if len(dfs_matchup[0]) == 5:
                df_ytd = dfs_matchup[0]
                df_ytd.columns = ['Player_1', 'Stat', 'Player_2']
                try:
                    df_h2h = dfs_matchup[1]
                    df_h2h.columns = ['Stat', 'Player_1', 'Player_2']
                    df_career_surface = dfs_matchup[3]
                    df_career_surface.columns = ['Stat', 'Player_1', 'Player_2']
                except:
                    df_h2h = dfs_matchup[2]
                    df_h2h.columns = ['Stat', 'Player_1', 'Player_2']
            else:
                df_ytd = dfs_matchup[1]
                df_ytd.columns = ['Player_1', 'Stat', 'Player_2']
                try:
                    df_career_surface = dfs_matchup[3]
                    df_career_surface.columns = ['Stat', 'Player_1', 'Player_2']
                except:
                    df_career_surface = dfs_matchup[4]
                    df_career_surface.columns = ['Stat', 'Player_1', 'Player_2']
        # Getting surface and event of contest
        try:
            surface = driver.find_element(By.CSS_SELECTOR, '[class*="px-3 ms-2 text-uppercase"]').text
            event = driver.find_element(By.CSS_SELECTOR, '[class*="ms-2"]').text.split('-')[0].strip(' ')
        except:
            try:
                surface = driver.find_element(By.CSS_SELECTOR, '[class*="header-court"]').text
                event = driver.find_element(By.CSS_SELECTOR, '[class*="sub-heading"]').text
            except:
                surface = None
                event = None
        # YTD data
        career_win_pct_1 = float(df_ytd.loc[df_ytd.Stat == 'Career W/L', 'Player_1'].values[0].split('%')[0])
        career_win_pct_2 = float(df_ytd.loc[df_ytd.Stat == 'Career W/L', 'Player_2'].values[0].split('%')[0])
        career_matches_1 = df_ytd.loc[df_ytd.Stat == 'Career W/L', 'Player_1'].values[0].split('%')[1].strip(' ()').split('-')
        career_matches_1 = float(career_matches_1[0]) + float(career_matches_1[1])
        career_matches_2 = df_ytd.loc[df_ytd.Stat == 'Career W/L', 'Player_2'].values[0].split('%')[1].strip(' ()').split('-')
        career_matches_2 = float(career_matches_2[0]) + float(career_matches_2[1])
        ytd_win_pct_1 = float(df_ytd.loc[df_ytd.Stat == 'YTD W/L', 'Player_1'].values[0].split('%')[0])
        ytd_win_pct_2 = float(df_ytd.loc[df_ytd.Stat == 'YTD W/L', 'Player_2'].values[0].split('%')[0])
        ytd_matches_1 = df_ytd.loc[df_ytd.Stat == 'YTD W/L', 'Player_1'].values[0].split('%')[1].strip(' ()').split('-')
        ytd_matches_1 = float(ytd_matches_1[0]) + float(ytd_matches_1[1])
        ytd_matches_2 = df_ytd.loc[df_ytd.Stat == 'YTD W/L', 'Player_2'].values[0].split('%')[1].strip(' ()').split('-')
        ytd_matches_2 = float(ytd_matches_2[0]) + float(ytd_matches_2[1])
        ytd_titles_1 = float(df_ytd.loc[df_ytd.Stat == 'YTD Titles', 'Player_1'].values[0])
        ytd_titles_2 = float(df_ytd.loc[df_ytd.Stat == 'YTD Titles', 'Player_2'].values[0])
        # H2H data (some players may not have)
        try:
            h2h_matches = float(df_h2h.loc[df_h2h.Stat == 'All H2H Matches', 'Player_1'].values[0]) + float(df_h2h.loc[df_h2h.Stat == 'All H2H Matches', 'Player_2'].values[0])
            h2h_win_pct_1 = float(df_h2h.loc[df_h2h.Stat == 'All H2H Matches', 'Player_1'].values[0])/h2h_matches
            h2h_win_pct_2 = float(df_h2h.loc[df_h2h.Stat == 'All H2H Matches', 'Player_2'].values[0])/h2h_matches
            if event in ['Wimbledon']:
                h2h_win_pct_length_1 = float(df_h2h.loc[df_h2h.Stat == 'Best of 5 Sets W%', 'Player_1'].values[0].split('%')[0])
                h2h_win_pct_length_2 = float(df_h2h.loc[df_h2h.Stat == 'Best of 5 Sets W%', 'Player_2'].values[0].split('%')[0])
            else:
                h2h_win_pct_length_1 = float(df_h2h.loc[df_h2h.Stat == 'Best of 3 Sets W%', 'Player_1'].values[0].split('%')[0])
                h2h_win_pct_length_2 = float(df_h2h.loc[df_h2h.Stat == 'Best of 3 Sets W%', 'Player_2'].values[0].split('%')[0])
        except:
            h2h_matches = None
            h2h_win_pct_1 = None
            h2h_win_pct_2 = None
            h2h_win_pct_length_1 = None
            h2h_win_pct_length_2 = None
        # Career stats on surface (going to be different based on if they have H2H stuff) & some players may not have
        try:
            try:
                career_win_pct_surface_1 = float(df_career_surface.loc[df_career_surface.Stat == 'Career W/L', 'Player_1'].values[0].split('%')[0])
                career_matches_surface_1 = df_career_surface.loc[df_career_surface.Stat == 'Career W/L', 'Player_1'].values[0].split('%')[1].strip(' ()').split('/')
                career_matches_surface_1 = float(career_matches_surface_1[0]) + float(career_matches_surface_1[1])
            except:
                career_win_pct_surface_1 = float(df_career_surface.loc[df_career_surface.Stat == 'YTD W/L', 'Player_1'].values[0].split('%')[0])
                career_matches_surface_1 = df_career_surface.loc[df_career_surface.Stat == 'YTD W/L', 'Player_1'].values[0].split('%')[1].strip(' ()').split('/')
                career_matches_surface_1 = float(career_matches_surface_1[0]) + float(career_matches_surface_1[1])
            aces_pg_surface_1 = float(df_career_surface.loc[df_career_surface.Stat == 'Aces pg', 'Player_1'].values[0])
            first_serve_pct_surface_1 = float(df_career_surface.loc[df_career_surface.Stat == '1st Serve %', 'Player_1'].values[0].split('%')[0])
            first_serve_win_pct_surface_1 = float(df_career_surface.loc[df_career_surface.Stat == '1st Serve W%', 'Player_1'].values[0].split('%')[0])
            second_serve_win_pct_surface_1 = float(df_career_surface.loc[df_career_surface.Stat == '2nd Serve W%', 'Player_1'].values[0].split('%')[0])
            bp_win_pct_surface_1 = float(df_career_surface.loc[df_career_surface.Stat == 'BPs Won% Total', 'Player_1'].values[0].split('%')[0])
            return_win_pct_surface_1 = float(df_career_surface.loc[df_career_surface.Stat == 'Return Pts W%', 'Player_1'].values[0].split('%')[0])
            slam_win_pct_surface_1 = float(df_career_surface.loc[df_career_surface.Stat == 'Slam W/L', 'Player_1'].values[0].split('%')[0])
            slam_matches_surface_1 = df_career_surface.loc[df_career_surface.Stat == 'Slam W/L', 'Player_1'].values[0].split('%')[1].strip(' ()').split('/')
            slam_matches_surface_1 = float(slam_matches_surface_1[0]) + float(slam_matches_surface_1[1])
            try:
                career_win_pct_surface_2 = float(df_career_surface.loc[df_career_surface.Stat == 'Career W/L', 'Player_2'].values[0].split('%')[0])
                career_matches_surface_2 = df_career_surface.loc[df_career_surface.Stat == 'Career W/L', 'Player_2'].values[0].split('%')[1].strip(' ()').split('/')
                career_matches_surface_2 = float(career_matches_surface_2[0]) + float(career_matches_surface_2[1])
            except:
                career_win_pct_surface_2 = float(df_career_surface.loc[df_career_surface.Stat == 'YTD W/L', 'Player_2'].values[0].split('%')[0])
                career_matches_surface_2 = df_career_surface.loc[df_career_surface.Stat == 'YTD W/L', 'Player_2'].values[0].split('%')[1].strip(' ()').split('/')
                career_matches_surface_2 = float(career_matches_surface_2[0]) + float(career_matches_surface_2[1])
            aces_pg_surface_2 = float(df_career_surface.loc[df_career_surface.Stat == 'Aces pg', 'Player_2'].values[0])
            first_serve_pct_surface_2 = float(df_career_surface.loc[df_career_surface.Stat == '1st Serve %', 'Player_2'].values[0].split('%')[0])
            first_serve_win_pct_surface_2 = float(df_career_surface.loc[df_career_surface.Stat == '1st Serve W%', 'Player_2'].values[0].split('%')[0])
            second_serve_win_pct_surface_2 = float(df_career_surface.loc[df_career_surface.Stat == '2nd Serve W%', 'Player_2'].values[0].split('%')[0])
            bp_win_pct_surface_2 = float(df_career_surface.loc[df_career_surface.Stat == 'BPs Won% Total', 'Player_2'].values[0].split('%')[0])
            return_win_pct_surface_2 = float(df_career_surface.loc[df_career_surface.Stat == 'Return Pts W%', 'Player_2'].values[0].split('%')[0])
            slam_win_pct_surface_2 = float(df_career_surface.loc[df_career_surface.Stat == 'Slam W/L', 'Player_2'].values[0].split('%')[0])
            slam_matches_surface_2 = df_career_surface.loc[df_career_surface.Stat == 'Slam W/L', 'Player_2'].values[0].split('%')[1].strip(' ()').split('/')
            slam_matches_surface_2 = float(slam_matches_surface_2[0]) + float(slam_matches_surface_2[1])
        except:
            career_win_pct_surface_1 = None
            career_matches_surface_1 = None
            career_matches_surface_1 = None
            aces_pg_surface_1 = None
            first_serve_pct_surface_1 = None
            first_serve_win_pct_surface_1 = None
            second_serve_win_pct_surface_1 = None
            bp_win_pct_surface_1 = None
            return_win_pct_surface_1 = None
            slam_win_pct_surface_1 = None
            slam_matches_surface_1 = None
            slam_matches_surface_1 = None
            career_win_pct_surface_2 = None
            career_matches_surface_2 = None
            career_matches_surface_2 = None
            aces_pg_surface_2 = None
            first_serve_pct_surface_2 = None
            first_serve_win_pct_surface_2 = None
            second_serve_win_pct_surface_2 = None
            bp_win_pct_surface_2 = None
            return_win_pct_surface_2 = None
            slam_win_pct_surface_2 = None
            slam_matches_surface_2 = None
            slam_matches_surface_2 = None


        # Filtering out data that isn't relevant to the surface/player

        # Relevant rank win percentage
        if current_rank_1 == 1:
            rank_win_pct_2 = top_1_win_pct_2
            rank_matches_2 = top_1_matches_2
        elif current_rank_1 <= 5:
            rank_win_pct_2 = top_5_win_pct_2
            rank_matches_2 = top_5_matches_2
        elif current_rank_1 <= 10:
            rank_win_pct_2 = top_10_win_pct_2
            rank_matches_2 = top_10_matches_2
        elif current_rank_1 <= 100:
            rank_win_pct_2 = top_100_win_pct_2
            rank_matches_2 = top_100_matches_2
        else:
            rank_win_pct_2 = None
            rank_matches_2 = None

        if current_rank_2 == 1:
            rank_win_pct_1 = top_1_win_pct_1
            rank_matches_1 = top_1_matches_1
        elif current_rank_2 <= 5:
            rank_win_pct_1 = top_5_win_pct_1
            rank_matches_1 = top_5_matches_1
        elif current_rank_2 <= 10:
            rank_win_pct_1 = top_10_win_pct_1
            rank_matches_1 = top_10_matches_1
        elif current_rank_2 <= 100:
            rank_win_pct_1 = top_100_win_pct_1
            rank_matches_1 = top_100_matches_1
        else:
            rank_win_pct_1 = None
            rank_matches_1 = None
        date = dt.today().strftime("%B %d, %Y")
        
        # Appending data to dictionary
        data_dict['date'].append(date)
        data_dict['player_1'].append(player_1)
        data_dict['player_2'].append(player_2)
        data_dict['current_rank_1'].append(current_rank_1)
        data_dict['current_rank_2'].append(current_rank_2)
        data_dict['best_rank_1'].append(best_rank_1)
        data_dict['best_rank_2'].append(best_rank_2)
        data_dict['time_elapsed_best_rank_1'].append(time_elapsed_best_rank_1)
        data_dict['time_elapsed_best_rank_2'].append(time_elapsed_best_rank_2)
        data_dict['titles_1'].append(titles_1)
        data_dict['titles_2'].append(titles_2)
        data_dict['slams_1'].append(slams_1)
        data_dict['slams_2'].append(slams_2)
        data_dict['tour_titles_1'].append(tour_titles_1)
        data_dict['tour_titles_2'].append(tour_titles_2)
        data_dict['masters_1'].append(masters_1)
        data_dict['masters_2'].append(masters_2)
        data_dict['challengers_1'].append(challengers_1)
        data_dict['challengers_2'].append(challengers_2)
        data_dict['futures_1'].append(futures_1)
        data_dict['futures_2'].append(futures_2)
        data_dict['age_1'].append(age_1)
        data_dict['age_2'].append(age_2)
        data_dict['rank_win_pct_1'].append(rank_win_pct_1)
        data_dict['rank_win_pct_2'].append(rank_win_pct_2)
        data_dict['rank_matches_1'].append(rank_matches_1)
        data_dict['rank_matches_2'].append(rank_matches_2)
        data_dict['aces_per_game_1'].append(aces_per_game_1)
        data_dict['aces_per_game_2'].append(aces_per_game_2)
        data_dict['dfs_per_game_1'].append(dfs_per_game_1)
        data_dict['dfs_per_game_2'].append(dfs_per_game_2)
        data_dict['first_serve_pct_1'].append(first_serve_pct_1)
        data_dict['first_serve_pct_2'].append(first_serve_pct_2)
        data_dict['first_serve_win_pct_1'].append(first_serve_win_pct_1)
        data_dict['first_serve_win_pct_2'].append(first_serve_win_pct_2)
        data_dict['second_serve_win_pct_1'].append(second_serve_win_pct_1)
        data_dict['second_serve_win_pct_2'].append(second_serve_win_pct_2)
        data_dict['serve_win_pct_1'].append(serve_win_pct_1)
        data_dict['serve_win_pct_2'].append(serve_win_pct_2)
        data_dict['bp_saved_1'].append(bp_saved_1)
        data_dict['bp_saved_2'].append(bp_saved_2)
        data_dict['bp_faced_1'].append(bp_faced_1)
        data_dict['bp_faced_2'].append(bp_faced_2)
        data_dict['bp_saved_pct_1'].append(bp_saved_pct_1)
        data_dict['bp_saved_pct_2'].append(bp_saved_pct_2)
        data_dict['serve_hold_pct_1'].append(serve_hold_pct_1)
        data_dict['serve_hold_pct_2'].append(serve_hold_pct_2)
        data_dict['bp_won_pg_1'].append(bp_won_pg_1)
        data_dict['bp_won_pg_2'].append(bp_won_pg_2)
        data_dict['bp_opps_1'].append(bp_opps_1)
        data_dict['bp_opps_2'].append(bp_opps_2)
        data_dict['bp_won_pct_1'].append(bp_won_pct_1)
        data_dict['bp_won_pct_2'].append(bp_won_pct_2)
        data_dict['bp_opp_hold_pct_1'].append(bp_opp_hold_pct_1)
        data_dict['bp_opp_hold_pct_2'].append(bp_opp_hold_pct_2)
        data_dict['career_win_pct_1'].append(career_win_pct_1)
        data_dict['career_win_pct_2'].append(career_win_pct_2)
        data_dict['career_matches_1'].append(career_matches_1)
        data_dict['career_matches_2'].append(career_matches_2)
        data_dict['ytd_win_pct_1'].append(ytd_win_pct_1)
        data_dict['ytd_win_pct_2'].append(ytd_win_pct_2)
        data_dict['ytd_matches_1'].append(ytd_matches_1)
        data_dict['ytd_matches_2'].append(ytd_matches_2)
        data_dict['ytd_titles_1'].append(ytd_titles_1)
        data_dict['ytd_titles_2'].append(ytd_titles_2)
        data_dict['h2h_matches'].append(h2h_matches)
        data_dict['h2h_win_pct_1'].append(h2h_win_pct_1)
        data_dict['h2h_win_pct_2'].append(h2h_win_pct_2)
        data_dict['h2h_win_pct_length_1'].append(h2h_win_pct_length_1)
        data_dict['h2h_win_pct_length_2'].append(h2h_win_pct_length_2)
        data_dict['career_win_pct_surface_1'].append(career_win_pct_surface_1)
        data_dict['career_win_pct_surface_2'].append(career_win_pct_surface_2)
        data_dict['aces_pg_surface_1'].append(aces_pg_surface_1)
        data_dict['aces_pg_surface_2'].append(aces_pg_surface_2)
        data_dict['first_serve_pct_surface_1'].append(first_serve_pct_surface_1)
        data_dict['first_serve_pct_surface_2'].append(first_serve_pct_surface_2)
        data_dict['first_serve_win_pct_surface_1'].append(first_serve_win_pct_surface_1)
        data_dict['first_serve_win_pct_surface_2'].append(first_serve_win_pct_surface_2)
        data_dict['second_serve_win_pct_surface_1'].append(second_serve_win_pct_surface_1)
        data_dict['second_serve_win_pct_surface_2'].append(second_serve_win_pct_surface_2)
        data_dict['bp_win_pct_surface_1'].append(bp_win_pct_surface_1)
        data_dict['bp_win_pct_surface_2'].append(bp_win_pct_surface_2)
        data_dict['return_win_pct_surface_1'].append(return_win_pct_surface_1)
        data_dict['return_win_pct_surface_2'].append(return_win_pct_surface_2)
        data_dict['slam_win_pct_surface_1'].append(slam_win_pct_surface_1)
        data_dict['slam_win_pct_surface_2'].append(slam_win_pct_surface_2)
        data_dict['slam_matches_surface_1'].append(slam_matches_surface_1)
        data_dict['slam_matches_surface_2'].append(slam_matches_surface_2)
        

    matchup_df = pd.DataFrame(data_dict)
    matchup_df['result'] = -2

    driver.quit()

    return matchup_df

def append_matchups(matchup_df):

    # Dropping duplicate matches

    # Calling in existing matchups
    matchup_df_old = pd.read_csv('tennis_matchup_data.csv', index_col = 0)
    matchup_df_new = pd.concat([matchup_df_old, matchup_df])
    matchup_df_new = matchup_df_new.drop_duplicates(subset = ['player_1', 'date']).reset_index(drop = True)
    drop_list = []
    # Dropping matchups if they occur w/in 5 days of each other and have same combatants
    for index, row in matchup_df_new.iterrows():
        same_matchup_df = matchup_df_new[((matchup_df_new.player_1 == row.player_1) | (matchup_df_new.player_2 == row.player_1)) & 
                                    ((matchup_df_new.player_1 == row.player_2) | (matchup_df_new.player_2 == row.player_2))]
        if len(same_matchup_df) == 1:
            continue
        else:
            same_matchup_df['date'] = same_matchup_df.date.apply(lambda x: dt.strptime(x, "%B %d, %Y"))
            date = same_matchup_df.iloc[-1, 0]
            same_matchup_df['DAY_DIFF'] = same_matchup_df.date - date
            same_matchup_df['DAY_DIFF'] = same_matchup_df['DAY_DIFF'].apply(lambda x: x.days)
            drop_list = []
            for index, row in same_matchup_df.iterrows():
                if (row.DAY_DIFF > -5) & (row.DAY_DIFF < 0):
                    drop_list.append(index)
    matchup_df_new = matchup_df_new.drop(drop_list).reset_index(drop = True)

    # Saving updated matchups
    matchup_df_new.to_csv('tennis_matchup_data.csv')

    return

