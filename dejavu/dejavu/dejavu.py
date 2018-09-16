from .fingerprinte import *
from ..views import *
from itertools import zip_longest, groupby, _grouper
from . import decoder
import time
import queue

def grouper(iterable, n, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


class Dejavu(object):
    def __init__(self):
        super(Dejavu, self).__init__()


    def get_fingerprinted_song(self):
        fingerprinted_song_list = Song.objects.all()
        return fingerprinted_song_list

    def return_matches(self, hashes):
        mapper = {}
        for song_hash, offset in hashes:
            mapper[song_hash.upper()] = offset

        values = mapper.keys()

        for split_values in grouper(values, 10):
            query = ("SELECT %s, (%s), %s, %s FROM %s WHERE %s IN (%%s);"
                     % ("id", "song_hash", "song_id", "offset", "dejavu_fingerprint", "song_hash"))

            query = query % ', '.join(['(%s)'] * len(split_values))


            result = Fingerprint.objects.raw(query, split_values)
            for hash, offset, sid in result:
                print(hash)
                yield (sid, offset - mapper[hash])

    def find_matches(self, samples, Fs = DEFAULT_FS):
        hashes = fingerprint(samples, Fs=Fs)
        return self.return_matches(hashes)

    def align_matches(self, matches):
        diff_counter = {}
        largest = 0
        largest_count = 0
        song_id = -1
        for tup in matches:
            sid, diff = tup
            if diff not in diff_counter:
                diff_counter[diff] = {}
            if sid not in diff_counter[diff]:
                diff_counter[diff][sid] = 0
            diff_counter[diff][sid] += 1

            if diff_counter[diff][sid] > largest_count:
                largest = diff
                largest_count = diff_counter[diff][sid]
                song_id = sid

        song = Song.objects.get(id = song_id)
        if song:
            # TODO: Clarify what `get_song_by_id` should return.
            songname = song.name
        else:
            return None
        nseconds = round(float(largest) / DEFAULT_FS *
                         DEFAULT_WINDOW_SIZE *
                         DEFAULT_OVERLAP_RATIO, 5)
        song_info = {
            "song_id": song.id,
            "song_name": song.name,
            "song_confidence": largest_count,
            "song_offset": int(largest),
            "song_offser_secs": nseconds,
            "song_sha1": song.get_file_sha1(),
        }
        return song_info



class Recognizer(object):
    def __init__(self, dejavu):
        self.dejavu = dejavu
        self.Fs = DEFAULT_FS

    def recognize(self, *data):
        matches = []
        for d in data:
            matches.extend(self.dejavu.find_matches(d, Fs=self.Fs))
        return self.dejavu.align_matches(matches)

    def recognize_file(self, filename):
        frames, self.Fs, file_hash = decoder.read(filename, None)
        t = time.time()
        match = self.recognize(*frames)
        t = time.time() - t
        if match:
            match['match_time'] = t
        return match

