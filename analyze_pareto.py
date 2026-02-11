import pandas as pd
import numpy as np

def identify_pareto(scores):
    """
    Identify Pareto optimal points.
    scores: DataFrame with 'aesthetic_score' and 'profit_margin' columns.
    Returns: Boolean Series indicating if the point is Pareto optimal.
    """
    population_size = scores.shape[0]
    is_pareto = np.ones(population_size, dtype=bool)
    
    # Extract columns as numpy arrays for faster comparison
    aesthetic = scores['aesthetic_score'].values
    profit = scores['profit_margin'].values
    
    for i in range(population_size):
        if is_pareto[i]:
            # Compare point i with all other points
            # If any other point is better or equal in both dimensions AND better in at least one, i is not Pareto optimal
            is_dominated = np.logical_and(
                aesthetic >= aesthetic[i],
                profit >= profit[i]
            ) & np.logical_or(
                aesthetic > aesthetic[i],
                profit > profit[i]
            )
            
            if np.any(is_dominated):
                is_pareto[i] = False
                
    return is_pareto

# Load data
df = pd.read_csv('travel_agent_tradeoff_data.csv')

# 1. Base Data Filter (logic_score >= 8.0)
base_data = df[df['logic_score'] >= 8.0].copy()
print(f"Base data count (logic_score >= 8.0): {len(base_data)}")

# 2. Identify Pareto Frontier
# We focus on aesthetic_score and profit_margin for the frontier
base_data['is_frontier'] = identify_pareto(base_data[['aesthetic_score', 'profit_margin']])
pareto_frontier = base_data[base_data['is_frontier']]

# 3. Aggregate Results (Simulating the SQL Group By)
stats = pareto_frontier.groupby('agent_version').agg(
    pareto_optimal_count=('plan_id', 'count'),
    avg_aesthetic_on_frontier=('aesthetic_score', 'mean'),
    avg_profit_margin_on_frontier=('profit_margin', 'mean'),
    conversion_rate=('is_converted', 'mean')
).reset_index()

# Calculate win rate percentage
total_frontier_points = stats['pareto_optimal_count'].sum()
stats['win_rate_percentage'] = (stats['pareto_optimal_count'] / total_frontier_points * 100).round(2)

# Format profit margin and conversion rate as percentage for display
stats['avg_profit_margin_pct'] = (stats['avg_profit_margin_on_frontier'] * 100).round(2)
stats['conversion_rate_pct'] = (stats['conversion_rate'] * 100).round(2)
stats['avg_aesthetic_on_frontier'] = stats['avg_aesthetic_on_frontier'].round(2)

# Sort by count desc
stats = stats.sort_values('pareto_optimal_count', ascending=False)

# Display Results
print("\n=== Agent 胜率榜单 (Pareto Frontier Analysis) ===")
print(stats[['agent_version', 'pareto_optimal_count', 'win_rate_percentage', 'avg_aesthetic_on_frontier', 'avg_profit_margin_pct', 'conversion_rate_pct']].to_string(index=False))

# Interpretation Helper
top_agent = stats.iloc[0]['agent_version']
print("\n=== 预判结论 ===")
if top_agent == 'v2-aesthetic-first':
    print("🏆 冠军: v2-aesthetic-first")
    print("结论: 高端定制市场潜力巨大。美感壁垒强。")
    print("决策: 建议加大针对“高净值人群”的营销投入。")
elif top_agent == 'v1-balanced':
    print("🏆 冠军: v1-balanced")
    print("结论: 系统收敛稳定，既美又赚钱。")
    print("决策: 可作为标准作业程序(SOP)集成到 SaaS 系统。")
elif top_agent == 'v3-profit-seeker':
    print("🏆 冠军: v3-profit-seeker")
    print("结论: 利润极高，但需警惕转化率风险。")
    print("决策: 检查转化率。如果低，说明 AI 自嗨，需牺牲利润换留存。")
