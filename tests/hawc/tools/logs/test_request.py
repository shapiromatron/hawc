from hawc.tools.logs.request import parse_request_logs


def test_parse_request_logs():
    logs = """

    GET /study/1/ 200 15 ip-127.0.0.1 user-0 assess-456
    GET /study/2/ 200 15 ip-127.0.0.1 user-123 assess-0
    GET /study/3/ 200 15 ip-127.0.0.1 user-123 assess-456
    GET /study/1/ 200 15 ip-127.0.0.1 user-1 assess-2
    GET /study/1/ 200 15 ip-127.0.0.1 user-1 assess-3

    """
    df = parse_request_logs(logs)
    assert df.shape == (5, 7)
    assert set(df.status_code.values.tolist()) == {200}
    assert set(df.ip.values.tolist()) == {"127.0.0.1"}
    assert set(df.user_id.values.tolist()) == {0, 1, 123}
    assert set(df.assessment_id.values.tolist()) == {0, 2, 3, 456}
