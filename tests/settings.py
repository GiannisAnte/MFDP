from app.auth.jwt_handler import create_access_token


def test_users():
    test_users = [
    {"id": i + 1, "username": f"test{i + 1}", "email": f"test{i + 1}@g.com", "password": f"t{i + 1}"}
    for i in range(2)]

    for user in test_users:
        user['token'] = create_access_token(user['id'])
    return test_users


test_data = {
      "Pregnancies":8,
      "Glucose":183,
      "Blood_Pressure":64,
      "Skin_Thickness":0,
      "Insulin":0,
      "BMI":23.3,
      "Diabetes_Pedigree_Function":0.672,
      "Age":32
        }