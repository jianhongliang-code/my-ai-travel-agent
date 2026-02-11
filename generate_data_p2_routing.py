import pandas as pd
import numpy as np
from faker import Faker
import uuid
import random

# 初始化
fake = Faker()
n_samples = 1500 # 增加样本量以观察分流效果

def generate_p2_data(n):
    data = []
    
    # 定义用户画像
    user_segments = ['high_net_worth', 'price_sensitive', 'standard']
    
    # 定义 Agent 版本
    agent_versions = ['v1-balanced', 'v2-aesthetic-first', 'v3-profit-seeker', 'v3-profit-seeker-p2-patched']
    
    for i in range(n):
        plan_id = str(uuid.uuid4())[:8]
        
        # 1. 随机生成用户类型
        user_segment = np.random.choice(user_segments, p=[0.2, 0.5, 0.3])
        
        # 2. 动态路由逻辑 (Dynamic Routing)
        # 根据用户类型分配最合适的 Agent
        if user_segment == 'high_net_worth':
            # 高净值用户：优先 v2 (80%), 少量 v1 (15%), 极少 v3 (5%) 用于 A/B 测试
            version = np.random.choice(
                ['v2-aesthetic-first', 'v1-balanced', 'v3-profit-seeker-p2-patched'], 
                p=[0.8, 0.15, 0.05]
            )
        elif user_segment == 'price_sensitive':
            # 价格敏感用户：优先 v3 (70%), v1 (20%), v2 (10%)
            version = np.random.choice(
                ['v3-profit-seeker-p2-patched', 'v1-balanced', 'v2-aesthetic-first'], 
                p=[0.7, 0.2, 0.1]
            )
        else:
            # 普通用户：均衡分配
            version = np.random.choice(
                ['v1-balanced', 'v2-aesthetic-first', 'v3-profit-seeker-p2-patched'],
                p=[0.5, 0.25, 0.25]
            )
            
        # 3. 核心博弈逻辑模拟 (含 P2 算法反哺)
        if version == 'v2-aesthetic-first':
            aesthetic_score = np.random.normal(8.8, 0.6) # 进一步优化审美
            base_margin = 0.12
        elif version == 'v3-profit-seeker-p2-patched':
            # P2 反哺：v3 被约束，不能无底线牺牲审美
            # 原 v3: aesthetic_score = np.random.normal(5.5, 1.2)
            aesthetic_score = np.random.normal(6.5, 1.0) # 均值提升，方差减小
            base_margin = 0.25 # 基础利润率略微下调 (从 0.28) 以换取转化
        else:
            # v1 balanced
            aesthetic_score = np.random.normal(7.5, 0.9)
            base_margin = 0.20

        # 约束评分
        aesthetic_score = max(min(aesthetic_score, 10.0), 2.0)
        
        # 利润率计算
        noise = np.random.normal(0, 0.03)
        profit_margin = base_margin - (aesthetic_score - 7.0) * 0.025 + noise
        
        # --- P2 算法反哺核心逻辑 ---
        # 惩罚项：如果审美过低，预测转化率极低，强制压低利润率以试图挽回（或直接被过滤）
        if version == 'v3-profit-seeker-p2-patched' and aesthetic_score < 6.0:
            profit_margin *= 0.8 # 惩罚因子：利润打八折
            
        profit_margin = max(min(profit_margin, 0.45), 0.05)
        
        # 逻辑分
        logic_score = np.random.beta(a=5, b=1) * 10
        
        # 商业数据
        total_revenue = random.randint(3000, 20000)
        # 高净值用户通常客单价更高
        if user_segment == 'high_net_worth':
            total_revenue *= 1.5
            
        net_profit = total_revenue * profit_margin
        
        # 4. 转化率逻辑 (更精细化)
        # 基础转化概率
        prob = (aesthetic_score / 10.0) * 0.4
        
        # 用户画像对转化率的影响
        if user_segment == 'high_net_worth':
            # 极度挑剔：审美低于 8.0 转化率大幅下降
            if aesthetic_score < 8.0:
                prob *= 0.3
            else:
                prob *= 1.2 # 满意则更容易转化
        elif user_segment == 'price_sensitive':
            # 价格敏感：对高利润率极其敏感（嫌贵）
            if profit_margin > 0.25:
                prob *= 0.5
            else:
                prob *= 1.1 # 便宜则更容易转化
                
        # Agent 版本加成
        if version == 'v2-aesthetic-first':
            prob += 0.1
            
        prob = max(min(prob, 0.95), 0.01)
        is_converted = random.random() < prob
        
        data.append({
            "plan_id": plan_id,
            "user_segment": user_segment,
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
df_p2 = generate_p2_data(n_samples)
file_name = "travel_data_p2_routing.csv"
df_p2.to_csv(file_name, index=False)

print(f"成功生成 P2 阶段数据 {n_samples} 条，已保存至 {file_name}")
print(df_p2.groupby(['user_segment', 'agent_version']).size())
