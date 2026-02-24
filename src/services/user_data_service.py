import json


def load_user_data():
    with open("users_data.json", "r") as file:
        return json.load(file)


def get_user_data_by_id(user_id: str):
    return _USERS_DATA.get(str(user_id))


_USERS_DATA: dict = load_user_data()
