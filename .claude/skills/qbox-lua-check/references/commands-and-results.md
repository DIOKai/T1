# 命令与结果

以安装版本的帮助为准。当前上游示例：

```text
qbx-lint --version
qbx-lint client/main.lua server/main.lua
qbx-lint --format json --output /absolute/new-report.json client/main.lua server/main.lua
qbx-lint fmt --check client/main.lua server/main.lua
```

报告文件使用明确的新输出位置，不能覆盖源文件/配置。无参数会检查当前目录；不在服务器或仓库根目录无意扩大范围。配置需要时用 --config 显式选择，并保留项目约定。

当前 README：lint 退出 1 表示错误或超过警告阈值，2 表示调用/处理失败；fmt --check 不写源文件，需格式化时退出 1。默认显示 info 及以上；未设置警告阈值时，0 不代表零警告。--no-fail 会抑制诊断导致的失败，不能当作严格检查通过。每次仍以实际安装版本核对。

--fix 与 fmt（无 --check）会改文件；不能把“检查”命令替换成它们。CI 的 --max-warnings 0 是项目可选门槛，不能无授权强加或删掉既有门槛。

来源：[Qbox qbx-lua README](https://github.com/Qbox-project/qbx-lua#use)、[配置与分析参考](https://github.com/Qbox-project/qbx-lua/blob/main/docs/reference.md)，核对于 2026-10-17。仓库曾用名 qbx-lint；使用固定、已核对版本，不自动追 latest 或照搬旧 Action 地址。
