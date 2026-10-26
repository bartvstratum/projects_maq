from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class File_entry:
    relpath: str
    size: int


class Backend(Protocol):
    def exists(self, path: Path) -> bool: ...
    def copy_tree(self, src: Path, dst: Path) -> None: ...
    def list_tree(self, path: Path) -> list[File_entry]: ...
    def remove_tree(self, path: Path) -> None: ...
    def copy_file(self, src: Path, dst: Path) -> None: ...
    def remove_file(self, path: Path) -> None: ...


class Local_backend(Backend):
    def exists(self, path: Path | str) -> bool:
        return Path(path).exists()

    def copy_tree(self, src: Path | str, dst: Path | str) -> None:
        shutil.copytree(Path(src), Path(dst))

    def list_tree(self, path: Path | str) -> list[File_entry]:
        root = Path(path)
        if not root.exists():
            raise FileNotFoundError(root)

        entries = []
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            relpath = str(p.relative_to(root))
            entries.append(File_entry(relpath=relpath, size=p.stat().st_size))

        return sorted(entries, key=lambda e: e.relpath)

    def remove_tree(self, path: Path | str) -> None:
        root = Path(path)

        if not root.exists():
            raise FileNotFoundError(root)

        shutil.rmtree(root)

    def copy_file(self, src: Path | str, dst: Path | str) -> None:
        dst = Path(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(src), dst)

    def remove_file(self, path: Path | str) -> None:
        file = Path(path)

        if not file.exists():
            raise FileNotFoundError(file)

        file.unlink()


class Rclone_backend(Backend):
    def exists(self, path: str) -> bool:
        result = subprocess.run(
            ['rclone', 'lsf', str(path)],
            capture_output=True, text=True)
        return result.returncode == 0 and result.stdout.strip() != ''

    def copy_tree(self, src: str, dst: str) -> None:
        subprocess.run(['rclone', 'copy', '--checksum', str(src), str(dst)], check=True)

    def list_tree(self, path: str) -> list[File_entry]:
        result = subprocess.run(
            ['rclone', 'lsjson', '--recursive', '--files-only', str(path)],
            capture_output=True, text=True, check=True)

        entries = [
            File_entry(relpath=e['Path'], size=e['Size'])
            for e in json.loads(result.stdout)
        ]

        return sorted(entries, key=lambda e: e.relpath)

    def remove_tree(self, path: str) -> None:
        subprocess.run(['rclone', 'purge', str(path)], check=True)

    def copy_file(self, src: str, dst: str) -> None:
        subprocess.run(['rclone', 'copyto', '--checksum', str(src), str(dst)], check=True)

    def remove_file(self, path: str) -> None:
        subprocess.run(['rclone', 'deletefile', str(path)], check=True)
