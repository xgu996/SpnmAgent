"""Build docs/article/article-plan.html with the same styling as the lessons."""

from pathlib import Path

from build_lessons import page

OUT = Path(__file__).resolve().parents[1] / "article"

BODY = (Path(__file__).resolve().parent / "article_body.html").read_text(encoding="utf-8")

NOTES = """# 研究日志（GeoStructure-Agent 文章素材）

每完成一课或一次实验追加一条。数字只引用输出文件路径，不手写。

模板：

```
## YYYY-MM-DD · <课程或实验编号>
- 做了什么：
- 关键结果：（输出文件路径）
- 决策（如有）：选择 / 备选 / 理由
- 对文章的意义：（对应哪一节、哪张图表）
```

---

## 2026-10-24 · 规划
- 做了什么：完成蓝图 v0.4（五模块架构、GSGE 语言、投影 gauge、Agent 工具栈、MCP、上下文/内存/记忆/安全）；建立课程体系（Rule 0）；P0、P1-01 课程页。
- 决策：默认模型 OpenAI（gpt-6.1-sol），免费模型做对比 / 备选：Anthropic、Google / 理由：用户指定；同时便于做“强模型 vs 免费模型”实验。
- 决策：编程子 Agent 用 LangChain Deep Agents / 备选：Claude Agent SDK、OpenAI Codex / 理由：与模型无关，免费模型也能参加 Program 阶段对比。
- 决策：MCP 按 2026-07-28 规范，一个模块一个服务器 / 理由：权限边界即服务器边界。
- 对文章的意义：相关工作（GradAgent 审计错误类型 → E1 错误目录）；3.4 工具栈。
"""

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "article-plan.html").write_text(page("GeoStructure 文章规划", BODY), encoding="utf-8")
    notes = OUT / "notes.md"
    if not notes.exists():
        notes.write_text(NOTES, encoding="utf-8")
    print("written", sorted(p.name for p in OUT.iterdir()))
