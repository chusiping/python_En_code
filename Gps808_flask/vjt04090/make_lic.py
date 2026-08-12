import base64
import hashlib

# 🌟 你的专属私密密钥（绝对不能泄露，要和核心代码里的一致）
SECRET_KEY = "K9#mX!2pQ$zL7vW@eR9t" 

def generate_license(expire_date_str):
    """
    输入格式: "2026-12-31"
    """
    # 1. 拼接原始数据
    raw_data = f"{expire_date_str}|{SECRET_KEY}"
    
    # 2. 生成哈希签名，防止客户手动修改日期
    sign = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
    
    # 3. 组合并用 Base64 加密成乱码，让肉眼看不懂
    final_content = f"{expire_date_str}|{sign}"
    encoded_content = base64.b64encode(final_content.encode('utf-8')).decode('utf-8')
    
    # 4. 写入文件
    with open("license.lic", "w", encoding="utf-8") as f:
        f.write(encoded_content)
    
    print(f"✅ 成功生成证书！到期时间：{expire_date_str}，文件已保存为 license.lic")

if __name__ == "__main__":
    # 比如你想给客户开通到 2026 年 10 月 1 日
    generate_license("2026-10-01")
