import models
import uuid
import pytest
import json


class TestRoom:
    @pytest.fixture(scope='function')
    def room(self):
        room = models.Room.new()
        id = room.id
        yield models.Room.load(id)
        room.delete()

    def test_create(self, room):
        assert isinstance(room.id, uuid.UUID), "room.id is actually of type {}".format(str(type(room.id)))

    def test_add_player_byinstance(self, room):
        player = models.Player.new()
        player = room.add_player(player)
        assert player.id in room.players
        assert player.room == room.id

    def test_add_player_byuuid(self, room):
        player = models.Player.new().id
        player = room.add_player(player)
        assert player.id in room.players
        assert player.room == room.id

    def test_add_player_wrongtype(self, room):
        with pytest.raises(TypeError):
            room.add_player(5)

    def test_remove_player_wrongtype(self, room):
        with pytest.raises(TypeError):
            room.remove_player(9)

    def test_remove_player_byuuid(self, room):
        player = models.Player.new()
        room.add_player(player)
        room.remove_player(player.id)
        assert len(room.players) == 0

    def test_remove_player_byinstance(self, room):
        player = models.Player.new()
        room.add_player(player.id)
        room.remove_player(player)
        assert len(room.players) == 0

    def test_ball_at(self, room):
        added = room.add_ball()
        in_list = room.ball_at(0)
        assert added.id == in_list.id

    def test_add_ball(self, room):
        num = 5
        for i in range(num):
            room.add_ball()
        assert len(list(room.balls)) == num

    def test_delete_ball(self, room):
        balls_in_redis = len(list(models.Ball.all()))
        ball = room.add_ball()
        room.delete_ball(ball.id)
        # Check that ball is removed from container
        assert len(list(room.balls)) == 0
        # Check that number of balls in redis is net unchanged
        assert len(list(models.Ball.all())) == balls_in_redis

    def test_uniqueness(self, room):
        room2 = models.Room.new()
        assert room.id != room2.id
        room2.delete()


class TestBall:
    @pytest.fixture(scope='function')
    def ball(self):
        ball = models.Ball.new()
        id = ball.id
        yield models.Ball.load(id)
        ball.delete()

    def test_create(self, ball):
        as_int = lambda obj: int(obj.decode('utf-8'))
        assert isinstance(ball.id, uuid.UUID)
        assert as_int(ball.position['x']) <= 500 + models.MAX_SPEED
        assert as_int(ball.position['x']) >= 500 - models.MAX_SPEED
        assert as_int(ball.position['y']) <= 500 + models.MAX_SPEED
        assert as_int(ball.position['y']) >= 500 - models.MAX_SPEED
        assert as_int(ball.vector['x']) >= -models.MAX_SPEED
        assert as_int(ball.vector['x']) <= models.MAX_SPEED
        assert as_int(ball.vector['y']) >= -models.MAX_SPEED
        assert as_int(ball.vector['y']) <= models.MAX_SPEED
        assert ball.ballType in models.BALL_TYPES

    def test_uniqueness(self, ball):
        ball2 = models.Ball.new()
        assert ball.id != ball2.id
        ball2.delete()


class TestPlayer:
    @pytest.fixture(scope='function')
    def player(self):
        player = models.Player.new()
        id = player.id
        yield models.Player.load(id)
        player.delete()

    def test_create(self, player):
        assert isinstance(player.id, uuid.UUID)

    def test_uniqueness(self, player):
        player2 = models.Player.new()
        assert player.id != player2.id
        player2.delete()
