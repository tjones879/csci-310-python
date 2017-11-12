from multipong import models
import uuid
import pytest


class TestRoom:
    @pytest.fixture(scope='function')
    def room(self):
        room = models.Room.new()
        yield room
        room.delete()

    def test_create(self, room):
        assert isinstance(room.id, uuid.UUID), "room.id is actually of type {}".format(str(type(room.id)))
        assert room.arenasize == models.DEFAULT_ARENA_SIZE

    def test_playeradd(self, room):
        assert room.players.add("testplayer")
        room.save()
        assert "testplayer" in room.players
        room.players.remove("testplayer")
        assert "testplayer" not in room.players

    def test_specadd(self, room):
        assert room.spectators.add("testspectator")
        room.save()
        assert "testspectator" in room.spectators
        room.spectators.remove("testspectator")
        assert "testspectator" not in room.spectators

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
        yield ball
        ball.delete()

    def test_create(self, ball):
        assert isinstance(ball.id, uuid.UUID)
        assert ball.position['x'] == 500
        assert ball.position['y'] == 500
        assert ball.vector['x'] >= -models.MAX_SPEED
        assert ball.vector['x'] <= models.MAX_SPEED
        assert ball.vector['y'] >= -models.MAX_SPEED
        assert ball.vector['y'] <= models.MAX_SPEED
        assert ball.ballType in models.BALL_TYPES

    def test_uniqueness(self, ball):
        ball2 = models.Ball.new()
        assert ball.id != ball2.id
        ball2.delete()


class TestPlayer:
    @pytest.fixture(scope='function')
    def player(self):
        player = models.Player.new()
        yield player
        player.delete()

    def test_create(self, player):
        assert isinstance(player.id, uuid.UUID)

    def test_uniqueness(self, player):
        player2 = models.Player.new()
        assert player.id != player2.id
        player2.delete()
