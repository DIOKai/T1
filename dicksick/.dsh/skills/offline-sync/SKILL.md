---
name: offline-sync
description: Design and verify durable local data, outbox delivery, idempotent synchronization, conflict handling, and account isolation in offline-capable apps. Use for persistent offline workflows beyond network-status and request-cancellation setup.
---

# Offline Data and Sync

先检查现有数据模型、本地存储、查询缓存和后端协议。现有expo-data-fetching已覆盖基础网络状态；本Skill补充持久化同步，不重复更换框架。

## 明确合同

记录哪些操作允许离线、账号/租户、实体标识、服务端版本、幂等机制、确认语义、冲突策略、保留/删除与恢复要求。缺少服务端协议时先标明限制，不承诺客户端单方面实现“恰好一次”。

## 实施

1. 记录本地意图与outbox消息的事务边界；进程崩溃后应能恢复。区分queued、in-flight、acknowledged、retryable、blocked/conflict和failed，状态名按项目实际约定。
2. 请求携带稳定操作ID、账号范围和适用的版本前提。服务端需要验证身份并实现相应幂等/并发控制；仅靠本地去重不能防止服务端重复副作用。
3. 超时或取消可能发生在服务端提交之后。保留待确认状态，重试复用同一操作身份；不要生成新ID假装是新操作。
4. 冲突按业务规则处理，不默认为最后写入获胜。删除、过期数据、依赖操作与权限撤销要有显式策略。
5. 账号切换停止旧任务，隔离本地命名空间、排队写入与迟到结果；缓存或已登录UI不代表请求有权限。
6. schema迁移与同步流程按 [persistence-and-migration.md](references/persistence-and-migration.md) 验证；故障场景按 [delivery-and-tests.md](references/delivery-and-tests.md) 验证。

交付协议、状态转移、版本/迁移、故障测试与恢复限制。默认只在测试副本/模拟后端操作，不清空用户缓存、删除数据或迁移真实数据库来“修复同步”。
