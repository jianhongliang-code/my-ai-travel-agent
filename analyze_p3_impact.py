import pandas as pd
import numpy as np

# Load Data
df = pd.read_csv('travel_data_p3_refined.csv')

print("=== P3 阶段：阶梯惩罚与 v2 扩量效果验证 ===\n")

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

# 格式化
segment_stats['profit_contribution'] = (segment_stats['total_realized_profit'] / total_profit * 100).round(2)
segment_stats['avg_profit_margin'] = (segment_stats['avg_profit_margin'] * 100).round(2)
segment_stats['conversion_rate'] = (segment_stats['conversion_rate'] * 100).round(2)
segment_stats['avg_aesthetic'] = segment_stats['avg_aesthetic'].round(2)

print(segment_stats.to_string())

# 3. 验证 v2 在 Standard 用户中的扩量效果
standard_v2 = df[(df['user_segment'] == 'standard') & (df['agent_version'] == 'v2-aesthetic-first')]
standard_v1 = df[(df['user_segment'] == 'standard') & (df['agent_version'] == 'v1-balanced')]

print("\n--- 重点验证 1: Standard 用户扩量 v2 效果 ---")
print(f"Standard - v2 样本数: {len(standard_v2)} (P2 约 25% -> P3 目标 45%)")
print(f"Standard - v2 转化率: {standard_v2['is_converted'].mean():.2%} (对比 v1: {standard_v1['is_converted'].mean():.2%})")
v2_profit = standard_v2[standard_v2['is_converted']]['net_profit'].sum()
v2_epp = v2_profit / len(standard_v2) if len(standard_v2) > 0 else 0
v1_profit = standard_v1[standard_v1['is_converted']]['net_profit'].sum()
v1_epp = v1_profit / len(standard_v1) if len(standard_v1) > 0 else 0
print(f"Standard - v2 单方案期望利润: ${v2_epp:.2f} vs v1: ${v1_epp:.2f}")

if v2_epp > v1_epp:
    print("✅ 结论：扩量 v2 是正确的，虽然利润率低，但高转化带来了更高的期望收益。")
else:
    print("⚠️ 结论：v2 扩量并未带来更高的期望收益，需权衡品牌价值与短期利润。")

# 4. 验证 v3 阶梯惩罚效果
v3_stats = df[df['agent_version'] == 'v3-profit-seeker-p3-tiered']
print("\n--- 重点验证 2: v3 阶梯惩罚效果 ---")
print(f"v3 P3 转化率: {v3_stats['is_converted'].mean():.2%} (P2: ~23.5%)")
print(f"v3 P3 平均审美: {v3_stats['aesthetic_score'].mean():.2f} (P2: ~6.48)")
print(f"v3 P3 平均利润率: {v3_stats['profit_margin'].mean():.2%} (P2: ~24.4%)")

if v3_stats['is_converted'].mean() > 0.24 and v3_stats['profit_margin'].mean() > 0.24:
    print("✅ 结论：阶梯惩罚奏效！v3 成功实现了“软着陆”，在维持利润的同时提升了转化。")
else:
    print("⚠️ 结论：v3 指标仍需观察。")
