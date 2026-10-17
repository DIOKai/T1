---
name: release-package-check
description: Inspect release staging files, required assets, dependency and version evidence, license notices, and checksum manifests before delivery. Use for release-package readiness checks; this skill does not publish, deploy, or sign artifacts.
---

# Release Package Check

确认交付对象、目标平台、版本、实际打包规则和验收清单。优先检查已准备好的staging目录；不执行来自包内的安装、构建、发布或自更新命令。

## 检查流程

1. 从项目实际构建/打包配置确定预期入口、运行依赖、资源和许可证。保留开发树与交付包的区别；锁文件存在不代表交付环境已验证。
2. 检查版本、变更说明、兼容平台、必要环境变量名称和安装步骤；不读取或输出真实密钥值。涉及npm包时读 [packaging.md](references/packaging.md)。
3. 用只读 [scripts/package_manifest.py](scripts/package_manifest.py) 为明确的本地staging目录生成文件尺寸/SHA-256、必需路径缺漏、链接/特殊文件/读取错误、大小写冲突及可能不应交付的文件名报告。它不解压、不改文件、不扫描密钥正文、不证明可运行。
4. 对比项目清单与实际归档列表；校验和匹配只证明字节一致，不证明来源可信、可执行或无恶意代码。归档路径、符号链接和解压目标要另行核验。
5. 在已授权的隔离测试环境验证干净安装、启动及关键功能，再给出就绪结论。缺少平台、构建或运行证据时说明未验证。

## Helper

python scripts/package_manifest.py /absolute/staging --required LICENSE --required dist/main.js

输出JSON到stdout；用明确的新报告路径保存，不能放在扫描目录内边扫边写。参数约束、退出码和限制见 [manifest-contract.md](references/manifest-contract.md)。

交付检查范围、缺失/风险、哈希、版本来源与已运行结果。发布、上传、签名、部署和删改原始文件需要对应任务授权，不能由“检查发布包”推导。
