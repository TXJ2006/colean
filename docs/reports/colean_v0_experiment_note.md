# CoLean v0 实验说明

## 这个实验已经说明了什么

这个实验验证了对应计算思想的第一个核心判断：

> 不要把结构先压成矩阵、embedding 或 prompt；先保留事件空间、纤维和可复合关系。

在 `CoLean v0` 中，我们把一个 toy 形式化任务拆成三层对应：

- `paper lemma -> formal statement`
- `formal statement -> mathlib declaration`
- `mathlib declaration -> tactic`

每一层都不是单一答案，而是一组带权事件：

```text
X <- E -> Y
```

系统通过中间端点做 fiber join，再做局部复合与 push/reduce，得到从论文 lemma 到 tactic 的候选路径。

这正对应讲义里的核心流水线：

```text
fiber join -> local compose -> push/reduce -> graph update
```

## 关键结果

在结构化关系 benchmark 中：

```text
left_events = 800
right_events = 360
fiber_join_pairs = 2400
dense_triple_loop_cells = 19,200,000
estimated_avoidance_ratio = 8000x
```

也就是说，如果按朴素矩阵化/三重展开的方式，需要检查约 1920 万个潜在组合；而对应计算只枚举 2400 个真实可复合事件。

这个结果说明：

```text
加速不是来自单步乘法更快，
而是来自避免展开大量不存在或无意义的候选组合。
```

这正是 CoPU/C-IR 的理论价值。

## 对 CoLean 的意义

在 Lean 自动形式化场景中，类似的展开浪费来自：

- 一个 informal lemma 对应很多 formal statement 候选；
- 一个 Lean goal 对应很多 Mathlib declaration 候选；
- 一个 proof state 对应很多 tactic 候选；
- 普通 agent 容易把这些中间结构压进一次 prompt；
- CoLean 则保留候选纤维，并用 Lean checker 的成功/失败反馈更新边权。

因此，CoLean 的核心不是“让 LLM 一次猜对”，而是：

```text
每次失败都留下结构化事件；
每次成功都强化可复用对应路径。
```

## 这个实验还没有说明什么

这个 v0 还没有证明：

- 它已经能自动完成真实 Lean 证明；
- 它已经优于成熟 Lean agent；
- 它已经能形式化 Kakeya 证明片段；
- 它已经能在硬件上达到 8000x 实测加速。

现在的 8000x 是结构化枚举成本对比，不是端到端硬件加速结论。

更准确的表述应该是：

> v0 证明了对应计算可以在结构化任务中大幅减少候选组合空间；这是 CoLean 和 CoPU 继续做下去的核心实验依据。

## 下一步实验

真实 Lean kernel 已经接入了一个纯 Lean toy verifier。当前结果是：

```text
Lean version = 4.30.0
candidates_checked = 6
accepted = 3
rejected = 3
```

这意味着 v0 已经不只是模拟 verifier，而是可以把 tactic candidate 交给 Lean 进程，并根据 kernel 接受/拒绝更新边权。

进一步地，Mathlib-backed verifier 也已经接入。当前结果是：

```text
Mathlib project = work/colean_mathlib
lake build = pass
candidates_checked = 4
accepted = 2
rejected = 2
```

其中第一个 Mathlib theorem 是有限集合上的求和 filter split：

```text
(∑ x ∈ s.filter p, f x) + (∑ x ∈ s.filter (fun x => ¬ p x), f x)
=
∑ x ∈ s, f x
```

这个 theorem 用到了真实 Mathlib lemma：

```text
Finset.sum_filter_add_sum_filter_not
```

现在还完成了一个两步 proof-chain：

```text
split_positive_mass_bucket
```

其证明脚本是：

```lean
rw [Finset.sum_filter_add_sum_filter_not] at h
exact (Finset.sum_pos_iff).mp h
```

这个 proof-chain verifier 检查了 4 个候选脚本：

```text
scripts_checked = 4
accepted = 1
rejected = 3
```

Lean 接受了正确的两步脚本，并拒绝了“缺少 rewrite”“顺序错误”“rfl 猜测”等错误脚本。这说明系统已经不只是在检查单个 tactic，而是在验证 tactic 顺序对 proof state 的影响。

随后又扩展了一个更接近 dyadic pigeonhole 的二分层 theorem：

```text
binary_level_positive_bucket
```

其证明结构是：

```lean
have hside :
    0 < (∑ x ∈ s.filter p, f x) ∨
    0 < (∑ x ∈ s.filter (fun x => ¬ p x), f x) := by
  omega
rcases hside with hp | hnp
· left
  exact (Finset.sum_pos_iff).mp hp
· right
  exact (Finset.sum_pos_iff).mp hnp
```

更新后的 proof-chain verifier 结果是：

```text
scripts_checked = 7
accepted = 2
rejected = 5
```

这说明系统已经可以区分：

```text
正确的 proof-state 分支脚本
错误地假设左侧为正的脚本
只得到“某侧为正”但忘记转成 witness 的脚本
顺序错误或定义相等猜测脚本
```

随后继续扩展为有限层级版本：

```text
finite_level_positive_bucket
```

其数学含义是：

```text
若 s 上总质量为正，并且每个 x ∈ s 都被 level 映到某个有限 levels 中，
则存在一个 level bucket，其总质量为正。
```

对应证明结构是：

```lean
rcases (Finset.sum_pos_iff).mp h with ⟨x, hxs, hfx⟩
refine ⟨level x, hcover x hxs, ?_⟩
exact (Finset.sum_pos_iff).mpr ⟨x, by simp [hxs], hfx⟩
```

更新后的 proof-chain verifier 结果是：

```text
scripts_checked = 10
accepted = 3
rejected = 7
```

新增的错误反馈包括：

```text
把单点质量 0 < f x 误当成 bucket 总质量为正
把 x ∈ s 误当成 level x ∈ levels
```

这已经很接近真实形式化中的 proof repair：错误不是笼统的“证明失败”，而是落在具体的类型/目标不匹配上，可以回写到对应图的边权。

最新一步加入了阈值版 pigeonhole：

```text
finite_level_threshold_bucket
```

数学含义：

```text
若 levels.card • threshold ≤ ∑ x ∈ s, f x，
且每个 x ∈ s 都映到 levels 中，
则存在某个 level bucket，其质量至少为 threshold。
```

Lean proof 使用了 Mathlib 的加权 pigeonhole theorem：

```lean
exact Finset.exists_le_sum_fiber_of_maps_to_of_nsmul_le_sum hcover hnonempty hbig
```

更新后的 proof-chain verifier 结果是：

```text
scripts_checked = 13
accepted = 4
rejected = 9
```

新增错误类型包括：

```text
忘记传入阈值不等式 hbig
试图用“正质量点”证明“bucket ≥ threshold”这种更强结论
```

这一步已经从“存在正 bucket”推进到“存在达到阈值的 bucket”，对应 dyadic pigeonhole/平均值论证中真正有用的形式。

随后加入了 incremental proof-chain verifier。它不只检查整段脚本是否通过，还会逐步检查 prefix：

```text
step 1
step 1 + step 2
step 1 + step 2 + step 3
...
```

当前结果：

```text
scripts_checked = 6
accepted = 3
rejected = 3
```

并且能够定位第一处失败：

```text
missing rewrite -> first_failure_step = 1
forgets bucket sum proof -> first_failure_step = 2
missing threshold inequality -> first_failure_step = 1
```

这使得 verifier feedback 更接近真实 proof repair：系统不只知道“整段脚本失败”，还能知道哪条对应边/哪个 tactic step 应该降权。

最新一步加入 feedback learner，把 verifier 结果回写为对应边权更新：

```text
accepted proof step -> +0.12
first failing proof step -> -0.10
valid prefix before later failure -> +0.03
```

一轮学习后的排序变化：

```text
rewrite hypothesis -> positive mass declaration: 0.91 -> 1.06
direct weighted pigeonhole declaration:        0.90 -> 1.05
positive point -> level witness -> bucket sum: 0.86 -> 1.01
missing rewrite:                              0.46 -> 0.38
forgets bucket sum proof:                     0.33 -> 0.28
missing threshold inequality:                 0.32 -> 0.24
```

这一步完成了真正的闭环：

```text
candidate proof-chain
-> Lean/Mathlib verifier
-> first failure localization
-> edge-level weight update
-> reranking
```

下一步应该做三个递进实验：

1. 扩展 Mathlib proof chain

   在已经可用的 Lean/lake/toolchain 和 Mathlib 项目上，生成一个 `KakeyaToy.lean` 或 `DyadicPigeonholeToy.lean`，要求：

   ```text
   lake build
   sorry = 0
   ```

2. 加入 proof-state 反馈

   每次 tactic 成功或失败后，记录：

   ```text
   old proof state
   tactic candidate
   checker result
   new proof state
   weight update
   ```

3. 建立人工 baseline

   让同一组 lemma 分别由人工和 CoLean 辅助完成，记录：

   ```text
   time to first proof
   proof repair iterations
   Mathlib lookup count
   final edit distance
   compile pass rate
   ```

## 论文中可以怎么写

可以把这个实验作为毕业论文中的第一个验证实验：

> We first validate the computational advantage of preserving correspondences before materialization. In a structured relation-composition benchmark, the correspondence interpreter enumerates only 2,400 fiber-compatible event pairs, while the naive materialized triple space contains 19,200,000 candidate cells, yielding an 8000x reduction in candidate enumeration.

中文表述：

> 我们首先验证“不提前矩阵化”的计算优势。在一个结构化关系复合任务中，对应解释器仅枚举 2400 个纤维兼容事件对，而朴素展开需要检查 1920 万个候选单元，候选枚举空间减少约 8000 倍。
