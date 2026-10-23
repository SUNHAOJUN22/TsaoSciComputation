# CI dependency policy / CI 依赖管理

## 安装与可复现性

`requirements-ci.txt` 从 `pyproject.toml` 的全部可选验证依赖解析，固定直接及传递依赖的版本、适用平台/Python 条件和发行文件 SHA-256。它服务于 Python 3.10 及以上的验证环境，不向零运行时依赖的科学控制平面引入新的生产依赖。

```bash
python -m pip install --require-hashes --only-binary=:all: -r requirements-ci.txt
python -m pip install --no-index --no-deps --no-build-isolation -e '.[validation,quality,security]'
```

第一步验证下载的第三方 wheel 身份；第二步只安装已经检出的项目，禁止索引、依赖解析和隔离构建依赖下载。缺少当前平台所需 wheel 时必须失败，不得静默退回未记录的源码构建环境。哈希固定不表示依赖没有漏洞；原有定时 `pip-audit` 仍检查实际安装环境。

## 有审查的更新

此锁文件由 `uv 0.12.23` 生成。维护者可在隔离工作区使用相同解析器重新生成候选文件，再检查版本、条件标记及 SHA-256 的差异：

```bash
uv pip compile pyproject.toml --all-extras --universal --generate-hashes \
  --python-version 3.10 --default-index https://pypi.org/simple \
  --output-file requirements-ci.txt --upgrade
```

发布候选更新前运行原有 Python/Windows/Linux 矩阵、95% 总覆盖率和关键模块门槛、质量、包构建与漏洞检查。新的锁文件和源码提交需要自己的验收记录，历史六小时结果不继承给新版本。保持 `main` 为唯一长期分支；这里没有启用自动创建更新分支的机器人，也不通过一个禁用更新的空配置声称自动维护已经完成。

## 权限与现存治理边界

- CodeQL 的 `security-events: write` 仅授予分析任务，默认权限保持只读。
- 派生 Git 对象发布任务的 `contents: write` 用于写入经过验证的 blob/tree；该任务不更新引用。
- Release 任务的写权限用于显式请求的不可变标签、发布和证明文件；这些实际功能所需权限仍保留。
- 分支保护、独立人工审查历史、OpenSSF 最佳实践认证、持续模糊测试及自动依赖更新，需要各自的真实治理或运行证据。代码中的 hash 锁、说明文档或工作流成功不能替代它们。

## Installation and reproducibility

The checked-in lock is resolved from all validation extras in `pyproject.toml`. It pins direct and transitive dependencies, environment markers and distribution SHA-256 hashes for supported Python versions. The two commands above install hash-checked third-party wheels, then install the checked-out project without an index, dependency resolution or isolated build dependency downloads. Missing compatible wheels fail closed. No production dependency is added to the runtime core.

Hash matching proves distribution identity, not freedom from vulnerabilities. The existing scheduled `pip-audit` workflow audits the installed locked environment. Regenerate an update candidate with the recorded resolver and command, review the dependency diff, and run the unchanged platform, coverage, quality, package and vulnerability gates before publishing a new accepted revision.

## Governance boundary

CodeQL write permission is scoped to its analysis job. The derived-object and explicit Release jobs retain only the write capabilities their existing publishing functions need. A hash lock does not replace branch protection, independent code-review history, a best-practices certification, continuous fuzzing or an operating dependency-update service. No disabled bot configuration is presented as a completed update service. Previous acceptance receipts remain bound to their original source revisions.
