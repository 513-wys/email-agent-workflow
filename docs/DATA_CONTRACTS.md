# 数据契约与迁移基线

`/schemas/email_agent_contracts.schema.json` 定义 v1 的九个领域对象。Schema 是 Agent、确定性工具、数据库层和 UI 之间的结构基线；数据库表可以为查询优化，但不得改变字段语义。

| 编号 | 对象 | 作用 |
|---|---|---|
| DC-01 | `MailAccount` | 邮箱来源、服务商、时区与密钥引用 |
| DC-02 | `EmailEvent` | 邮箱适配器取得的原始邮件事件 |
| DC-03 | `NormalizedEmail` | MIME、正文、转发上下文和链接标准化结果 |
| DC-04 | `SecurityAssessment` | 规则与语义安全判断 |
| DC-05 | `TriageResult` | 分类、优先级、摘要和置信度 |
| DC-06 | `ContextBundle` | 联系人、网站和知识引用 |
| DC-07 | `ProcessingRun` | 每次处理的状态、耗时和错误 |
| DC-08 | `CorrectionRecord` | 用户对分类和优先级的纠正 |
| DC-09 | `DigestReport` | 晨报统计、分组和正文 |

## 通用约束

- ID 为不透明字符串；时间使用带时区 RFC 3339；账户时区使用 IANA 名称。
- 数据库存英文稳定枚举，展示层负责中文翻译。
- 邮件 HTML 属于不可信输入，不得直接在页面执行。
- `secret_ref` 只保存密钥引用，不保存明文密钥。
- Agent 输出通过对应 Schema 校验后才能进入持久层。
- 未识别分类使用 `OTHER`，不得临时生成新枚举。

## 版本与迁移规则

1. 当前契约版本为 `1.0.0`。
2. 新增可选字段升级次版本；删除、改名或改变字段语义升级主版本。
3. 数据库以 `schema_migrations(version, applied_at, checksum)` 记录迁移。
4. 每个迁移包含向前 SQL、数据回填策略、回滚说明和旧版本兼容窗口。
5. 应用启动前按版本执行迁移并校验 checksum；失败时拒绝继续写入。
6. 迁移现有 `emails` 表时，回填 `received_at`、`account_id`、`source_id` 和稳定 `message_id`；无法确定的值标记迁移来源，不伪造为当前时间。
7. 运行时迁移框架属于 H-06；本文件完成 A-04 的领域契约与迁移规范，不表示现有数据库已经升级。

## 现有字段映射

| 现有概念 | 新契约字段 | 处理方式 |
|---|---|---|
| `trace_id` | `ProcessingRun.id` | 保留为历史运行标识 |
| 邮件数据库主键 | `NormalizedEmail.id` | 新建稳定领域 ID |
| 当前处理时间 | `ProcessingRun.started_at/completed_at` | 不再作为收件时间展示 |
| 邮件 Date 头 | `EmailEvent.received_at` | 解析并转成带时区时间 |
| 发件人 | `NormalizedEmail.from` | 拆分地址与显示名 |
| 当前分类文本 | `TriageResult.category` | 映射为稳定英文枚举 |
| IMAP UID | `EmailEvent.source_id` | 用于去重和原文定位 |

