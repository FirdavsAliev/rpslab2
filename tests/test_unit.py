import pytest
import logic

def test_calculate_norm():
    norm = logic.calculate_norm(weight=70, height=175, age=25, gender="муж", activity="низкая")
    assert norm > 1500

def test_register_short_password(test_db):
    with pytest.raises(ValueError, match="Пароль должен быть не короче 6 символов"):
        logic.register_user("user1", "123", test_db)

def test_register_empty_login(test_db):
    with pytest.raises(ValueError, match="Логин должен быть не короче 3 символов"):
        logic.register_user("", "123456", test_db)