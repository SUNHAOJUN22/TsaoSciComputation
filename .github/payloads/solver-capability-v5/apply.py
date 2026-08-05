from __future__ import annotations

import hashlib
import io
import shutil
import tarfile
from pathlib import Path, PurePosixPath

PAYLOAD_ROOT = Path('.github/payloads/solver-capability-v5')
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
HEX_SHA256 = '3809b9a5bc36fe9b144d89487b34dca0b8bcd0da120ef50bd33e855a35b0d436'
ARCHIVE_SHA256 = '68a978f7d5aba1d90180ac54c0794269ba3bd57e38bb7716f92b87744173317f'
ARCHIVE_SIZE = 26339
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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_archive() -> bytes:
    paths = [PAYLOAD_ROOT / f'part-{index:02d}' for index in range(len(PART_HASHES))]
    actual = sorted(PAYLOAD_ROOT.glob('part-*'))
    if actual != paths:
        raise SystemExit(f'payload part set mismatch: {[path.name for path in actual]}')
    chunks: list[bytes] = []
    for index, (path, expected) in enumerate(zip(paths, PART_HASHES, strict=True)):
        data = path.read_bytes().replace(b'\n', b'').replace(b'\r', b'')
        if sha256(data) != expected:
            raise SystemExit(f'payload part {index:02d} digest mismatch')
        if any(byte not in b'0123456789abcdef' for byte in data):
            raise SystemExit(f'payload part {index:02d} contains non-hex data')
        chunks.append(data)
    encoded = b''.join(chunks)
    if sha256(encoded) != HEX_SHA256:
        raise SystemExit('complete hex payload digest mismatch')
    archive = bytes.fromhex(encoded.decode('ascii'))
    if len(archive) != ARCHIVE_SIZE or sha256(archive) != ARCHIVE_SHA256:
        raise SystemExit('binary archive identity mismatch')
    return archive


def apply_archive(archive: bytes) -> None:
    expected_names = set(FILE_HASHES)
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as handle:
        members = handle.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)) or set(names) != expected_names:
            raise SystemExit(f'archive member set mismatch: {names}')
        for member in members:
            pure = PurePosixPath(member.name)
            if pure.is_absolute() or '..' in pure.parts or not member.isfile():
                raise SystemExit(f'unsafe archive member: {member.name}')
            source = handle.extractfile(member)
            if source is None:
                raise SystemExit(f'archive member cannot be read: {member.name}')
            data = source.read()
            if sha256(data) != FILE_HASHES[member.name]:
                raise SystemExit(f'file digest mismatch: {member.name}')
            target = Path(*pure.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    for name, expected in FILE_HASHES.items():
        if sha256(Path(name).read_bytes()) != expected:
            raise SystemExit(f'post-write digest mismatch: {name}')


def main() -> None:
    apply_archive(read_archive())
    shutil.rmtree(PAYLOAD_ROOT)


if __name__ == '__main__':
    main()
