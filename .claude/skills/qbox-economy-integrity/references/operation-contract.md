# 操作合同与边界

为一次购买、奖励或合成记录：服务端认可的业务操作身份、角色/账户、商品/配方、服务端金额与数量、适用版本/前提、交付状态和恢复责任。拒绝非有限数、负数、零值、非整数数量及越界乘法结果；按当前货币单位核对取整和上限。

重复与并发是两件事：相同意图重试应取得同一结果；不同请求 ID 仍不能绕过配方次数、冷却、库存或账户条件。身份必须绑定角色和具体操作，不能仅接受客户端随机键。source 是临时连接 ID，不是持久角色身份。只在内存加锁不能覆盖进程重启；若设计要求重启后恢复，需持久化操作记录及可查询的交付证据。

按实际协议列出 prepared、debited、delivered、compensated、unknown 等状态的合法转换。名称可变，但不能把超时当作“未发生”。退款失败也需有状态和处置；不能每次恢复都再次退款。多种货币/组织账户要分别核对相应资源权限和 API，不假设 AddMoney/RemoveMoney 的所有实现相同。

SQL 条件更新影响 0 行可能仍是成功执行的 SQL；事务返回 true 不等于业务条件成立。检查当前驱动和业务 API 是否提供所需条件结果/锁语义，不拿两条普通 UPDATE 示例当作通用转账实现。对自有业务表可以设计事务；核心持有表按 Qbox 公共接口操作。

核对来源（2026-10-17）：
- [Qbox 开发指南](https://docs.qbox.re/developers)：公开接口、核心数据所有权与版本。
- [Qbox 服务端 exports](https://docs.qbox.re/resources/qbx_core/exports/server)：以服务器安装版本验证具体签名与返回值。
- [ox_inventory 服务端接口](https://overextended.dev/docs/ox_inventory/Functions/Server)：AddItem、RemoveItem、CanCarryItem 与失败结果。
- [oxmysql transaction](https://overextended.dev/docs/oxmysql/Functions/transaction)：事务与查询结果的边界。
- [Cfx 事件安全](https://docs.fivem.net/docs/developers/server-security/)：使用服务端可信值校验客户端意图。

以上是流程设计依据，不是对用户资源完成实测的证明。
