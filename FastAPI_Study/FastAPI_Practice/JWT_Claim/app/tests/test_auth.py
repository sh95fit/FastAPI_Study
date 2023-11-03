from database.conn import db
from database.schema import Users


def test_registration(client, session):
    """
    레버 로그인
    :param client:
    :param session:
    :return:
    """
    user = dict(email="test@test.com", pw="test1234",
                name="KSH", phone="01012341234")
    res = client.post("api/auth/register/email", json=user)
    res_body = res.json()
    print(res.json())
    assert res.status_code == 201
    assert "Authorization" in res_body


def test_registration_exist_email(client, session):
    """
    레버 로그인
    :param client:
    :param session:
    :return:
    """
    user = dict(email="test@test.com", pw="test1234",
                name="KSH", phone="01012341234")
    db_user = Users.create(session=session, **user)
    session.commit()
    res = client.post("api/auth/register/email", json=user)
    res_body = res.json()
    assert res.status_code == 400
    assert "EMAIL_EXIST" == res_body["msg"]
