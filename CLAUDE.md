# 技能使用规则

用户用中文交流，回复也用中文。

## 什么时候直接用、什么时候先问

每次收到请求，先看已安装的技能里有没有和这件事相关的。

**直接用，用的时候告诉用户用了哪个**（一句话，例如"我用 systematic-debugging 来查这个问题"）：
- 请求和技能明显对得上，比如要 PDF 就用 `document-skills:pdf`，要查 bug 就用 `superpowers:systematic-debugging`
- 技能只是给出做事的方法或步骤，不会额外改文件、装东西或连外部服务

**先问用户要不要用，说明这个技能会做什么、为什么适合**：
- 只是可能相关，不确定是不是用户要的
- 技能会大幅改变做法，比如 superpowers 的 brainstorming 会先问一轮需求，TDD 会先写测试
- 会安装依赖、跑脚本、开浏览器、连外部服务或需要登录，比如 playwright-skill、video-downloader、knowledge-work 插件里的连接器
- 会派出多个子代理或跑很久，比如 trailofbits 的 c-review、zeroize-audit
- 用户没要求、但用了明显有帮助的技能（主动建议）

**不用**：没有相关技能，或者用户明确说不要用。

## 写 FiveM / QBCore / Qbox 相关代码时

优先用用户自己的 `fivem-script` 技能，再按需要搭配 superpowers（规划、调试、审查）和安全检查技能（insecure-defaults、sharp-edges）。
