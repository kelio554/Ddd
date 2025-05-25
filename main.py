import discord
from discord.ext import commands
import requests
import asyncio

# ตั้งค่าโทเคนบอทและ API key เองนะ
DISCORD_BOT_TOKEN = "MTMzNTY1NDQyMzEyMDMxODQ3Ng.GmOc5Y.py6k9je-o-K5mVmdejPGUlTVSE_0Yl6SSqdjNs"
OPENROUTER_API_KEY = "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"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

messages_dict = {}
active_channels = set()

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")

@tree.command(name="ai", description="เปิดโหมดพูดคุยกับ AI ในห้องนี้")
async def ai_command(interaction: discord.Interaction):
    cid = interaction.channel.id
    active_channels.add(cid)
    messages_dict[cid] = []
    await interaction.response.send_message("โหมด AI เปิดแล้ว! พิมพ์ได้เลย")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    cid = message.channel.id
    content = message.content

    if content.lower() == "clear" and cid in active_channels:
        messages_dict[cid] = []
        await message.channel.send("ล้างประวัติแล้ว!")
        return

    if cid in active_channels:
        await handle_ai(message.channel, content, cid)
    elif bot.user in message.mentions:
        cleaned = content.replace(f"<@{bot.user.id}>", "").strip()
        await handle_ai(message.channel, cleaned, cid)

async def handle_ai(channel, prompt, cid):
    if cid not in messages_dict:
        messages_dict[cid] = []

    messages_dict[cid].append({"role": "user", "content": prompt})

    msg = await channel.send("กำลังประมวลผล...")

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": messages_dict[cid]
            }
        ))

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            messages_dict[cid].append({"role": "assistant", "content": reply})
            await msg.edit(content=reply)
        else:
            await msg.edit(content="เกิดข้อผิดพลาดกับ API.")
    except Exception as e:
        await msg.edit(content=f"ผิดพลาด: {e}")

bot.run(DISCORD_BOT_TOKEN)
