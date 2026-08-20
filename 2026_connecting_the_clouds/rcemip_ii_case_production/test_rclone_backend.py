import shutil
import sys
import tempfile
from pathlib import Path

from filesystem_backend import Rclone_backend


def check(name, condition):
    status = 'PASS' if condition else 'FAIL'
    print(f'[{status}] {name}')
    return condition


def main():
    backend = Rclone_backend()
    root = Path(tempfile.mkdtemp(prefix='rclone_backend_test_'))
    ok = True

    try:
        src_dir = root / 'src'
        dst_dir = root / 'dst'
        src_dir.mkdir()
        (src_dir / 'a.txt').write_text('hello')
        (src_dir / 'sub').mkdir()
        (src_dir / 'sub' / 'b.txt').write_text('world')

        ok &= check('exists: false before copy_tree', backend.exists(dst_dir) is False)

        backend.copy_tree(src_dir, dst_dir)
        ok &= check('exists: true after copy_tree', backend.exists(dst_dir))

        entries = backend.list_tree(dst_dir)
        relpaths = sorted(e.relpath for e in entries)
        ok &= check('list_tree: relpaths match', relpaths == ['a.txt', 'sub/b.txt'])

        sizes = {e.relpath: e.size for e in entries}
        ok &= check(
            'list_tree: sizes match',
            sizes.get('a.txt') == len('hello') and sizes.get('sub/b.txt') == len('world'))

        single_dst = root / 'copied_a.txt'
        backend.copy_file(src_dir / 'a.txt', single_dst)
        ok &= check('copy_file: content matches', single_dst.exists() and single_dst.read_text() == 'hello')

        backend.remove_file(single_dst)
        ok &= check('remove_file: gone after removal', not single_dst.exists())

        backend.remove_tree(dst_dir)
        ok &= check('remove_tree: gone after removal', backend.exists(dst_dir) is False)

    finally:
        shutil.rmtree(root, ignore_errors=True)

    print()
    print('ALL PASSED' if ok else 'SOME FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
