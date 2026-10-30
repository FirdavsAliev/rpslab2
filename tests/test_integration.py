import pytest
import logic

def test_registration_and_login(test_db):
    logic.register_user("testuser", "password123", test_db)
    user_id = logic.login_user("testuser", "password123", test_db)
    assert user_id is not None
    
def test_login_wrong_password(test_db):
    logic.register_user("testuser", "password123", test_db)
    with pytest.raises(ValueError, match="Неверный логин или пароль"):
        logic.login_user("testuser", "wrongpass", test_db)

def test_add_and_get_food(test_db):
    logic.add_food("Куриная грудка", cal=165, prot=31, fat=3.6, carbs=0, db_path=test_db)
    foods = logic.get_all_foods(test_db)
    assert len(foods) == 1
    assert foods[0]["name"] == "Куриная грудка"