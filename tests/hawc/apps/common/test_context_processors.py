from hawc.apps.common.context_processors import is_supported_agent


def test_is_supported_agent():
    # fmt: off
    uas = [
        ("chrome", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36", True),
        ("firefox", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0", True),
        ("edge", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.58", True),
        ("safari", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15", True),
        ("ie11", "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko", False)
    ]
    # fmt: on
    for _, ua, valid in uas:
        assert is_supported_agent(ua) is valid
