from hawc.apps.myuser.synthetic import UserData, generate


def test_generate():
    data = generate()
    assert isinstance(data, UserData)
    assert data.first_name.lower() in data.email
    assert data.last_name.lower() in data.email
    assert data.username in data.email
