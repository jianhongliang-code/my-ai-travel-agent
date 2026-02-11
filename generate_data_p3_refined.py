import pandas as pd
import numpy as np
from faker import Faker
import uuid
import random

# 初始化
fake = Faker()
n_samples = 1500

def generate_p3_data(n):
    data = []
    
    # 定义用户画像
    user_segments = ['high_net_worth', 'price_sensitive', 'standard']
    
    # 定义 Agent 版本
    # v3-profit-seeker-p3-tiered: 采用阶梯式惩罚的新版 v3
    agent_versions = ['v1-balanced', 'v2-aesthetic-first', 'v3-profit-seeker-p3-tiered']
    
    for i in range(n):
        plan_id = str(uuid.uuid4())[:8]
        
        # 1. 随机生成用户类型
        user_segment = np.random.choice(user_segments, p=[0.2, 0.5, 0.3])
        
        # 2. 动态路由逻辑 (P3 Refined)
        if user_segment == 'high_net_worth':
            # 高净值：维持 P2 策略 (v2 主导)
            version = np.random.choice(
                ['v2-aesthetic-first', 'v1-balanced', 'v3-profit-seeker-p3-tiered'], 
                p=[0.8, 0.15, 0.05]
            )
        elif user_segment == 'price_sensitive':
            # 价格敏感：维持 P2 策略 (v3 主导)
            version = np.random.choice(
                ['v3-profit-seeker-p3-tiered', 'v1-balanced', 'v2-aesthetic-first'], 
                p=[0.7, 0.2, 0.1]
            )
        else:
            # 普通用户 (Standard) - P3 调整：扩大 v2 适用范围
            # 原 P2: v1(0.5), v2(0.25), v3(0.25)
            # 新 P3: v2(0.45) - 显著增加, v1(0.35), v3(0.20)
            version = np.random.choice(
                ['v2-aesthetic-first', 'v1-balanced', 'v3-profit-seeker-p3-tiered'],
                p=[0.45, 0.35, 0.20]
            )
            
        # 3. 核心博弈逻辑模拟
        if version == 'v2-aesthetic-first':
            aesthetic_score = np.random.normal(8.8, 0.6)
            base_margin = 0.12
        elif version == 'v3-profit-seeker-p3-tiered':
            # P3 阶梯惩罚下的 Agent 行为模拟
            # 相比 P2 (mean=6.5), 假设 Agent 学会了避免重罚，进一步微调了审美均值
            aesthetic_score = np.random.normal(6.8, 0.9) 
            base_margin = 0.26 # 基础利润率尝试回调
        else:
            # v1 balanced
            aesthetic_score = np.random.normal(7.5, 0.9)
            base_margin = 0.20

        # 约束评分
        aesthetic_score = max(min(aesthetic_score, 10.0), 2.0)
        
        # 初始利润率计算
        noise = np.random.normal(0, 0.03)
        profit_margin = base_margin - (aesthetic_score - 7.0) * 0.025 + noise
        
        # --- P3 阶梯式惩罚逻辑 ---
        # 规则：审美每降低 1 分 (低于 7.0)，利润率惩罚 2% (0.02)
        # 模拟“系统强制压价”或“算法降权”带来的利润损失
        if version == 'v3-profit-seeker-p3-tiered':
            penalty_threshold = 7.0
            if aesthetic_score < penalty_threshold:
                # 计算差值
                gap = penalty_threshold - aesthetic_score
                # 阶梯惩罚: gap * 0.02
                penalty = gap * 0.02
                profit_margin -= penalty
            
        profit_margin = max(min(profit_margin, 0.45), 0.05)
        
        # 逻辑分
        logic_score = np.random.beta(a=5, b=1) * 10
        
        # 商业数据
        total_revenue = random.randint(3000, 20000)
        if user_segment == 'high_net_worth':
            total_revenue *= 1.5
            
        net_profit = total_revenue * profit_margin
        
        # 4. 转化率逻辑
        prob = (aesthetic_score / 10.0) * 0.4
        
        if user_segment == 'high_net_worth':
            if aesthetic_score < 8.0:
                prob *= 0.3
            else:
                prob *= 1.2
        elif user_segment == 'price_sensitive':
            if profit_margin > 0.25:
                prob *= 0.5
            else:
                prob *= 1.1
                
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
df_p3 = generate_p3_data(n_samples)
file_name = "travel_data_p3_refined.csv"
df_p3.to_csv(file_name, index=False)

print(f"成功生成 P3 阶段数据 {n_samples} 条，已保存至 {file_name}")
print(df_p3.groupby(['user_segment', 'agent_version']).size())
