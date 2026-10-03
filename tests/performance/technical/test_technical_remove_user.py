import pytest

# Technical testcases only for intern use of taurus jmeter to reuse fixture 
@pytest.mark.intern
def test_remove_users(jmeter_remove_user_accounts):
    assert True