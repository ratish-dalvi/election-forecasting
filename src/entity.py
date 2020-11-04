import pandas as pd

from .helpers import process_poll_date
from .config import ELECTION_DATE


class Entity(object):
    def __init__(self, df_polls=None):
        if df_polls is not None:
            self.load_polls_from_dataframe(df_polls)

    def load_polls_from_dataframe(self, df):
        self.polls = [
            Poll(row.Name, row.Date, row.Size, row.Democrat, row.Republican)
            for _, row in df.iterrows()
        ]


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
