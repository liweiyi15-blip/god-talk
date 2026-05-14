import discord
from discord import app_commands
from discord.ext import commands
import os

# 1. 定义机器人本体并加载命令
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        await self.add_cog(TradeShare(self))
        await self.tree.sync()
        print("✅ 机器人已启动，斜杠命令已同步！")

# 2. 你的分享命令功能
class TradeShare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="share", description="发布交易代码分享")
    @app_commands.describe(
        code="交易代码", direction="交易方向", position="仓位大小", period="交易周期"
    )
    @app_commands.choices(
        direction=[
            app_commands.Choice(name="看多", value="看多"),
            app_commands.Choice(name="看空", value="看空"),
            app_commands.Choice(name="持有", value="持有"),
        ],
        position=[
            app_commands.Choice(name="重仓", value="重仓"),
            app_commands.Choice(name="轻仓", value="轻仓"),
            app_commands.Choice(name="微仓", value="微仓"),
        ],
        period=[
            app_commands.Choice(name="长线", value="长线"),
            app_commands.Choice(name="短线", value="短线"),
        ]
    )
    async def share(
        self, interaction: discord.Interaction, code: str, 
        direction: app_commands.Choice[str], position: app_commands.Choice[str], 
        period: app_commands.Choice[str]
    ):
        target_channel_id = 1436730809749864652
        channel = self.bot.get_channel(target_channel_id)

        if not channel:
            await interaction.response.send_message("❌ 找不到目标频道，请检查机器人在目标频道的权限。", ephemeral=True)
            return

        # 将所有信息整合进 description 强制一行显示
        content = f"**代码:** `{code}` ｜ **方向:** `{direction.value}` ｜ **仓位:** `{position.value}` ｜ **周期:** `{period.value}`"

        # 设置 Embed 颜色为 #8F4313 (十六进制 0x8F4313)
        embed = discord.Embed(
            title="仙人说了：", 
            description=content,
            color=discord.Color(0x8F4313)
        )
        
        # 修改脚注内容
        embed.set_footer(text="（此消息为主观分享，不构成投资建议，盈亏自负）")

        await channel.send(embed=embed)
        await interaction.response.send_message("✅ 分享已成功发布至指定频道！", ephemeral=True)

# 3. 读取 Token 并启动机器人
bot = MyBot()
bot.run(os.environ.get("DISCORD_TOKEN"))
