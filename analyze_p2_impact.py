import pandas as pd
import numpy as np

# Load Data
df = pd.read_csv('travel_data_p2_routing.csv')

print("=== P2 阶段：动态路由与算法反哺效果分析 ===\n")

# 1. 整体指标概览
total_plans = len(df)
overall_conversion = df['is_converted'].mean()
total_profit = df[df['is_converted']]['net_profit'].sum()
avg_profit_per_plan = total_profit / total_plans

print(f"总方案数: {total_plans}")
print(f"整体转化率: {overall_conversion:.2%}")
print(f"总实现利润: ${total_profit:,.2f}")
print(f"单方案期望利润 (Earning Per Plan): ${avg_profit_per_plan:.2f}")

# 2. 细分用户群体的路由效果
print("\n--- 用户群体 x Agent 版本表现 ---")
segment_stats = df.groupby(['user_segment', 'agent_version']).agg(
    count=('plan_id', 'count'),
    conversion_rate=('is_converted', 'mean'),
    avg_profit_margin=('profit_margin', 'mean'),
    avg_aesthetic=('aesthetic_score', 'mean'),
    total_realized_profit=('net_profit', lambda x: x[df.loc[x.index, 'is_converted']].sum())
).reset_index()

# 计算各组的利润贡献占比
segment_stats['profit_contribution'] = segment_stats['total_realized_profit'] / total_profit
segment_stats['avg_profit_margin'] = (segment_stats['avg_profit_margin'] * 100).round(2)
segment_stats['conversion_rate'] = (segment_stats['conversion_rate'] * 100).round(2)
segment_stats['profit_contribution'] = (segment_stats['profit_contribution'] * 100).round(2)

print(segment_stats.to_string())

# 3. v3 版本改进验证 (对比 P1 的历史数据特征)
# P1 v3: 转化率 ~23%, 审美 ~5.7, 利润率 ~36%
v3_stats = df[df['agent_version'] == 'v3-profit-seeker-p2-patched']
print("\n--- v3 (P2 Patched) 核心指标验证 ---")
print(f"v3 P2 转化率: {v3_stats['is_converted'].mean():.2%} (目标: > 25%)")
print(f"v3 P2 平均审美: {v3_stats['aesthetic_score'].mean():.2f} (目标: > 6.0)")
print(f"v3 P2 平均利润率: {v3_stats['profit_margin'].mean():.2%} (目标: 保持在 25% 以上)")

# 4. 结论生成
print("\n=== 决策验证结论 ===")
if v3_stats['is_converted'].mean() > 0.25 and v3_stats['aesthetic_score'].mean() > 6.0:
    print("✅ 算法反哺成功：v3 在保持高利润的同时，通过提升审美底线显著改善了转化率。")
else:
    print("⚠️ 警告：v3 改进效果未达预期，需进一步调整惩罚权重。")

high_worth_v2 = df[(df['user_segment'] == 'high_net_worth') & (df['agent_version'] == 'v2-aesthetic-first')]
if high_worth_v2['is_converted'].mean() > 0.4:
    print("✅ 动态路由成功：高净值用户在 v2 版本下表现出极高的转化意愿。")
else:
    print("⚠️ 警告：高净值用户对 v2 的响应不如预期，请检查价格弹性。")
