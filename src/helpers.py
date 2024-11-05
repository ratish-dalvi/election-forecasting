import pandas as pd


def process_poll_date(x):
    """
    Input is of type '9/30 - 10/3'
    """
    date_st, date_end = x.split(" - ")
    return pd.to_datetime(date_st + "/2024")


def pretty_print(x):
    print(vars(x))
    for p in x.polls:
        print(vars(p))
