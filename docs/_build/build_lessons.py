"""Build docs/lessons/*.html from lesson definitions + real source files.

Run: python3 docs/_build/build_lessons.py   (then python3 docs/_build/build_article.py)
Lesson code lives in docs/_build/lesson_src/<lesson>/ and is syntax-checked before embedding.

Code is read from disk and HTML-escaped, so what the user copies is exactly what was
syntax-checked.
"""

import html
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = REPO / "docs" / "lessons"

CSS = r"""
/* Layout: 单栏课程页，约 76ch；文件块 = 路径栏 + 代码 + 讲解。与蓝图共用同一套色板。 */
:root {
  --bg: #F4F6F8; --surface: #FFFFFF; --sunk: #E9EDF1; --fg: #16202A; --muted: #55636F; --rule: #CBD3DB;
  --accent: #0B6B70; --accent-soft: #D6ECEC; --warn: #A63A5E; --warn-soft: #F5E1E8;
  --ok: #2E7D4F; --ok-soft: #DDF0E3; --amber: #8A5A00; --amber-soft: #F6EBD3;
  --code-bg: #1C2733; --code-fg: #E3EAF0; --code-bar: #263443;
  --f-display: "Noto Serif SC", "Songti SC", "STSong", serif;
  --f-body: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", system-ui, sans-serif;
  --f-mono: "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0F151B; --surface: #161E26; --sunk: #1D2731; --fg: #E2E8EE; --muted: #9AA8B4; --rule: #2C3946;
    --accent: #5FC3C1; --accent-soft: #15383A; --warn: #E58AA8; --warn-soft: #3A1F2A;
    --ok: #79C996; --ok-soft: #173325; --amber: #E2B866; --amber-soft: #3A2E15;
    --code-bg: #0A1016; --code-fg: #DCE5EC; --code-bar: #121B24; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #0F151B; --surface: #161E26; --sunk: #1D2731; --fg: #E2E8EE; --muted: #9AA8B4; --rule: #2C3946;
  --accent: #5FC3C1; --accent-soft: #15383A; --warn: #E58AA8; --warn-soft: #3A1F2A;
  --ok: #79C996; --ok-soft: #173325; --amber: #E2B866; --amber-soft: #3A2E15;
  --code-bg: #0A1016; --code-fg: #DCE5EC; --code-bar: #121B24; color-scheme: dark;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg); font-family: var(--f-body); font-size: 16px; line-height: 1.75; padding: 0 16px; }
main { max-width: 860px; margin: 0 auto; padding-block: 40px 96px; }
a { color: var(--accent); text-underline-offset: 3px; }
a:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.eyebrow { font-family: var(--f-mono); font-size: 12px; letter-spacing: .1em; text-transform: uppercase; color: var(--accent); }
h1 { font-family: var(--f-display); font-weight: 800; font-size: clamp(28px, 4.5vw, 40px); line-height: 1.25; margin: 8px 0 12px; text-wrap: balance; }
h2 { font-family: var(--f-display); font-weight: 800; font-size: 24px; margin: 48px 0 10px; text-wrap: balance; }
h3 { font-size: 18px; margin: 28px 0 8px; }
p, li { max-width: 72ch; }
code { font-family: var(--f-mono); font-size: .88em; background: var(--sunk); padding: 1px 5px; border-radius: 4px; }
.lede { color: var(--muted); font-size: 17px; margin: 0; }
.pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.pill { font-family: var(--f-mono); font-size: 12px; padding: 2px 10px; border-radius: 999px; border: 1px solid currentColor; }
.pill.ok { color: var(--ok); background: var(--ok-soft); }
.pill.warn { color: var(--warn); background: var(--warn-soft); }
.pill.amber { color: var(--amber); background: var(--amber-soft); }
.pill.acc { color: var(--accent); background: var(--accent-soft); }
.note { border: 1px solid var(--rule); background: var(--surface); border-radius: 8px; padding: 12px 16px; margin: 16px 0; }
.note.key { border-color: var(--accent); background: var(--accent-soft); }
.note.amber { border-color: var(--amber); background: var(--amber-soft); }
.note > :first-child { margin-top: 0; } .note > :last-child { margin-bottom: 0; }
.file { margin: 22px 0 30px; }
.bar { display: flex; align-items: center; gap: 10px; background: var(--code-bar); color: var(--code-fg); border-radius: 8px 8px 0 0; padding: 8px 12px; font-family: var(--f-mono); font-size: 13px; flex-wrap: wrap; }
.bar .path { flex: 1 1 auto; min-width: 0; overflow-wrap: anywhere; }
.bar .tag { font-size: 11px; padding: 1px 8px; border-radius: 999px; border: 1px solid currentColor; opacity: .85; }
.bar button { font: inherit; font-size: 12px; color: var(--code-fg); background: transparent; border: 1px solid var(--code-fg); border-radius: 6px; padding: 2px 10px; cursor: pointer; }
.bar button:hover { background: rgba(255,255,255,.08); }
pre { margin: 0; background: var(--code-bg); color: var(--code-fg); font-family: var(--f-mono); font-size: 13.5px; line-height: 1.6; padding: 14px 16px; border-radius: 0 0 8px 8px; overflow-x: auto; }
pre.cmd { border-radius: 8px; }
.explain { margin-top: 10px; }
.check { list-style: none; padding-left: 0; }
.check li { padding-left: 1.6em; position: relative; }
.check li::before { content: "□"; position: absolute; left: 0; color: var(--accent); font-family: var(--f-mono); }
ol.files { font-family: var(--f-mono); font-size: 14px; }
nav.pager { display: flex; justify-content: space-between; gap: 12px; margin-top: 64px; padding-top: 16px; border-top: 1px solid var(--rule); flex-wrap: wrap; }
table { border-collapse: collapse; width: 100%; font-size: 15px; }
th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--rule); vertical-align: top; }
th { color: var(--muted); font-size: 13px; }
.table-wrap { overflow-x: auto; background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; }
"""

JS = r"""
document.querySelectorAll("button[data-copy]").forEach(function (btn) {
  btn.addEventListener("click", function () {
    var pre = document.getElementById(btn.getAttribute("data-copy"));
    var text = pre.innerText;
    function done(msg) { var old = btn.textContent; btn.textContent = msg; setTimeout(function () { btn.textContent = old; }, 1500); }
    function fallback() {
      var range = document.createRange(); range.selectNodeContents(pre);
      var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
      try { document.execCommand("copy") ? done("已复制") : done("已选中，按 ⌘C"); } catch (e) { done("已选中，按 ⌘C"); }
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () { done("已复制"); }, fallback);
    } else { fallback(); }
  });
});
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;800'
         '&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap">')


def page(title: str, body: str) -> str:
    return (f'<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<title>{html.escape(title)}</title>\n{FONTS}\n<style>{CSS}</style>\n</head>\n<body>\n'
            f'<main>\n{body}\n</main>\n<script>{JS}</script>\n</body>\n</html>\n')


_counter = [0]


def code_block(path: str, code: str, tag: str = "新建") -> str:
    _counter[0] += 1
    cid = f"code{_counter[0]}"
    return (f'<div class="bar"><span class="path">{html.escape(path)}</span><span class="tag">{tag}</span>'
            f'<button type="button" data-copy="{cid}">复制</button></div>'
            f'<pre id="{cid}"><code>{html.escape(code)}</code></pre>')


def cmd_block(cmds: str) -> str:
    _counter[0] += 1
    cid = f"code{_counter[0]}"
    return (f'<div class="bar"><span class="path">终端</span>'
            f'<button type="button" data-copy="{cid}">复制</button></div>'
            f'<pre id="{cid}"><code>{html.escape(cmds)}</code></pre>')


def lesson(meta: dict) -> str:
    parts = [
        f'<div class="eyebrow">{meta["eyebrow"]}</div>',
        f'<h1>{meta["h1"]}</h1>',
        f'<p class="lede">{meta["lede"]}</p>',
        '<div class="pills">' + "".join(f'<span class="pill {c}">{t}</span>' for c, t in meta["pills"]) + "</div>",
    ]
    parts.append(meta["intro"])
    parts.append("<h2>要创建的文件</h2><ol class=\"files\">" +
                 "".join(f"<li>{html.escape(f['path'])}</li>" for f in meta["files"]) + "</ol>")
    if meta.get("before"):
        parts.append(meta["before"])
    for f in meta["files"]:
        code = (meta["root"] / f["src"]).read_text(encoding="utf-8")
        parts.append(f'<section class="file"><h3>{html.escape(f["path"])}</h3>'
                     f'{code_block(f["path"], code, f.get("tag", "新建"))}'
                     f'<div class="explain">{f["explain"]}</div></section>')
    parts.append("<h2>运行</h2>" + cmd_block(meta["commands"]) + meta["expected"])
    parts.append("<h2>你需要审的数学与设计</h2>" + meta["review"])
    if meta.get("article"):
        parts.append('<h2>文章素材</h2><div class="note key">' + meta["article"] + "</div>")
    parts.append("<h2>验收清单</h2><ul class=\"check\">" + "".join(f"<li>{c}</li>" for c in meta["checklist"]) + "</ul>")
    parts.append(f'<nav class="pager"><a href="index.html">← 课程目录</a>{meta.get("next", "")}</nav>')
    return page(meta["title"], "\n".join(parts))


# ---------------------------------------------------------------------------------------
# P0
# ---------------------------------------------------------------------------------------

P0 = dict(
    title="P0 工程地基",
    eyebrow="课程 P0-01 · 阶段 P0",
    h1="P0：工程地基",
    lede="建立一个可安装、可测试的 Python 包骨架。这一步没有任何数学。",
    pills=[("ok", "代码已在仓库中"), ("ok", "测试：2 passed（2026-10-24，uv 0.13.5，Python 3.12.6）")],
    root=REPO,
    intro="""
<div class="note amber"><p>这一课的文件在定下“代码先写进课程页”规矩之前已经由 Agent 写入仓库，所以它们已经存在。你可以对照着读；想自己敲一遍的话，先删除 <code>src/</code>、<code>tests/</code> 和 <code>pyproject.toml</code>，再按本页重建。</p></div>
<h2>目标</h2>
<ul>
<li>理解 src 布局：代码放在 <code>src/geostructure/</code>，测试放在 <code>tests/</code>。</li>
<li>用 <strong>uv</strong> 管理环境：它跨平台（macOS、Linux、Windows），会按 <code>.python-version</code> 准备 Python，按 <code>pyproject.toml</code> 建 <code>.venv</code>、以可编辑方式安装本包，并生成跨平台的锁文件 <code>uv.lock</code>。</li>
<li>跑通第一个 pytest。</li>
</ul>""",
    files=[
        dict(path="pyproject.toml", src="pyproject.toml", explain="""
<p>包的“身份证”，三段：</p>
<ul>
<li><code>[build-system]</code>：用 setuptools 构建。</li>
<li><code>[project]</code>：包名、版本、Python 版本要求、运行时依赖。</li>
<li><code>[dependency-groups] dev</code>：只在开发时需要的工具（pytest），这是 PEP 735 的标准写法，<code>uv sync</code> 默认会装上。它不会成为别人安装本包时的依赖。</li>
<li><code>[tool.setuptools.packages.find] where = ["src"]</code>：告诉 setuptools 包在 <code>src/</code> 下。src 布局的好处是测试时导入的一定是安装好的包，而不是当前目录里碰巧能找到的文件。</li>
<li><code>[tool.pytest.ini_options]</code>：pytest 去 <code>tests/</code> 找测试；<code>-ra</code> 在结尾汇总跳过和失败的原因。</li>
</ul>"""),
        dict(path=".python-version", src=".python-version", explain="""
<p>只有一行 <code>3.12</code>。uv 读它来决定用哪个 Python；机器上没有就自动下载一个独立的 3.12。换电脑、换操作系统都是同一个版本。</p>"""),
        dict(path="src/geostructure/__init__.py", src="src/geostructure/__init__.py", explain="""
<p>有了这个文件，<code>geostructure</code> 目录才是一个 Python 包。现在只放版本号。docstring 写明了一条架构规则：数学内核的子包不能导入任何 LLM 库。</p>"""),
        dict(path="tests/unit/test_import.py", src="tests/unit/test_import.py", explain="""
<p>pytest 会自动收集 <code>test_</code> 开头的文件和函数。第一个测试检查包能导入且版本号格式正确；第二个检查科学计算依赖都装上了，环境有问题时会最先在这里报错。</p>"""),
    ],
    commands="""# 只需一次：安装 uv（macOS）
brew install uv

cd ~/Codes/SpnmAgent
uv sync            # 建 .venv、装 Python 3.12（如需要）、装本包与 pytest，生成 uv.lock
uv run pytest -q   # 在项目环境里运行测试""",
    expected="""<p>预期输出最后一行：</p><pre class="cmd"><code>2 passed in 0.xxs</code></pre>
<p>如果报证书或网络错误，说明是在 Claude Code 的沙箱里运行的。在提示符前加 <code>!</code>，或在你自己的终端里运行。<code>uv.lock</code> 生成后要提交到 git。</p>
<p>不想每次写 <code>uv run</code>，也可以 <code>source .venv/bin/activate</code> 激活环境后直接用 <code>pytest</code>。</p>""",
    review="<ul><li>依赖的最低版本是否与你其他项目兼容（尤其 numpy、scipy）。</li><li>包名 <code>geostructure</code> 是否作为最终名字。</li><li>Python 固定 3.12 是否合适（集群上若只有别的版本，uv 会自己下载 3.12）。</li></ul>",
    checklist=["<code>uv sync</code> 成功，仓库里出现 <code>uv.lock</code>", "<code>uv run pytest -q</code> 显示 2 passed",
               "<code>git add -A &amp;&amp; git commit -m \"P0: project skeleton\"</code>（包含 <code>uv.lock</code>）"],
    article="<p>无直接素材（工程准备）。在 <code>docs/article/notes.md</code> 记一条：环境与依赖版本，供可复现性附录使用。</p>",
    next='<a href="P1-01-core.html">下一课：P1-01 core →</a>',
)

# ---------------------------------------------------------------------------------------
# P1-01
# ---------------------------------------------------------------------------------------

P101_ROOT = HERE / "lesson_src" / "P1-01"
P101 = dict(
    title="P1-01 证据等级与 Package",
    eyebrow="课程 P1-01 · 阶段 P1 · 模块：core",
    h1="P1-01：证据等级与 Package",
    lede="实现整个系统的“通信协议”：每条结论的证据等级（Status），以及阶段之间传递的 Package。这一课没有数学，但后面每一课都建立在它上面。",
    pills=[("acc", "依赖：P0"), ("amber", "测试：not run（沙箱内缺 pydantic）"), ("ok", "已做：语法检查；status.py 的逻辑已在沙箱外单独验证")],
    root=P101_ROOT,
    intro="""
<h2>目标</h2>
<ul>
<li><strong>Status</strong>：七个证据等级，以及把多条结论合并成一个等级的规则（例如“能量律成立且质量守恒”的等级取两者中较弱的）。</li>
<li><strong>Package</strong>：照 GradAgent 的八个字段设计（Manifest、Core、Claims、Evidence、Traceability、Interface、Applicability、Report），并加上三道自动检查：
  <ol><li>结论声称有支持时必须引用证据；声称已证明时必须写出假设。</li>
  <li>引用的证据和依赖的结论必须存在。</li>
  <li>内容哈希：Package 发布后若被改动，能立刻发现。</li></ol></li>
<li>“发布”的定义：哈希完好，并且每个审计门最近一次结论都是 PASS。</li>
</ul>
<h2>新概念</h2>
<div class="table-wrap"><table>
<tr><th>概念</th><th>一句话</th></tr>
<tr><td><code>Enum</code></td><td>一组固定的取值。<code>class Status(str, Enum)</code> 让每个值同时是字符串，写进 JSON 时自然变成 <code>"symbolically_checked"</code>。</td></tr>
<tr><td>Pydantic <code>BaseModel</code></td><td>声明字段和类型，构造时自动校验；类型不对或缺字段会抛 <code>ValidationError</code>。</td></tr>
<tr><td><code>extra="forbid"</code></td><td>出现未声明的字段就报错。防止把 <code>status</code> 拼成 <code>stauts</code> 后被悄悄忽略。</td></tr>
<tr><td><code>Field(default_factory=list)</code></td><td>每个对象拿到自己的一个新列表，而不是所有对象共用一个。</td></tr>
<tr><td><code>@model_validator(mode="after")</code></td><td>所有字段校验完后再跑的整体检查，用来写跨字段的规则。</td></tr>
<tr><td><code>model_copy(update=...)</code></td><td>复制一个对象并替换部分字段。这里所有“修改”都返回新对象，原 Package 不变。</td></tr>
<tr><td>SHA-256 内容哈希</td><td>把内容序列化成规范 JSON（键排序）再取哈希；内容变一个字符，哈希就完全不同。</td></tr>
<tr><td><code>pytest.raises</code>、<code>tmp_path</code></td><td>前者断言某段代码必须抛错；后者是 pytest 提供的临时目录。</td></tr>
</table></div>""",
    before="""<div class="note"><p>先建目录：<code>mkdir -p src/geostructure/core</code>。然后按顺序创建下面五个文件。</p></div>""",
    files=[
        dict(path="src/geostructure/core/status.py", src="src/geostructure/core/status.py", explain="""
<p><code>EVIDENCE_RANK</code> 给三个“支持性”等级排序。<code>combine</code> 的规则按顺序判断：有一项 <code>failed</code> 整体就失败；有一项没跑整体就是 <code>not_run</code>；有一项不确定整体就是 <code>unknown</code>；<code>not_applicable</code> 的项不参与；其余取最弱的支持等级。空输入返回 <code>not_run</code>，表示什么都还没检查。</p>"""),
        dict(path="src/geostructure/core/package.py", src="src/geostructure/core/package.py", explain="""
<p>从上到下：</p>
<ul>
<li><code>_Strict</code>：所有模型的基类，统一打开 <code>extra="forbid"</code>。</li>
<li><code>Evidence</code>：一条证据，<code>kind</code> 区分推导、契约检查、数值结果、文献来源。</li>
<li><code>Claim</code>：一条结论。校验器实现两条规矩：支持性等级必须有证据引用；<code>proved_under_assumptions</code> 必须写明假设。</li>
<li><code>Link</code>：可追溯性的一条边，例如“连续能量律 —由…保持→ 离散能量律”。</li>
<li><code>Interface</code>、<code>Applicability</code>：交给下游的接口约定，以及适用范围和不能外推的结论。</li>
<li><code>AuditRecord</code>、<code>Manifest</code>：审计记录和清单。<code>upstream</code> 记录所依赖的上游 Package 的哈希，上游一变就能发现。</li>
<li><code>Package._references_resolve</code>：检查 id 不重复、引用都存在。形如 <code>"other_package:c7"</code> 的依赖指向别的 Package，这里不检查。</li>
<li><code>_HASH_EXCLUDE</code>：哈希不包括 <code>content_hash</code> 本身、审计记录和创建时间。审计一个 Package 不应该改变它的内容哈希。</li>
<li><code>is_released</code>：按时间排序取每个门的最近结论，全部 PASS 才算发布。</li>
</ul>"""),
        dict(path="src/geostructure/core/__init__.py", src="src/geostructure/core/__init__.py", explain="""
<p>把常用的名字从子模块“提”到 <code>geostructure.core</code> 这一层，使用时写 <code>from geostructure.core import Package</code> 即可。<code>__all__</code> 列出公开接口。</p>"""),
        dict(path="tests/unit/test_status.py", src="tests/unit/test_status.py", explain="""
<p>逐条覆盖 <code>combine</code> 的五条规则。测试就是规格说明：将来有人改合并规则，这些测试会先失败。</p>"""),
        dict(path="tests/unit/test_package.py", src="tests/unit/test_package.py", explain="""
<p><code>make_package()</code> 构造一个 Cahn–Hilliard 结构分析的示例 Package。测试分三组：</p>
<ul><li>Claim 的规矩：没有证据的支持性结论、没有假设的“已证明”、拼错的字段，都必须被拒绝。</li>
<li>Package 的引用：引用不存在的证据、重复的 id、悬空的依赖都被拒绝；外部依赖允许。</li>
<li>哈希、审计、文件：密封后改内容会被发现；审计不改哈希；发布规则；保存再读取后完全一致。</li></ul>
<p>反例测试和正例一样重要，GradAgent 审计抓到的问题，在我们这里要尽量由这类测试自动抓住。</p>"""),
    ],
    commands="""mkdir -p src/geostructure/core
# 创建上面五个文件后：
uv run pytest -q""",
    expected="""<p>预期（含 P0 的 2 个测试）：</p><pre class="cmd"><code>20 passed in 0.xxs</code></pre>
<p>这一课的代码在沙箱中没能完整运行（缺 pydantic），只做了语法检查，<code>status.py</code> 的合并逻辑单独验证过。你录入后告诉我，我来跑测试并报告真实结果。</p>""",
    review="""<ul>
<li><strong>合并规则</strong>：<code>not_run</code> 排在 <code>unknown</code> 前面是否合适？我的理由是“没跑”比“跑了但不确定”信息更少。</li>
<li><strong>“已证明”的门槛</strong>：现在只要求有假设和证据引用。是否还要求至少一条证据的 <code>kind</code> 是 <code>derivation</code>？</li>
<li><strong>哈希的范围</strong>：审计记录和创建时间不算内容，你是否同意？</li>
<li><strong>Evidence.kind</strong> 的四类是否够用，例如是否需要单独的 <code>symbolic</code>。</li>
</ul>""",
    checklist=["五个文件已创建", "<code>pytest -q</code> 显示 20 passed",
               "理解每个测试为什么存在，能说出任意一个反例测试防止的错误",
               "<code>git commit -m \"P1-01: core status and package\"</code>"],
    article="""<ul>
<li><strong>3.3 节</strong>：表 T1“七个证据等级”与合并规则；Package 八个字段与 GradAgent 的对照（我们加了 Status 和契约记录）。</li>
<li><strong>E1 错误目录·报告层</strong>：“声称已证明但没有假设 / 证据”的反例测试就是一类可注入错误，校验器能百分之百拦截。</li>
<li><strong>3.5 节</strong>：内容哈希是“裁判不可篡改”和 ASI07 对策的基础。</li>
</ul><p>录入并通过测试后，在 <code>docs/article/notes.md</code> 追加一条，引用 pytest 输出。</p>""",
    next='<span>下一课：P1-02 gsge 内核（待写）</span>',
)

INDEX_ROWS = [
    ("P0-01-foundation.html", "P0-01", "工程地基", "pyproject、uv、包骨架、第一个测试", "已完成 · 2 passed"),
    ("P1-01-core.html", "P1-01", "证据等级与 Package", "Status、Claim、Evidence、Package、哈希、审计", "待录入"),
]


def index() -> str:
    rows = "".join(f'<tr><td><a href="{f}">{n}</a></td><td>{t}</td><td>{d}</td><td>{s}</td></tr>'
                   for f, n, t, d, s in INDEX_ROWS)
    body = f"""
<div class="eyebrow">GeoStructure-Agent · 课程</div>
<h1>代码课程目录</h1>
<p class="lede">按项目规矩，所有代码先发布在这里。每一课给出完整文件、讲解、运行命令和验收清单；你自己敲或复制到仓库里。</p>
<div class="note key"><p>每一课的流程：读目标和新概念 → 创建文件 → 运行测试 → 审数学与设计 → 打勾验收 → 提交。录入后告诉 Agent，它会跑测试并报告真实输出。</p></div>
<h2>课程</h2>
<div class="table-wrap"><table><tr><th>编号</th><th>标题</th><th>内容</th><th>状态</th></tr>{rows}</table></div>
<p><a href="../GeoStructure-Agent-Blueprint.html">返回蓝图</a> · <a href="../article/article-plan.html">文章规划</a></p>"""
    return page("GeoStructure 课程", body)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "P0-01-foundation.html").write_text(lesson(P0), encoding="utf-8")
    (OUT / "P1-01-core.html").write_text(lesson(P101), encoding="utf-8")
    (OUT / "index.html").write_text(index(), encoding="utf-8")
    print("written:", sorted(p.name for p in OUT.iterdir()))
