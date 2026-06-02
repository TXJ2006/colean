# CoLean 本地 LLM 实验说明

## 实验目的

本轮实验验证一个省钱路线：

```text
本地小模型生成/排序候选
-> CoLean 保留候选证明链
-> Lean/Mathlib 验证正确性
-> 失败或成功反馈回写权重
```

这里的本地 LLM 不承担“最终证明器”的角色。它只提供候选或排序信号，最终是否正确仍由 Lean kernel 和 Mathlib 检查。

## 本地部署结果

已经安装并启动 Ollama：

```text
Ollama 0.24.0
```

已经下载轻量代码模型：

```text
qwen2.5-coder:1.5b
```

这台机器约 32GB 内存、16 逻辑线程，没有检测到 NVIDIA GPU，因此当前按 CPU/内存路线运行。成本为 0 元，但速度和模型能力会低于云端大模型。

## 对比实验

同一个本地模型跑了两种模式。

### 1. 自由生成 Lean tactics

让 `qwen2.5-coder:1.5b` 直接写完整 Lean tactic 脚本：

```text
candidates_checked = 2
accepted = 0
rejected = 2
```

模型能猜到方向，例如想到 `apply` 或相关 theorem，但 Lean 语法和参数经常不精确，所以无法通过 Mathlib 验证。

### 2. CoLean 约束候选排序

让同一个模型不再自由写证明，而是在 CoLean 给出的候选 proof-chain 中排序：

```text
candidates_checked = 2
accepted = 2
rejected = 0
```

具体结果：

```text
split_positive_mass_bucket:
  model ranking = A, B, C
  first accepted rank = 1

finite_level_threshold_bucket:
  model ranking = B, A
  first accepted rank = 2
```

也就是说，本地小模型自由证明失败，但在 CoLean 候选图约束下，top-k 验证可以命中正确证明。

## 这说明了什么

这轮实验支持我们的核心思想：

```text
不要期待小模型一次性写出完全正确的形式化证明。
应该让小模型参与候选生成和候选排序，
再让 CoLean 通过对应图保留多条路径，
最后用 Lean/Mathlib 做硬验证。
```

这种设计同时带来两个好处：

```text
省钱：本地模型即可提供可用信号，不必每步调用云端大模型。
提高正确率：错误候选不会直接进入最终结果，而是被 Lean 拒绝并反馈降权。
```

## 当前结论

在这个小规模 Mathlib proof-chain 实验中：

```text
free local LLM generation: 0/2 accepted
CoLean-constrained local LLM ranking: 2/2 accepted
```

这不是最终科研结论，但已经是一个很有力的机制级证据：CoLean 的结构化候选图能把弱本地模型转化为有用的证明搜索组件。

## 下一步

建议继续做三件事：

```text
1. 扩展候选 proof-chain 数量，从 2 个 lemma 扩到 10-20 个 lemma。
2. 加入 3-5 个候选脚本的 top-k 曲线，统计 top-1/top-3/top-5 通过率。
3. 尝试更强但仍免费的本地模型，例如 qwen2.5-coder:7b，比较 1.5B 与 7B 的排序质量。
```
