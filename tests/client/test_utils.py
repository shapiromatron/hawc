import numpy as np
import pandas as pd

from hawc_client.utils import fuzz_match


def test_fuzz_match():
    df1 = pd.DataFrame(data={"key": [1, 2], "text": ["hello world", "goodbye world"]})
    df2 = pd.DataFrame(data={"key": [3, 4], "text": ["hello world", "goodbye waldo"]})
    resp = fuzz_match(
        df1, df2, src_match_column="text", dst_match_column="text", dst_key_column="key"
    )
    assert resp.matched_key.values.tolist() == [3, 4]
    assert np.allclose(resp.matched_score.values, [100, 84.6], atol=1.0)
    assert resp.matched_text.values.tolist() == ["hello world", "goodbye waldo"]
