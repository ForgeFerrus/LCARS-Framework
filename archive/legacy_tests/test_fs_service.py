import tempfile
from pathlib import Path
from lcars.modules.file_manager import FsSubsystem, FsError


def test_fs_service_basic(tmp_path):
    svc = FsSubsystem(base_dir=tmp_path)
    # write file
    svc.write_file('a.txt', 'hello', overwrite=True)
    lst = svc.list_dir()
    assert any(x['name'] == 'a.txt' for x in lst)

    # read preview
    content = svc.read_preview('a.txt')
    assert 'hello' in content

    # copy
    svc.copy('a.txt', 'b.txt', overwrite=True)
    assert any(x['name'] == 'b.txt' for x in svc.list_dir())

    # mkdir + move
    svc.make_dir('sub')
    svc.move('b.txt', 'sub/b2.txt')
    assert any(x['name'] == 'sub' and x['is_dir'] for x in svc.list_dir())
    assert any(x['name'] == 'b2.txt' for x in svc.list_dir('sub'))

    # delete file
    svc.delete('a.txt')
    assert not any(x['name'] == 'a.txt' for x in svc.list_dir())

    # delete dir recursive
    svc.delete('sub', recursive=True)
    assert not any(x['name'] == 'sub' for x in svc.list_dir())
