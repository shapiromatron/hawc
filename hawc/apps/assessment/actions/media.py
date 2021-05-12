from hashlib import blake2b
from pathlib import Path

import pandas as pd
from django.conf import settings


def media_metadata_report(root_uri: str) -> pd.DataFrame:
    """Return tabular report on all media files for review

    Args:
        root_uri (str): The MEDIA_URL for the incoming request

    Returns:
        pd.DataFrame: a dataframe of content
    """
    # grab all files recursively in the media root path
    path = Path(settings.MEDIA_ROOT)
    files = [f for f in path.glob("**/*") if f.is_file()]

    # process metadata for each file individually
    data = []
    for fn in files:
        metadata = fn.stat()
        data.append(
            dict(
                name=fn.name,
                extension=fn.suffix,
                full_path=fn,
                hash=blake2b(fn.read_bytes()).hexdigest(),
                uri=fn.as_uri(),
                size_mb=metadata.st_size,
                created=metadata.st_ctime,
                modified=metadata.st_mtime,
            )
        )

    # build dataframe
    df = pd.DataFrame(data)

    # transform columns using vectorized operations
    df.uri = df.uri.str.replace(path.as_uri(), root_uri)
    df.size_mb = df.size_mb / (1024 * 1024)
    df.created = pd.to_datetime(df.created, unit="s")
    df.modified = pd.to_datetime(df.modified, unit="s")

    # sort in descending order
    df = df.sort_values("created", ascending=False)

    return df
