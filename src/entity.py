import pandas as pd
import numpy as np

from helpers import process_poll_date
from config import ELECTION_DATE


class Entity(object):
    def __init__(self, df_polls=None):
        if df_polls is not None:
            self.load_polls_from_dataframe(df_polls)

    def load_polls_from_dataframe(self, df):
        self.polls = [
            Poll(row.Name, row.Date, row.Size, row.Democrat, row.Republican)
            for _, row in df.iterrows()
        ]

    def get_weighted_average_poll_dem_share(self, months):
        start_dt = pd.to_datetime('2020-11-03') - pd.Timedelta(days=months*30)
        polls = [p for p in self.polls if p.date > start_dt]
        if len(polls) == 0:
            return np.nan
        return 1.0 * sum([p.p_dem * p.size for p in polls]) / sum([p.size for p in polls])


class National(Entity):
    def __init__(self, df_polls, df_past_elections=None):
        super().__init__(df_polls)


class State(Entity):
    def __init__(self, abbr, df_polls, df_past_elections):
        self.abbr = abbr
        super().__init__(df_polls)
        self.df_past_elections = df_past_elections

    def get_dem_share(self, year):
        return self.df_past_elections.loc[year]

    def is_blue(self, year):
        return self.get_dem_share(year) > 0.5


class Poll(object):
    def __init__(self, name, date, size, p_dem, p_rep):
        self.name = name
        self.size = size
        self.p_dem = p_dem / (p_dem + p_rep)
        self.p_rep = 1 - self.p_dem
        self.date = process_poll_date(date)
        self.months_from_election = self.get_months_from_election()

    def get_months_from_election(self):
        x = (pd.to_datetime(ELECTION_DATE) - self.date).days / 30.0
        return 0.2 if x < 0 else x
