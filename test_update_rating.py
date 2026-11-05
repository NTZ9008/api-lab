import pytest


# Boundary values for updating stars: 1 and 5 are saved (200), while 0 and 6 are refused (400) and leave stars at 3.
@pytest.mark.parametrize(
    "stars, status, expected_stars",
    [(0, 400, 3), (1, 200, 1), (5, 200, 5), (6, 400, 3)],
)
def test_update_rating_boundary_values(api, auth, rating, stars, status, expected_stars):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": stars}, headers=auth)
    assert res.status_code == status
    res = api.get(path, headers=auth)
    assert res.status_code == 200
    assert res.json()["stars"] == expected_stars
