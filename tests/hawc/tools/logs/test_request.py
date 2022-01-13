from hawc.tools.logs.request import parse_request_logs

logs = """
INFO 2021-08-26 19:51:02,705 hawc.request GET /assessment/public/ 200 4887 ip-127.0.0.1 user-0 assess-0
INFO 2021-08-26 19:51:10,325 hawc.request GET /study/7/ 200 20116 ip-127.0.0.1 user-1 assess-2
INFO 2021-08-26 19:51:11,389 hawc.request GET /study/7/update/ 200 18401 ip-127.0.0.1 user-1 assess-2
INFO 2021-08-26 19:51:12,891 hawc.request GET /study/api/study/7/ 200 29000 ip-127.0.0.1 user-1 assess-0
"""


def test_parse_request_logs():
    df = parse_request_logs(logs)
    assert df.shape == (4, 9)
    assert set(df.status_code.values.tolist()) == {200}
    assert set(df.ip.values.tolist()) == {"127.0.0.1"}
    assert set(df.user_id.values.tolist()) == {0, 1}
    assert set(df.assessment_id.values.tolist()) == {0, 2}
