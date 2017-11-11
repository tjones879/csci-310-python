from multipong import models
import uuid

class TestRoom:
    def test_create(self):
        room = models.Room.new()
        room.balls.append(models.Ball.new().id)
        assert isinstance(room.id, uuid.UUID), "room.id is actually of type {}".format(str(type(room.id)))
        assert isinstance(uuid.UUID(bytes.decode(list(room.balls)[0], 'utf-8')), uuid.UUID), "stored ball id is not a valid UUID"
        assert room.arenasize == models.DEFAULT_ARENA_SIZE
        room.delete()

    def test_playeradd(self):
        room = models.Room.new()
        assert room.players.add("testplayer")
        room.save()
        assert "testplayer" in room.players
        room.players.remove("testplayer")
        assert "testplayer" not in room.players
        room.delete()

    def test_specadd(self):
        room = models.Room.new()
        assert room.spectators.add("testspectator")
        room.save()
        assert "testspectator" in room.spectators
        room.spectators.remove("testspectator")
        assert "testspectator" not in room.spectators
        room.delete()

    def test_uniqueness(self):
        room1 = models.Room.new()
        room2 = models.Room.new()
        assert room1.id != room2.id
        room1.delete()
        room2.delete()


class TestBall:
    def test_create(self):
        ball = models.Ball.new()
        assert isinstance(ball.id, uuid.UUID)
        assert ball.position['x'] == 500
        assert ball.position['y'] == 500
        assert ball.vector['x'] == 50
        assert ball.vector['y'] == 50
        assert ball.ballType in models.BALL_TYPES
        ball.delete()

    def test_uniqueness(self):
        ball1 = models.Ball.new()
        ball2 = models.Ball.new()
        assert ball1.id != ball2.id
        ball1.delete()
        ball2.delete()


class TestPlayer:
    def test_create(self):
        player = models.Player.new()
        assert isinstance(player.id, uuid.UUID)
        player.delete()

    def test_uniqueness(self):
        player1 = models.Player.new()
        player2 = models.Player.new()
        assert player1.id != player2.id
        player1.delete()
        player2.delete()