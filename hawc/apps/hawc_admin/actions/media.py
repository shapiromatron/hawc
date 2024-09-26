from hashlib import blake2b
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.urls import reverse
from django.utils.html import urlencode


def media_metadata_report(root_uri: str) -> pd.DataFrame:
    """Return tabular report on all media files for review

    Args:
        root_uri (str): The MEDIA_URL for the incoming request

    Returns:
        pd.DataFrame: a dataframe of content
    """
    # grab all files recursively in the media root path
    media_root = Path(settings.MEDIA_ROOT)
    media_url = root_uri + settings.MEDIA_URL[:-1]
    files = [f for f in media_root.glob("**/*") if f.is_file()]
    media_preview = root_uri + reverse("admin_media_preview")

    # process metadata for each file individually
    data = []
    for fn in files:
        metadata = fn.stat()
        item = str(fn).replace(str(media_root) + "/", "")
        data.append(
            dict(
                name=fn.name,
                extension=fn.suffix,
                full_path=fn,
                hash=blake2b(fn.read_bytes()).hexdigest(),
                uri=fn.as_uri(),
                media_preview=media_preview + f"?{urlencode(dict(item=item))}",
                size_mb=metadata.st_size,
                created=metadata.st_ctime,
                modified=metadata.st_mtime,
            )
        )

    # build dataframe
    df = pd.DataFrame(data)

    if not df.empty:
        # transform columns using vectorized operations
        df.uri = df.uri.str.replace(media_root.as_uri(), media_url)
        df.size_mb = df.size_mb / (1024 * 1024)
        df.created = pd.to_datetime(df.created, unit="s")
        df.modified = pd.to_datetime(df.modified, unit="s")
        df.full_path = df.full_path.astype(str)

        # sort in descending order
        df = df.convert_dtypes().sort_values("created", ascending=False)

    return df
