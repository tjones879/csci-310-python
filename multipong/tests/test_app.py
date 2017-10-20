from flask import url_for


class TestApp:
    def test_index(self, client):
        result = client.get(url_for('index'))
        assert result.status_code == 200
        # assert result