from multipong import mongo
from datetime import datetime


def test_mongo():
    mongo.get_database().drop_collection('test_mongo')
    collection = mongo.get_database()['test_mongo']
    timestamp = datetime.now()
    test_entry = {
        "name": "test_entry",
        "timestamp": timestamp
    }
    assert collection.insert_one(test_entry).acknowledged, "Failed to insert test_entry into test_mongo collection"
    found_entry = collection.find_one({"name": "test_entry"})
    assert found_entry is not None, "Cannot find test_entry in test_mongo collection"
    assert found_entry['timestamp'].strftime("%I:%M%p on %B %d, %Y") == timestamp.strftime("%I:%M%p on %B %d, %Y"), "Timestamp in test_entry does not approximately match original timestamp: '{}' vs '{}'".format(found_entry['timestamp'].strftime("%I:%M%p on %B %d, %Y"), timestamp.strftime("%I:%M%p on %B %d, %Y"))
    assert collection.delete_one({"name": "test_entry"}).acknowledged, "Failed to delete document 'test_entry' in collection 'test_mongo'"
