from . import decoder
import dejavu
import time

class Recognizer(object):
    def __init__(self, dejavu):
        self.dejavu = dejavu
        self.Fs = dejavu.DEFAULT_FS

    def recognize(self, *data):
        matches = []
        for d in data:
            matches.extend(self.dejavu.find_matches(d, Fs=self.Fs))

        # for d in matches:
        #     print(d)
        return self.dejavu.align_matches(matches)

    def recognize_file(self, filename):
        frames, self.Fs, file_hash = decoder.read(filename, None)
        t = time.time()
        match = self.recognize(*frames)
        t = time.time() - t
        if match:
            match['match_time'] = t
        return match