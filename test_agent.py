import googlemaps
import json

# 1. 基础配置
# 注意：暂时用一个假的 KEY 测试代码逻辑，跑通后再换成你那个 AIza 开头的真 KEY
MY_KEY = "AIzaSyBMN6Iws_zPBw9fthTapR4sLIpdkngI3xw" 
gmaps = googlemaps.Client(key=MY_KEY)

def simple_audit(origin, destination):
    print(f"正在审计路线: {origin} -> {destination}")
    try:
        # 尝试获取一次真实路况（这会消耗极少量 Google 额度）
        matrix = gmaps.distance_matrix(origin, destination, mode="driving")
        return matrix
    except Exception as e:
        return f"错误: {e}"

# 2. 执行测试
if __name__ == "__main__":
    print("--- 旅游 Agent 逻辑启动 ---")
    print("API Key 已加载，格式有效")
    print(f"Client 已初始化: {type(gmaps)}")
    
    # 测试 API 调用
    try:
        result = simple_audit("天安门", "北京首都机场")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"调用失败: {e}")