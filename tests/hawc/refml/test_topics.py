import pandas as pd
import pytest

from hawc.refml import topics


@pytest.fixture(scope="session")
def load_nltk_data():
    assert topics.stopwords_ is None
    topics._load_nltk_data()
    assert topics.stopwords_ is not None


def test_stem_and_tokenize(load_nltk_data):
    data_checks = [
        (
            "Alice opened the door and found that it led into a small passage,",
            "alic open door found small passag",
        ),
        (
            'However, this bottle was not marked "poison" so Alice ventured to taste it, and finding it very nice',
            "howev bottl mark poison alic ventur tast find nice",
        ),
    ]
    for raw, processed in data_checks:
        assert topics.stem_and_tokenize(raw) == processed


def test_textwrapper():
    raw = "Soon her eye fell on a little glass box that was lying under the table: she opened it, and found in it a very small cake, on which the words “EAT ME” were beautifully marked in currants."
    processed = "Soon her eye fell on a little glass box that was lying under the<br>table: she opened it, and found in it a very small cake, on which the<br>words “EAT ME” were beautifully marked in currants."
    assert topics.textwrapper(raw) == processed


class TestTopicModelTsne:
    def test_failure(self, load_nltk_data):
        df = pd.DataFrame(data=[dict(test="test")])
        with pytest.raises(ValueError) as err:
            topics.topic_model_tsne(df)
        assert err.value.args[0] == 'Data frame must contain a "text" column'

    def test_success(self, load_nltk_data):
        input_df = pd.Series(
            data=[
                "Down the Rabbit-Hole",
                "The Pool of Tears",
                "A Caucus-Race and a Long Tale",
                "The Rabbit Sends in a Little Bill",
                "Advice from a Caterpillar",
                "Pig and Pepper",
                "A Mad Tea-Party",
                "The Queen’s Croquet-Ground",
                "The Mock Turtle’s Story",
                "The Lobster Quadrille",
                "Who Stole the Tarts?",
                "Alice’s Evidence",
                "The Looking-Glass House",
                "The Garden of Live Flowers",
                "Looking-Glass Insects",
                "Tweedledum and Tweedledee",
                "Jam Every Other Day",
                "Humpty Dumpty",
                "The Lion and the Unicorn",
                "The Great Art of Riding",
                "Queen Alice",
                "Shaking and Waking",
                "Who Dreamed It?",
            ],
            name="text",
        ).to_frame()
        df, df_topics = topics.topic_model_tsne(input_df)

        assert df.shape == (23, 3)
        assert set(df.columns.tolist()) == {"max_topic", "tsne_x", "tsne_y"}

        assert df_topics.shape == (10, 2)
        assert set(df_topics.columns.tolist()) == {"topic", "top_words"}
