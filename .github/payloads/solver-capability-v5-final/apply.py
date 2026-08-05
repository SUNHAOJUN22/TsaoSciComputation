from __future__ import annotations

import hashlib
import io
import shutil
import subprocess
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path('.github/payloads/solver-capability-v5-final')
CHUNK_HASHES = (
    'a7fce72129035e2a4c80398fbaa31d32d0f642ea7b33f597d75f44bfdd1d26bb',
    'a50bcf9b0e1898830a8e0eb8d7dc70a60b56b9791d8d1184c8284009818b2566',
    '331664a1f02d453b9fc615ed9315899f7244510c814f4e79c7f1a69850c80a4e',
    '0959bd6a35d6e6465bc7873d76768b2c2f2405ed7eba7e3af5b1013bb727d1dd',
    'b66725de14f02bdcc6784f58b401dc224040a25444f3b6116d316224306cbbf6',
    'edb08c7a183cacef2286dcd5d1f54a16fe3abd456a0d56a3cd920aaaf6ce1bf3',
)
PART_SOURCES = (
    ('9c2edcc3ddf742fbd9ee0575ff39a46aa57f4abd', '.github/payloads/solver-capability-v5/part-00'),
    None,
    ('a131ab8f461e92fef277ca919e12aad01d78eb23', '.github/payloads/solver-capability-v5-retry/part-02'),
    ('89159694b307c316e86d017911f5de1653dd47ae', '.github/payloads/solver-capability-v5/part-03'),
    ('c442cdf4356ca38346f48c6366d8b8bb6f81a5df', '.github/payloads/solver-capability-v5/part-04'),
    ('08526d20be74140a14748d11dafa94d8a1599aa1', '.github/payloads/solver-capability-v5/part-05'),
    ('01421c0bb1900fedaddc8bf2278d93379faf660c', '.github/payloads/solver-capability-v5/part-06'),
    ('99db53c7e919a1acf43fbc7c6ca3d3385eedb9b3', '.github/payloads/solver-capability-v5/part-07'),
    ('64b7c6a98b01b139701ea60d57c9a1769e6bed6b', '.github/payloads/solver-capability-v5/part-08'),
)
PART_HASHES = (
    '37a113145283f0bc0d4303abad0c94e44dabbda260eef7060d750f57fda7a908',
    'e7fab9c090f586b6b0415fb6450405cdb8f1345df283dcd45cbf07355313d16a',
    'a58dea7d29a1ae91fdd46293d8a9a7ef99a1bab8f0ee6eb842b51eb78e4657c3',
    '0afdf2dc332e105267b2f6be1563d417da42b33d56ec1f657c06c730611590af',
    '008d13816a8232fb43acdee9eaca709bd7077f993add9b8a7cda459ed34317fc',
    '997734842c96255de54f4262b711f219e8b866106c2c20d4e6a6d6f48a28851b',
    '8c5fb7bf42a0d24662b8882b453c0703cc63ffb5a7e6ce724da352345b3b92d8',
    '8d219ac91d9638ae2b768229e1b345b549c3ef920d6ae22b3bd295230cafbbf5',
    '56df68f8c3621b6030751e56f7af04840bd46afaaa12716128e49dd10bc7c3f1',
)
FILE_HASHES = {
    'CHANGELOG.md': '89d4adf70e081b726777962bb73f6c95f06cf442afdcebf016e0ae3b7a9f345e',
    'README.md': 'c1d4e79e94b193e95702567d8aeab82dd02414f5fb5b3682c8367ed66ad1015f',
    'README.zh-CN.md': '44d139049d1183275f9cbf047e7320e60ee9b46bb79d39b3de0139eb67bcb8ac',
    'docs/accelerated-native-backend.md': 'b8bcaaf32671ba470a01b0faae94eef8270ec199442d98b58797c638960b29e9',
    'schemas/solver-capability-evidence.schema.json': '7212dfbfc69b4366578c1cf47763859486cbd8a4e727ed8cf01d892cbfd1cd12',
    'tests/test_solver_capability_v5.py': '35d365ea6320e50dd06bc0eeb11e260d287aff37ffac87126c58f89836208e6c',
    'tsao_computation/accelerators/__init__.py': '845d2754b7913a63588ae4e703b601e5d28767929d866398fa24ab1de7e229da',
    'tsao_computation/accelerators/solver.py': 'cd890d0634d41d6d6bbf19c58f9769c5e5bbb3273b43b2e7ceebdec3565d1d59',
    'tsao_computation/cli.py': '02e5961adba175477929b5eb826f4d6bf61cdd81bbf6d36f61673cfcc0a7df11',
    'tsao_computation/security/process.py': 'a5170b578cfff706ee473ce0c9d4e8a13d9e52222664d4a87a76848f8e15d8e3',
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def corrected_part_one() -> bytes:
    chunks: list[bytes] = []
    for index, expected in enumerate(CHUNK_HASHES):
        data = (ROOT / f'part-01-{index:02d}').read_bytes().replace(b'\n', b'').replace(b'\r', b'')
        if len(data) != 1000 or sha(data) != expected:
            raise SystemExit(f'part-01 chunk {index:02d} mismatch')
        chunks.append(data)
    result = b''.join(chunks)
    if sha(result) != PART_HASHES[1]:
        raise SystemExit('corrected part-01 digest mismatch')
    return result


def history_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(('git', 'show', f'{commit}:{path}')).replace(b'\n', b'').replace(b'\r', b'')


def archive_bytes() -> bytes:
    part_one = corrected_part_one()
    parts: list[bytes] = []
    for index, source in enumerate(PART_SOURCES):
        data = part_one if source is None else history_bytes(*source)
        if sha(data) != PART_HASHES[index]:
            raise SystemExit(f'part {index:02d} digest mismatch')
        parts.append(data)
    encoded = b''.join(parts)
    if sha(encoded) != '3809b9a5bc36fe9b144d89487b34dca0b8bcd0da120ef50bd33e855a35b0d436':
        raise SystemExit('hex payload digest mismatch')
    archive = bytes.fromhex(encoded.decode('ascii'))
    if len(archive) != 26339 or sha(archive) != '68a978f7d5aba1d90180ac54c0794269ba3bd57e38bb7716f92b87744173317f':
        raise SystemExit('archive identity mismatch')
    return archive


def apply(archive: bytes) -> None:
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as handle:
        members = handle.getmembers()
        if len({member.name for member in members}) != len(members) or {member.name for member in members} != set(FILE_HASHES):
            raise SystemExit('archive member set mismatch')
        for member in members:
            pure = PurePosixPath(member.name)
            if pure.is_absolute() or '..' in pure.parts or not member.isfile():
                raise SystemExit(f'unsafe member: {member.name}')
            stream = handle.extractfile(member)
            if stream is None:
                raise SystemExit(f'unreadable member: {member.name}')
            data = stream.read()
            if sha(data) != FILE_HASHES[member.name]:
                raise SystemExit(f'file digest mismatch: {member.name}')
            target = Path(*pure.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)


def main() -> None:
    apply(archive_bytes())
    shutil.rmtree(ROOT)


if __name__ == '__main__':
    main()
