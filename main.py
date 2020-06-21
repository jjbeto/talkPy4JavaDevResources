import pandas as pd

url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series'


def cleanup_country_data(df):
    """
    Cleanup country information using alpha-2 code only
    """
    countries = pd.read_csv('countries/list.csv')
    country_labels = pd.read_csv('countries/labels.csv')

    # dict with all countries (and its possible extra lables)
    alpha2 = countries.set_index('name')['alpha-2'].to_dict()
    alpha2.update(country_labels.set_index('label')['alpha-2'].to_dict())

    # replace country codes
    filtered = df.filter(like='country')
    df[filtered.columns] = filtered.replace(alpha2)

    # remove all items that is not recognized as countries (don't use alpha-2 code)
    df.drop(df[df.country.str.len() > 2].index, inplace=True)

    # sum up all values
    return df.groupby('country').sum()


def load_data(filename):
    """
    Loads data provided by John Hopkins
    """
    df = pd.read_csv(f'{url}/{filename}')
    df = df.rename(columns={'Country/Region': 'country', 'Province/State': 'state'})
    # overwrite country using the province (when not null)
    df['country'] = df.apply(lambda each: each['country'] if pd.isnull(each['state']) else each['state'], axis=1)
    df = df.drop(columns=['state', 'Lat', 'Long'])
    # drop rows of nan
    df = df.dropna(how='all')

    print(f'Found {len(df)} entries for {filename}')
    return df


if __name__ == '__main__':
    # list all target files to download
    confirmed = 'time_series_covid19_confirmed_global.csv'
    deaths = 'time_series_covid19_deaths_global.csv'
    recovered = 'time_series_covid19_recovered_global.csv'

    for file in (confirmed, deaths, recovered):
        try:
            df = load_data(file)
            df = cleanup_country_data(df)
            if len(df):  # do overwrite data only if there is data to be stored
                df.to_csv(f'johns_hopkins/{file}')
        except Exception as e:
            print(e)
