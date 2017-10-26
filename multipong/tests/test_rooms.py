from multipong import rooms

class TestRoom:
    def test_playeradd(self):
        room = rooms.Room.create()
        assert room.players.add("testplayer")
        room.save()
        assert "testplayer" in room.players
        room.players.remove("testplayer")
        assert "testplayer" not in room.players
        room.delete()

    def test_specadd(self):
        room = rooms.Room.create()
        assert room.spectators.add("testspectator")
        room.save()
        assert "testspectator" in room.spectators
        room.spectators.remove("testspectator")
        assert "testspectator" not in room.spectators
        room.delete()

