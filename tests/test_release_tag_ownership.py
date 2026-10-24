"""Execute the Linux publication shell against an owned local bare repository.

No GitHub release, network Git remote, or real credential is used.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TAG = "v0.0.0-fixture"
pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="The release job and its shell fixture run on Ubuntu"
)


def _git(directory: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(directory), *arguments],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    return result.stdout.strip()


@pytest.fixture
def publication(tmp_path: Path) -> tuple[Path, Path, Path, dict[str, str]]:
    remote = tmp_path / "owned-remote.git"
    first = tmp_path / "first-publisher"
    second = tmp_path / "second-publisher"
    remote.mkdir()
    first.mkdir()
    _git(remote, "init", "--bare", "--initial-branch=main")
    _git(first, "init", "--initial-branch=main")
    _git(first, "config", "user.name", "Owned release fixture")
    _git(first, "config", "user.email", "fixture@localhost")
    (first / "fixture.txt").write_text("owned temporary fixture\n", encoding="utf-8")
    _git(first, "add", "fixture.txt")
    _git(first, "commit", "-m", "owned fixture")
    _git(first, "remote", "add", "origin", str(remote))
    _git(first, "push", "origin", "HEAD:refs/heads/main")
    _git(tmp_path, "clone", str(remote), str(second))
    # Both runners have checked out the same main before either creates its tag.
    assert _git(first, "rev-parse", "HEAD") == _git(second, "rev-parse", "HEAD")
    assert _git(second, "remote", "get-url", "origin") == str(remote)

    shim_directory = tmp_path / "owned-command-shims"
    shim_directory.mkdir()
    shim = shim_directory / "gh"
    shim.write_text(
        f"#!{sys.executable}\n"
        "import json,os,sys\n"
        "with open(os.environ['FIXTURE_GH_LOG'],'a',encoding='utf-8') as stream:\n"
        "    stream.write(json.dumps(sys.argv[1:])+'\\n')\n"
        "if sys.argv[1:3] == ['release','view']: sys.exit(1)\n"
        "if sys.argv[1:3] == ['release','create']: sys.exit(int(os.environ['FIXTURE_CREATE_CODE']))\n"
        "sys.exit(93)\n",
        encoding="utf-8",
    )
    shim.chmod(0o755)
    environment = {
        key: os.environ[key]
        for key in ("PATH", "LANG", "LC_ALL", "TMPDIR", "TMP", "TEMP")
        if key in os.environ
    }
    environment.update(
        {
            "PATH": str(shim_directory) + os.pathsep + os.environ.get("PATH", ""),
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_TERMINAL_PROMPT": "0",
            "GITHUB_SHA": _git(second, "rev-parse", "HEAD"),
            "GITHUB_REPOSITORY": "owned-fixture/never-contacted",
            "RELEASE_TAG": TAG,
            "VERSION_VALUE": "0.0.0-fixture",
            "FIXTURE_GH_LOG": str(tmp_path / "gh-calls.jsonl"),
            "FIXTURE_CREATE_CODE": "0",
        }
    )
    (second / "dist").mkdir()
    (second / "dist" / "fixture.whl").write_bytes(b"synthetic fixture, not a wheel\n")
    return first, second, remote, environment


def _publish(directory: Path, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    workflow = yaml.safe_load((ROOT / ".github/workflows/release.yml").read_text("utf-8"))
    step = next(
        step
        for step in workflow["jobs"]["release"]["steps"]
        if step.get("name") == "Publish immutable tag and GitHub Release"
    )
    return subprocess.run(
        ["bash", "-c", step["run"]],
        cwd=directory,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
        check=False,
    )


def _remote_tag(remote: Path) -> str:
    return _git(remote, "for-each-ref", "--format=%(objectname)", f"refs/tags/{TAG}")


def test_rejected_tag_push_preserves_competing_tag(publication) -> None:
    first, second, remote, environment = publication
    _git(first, "tag", "-a", TAG, "-m", "owned first publisher's immutable tag")
    _git(first, "push", "origin", f"refs/tags/{TAG}")
    original = _remote_tag(remote)
    assert original

    result = _publish(second, environment)

    assert result.returncode != 0, result.stdout
    assert _remote_tag(remote) == original, result.stdout
    assert _git(remote, "rev-parse", f"{TAG}^{{commit}}") == environment["GITHUB_SHA"]


def test_release_upload_failure_preserves_the_published_tag(publication) -> None:
    _, second, remote, environment = publication
    environment["FIXTURE_CREATE_CODE"] = "37"

    result = _publish(second, environment)

    assert result.returncode == 37, result.stdout
    assert _remote_tag(remote) == _git(second, "rev-parse", f"refs/tags/{TAG}"), result.stdout
    assert _git(remote, "rev-parse", f"{TAG}^{{commit}}") == environment["GITHUB_SHA"]


def test_successful_publication_retains_annotation_and_release_arguments(publication) -> None:
    _, second, remote, environment = publication

    result = _publish(second, environment)

    assert result.returncode == 0, result.stdout
    assert _remote_tag(remote) == _git(second, "rev-parse", f"refs/tags/{TAG}")
    assert _git(remote, "cat-file", "-t", f"refs/tags/{TAG}") == "tag"
    assert _git(remote, "rev-parse", f"{TAG}^{{commit}}") == environment["GITHUB_SHA"]
    calls = [
        json.loads(line) for line in Path(environment["FIXTURE_GH_LOG"]).read_text().splitlines()
    ]
    assert len(calls) == 1
    assert calls[0][:3] == ["release", "create", TAG]
    assert "--verify-tag" in calls[0]
    assert calls[0][calls[0].index("--repo") + 1] == environment["GITHUB_REPOSITORY"]
