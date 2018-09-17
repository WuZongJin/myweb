from .fingerprinte import *
from . import decoder
from . import database
import os



class Dejavu(object):

    DEFAULT_FS = 44100

    def __init__(self):
        super(Dejavu, self).__init__()
        self.limit = None
        self.db = database.SQLdatabase()
        self.get_fingerprinted_songs()


    def get_song_list(self):
        return self.db.get_song_list()

    def find_matches(self, samples, Fs=44100):
        hashes = fingerprint(samples, Fs=Fs)
        return self.db.return_matches(hashes)

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
        print(song_id)
        song = self.db.get_song_by_id(song_id)
        if song:
            pass
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

    def get_fingerprinted_songs(self):
        # get songs previously indexed
        self.songs = self.db.get_song_list()
        self.songhashes_set = set()  # to know which ones we've computed before
        for song in self.songs:
            print(song.id)
            song_hash = self.db.get_song_filesha(song.id)
            self.songhashes_set.add(song_hash)

    def fingerprint_directory(self, path, extensions):
        # Try to use the maximum amount of processes if not given.
        filenames_to_fingerprint = []
        for filename, _ in decoder.find_files(path, extensions):
            # don't refingerprint already fingerprinted files
            if decoder.unique_hash(filename)[:20] in self.songhashes_set:

                print("%s already fingerprinted, continuing..." % filename)
                continue
            else:
                print("%s is ready to fingerprint" % filename)
                filenames_to_fingerprint.append(filename)
        for i in range(len(filenames_to_fingerprint)):

            song_name, hashes, file_hash = _fingerprint_worker(filenames_to_fingerprint[i])
            file_hash = (str(file_hash)).encode('utf-8')[:20]
            #print(song_name, file_hash)
            sid = self.db.insert_song(song_name, file_hash)
            self.db.insert_fingerprint_song_hash(sid, hashes)

def _fingerprint_worker(filename, limit=None, song_name=None):
    # Pool.imap sends arguments as tuples so we have to unpack
    # them ourself.
    try:
        filename, limit = filename
    except ValueError:
        pass
    songname, extension = os.path.splitext(os.path.basename(filename))
    song_name = song_name or songname
    channels, Fs, file_hash = decoder.read(filename, limit)
    result = set()
    channel_amount = len(channels)

    for channeln, channel in enumerate(channels):
        # TODO: Remove prints or change them into optional logging.
        print("Fingerprinting channel %d/%d for %s" % (channeln + 1,
                                                       channel_amount,
                                                       filename))
        hashes = fingerprint(channel, Fs=Fs)
        print("Finished channel %d/%d for %s" % (channeln + 1, channel_amount,
                                                  filename))
        result |= set(hashes)
    return song_name, result, file_hash



