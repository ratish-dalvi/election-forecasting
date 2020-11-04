# POLL SCRAPING CODE COPIED FROM Joey Richards repo:
# https://github.com/jwrichar/bayesian_election_forecasting
#

import os
import pathlib
import urllib3
from os.path import exists as path_exists

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

urllib3.disable_warnings()

file_path = pathlib.Path(__file__).parent.absolute()
data_path = os.path.abspath('%s/../data' % file_path)

STATE_ABBREVS = np.loadtxt(
    os.path.join(data_path,
                 'state_abbreviations.txt'),
    usecols=(1, ), dtype=np.str)


def get_polls(year, refresh=False):
    polls_dir = os.path.join(data_path, "polls_%s" % year)

    if refresh or not path_exists(polls_dir):
        download_polls(year)
    else:
        print("Using pre-downloaded polls")

    state_polls = {}
    for abbr in STATE_ABBREVS:
        fname = "%s/%s_%s.dat" % (polls_dir, abbr, year)
        state_polls[abbr] = pd.read_csv(fname) if path_exists(fname) else pd.DataFrame()

    national_polls = pd.read_csv("%s/national_%s.dat" % (polls_dir, year))

    return (state_polls, national_polls)


def past_state_election_results():
    def extract_dem_share(df):
        df_dem = df[df.party == 'democrat']
        df_rep = df[df.party == 'republican']

        if len(df_dem) == 0:
            return 0.0
        return (df_dem.candidatevotes.iloc[0]) / (df_dem.candidatevotes.iloc[0] + df_rep.candidatevotes.iloc[0])

    df = pd.read_csv("../data/statewise-results-1976-2016-president.csv")
    return df.groupby(['state_po', 'year']).apply(extract_dem_share)


def download_polls(year):
    ''' Load and write all state-wise polling data for year '''

    master_table = _get_rcp_master_table()

    polls_dir = os.path.join(data_path, "polls_%s" % year)
    if not os.path.exists(polls_dir):
        os.mkdir(polls_dir)

    # State-level polls
    for abbr in STATE_ABBREVS:

        print('Getting polls for state %s' % abbr)

        poll_url = _get_state_poll_url(abbr, year, master_table)

        if not poll_url:
            continue

        http = urllib3.PoolManager()
        html_doc = http.request('GET', poll_url)
        page = BeautifulSoup(html_doc.data, features="lxml")

        data = _all_state_data_to_df(page)

        data.to_csv('%s/polls_%s/%s_%s.dat' % (
            data_path, year, abbr, year), index=False)

    # National polls for general election:
    print("Getting national level polls")
    nat_poll_url = _get_national_poll_url(year, master_table)

    http = urllib3.PoolManager()
    html_doc = http.request('GET', nat_poll_url)
    page = BeautifulSoup(html_doc.data, features="lxml")

    data = _all_state_data_to_df(page)

    data.to_csv('%s/polls_%s/national_%s.dat' % (
        data_path, year, year), index=False)


# Private functions:

def _get_rcp_master_table():
    ''' Read RCP latest_polls html table. '''

    http = urllib3.PoolManager()
    html_doc = http.request(
        'GET',
        'http://www.realclearpolitics.com/epolls/latest_polls/president/#')

    page = BeautifulSoup(html_doc.data, features="lxml")
    return str(page.find(id="table-1"))


def _get_state_poll_url(abbr, year, master_table):
    ''' Get URL to state-level polls '''

    # Find URL string
    start = master_table.find('epolls/%s/president/%s' % (year, abbr.lower()))
    if(start == -1):
        print('No polls found for %s, skipping.' % abbr)
        return ''

    end = start + master_table[start::].find("html") + 4

    url = "http://www.realclearpolitics.com/%s%s" % \
        (master_table[start:end], '#polls')
    return url


def _get_national_poll_url(year, master_table):
    ''' Get URL to national-level poll '''

    # Find URL string
    start = master_table.find('epolls/%s/president/us/general_election' % year)
    if(start == -1):
        print('No national polls found, skipping.')
        return ''

    end = start + master_table[start::].find("html") + 4

    url = "http://www.realclearpolitics.com/%s%s" % \
        (master_table[start:end], '#polls')
    return url


def _all_state_data_to_df(page):
    ''' Get all state polling data from page and comple in dataframe '''

    # Compile all poll data for the state:
    poll_names = []
    poll_dates = []
    dem_perc = []
    rep_perc = []
    poll_sizes = []

    header = page.find(id="polling-data-full").find_all('tr')[0]
    # Does the democrat appear first in the table?
    dem_first = (str(header).find("(D)")) < str(header).find("(R)")

    poll_html_list = [
        x.find_all("td") for x in
        page.find(id="polling-data-full").find_all('tr')
    ][1::]

    for poll_html in poll_html_list:

        if dem_first:
            poll_dict = dict(
                zip(["poll",
                     "dates",
                     "size",
                     "error",
                     "dem",
                     "rep",
                     "margin"],
                    [y.get_text() for y in poll_html]))
        else:
            poll_dict = dict(
                zip(["poll",
                     "dates",
                     "size",
                     "error",
                     "rep",
                     "dem",
                     "margin"],
                    [y.get_text() for y in poll_html]))

        # Overwrite pollster with properly parsed name:
        try:
            pollster_name = poll_html[0].find(
                None, {"class": "normal_pollster_name"})
            poll_dict['poll'] = pollster_name.text
        except AttributeError:
            # Skip non-polls (e.g., RCP Average)
            continue

        # If no sample size given, skip:
        if poll_dict['size'] in ['LV', 'RV', '--']:
            continue

        # Append poll info to lists:
        poll_names.append(poll_dict["poll"].rstrip("*"))
        poll_dates.append(poll_dict["dates"])
        rep_perc.append(float(poll_dict["rep"]))
        dem_perc.append(float(poll_dict["dem"]))
        poll_sizes.append(int(poll_dict["size"].lstrip().split(" ")[0]))

    data = pd.DataFrame(list(
        zip(poll_names, poll_dates, rep_perc, dem_perc, poll_sizes)),
        columns=['Name', 'Date', 'Republican', 'Democrat', 'Size'])

    return data

if __name__ == '__main__':
    download_polls(2020)
