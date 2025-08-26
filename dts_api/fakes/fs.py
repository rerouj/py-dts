from pyfakefs.fake_filesystem import FakeFilesystem

os_fs = FakeFilesystem()
os_fs.create_file('/data/metadata.json', contents='{"value": "ok"}')

win_fs = FakeFilesystem()
win_fs.create_file('C:\\data\\metadata.json', contents='{"value": "ok"}')