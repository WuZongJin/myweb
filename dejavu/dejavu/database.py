from django.db import connection
from itertools import zip_longest
from ..views import *

def grouper(iterable, n, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)

class SQLdatabase(object):
    #fingerprint表 及其内容
    TABLE_FINGERPRINT = "dejavu_fingerprint"
    FINGERPRINT_ID = "id"
    FINGERPRINT_SONG_ID = "song_id"
    FINGERPRINT_SONG_HASH = "song_hash"
    FINGERPRINT_OFFSET = "offset"
    #song表 及其内容
    TABLE_SONG = "dejavu_song"
    SONG_ID = "id"
    SONG_FINGERPRINTED = "fingerprinted"
    SONG_NAME = "name"
    SONG_FILESHA = "file_sha1"

    #所用到得SQL语句
    INSERT_SONG = ("INSERT INTO %s (%s, %s, %s) values (%%s, %%s, UNHEX(%%s));" % (
        TABLE_SONG, SONG_NAME, SONG_FINGERPRINTED, SONG_FILESHA))

    UPDATE_SONG_FINGERPRINTED = ("UPDATE %s SET %s = 1 WHERE %s = %%s") % (
        TABLE_SONG, SONG_FINGERPRINTED, SONG_ID)

    INSERT_FINGERPRINT = ("INSERT INTO %s (%s, %s, %s) values (UNHEX(%%s), %%s, %%s);" % (
        TABLE_FINGERPRINT, FINGERPRINT_SONG_HASH, FINGERPRINT_SONG_ID, FINGERPRINT_OFFSET))

    MATCH_SONG_HASH = ("SELECT %s, HEX(%s), %s, %s FROM %s WHERE %s IN (%%s);"
             % (FINGERPRINT_ID, FINGERPRINT_SONG_HASH, FINGERPRINT_SONG_ID, FINGERPRINT_OFFSET, TABLE_FINGERPRINT, FINGERPRINT_SONG_HASH))

    GET_SONG_FILESHA = ("SELECT HEX(%s) FROM %s WHERE %s IN (%%s);"
                        % (SONG_FILESHA, TABLE_SONG, SONG_ID))
    def __init__(self):
        super(SQLdatabase, self).__init__()
        self.cursor = connection.cursor()

    def get_song_list(self):
        return Song.objects.all()

    def get_song_by_id(self, song_id):
        return Song.objects.filter(id=song_id)[0]

    def insert_song(self, songname, file_hash):
        self.cursor.execute(self.INSERT_SONG, (songname, 1, file_hash))
        return self.cursor.lastrowid

    def update_song_fingerprinted(self, song_id):
        self.cursor.execute(self.UPDATE_SONG_FINGERPRINTED, song_id)

    def get_song_filesha(self, song_id):
        self.cursor.execute(self.GET_SONG_FILESHA, song_id)
        return self.cursor.fetchall()[0][0]

    def insert_fingerprint_song_hash(self, song_id, hashes):
        values = []
        for hash, offset in hashes:
            hash = (str(hash)).encode('utf-8')
            offset = int(offset)
            values.append((hash, song_id, offset))
        print(values[:3])
        for split_values in grouper(values, 1000, (b'00000000000000000000', 21, 0)):
            self.cursor.executemany(self.INSERT_FINGERPRINT, split_values)
        return True

    def return_matches(self, hashes):
        mapper = {}
        for song_hash, offset in hashes:
            mapper[song_hash.upper()] = offset

        values = mapper.keys()

        for split_values in grouper(values, 1000, 0):
            query = self.MATCH_SONG_HASH
            query = query % ', '.join(['UNHEX("%s")'] * len(split_values))
            query = (query % split_values)

            self.cursor.execute(query)
            result = self.cursor.fetchall()
            for id, hash, sid, offset in result:
                yield (sid, offset - mapper[hash])