import logging
import re
import textwrap

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from nltk.tokenize import word_tokenize
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.manifold import TSNE

logger = logging.getLogger(__name__)

stopwords_ = None
stemmer = None
re_words = re.compile(r"[a-zA-Z]+")


def _load_nltk_data():
    """
    Lazy load nltk data from disk, but only when it's needed
    """
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer

    global stopwords_
    global stemmer

    logger.info("Lazy loading nltk data from disk")
    stopwords_ = set(stopwords.words("english"))
    stemmer = PorterStemmer()


def stem_and_tokenize(words: str) -> str:
    """
    Tokenize, remove stopwords, temp, and remove non-numeric or short values in a string.
    """
    tokens = word_tokenize(words)
    tokens = [token for token in tokens if token not in stopwords_]
    tokens = [stemmer.stem(token) for token in tokens]
    tokens = [token for token in tokens if re_words.search(token) and len(token) > 3]
    return " ".join(tokens)


def textwrapper(text: str) -> str:
    return "<br>".join(textwrap.wrap(text))


def _get_nmf_topics(term_map, vectorizer, n_top_words: int = 10) -> pd.DataFrame:
    feat_names = vectorizer.get_feature_names_out()
    words = []
    for i in range(term_map.shape[1]):
        words_ids = term_map[:, i].argsort()[-n_top_words:][::-1]
        words.append(" ".join([feat_names[key] for key in words_ids]))
    return pd.DataFrame(data=dict(topic=list(range(term_map.shape[1])), top_words=words))


def topic_model_tsne(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Given an input dataframe containing a text column, using TFIDF build an NMF topic model.
    Then, reduce topics using TSNE to allow for displaying via a scatterplot.

    Returns two dataframes, the first contains reference-specific information, and the second contains
    topic-specific information.
    """
    if "text" not in df.columns:
        raise ValueError('Data frame must contain a "text" column')

    if stopwords_ is None or stemmer is None:
        _load_nltk_data()

    logger.info(f"Training topic model with {df.shape[0]} references")

    df.loc[:, "text"] = df.text.apply(stem_and_tokenize)
    tfidf_transformer = TfidfTransformer()
    vectorizer = CountVectorizer(analyzer="word", max_features=10000)
    x_counts = vectorizer.fit_transform(df.text)
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(x_counts)
    n_topics = int(max(min(30, np.sqrt(df.shape[0])), 10))
    model = NMF(n_components=n_topics, random_state=1, l1_ratio=0.5, init="nndsvdar")
    term_maps = model.fit_transform(X_train_tfidf.T)
    nmf_embedded = TSNE(
        n_components=2, perplexity=20, init="random", learning_rate="auto"
    ).fit_transform(model.components_.T)
    df.drop(columns=["text"], inplace=True)

    df.loc[:, "max_topic"] = model.components_.argmax(axis=0)
    df.loc[:, "tsne_x"] = nmf_embedded[:, 0]
    df.loc[:, "tsne_y"] = nmf_embedded[:, 1]

    topics_df = _get_nmf_topics(term_maps, vectorizer)

    return (df, topics_df)


def tsne_to_scatterplot(data: pd.DataFrame) -> go.Figure:
    """
    Build the plotly figure we'll use to display the figure
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            name="",
            x=data["df"].tsne_x,
            y=data["df"].tsne_y,
            text=data["df"].title,
            marker=dict(
                size=9,
                color=data["df"].max_topic,
                colorscale="rainbow",
                line_width=1,
                line_color="grey",
            ),
            mode="markers",
            hovertemplate="%{text}",
        )
    )
    fig.update_layout(
        autosize=True,
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20),  # noqa: E741
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    return fig
