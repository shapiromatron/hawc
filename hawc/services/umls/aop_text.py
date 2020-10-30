# -*- coding: utf-8 -*-
"""Turn AOP data into dataframe then find entities.

@author: scott
"""

import pandas as pd
import requests
import json
import os.path

from utils import loadUMLSLinker, loadDocs
from umls_linking import run_tiered_analysis


def get_aop_text():
    """Query aopwiki.org and pull text."""
    kes = []
    mies = []
    aos = []
    name = []
    short_name = []
    for i in range(3, 361+1):
        url = f'https://aopwiki.org/aops/{i}.json'
        print(f'Pulling AOP ID {i}...')
        r = requests.get(url)
        if r.status_code != 200:
            continue
        content = json.loads(r.text)
        if 'id' not in content:
            continue
        name.append(content['title'].strip())
        short_name.append(content['short_name'].strip())
        mies += [j['event'].strip() for j in content['aop_mies']]
        kes += [j['event'].strip() for j in content['aop_kes']]
        aos += [j['event'].strip() for j in content['aop_aos']]
    df = pd.concat([pd.DataFrame({'text': kes, 'type': 'kes'}),
                    pd.DataFrame({'text': mies, 'type': 'mies'}),
                    pd.DataFrame({'text': aos, 'type': 'aos'}),
                    # pd.DataFrame({'text': name, 'type': 'name'}),
                    # pd.DataFrame({'text': short_name, 'type': 'short_name'}),
                    ]).drop_duplicates()
    return df


def main() -> pd.DataFrame:
    """Call methods and loading data."""
    filename = 'aop_text.csv'
    if os.path.isfile(filename):
        df = pd.read_csv(filename)
    else:
        df = get_aop_text()
        df.to_csv(filename, index=False)

    # load model
    print('Loading models...')
    try:
        linker, nlp = loadUMLSLinker()
    except ConnectionError:
        linker, nlp = loadUMLSLinker()
    docs = loadDocs(pd.concat(
        [df['text']]),
        nlp)

    # map entities
    df_tier = run_tiered_analysis(df['text'], linker, nlp, docs,
                                  string=True, strict_matching=False)
    df = pd.concat([df, df_tier], axis=1)

    df = df[['text', 'text_UMLS', 'text_Tier', 'type']]

    return df


if __name__ == "__main__":
    df = main()
    df.to_csv('aop_text_results.csv', index=False)
