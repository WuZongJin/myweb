from django.db import models

# Create your models here.
class Song(models.Model):
    name = models.CharField(max_length=80, verbose_name="歌曲名字")
    file_sha1 = models.BinaryField(max_length=20, verbose_name="文件sha1")
    fingerprinted = models.BooleanField(default=0, verbose_name="是否已被记录")

    class Meta:
        verbose_name = "歌曲详情"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name
    def get_file_sha1(self):
        return self.file_sha1


class Fingerprint(models.Model):
    song_hash = models.BinaryField(max_length=10, verbose_name="歌曲hash")
    song = models.ForeignKey(Song, verbose_name="对应的歌曲", on_delete=models.CASCADE)
    offset = models.IntegerField(verbose_name="片段所在歌曲中的偏移")

    class Meta:
        verbose_name = "歌曲片段指纹"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.song




