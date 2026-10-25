# GeoStructure-Agent — 给终端 Coding Agent 的研究工程任务书（V0.1）

> 使用方法：将本文件放在一个新建的空 Git 仓库根目录，然后把下面“执行指令”一节连同本文件路径交给 Codex、OpenCode 或其他终端编程 Agent。此文档是研究工程任务书，不是已经验证的新数学方法或论文结论。

## 0. 执行指令（务必遵循）

你现在是**计算数学研究工程师 + 严格的科学软件开发者**，请在当前仓库启动一个真正可执行、可测试、可扩展、面向论文研究的项目：**GeoStructure-Agent: Agentic Synthesis and Verification of Geometric and Structure-Preserving Numerical Methods**。

**不要直接实现一个巨大而空洞的多 Agent 平台。先搭建独立于 LLM 的确定性数学内核，再构建 Agent。不要把“运行数值实验没有失败”写成“证明某算法保结构”。**

你的工作顺序：
1. 检查仓库和 Python 环境。若非空，保留现有文件，先报告影响范围；不要覆盖未知成果。
2. 建立 `AGENTS.md`、`docs/architecture.md`、`docs/research_roadmap.md`、`docs/math_contracts.md`、`docs/literature_matrix.md`、`docs/benchmark_plan.md` 和 `docs/progress.md`。先明确模块职责、数学假设、研究问题、验收标准。
3. **只落地 Milestone 1**：两个 Hamilton 算例（谐振子、非线性单摆）和一个耗散 ODE，集成辛方法和保能量方法，建立检查报告与测试。Milestone 1 完成之前，不开发真正的多 Agent 系统、Web UI、MCP 服务或 PDE 求解器。
4. 为后续扩展预留抽象接口，但避免臆造大量未用的类。坚持“最小有用抽象”。
5. 每完成一项运行 `pytest`，保存真实运行日志、数值结果和图表。若无法运行，明确标注 `not run`，不能声称通过。
6. 结束时报告：实际创建的文件、执行的命令、通过/失败的测试、数学上已经证明/仅数值支持/未验证的结论、下一阶段的最小任务。

请直接开始，不要停留在只有计划的回答。如果某项数学性质存在条件或不确定性，保留 `unknown` 状态，不要自行补造假设。

## 1. 总体研究目标

建立统一的**结构识别 → 数值格式合成 → 数学结构验证 → 程序实现 → 数值实验 → 证据报告**的 Agent 工作流。最终面向多物理场 PDE，但第一版从几何数值积分开始。

需要覆盖的结构与方法家族（**目标范围，非 V0.1 交付清单**）：

| 结构目标 | 典型数学框架 | 候选方法 |
| --- | --- | --- |
| 能量守恒 | Hamiltonian / Poisson | discrete gradient, AVF, HBVM |
| 辛结构保持 | 典则 Hamiltonian 系统 | symplectic Euler, Störmer–Verlet, implicit midpoint, Gauss RK |
| 动量和第一积分 | 对称性、momentum maps | variational integrators, projection, energy-momentum methods |
| 能量耗散与熵产生 | gradient flow, metriplectic, GENERIC, port-Hamiltonian | discrete gradient, convex splitting, SAV/IEQ（需说明辅助能量与原能量区别） |
| 质量/电荷/局部守恒 | conservation laws | conservative finite volume, compatible operators, SBP |
| Poisson、Casimir、约束与多辛结构 | Poisson brackets, constrained Hamiltonian, multisymplectic PDE | Poisson methods, SHAKE/RATTLE, multisymplectic schemes |
| 体积与时间对称性 | volume preservation, reversibility | volume-preserving schemes, symmetric compositions |
| 正性、最大值原理及熵结构 | positivity / bound preservation, entropy stability | positivity-preserving, invariant-domain, entropy-stable schemes |
| 多物理场耦合 | conservative–dissipative coupling | energy-compatible couplings, operator splitting, block solvers |

**数学底线**：一般非线性 Hamilton 系统不能默认某一步进法同时严格保能量与保辛。不同要求可能需要不同方法；外力、边界通量及数值非线性求解容差都会改变能量结论。所有输出必须给出适用条件。

## 2. 建议的分层架构

- **Model/Structure IR**：用 Pydantic/dataclass 表示变量、状态空间、Hamiltonian/自由能、约束、源项、边界条件、时间区间、结构目标以及适用假设。
- **Operator & Scheme Registry**：登记离散算子及数值方法；记录定义域、值域、离散配对、方程残差、收敛条件、模型适用性和能力声明。
- **Contract Engine**：对能量增量、离散梯度恒等式、反对称、半正定、离散伴随、守恒和辛条件建立可复用检查。检查输出必须同时包含前提和证据等级。
- **Numerical Backends**：初期只用 NumPy、SciPy、SymPy；未来可接 PETSc/FEniCSx/deal.II/VEM 自有程序。后端不得持有研究结论的唯一表示。
- **Experiment & Evidence**：可复现设置、求解状态、结构残差、能量图、误差、日志、证明说明及来源。
- **Agent Orchestrator（后续）**：由 LLM 提案、确定性验证器审查、失败反馈修正；状态编排考虑 LangGraph，但不得作为数学内核的依赖。

为未来引入 Danus 式事实依赖图保留字段，但不要在 V0.1 实现整套知识图谱。

## 3. 最小 IR 数据模型（先设计，再按需实现）

建议的核心对象：

- `ModelSpec`: `name, kind, state_variables, equations, energy_functional, constraints, parameters, boundary_conditions, assumptions, targets`。
- `SchemeSpec`: `name, family, one_step_equation, supported_models, assumptions, nonlinear_solver_config`。
- `StructureClaim`: `property, precise_statement, required_assumptions, method_id, evidence_refs, status`。
- `VerificationResult`: `status, checker, assumptions_checked, residuals, solver_status, evidence, limitations`。
- `ExperimentSpec`: `model, method, parameters, initial_data, dt, num_steps, tolerances, seed`。

状态枚举至少区分：`proved_under_assumptions`, `symbolically_checked`, `numerically_supported`, `failed`, `unknown`, `not_run`。`proved_under_assumptions` 必须有人工可审核的推导和完整假设；不允许仅凭 SymPy 化简或浮点测试标记为 `formally_verified`。

## 4. Milestone 1 — 要真正跑通的最小闭环

### 4.1 数学模型

A. **谐振子**：`H(q,p) = (q²+p²)/2`，`q'=p, p'=-q`。用于检查二次 Hamiltonian 的特殊性质。

B. **非线性单摆**：`H(q,p)=p²/2 + 1-cos(q)`，`q'=p, p'=-sin(q)`。**主要用于区分保辛与保能量方法，不可只用谐振子证明一般性结论**。

C. **耗散 Hamiltonian 系统**：`z'=(J-R)∇H(z)`，其中 `J^T=-J`、`R^T=R ⪰ 0`，先取二次 H 与常系数 J,R，验证无外部功输入时能量下降。

### 4.2 数值方法

- `explicit_euler`：非保结构基线。
- `symplectic_euler`：在可分离 Hamiltonian 上实现一种明确的变体。
- `stormer_verlet`：在可分离 Hamiltonian 上实现。
- `implicit_midpoint`：对典则 Hamiltonian 的辛方法；对一般非线性 Hamiltonian 不宣称严格保能量。
- `avf_discrete_gradient`：对常反对称 J 和正确计算的离散梯度，具有能量守恒恒等式（精确求解时）；实现时按非线性求解和积分精度报告残差。
- `dissipative_discrete_gradient`：验证离散能量非增条件，记录非线性求解器残差。

**重点**：单摆 AVF 使用沿状态线段的正确积分表达；可使用解析表达或经过校验的高精度求积，不得默默把低阶求积误差称为“严格能量守恒”。处理 `q_{n+1}-q_n≈0` 的数值稳定性。

### 4.3 数学契约 / 检查器

1. `energy_balance_check`：跟踪每步能量差；保能量情况检查 `H_{n+1}-H_n`；耗散情况检查相应离散能量平衡或不等式。
2. `symplecticity_diagnostic`：低维典则系统计算一步映射 Jacobian 并检查 `DΦ^T Ω DΦ−Ω`；有限差分结果是数值诊断，不能代替适用定理。注明 `Ω=[[0,1],[-1,0]]` 的坐标约定。
3. `operator_contract_check`：检查反对称、对称半正定等代数性质；数值特征值只支持浮点级诊断。
4. `solver_convergence_check`：若非线性求解失败、残差过大或发生 NaN，不能返回通过。
5. `invariant_report`：每条性质都输出 `claimed / checked / not applicable` 及其前提；区分能量、辛、守恒和耗散目标。

### 4.4 可执行 CLI

设计可安装的命令行 `geostructure`，至少支持以下命令（可根据最终 CLI 库调整参数拼写，但 README 要给出真实可运行的命令）：

```bash
geostructure list-models
geostructure list-methods
geostructure run --model pendulum --method stormer_verlet --dt 0.05 --steps 2000
geostructure run --model pendulum --method avf --dt 0.05 --steps 2000
geostructure verify --experiment <output-directory>
geostructure compare --model pendulum --methods explicit_euler,stormer_verlet,avf
pytest -q
```

每次实验单独输出：`config.json`, `trajectory.csv`, `metrics.json`, `energy.png`, `verification.json`, `report.md`。需要复现所需的参数、软件版本、容差和求解器状态。

### 4.5 Milestone 1 验收标准

- 完成上述 3 个模型、至少 5 个方法和基本 CLI；严格注明不适用方法。
- 在非线性单摆上真实展示：Verlet 主要保持辛结构，能量通常有有界振荡而不是逐步精确保守；AVF 对给定条件的能量变化达到所设数值容差。不要以“某一次算例看起来很好”取代理论证明。
- 在耗散例子上验证无外部功输入时的能量非增及其前提；记录求解器误差。
- `pytest` 包括参数正确性、反例、非线性求解失败、零步长/不合法配置等边界测试。
- 生成代表性的曲线和一份 `docs/math_audit.md`，逐条区分“已推导、已符号检查、仅数值验证、尚未完成”。
- 项目不需 API Key 即能运行确定性数值实验和验证，且没有 LLM 时仍完整工作。

## 5. Milestone 2/3/4 — 保留计划，不要抢跑

- **M2：加入 PDE 的半离散结构**。从周期边界 Allen–Cahn 与 Cahn–Hilliard 开始，明确离散内积、SBP、质量守恒和离散能量。不应在未处理空间离散一致性之前将 ODE 结论直接宣称为全离散 PDE 定理。
- **M3：两场耦合**。先使用耦合振子/保守–耗散 toy model 检查能量交换项抵消，再发展到 Cahn–Hilliard–Stokes 或相关相场–流体系统；边界条件、压力约束、非线性求解误差单独列出。
- **M4：Agentic synthesis**。加入真实的模型解析与方法选择 Agent、Scheme Agent、Proof/Verifier Agent、Code Agent；用 LangGraph 状态图组织，并让结构契约成为独立于 LLM 的裁决依据；最后增加符合权限规则的证据依赖图。
- **Long-term**：辛/多辛 PDE、Poisson/Casimir 系统、体积保持、可逆性、正性和熵稳定、变分积分器、DAE 约束、多物理场与多网格后端。针对每类结构增加特定的数学定义与检查条件，不能只贴标签。

## 6. 论文研究需要的证据与对照

建立 `docs/research_questions.md` 和 `docs/literature_matrix.md`，至少对照以下工作，区分已知方法与尚待验证的研究假设：

- Danus: https://arxiv.org/abs/2607.06447
- GradAgent: https://arxiv.org/abs/2609.24871
- AutoNumerics: https://arxiv.org/abs/2602.17607
- AutoPDE: https://arxiv.org/abs/2606.10752
- AVF for energy / dissipation: https://arxiv.org/abs/1202.4555

请明确：辛积分器、AVF、离散梯度、SBP 等既有理论本身并不是本项目的原创结论。潜在的创新点在于**机器可读的结构契约、基于约束的 Agent 组合、跨空间/时间/耦合层次的验证，以及数学证据与可执行程序的可追溯映射**。这些贡献仍需文献对照、理论结果和实验才能成立。

未来至少要有：(i) 完整结构验证，(ii) 故意注入的结构错误检测，(iii) 无契约/无反馈/单 Agent 的消融，(iv) 与经典数值方法和已有 Agent 系统的对照，(v) 调用成本和成功率。每个基准问题要指定初值、网格、步长、容差、重复次数和成功定义，避免选择性报告。

## 7. 建议初始仓库结构（按需创建，不要留空目录充数）

```text
GeoStructure-Agent/
  AGENTS.md
  pyproject.toml
  README.md
  src/geostructure/
    cli.py
    core/            # ModelSpec, SchemeSpec, claims, results, validation
    models/          # oscillator, pendulum, dissipative toy model
    schemes/         # symplectic, discrete gradient, baseline
    verify/          # energy, symplectic, algebraic contracts
    experiments/     # runner, metrics, reports
    agents/          # M4 才实现
  tests/
  examples/
  docs/
    architecture.md
    research_roadmap.md
    math_contracts.md
    literature_matrix.md
    benchmark_plan.md
    math_audit.md
    progress.md
  outputs/           # gitignore generated files
```

初期依赖：Python 3.11+、NumPy、SciPy、SymPy、Pydantic、pytest、Matplotlib、Typer（或 argparse）。依赖尽量轻量。不要为了“未来可能会用”而提前安装 LangGraph、FEniCSx、PETSc、MCP、数据库或云组件。

## 8. 开发规约与禁止事项

- 数学对象、数值方法和验证器分离；不把绘图或报告逻辑写进求解器。
- “保能量/保辛/无条件能量稳定/质量守恒”都必须附上模型条件、边界条件、离散定义、求解容差及证明层级。
- 禁止用普通数值能量曲线推断辛性；禁止把“长期能量表现良好”等同严格能量守恒。
- 禁止在未验证时声称一般非线性系统的辛与能量双重精确保留。
- 禁止随意将外力做功、开放边界能流或数值舍入误差忽略。
- 非线性求解失败必须显式失败，不得静默跳过时间步或伪造数据。
- 不要编造任何引用、定理证明、实验结果或测试日志。
- 不要修改已有科研代码或隐式上传私有文件；密钥只从环境变量读取，提交前检查是否泄漏。
- 对复杂数学问题优先输出尚缺少的假设及反例，再讨论如何自动修复。

## 9. 你本次终端会话最终必须交付

1. 可安装并可用的 Python 原型（仅 M1）；
2. 一套确定性测试，运行结果可在终端检查；
3. 单摆和耗散系统的曲线与机器可读验证报告；
4. 文档：架构、研究路线、数学契约、文献矩阵、审计与下一步；
5. 用一段简短的总结明确说明：**哪些确实实现了、哪些数学性质已在特定假设下推导、哪些只是计算证据、接下来该优先做什么**。

优先保证数学严谨和可复现，其次是架构的可扩展性，最后才是 Agent 编排形式和界面美观。
