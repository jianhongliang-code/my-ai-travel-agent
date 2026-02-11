import pandas as pd
import numpy as np
from faker import Faker
import uuid
import random

# 初始化
fake = Faker()
n_samples = 1000

def generate_travel_data(n):
    data = []
    
    # 定义几种 Agent 版本，模拟不同的权重配置
    agent_versions = ['v1-balanced', 'v2-aesthetic-first', 'v3-profit-seeker']
    
    for i in range(n):
        plan_id = str(uuid.uuid4())[:8]
        version = random.choice(agent_versions)
        
        # --- 核心博弈逻辑模拟 ---
        # 我们假设审美分 (0-10) 和 利润率 (0-0.4) 呈负相关
        # 基础分：版本不同，重心不同
        if version == 'v2-aesthetic-first':
            aesthetic_score = np.random.normal(8.5, 0.8)
            base_margin = 0.12  # 审美优先，基础利润率低
        elif version == 'v3-profit-seeker':
            aesthetic_score = np.random.normal(5.5, 1.2)
            base_margin = 0.28  # 利润优先，审美牺牲大
        else:
            aesthetic_score = np.random.normal(7.2, 1.0)
            base_margin = 0.20
            
        # 强制约束评分范围 0-10
        aesthetic_score = max(min(aesthetic_score, 10.0), 1.0)
        
        # 核心惩罚逻辑：审美越高，利润率越容易被挤压 (负相关噪声)
        # 逻辑：profit_margin = base_margin - (aesthetic_score - 5) * 0.02 + 随机噪声
        noise = np.random.normal(0, 0.03)
        profit_margin = base_margin - (aesthetic_score - 7.0) * 0.03 + noise
        profit_margin = max(min(profit_margin, 0.45), 0.05) # 约束在 5% - 45%
        
        # 逻辑分通常保持高位，否则方案不可用
        logic_score = np.random.beta(a=5, b=1) * 10 
        
        # 商业数据计算
        total_revenue = random.randint(3000, 20000)
        net_profit = total_revenue * profit_margin
        
        # 转化率逻辑：审美越高，转化率通常越高；但价格过高转化会降
        # 这里简化：审美 > 8.5 时，转化概率增加
        conversion_prob = (aesthetic_score / 10.0) * 0.4 + (0.1 if version == 'v2-aesthetic-first' else 0)
        is_converted = random.random() < conversion_prob
        
        data.append({
            "plan_id": plan_id,
            "agent_version": version,
            "total_revenue": round(total_revenue, 2),
            "net_profit": round(net_profit, 2),
            "profit_margin": round(profit_margin, 4),
            "aesthetic_score": round(aesthetic_score, 2),
            "logic_score": round(logic_score, 2),
            "is_converted": is_converted,
            "created_at": fake.date_time_this_year().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    return pd.DataFrame(data)

# 执行生成
df = generate_travel_data(n_samples)

# 保存为 CSV
file_name = "travel_agent_tradeoff_data.csv"
df.to_csv(file_name, index=False)
  
print(f"成功生成 {n_samples} 条模拟数据并保存至{file_name}")
print(df.head())
