"""Private, isolated metadata-only module probe; run with Python ``-I -S``."""

from __future__ import annotations

import importlib.machinery
import json
import site
import sys
from pathlib import Path


def _installed_search_paths() -> tuple[str, ...]:
    """Add declared interpreter site directories without processing their hooks.

    Before Python 3.14, ``-S`` leaves ``sys.prefix`` at the base installation even
    inside a venv. Read its adjacent pyvenv.cfg as data to recover the intended
    installation. User-site, PYTHONPATH, .pth files and import hooks are excluded.
    """

    executable_directory = Path(sys.executable).absolute().parent
    prefixes = [sys.prefix, sys.exec_prefix]
    for directory in (executable_directory, executable_directory.parent):
        configuration = directory / "pyvenv.cfg"
        if not configuration.is_file():
            continue
        entries = {}
        for line in configuration.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator:
                entries[key.strip().casefold()] = value.strip().casefold()
        prefixes = [str(directory)]
        if entries.get("include-system-site-packages") == "true":
            prefixes.extend((sys.base_prefix, sys.base_exec_prefix))
        break
    # site is imported with -S, so getsitepackages only computes directory names:
    # it does not add paths, execute .pth lines, or import sitecustomize.
    paths = [path for path in sys.path if path]
    paths.extend(site.getsitepackages(prefixes))
    return tuple(dict.fromkeys(paths))


def _module_available(name: str, search_paths: tuple[str, ...]) -> bool:
    """Resolve each path component without loading a parent package's __init__."""

    paths = search_paths
    components = name.split(".")
    prefix = []
    for index, component in enumerate(components):
        prefix.append(component)
        fullname = ".".join(prefix)
        spec = importlib.machinery.BuiltinImporter.find_spec(fullname)
        if spec is None:
            spec = importlib.machinery.FrozenImporter.find_spec(fullname)
        if spec is None:
            # The explicit path already identifies the parent. A component-only
            # lookup avoids _NamespacePath consulting an unimported parent in
            # sys.modules, so nested implicit namespace packages work as well.
            spec = importlib.machinery.PathFinder.find_spec(component, list(paths))
        if spec is None:
            return False
        if index < len(components) - 1:
            if spec.submodule_search_locations is None:
                return False
            paths = tuple(spec.submodule_search_locations)
    return True


def main() -> int:
    if not sys.flags.isolated or not sys.flags.no_site:
        return 2
    modules = sys.argv[1:]
    paths = _installed_search_paths()
    missing = [name for name in modules if not _module_available(name, paths)]
    print(json.dumps({"schema_version": 1, "requested": modules, "missing": missing}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
