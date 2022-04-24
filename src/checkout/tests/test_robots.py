from django.test.client import Client


def test_robots_txt(client: Client) -> None:
    res = client.get("/robots.txt")
    assert res.status_code == 200
    assert res["Content-Type"] == "text/plain"
    content = res.content.decode("utf-8")
    assert "User-Agent" in content
