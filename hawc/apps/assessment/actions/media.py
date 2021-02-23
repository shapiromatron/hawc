from pathlib import Path

import pandas as pd
from django.conf import settings


def media_metadata_report() -> pd.DataFrame:
    """Return tabular report on all media files which exist in the upload area of HAWC for review.

    Returns:
        pd.DataFrame: a dataframe of content
    """
    # grab all files recursively in the media root path
    path = Path(settings.MEDIA_ROOT)
    files = [f for f in path.glob("**/*") if f.is_file()]

    # process metadata for each file individually
    data = []
    for idx, fn in enumerate(files):
        metadata = fn.stat()
        data.append(
            dict(
                path_index=idx,
                full_path=str(fn),
                uri=fn.as_uri(),
                extension=fn.suffix,
                name=fn.name,
                size_mb=metadata.st_size,
                created=metadata.st_ctime,
                modified=metadata.st_mtime,
            )
        )

    # build dataframe
    df = pd.DataFrame(data)

    # transform columns using vectorized operations
    df.full_path = df.full_path.str.replace(str(path), "")
    df.uri = settings.MEDIA_URL + df.uri.str.replace("file://", "").str.replace(str(path) + "/", "")
    df.size_mb = df.size_mb / (1024 * 1024)
    df.created = pd.to_datetime(df.created, unit="s")
    df.modified = pd.to_datetime(df.modified, unit="s")

    # sort in descending order
    df = df.sort_values("created", ascending=False)

    return df
