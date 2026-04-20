import discord
from discord.ext import commands
import re
import os
from datetime import datetime

# ==========================================
# 控制面板 (Control Panel) - 请勿删除以下注释！
# ==========================================
# BOT_TOKEN: 机器人的 Token (部署在 Railway 时建议在 Variables 中配置)
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "把你的机器人_TOKEN_写在这里")

# CHANNEL_MAPPING: 频道一对一转发映射。格式为 {源频道ID: 目标频道ID}
CHANNEL_MAPPING = {
    1453957309444133007: 1495703923531583599,  # 第一组：源频道A : 目标频道A
    1478987667906760853: 1495712410898661448   # 第二组：源频道B : 目标频道B
}

# ROLE_IDS: 需要 @ 的身份组 ID 列表，用逗号分隔
ROLE_IDS = [444444444444444444, 555555555555555555]
# ==========================================

# 必须开启 message_content 意图才能读取消息内容
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def format_message(original_text):
    """提取原始消息内容并转换为极简格式"""
    # 1. 拆分“仓位变动”和“持仓明细”两大部分
    parts = re.split(r'【当前持仓明细】', original_text)
    changes_text = parts[0]
    holdings_text = parts[1] if len(parts) > 1 else ""

    # 2. 解析仓位变动
    changes = []
    # 以 "数字. " 为界限切分每一支股票的变动块
    change_blocks = re.split(r'\n(?=\d+\.\s)', changes_text.strip())
    for block in change_blocks:
        ticker_match = re.search(r'\((.*?)\)', block)
        action_match = re.search(r'变化类型[：:]\s*(\S+)', block)
        pos_match = re.search(r'占比变化[：:].*?(?:->|→)\s*([\d\.]+)%', block)
        price_match = re.search(r'参考成交价[：:]\s*([\d\.]+|无)', block)

        if ticker_match and action_match and pos_match and price_match:
            ticker = ticker_match.group(1)
            action = action_match.group(1).replace("清仓卖出", "清仓")
            pos = pos_match.group(1) + "%"
            price_str = price_match.group(1)
            price = f"{float(price_str):.2f}" if price_str != "无" else "无"
            changes.append(f"{action} `{ticker}` | 最新仓位: {pos} | 成交价: {price}")

    # 3. 解析当前持仓明细
    holdings = []
    if holdings_text:
        hold_blocks = re.split(r'\n(?=\d+\.\s)', holdings_text.strip())
        for i, block in enumerate(hold_blocks, 1):
            ticker_match = re.search(r'\((.*?)\)', block)
            pos_match = re.search(r'持仓占比[：:]\s*([\d\.]+)%', block)
            cost_match = re.search(r'成本[：:]\s*([\d\.]+)', block)
            pnl_match = re.search(r'盈亏比例[：:]\s*([+-]?[\d\.]+)%', block)

            if ticker_match and pos_match and cost_match and pnl_match:
                ticker = ticker_match.group(1)
                pos = pos_match.group(1) + "%"
                cost = f"{float(cost_match.group(1)):.2f}"
                pnl_raw = float(pnl_match.group(1))
                pnl = f"+{pnl_raw:.2f}%" if pnl_raw > 0 else f"{pnl_raw:.2f}%"
                holdings.append(f"{i}. `{ticker}` | 占比: {pos} | 成本: {cost} | 盈亏: {pnl}")

    # 4. 拼接身份组提醒与最终文本
    roles_str = " ".join([f"<@&{role_id}>" for role_id in ROLE_IDS])
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    final_msg = f"{roles_str}\n"
    final_msg += f"[18倍佬]仓位变动提醒 ({now_str})\n\n"

    final_msg += "【仓位变动】\n"
    final_msg += "\n".join(changes) if changes else "无记录"
    
    final_msg += "\n\n【当前持仓明细】\n"
    final_msg += "\n".join(holdings) if holdings else "无记录"

    return final_msg

@bot.event
async def on_ready():
    print(f"✅ 登录成功，当前正在运行的机器人: {bot.user}")
    print(f"📡 正在监视的频道映射: {CHANNEL_MAPPING}")

@bot.event
async def on_message(message):
    # 忽略机器人自己发出的消息
    if message.author == bot.user:
        return

    # 检查消息是否来自受监视的频道字典中
    if message.channel.id in CHANNEL_MAPPING:
        # 简单过滤：只处理包含关键标识符的消息，避免误伤普通聊天
        if "变化类型" in message.content and "当前持仓明细" in message.content:
            try:
                # 转换格式
                formatted_msg = format_message(message.content)
                # 获取对应的目标频道并发送
                target_channel_id = CHANNEL_MAPPING[message.channel.id]
                target_channel = bot.get_channel(target_channel_id)
                if target_channel:
                    await target_channel.send(formatted_msg)
                    print(f"✅ 成功解析并从 {message.channel.id} 转发到了 {target_channel_id}！")
                else:
                    print(f"❌ 错误：找不到目标频道 {target_channel_id}，请检查 CHANNEL_MAPPING 配置。")
            except Exception as e:
                print(f"❌ 解析消息时出错: {e}")

    # 确保命令正常运行
    await bot.process_commands(message)

# 启动机器人
bot.run(BOT_TOKEN)
