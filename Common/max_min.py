import pandas as pd


def get_max(df, var):
    df['is_max'] = (df[var] > df[var].shift(1)) \
                   & (df[var] > df[var].shift(2)) \
                   & (df[var] > df[var].shift(3)) \
                   & (df[var] > df[var].shift(4)) \
                   & (df[var] > df[var].shift(-4)) \
                   & (df[var] > df[var].shift(-3)) \
                   & (df[var] > df[var].shift(-2)) \
                   & (df[var] > df[var].shift(-1))


def get_min(df, var):
    df['is_min'] = (df[var] < df[var].shift(1)) \
                   & (df[var] < df[var].shift(2)) \
                   & (df[var] < df[var].shift(3)) \
                   & (df[var] < df[var].shift(4)) \
                   & (df[var] < df[var].shift(-4)) \
                   & (df[var] < df[var].shift(-3)) \
                   & (df[var] < df[var].shift(-2)) \
                   & (df[var] < df[var].shift(-1))


def get_max_and_min(df):
    dfmym = df.loc[df.is_max | df.is_min]
    dfmym = clean_repeat_points(dfmym)
    dfmym = clean_repeat_points(dfmym)
    return dfmym


def clean_repeat_points(dfmym):
    dfmym = dfmym[((pd.isnull(dfmym['is_min'].shift(1)) | pd.isnull(dfmym['is_min'].shift(-1)))
                   | (((dfmym['is_max']) \
                       & (((dfmym['is_min'].shift(1)) \
                           | (dfmym['High'] > dfmym['High'].shift(1))) \
                          & ((dfmym['is_min'].shift(-1)) \
                             | (dfmym['High'] > dfmym['High'].shift(-1))))) \
                      | ((dfmym['is_min']) \
                         & (((dfmym['is_max'].shift(1)) \
                             | (dfmym['Low'] < dfmym['Low'].shift(1))) \
                            & ((dfmym['is_max'].shift(-1)) \
                               | (dfmym['Low'] < dfmym['Low'].shift(-1)))))))]
    return dfmym


def get_all_fail(dfmym):
    dfmym['fail'] = (((dfmym['is_min']) & (dfmym['High'].shift(1) <= dfmym['High'].shift(3)) \
                      & (dfmym['Low'].shift(2) > dfmym['Low'].shift(4)) \
                      & (dfmym['Low'] < dfmym['Low'].shift(2)))
                     | ((dfmym['is_max']) & (dfmym['Low'].shift(1) >= dfmym['Low'].shift(3)) \
                        & (dfmym['High'].shift(2) < dfmym['High'].shift(4)) \
                        & (dfmym['High'] > dfmym['High'].shift(2))))


def get_all_double_rs(dfmym):
    dfmym['double_rs'] = (
            ((dfmym['is_min']) & (abs((dfmym['Low'] - dfmym['Low'].shift(2)) / dfmym['Low'].shift(2)) < 0.02))
            | ((dfmym['is_max']) & (abs((dfmym['High'] - dfmym['High'].shift(2)) / dfmym['High'].shift(2)) < 0.02)))


def get_all_price_reversion(dfmym):
    dfmym['reversion'] = (((dfmym['is_min']) \
                         & (dfmym['Low'].shift(2) > dfmym['Low'].shift(4)) \
                         & (dfmym['Low'] < dfmym['Low'].shift(2)))
                        | ((dfmym['is_max']) \
                           & (dfmym['High'].shift(2) < dfmym['High'].shift(4)) \
                           & (dfmym['High'] > dfmym['High'].shift(2))))
