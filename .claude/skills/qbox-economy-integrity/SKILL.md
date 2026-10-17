---
name: qbox-economy-integrity
description: Review or implement Qbox purchases, trades, crafting and rewards for server authority, duplicate delivery, concurrent access and failure recovery across money, inventory and database boundaries. Use for economic correctness, not price balancing or a general malware audit.
---

# Qbox Economy Integrity

先确认 qbx_core、库存、银行/组织账户及数据库的实际版本和调用路径。只研究或审查时不启动服务器、不触碰真实余额或数据库。保留现有框架；新实现以 Qbox exports 和公开模块为准，不直接改核心持有的数据表。

## 审查与实现

1. 画出从客户端/NUI 到服务端、账户、库存和持久化的路径。服务端从调用者身份重新取得角色、商品、价格、数量限制、位置、权限和库存；客户端只能提出意图。事件中的 source 在任何 yield 前保存，异步完成时还要核对会话/角色，防止 source 重用。
2. 先写清一次业务操作的身份、状态、资源锁/竞争范围和失败结果。按 [operation-contract.md](references/operation-contract.md) 检查重放、并发、扣款、交付和补偿。客户端按钮禁用、随机请求 ID、客户端限频或 CanCarryItem 预检查都不能单独保证防复制。
3. 分别核对每个 export 的返回值。容量检查后 AddItem 仍可能失败；不能扣款后忽略交付失败，也不能盲目先发物品再扣款。采用当前资源实际支持的预留、串行化、幂等或可追溯补偿；缺少这些能力就报告无法保证的窗口，不编造万能原子交易。
4. SQL 事务只覆盖该事务内的查询，不能回滚已发生的 qbx_core 或库存 export 副作用。禁止为求“原子性”绕过核心直接更新其余额/角色表。连接中断、确认丢失或进程崩溃产生的未知状态需核对后恢复，不无条件重发奖励/退款。
5. 按 [fault-tests.md](references/fault-tests.md) 在测试副本核对余额、物品、业务状态与副作用次数。审查输出证据和定位；真实环境没有运行时，明确写静态结论与待验证项。

## 交付与边界

返回版本、操作状态与不变量、可确认的问题、修复及故障测试结果。价格/收入曲线另属数值设计；广泛供应链审计另属安全审计。Skill 不内置已验证的支付实现，也不承诺跨服务恰好一次。
