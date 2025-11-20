def test_list_recipes(client):
    r = client.get("/recipes/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_create_and_get_recipe(client):
    payload = {
        "name": "Avocado Toast",
        "ingredients": ["bread", "avocado", "salt"],
        "instructions": "Mash and spread"
    }
    r = client.post("/recipes/", json=payload)
    assert r.status_code == 201
    rid = r.json()["id"]

    r2 = client.get(f"/recipes/{rid}")
    assert r2.status_code == 200
    data = r2.json()
    assert data["name"] == "Avocado Toast"
    assert data["ingredients"] == ["bread", "avocado", "salt"]
