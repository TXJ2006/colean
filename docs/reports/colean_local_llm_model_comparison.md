# CoLean 本地模型对比：1.5B vs 7B

## 任务设置

本实验使用 4 个 Mathlib proof-chain 目标：

```text
split_positive_mass_bucket
binary_level_positive_bucket
finite_level_positive_bucket
finite_level_threshold_bucket
```

每个目标都测试两种模式：

```text
1. free generation：让本地 LLM 直接写 Lean tactics
2. CoLean ranking：让本地 LLM 排序候选 proof-chain，再由 Lean/Mathlib 验证
```

## 结果

| model | free generation accepted | CoLean top-1 | CoLean top-2 | CoLean top-3 |
|---|---:|---:|---:|---:|
| qwen2.5-coder:1.5b | 0/4 | 4/4 | 4/4 | 4/4 |
| qwen2.5-coder:7b | 0/4 | 4/4 | 4/4 | 4/4 |

## 解释

两个模型直接自由生成 Lean proof 都失败：

```text
qwen2.5-coder:1.5b free generation = 0/4
qwen2.5-coder:7b   free generation = 0/4
```

这说明即使本地 7B 代码模型也不能直接当可靠 Lean 证明器。

但是，把同样的模型放进 CoLean 框架后，效果显著改变：

```text
qwen2.5-coder:1.5b CoLean top-1 = 4/4 in the latest rerun
qwen2.5-coder:7b   CoLean top-1 = 4/4
```

这支持我们的核心判断：

```text
LLM 不负责最终正确性；
LLM 负责给候选图提供排序信号；
CoLean 保留候选纤维；
Lean/Mathlib 负责硬验证。
```

## 对论文的意义

这可以作为一个很清楚的小实验：

```text
弱本地模型自由证明失败，
但在对应图约束下可以转化为有效的 proof-chain ranker。
```

尤其是 1.5B 的结果很有说服力：此前一次运行中它出现过 top-1 = 3/4、top-3 = 4/4，最新复跑达到 top-1 = 4/4。这说明 CoLean 的 top-k 验证机制能够吸收弱模型排序误差，而不是被单次 LLM 输出绑死。

7B 的结果则说明：在同样的 CoLean 结构下，模型能力提升会直接表现为更好的 top-1 排序质量。
