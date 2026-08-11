from utility.database.model import APIKey, TextAnalysisRequest, User


def test_user_defaults(db_session):
    user = User(email="model@test.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.credits == 100
    assert user.email == "model@test.com"


def test_api_key_links_to_user(db_session, test_user):
    key = APIKey(userid=test_user.id, thekey="safe_linktest")
    db_session.add(key)
    db_session.commit()
    db_session.refresh(key)
    assert key.userid == test_user.id


def test_text_analysis_request(db_session, test_user):
    row = TextAnalysisRequest(
        userid=test_user.id,
        inputtext="hello",
        isprofane=False,
        toxicityscore=5.0,
    )
    db_session.add(row)
    db_session.commit()
    assert row.inputtext == "hello"
