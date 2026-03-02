import discord
from discord import app_commands
from discord.ext import tasks
import asyncio
from datetime import datetime, timedelta


TOKEN = "

# Roles to bypass tracking
BYPASS_ROLE_IDS = [
    "enter_role_to_bypass_bot"  # Automod role
]

# Text channels to send warnings
WARNING_CHANNEL_IDS = [
   1185858984314417163,
]

# Timing in seconds
WARNING_TIME = 10 * 60
FINAL_TIME = 20 * 60
TIMEOUT_DURATION = timedelta(seconds=30)

# AFK channel IDs to ignore
AFK_CHANNEL_IDS = []


intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# TRACKING STATE

tracking_tasks = {}  #


def has_bypass_role(member: discord.Member) -> bool:
    return any(role.id in BYPASS_ROLE_IDS for role in member.roles)

async def apply_timeout(member: discord.Member):
    try:
        await member.timeout(TIMEOUT_DURATION, reason="Inactive in voice channel (mic muted)")
        print(f"[TIMEOUT] {member} has been timed out for {TIMEOUT_DURATION}.")
    except discord.Forbidden:
        print(f"[ERROR] Missing permissions to timeout {member}")
    except Exception as e:
        print(f"[ERROR] Timeout failed: {e}")

async def send_warning(member: discord.Member):
    channels_sent = 0
    for channel_id in WARNING_CHANNEL_IDS:
        channel = member.guild.get_channel(channel_id)
        if channel:
            try:
                await channel.send(
                    f" {member.mention}, you have been muted in voice for {WARNING_TIME} seconds. Please unmute yourself and start talking or else get ready to get TIMEOUT"
                )
                channels_sent += 1
            except Exception as e:
                print(f"[ERROR] Failed to send warning in channel {channel_id}: {e}")
    if channels_sent == 0:
        print(f"[WARNING] No valid text channel found to send warning for {member}.")

async def track_user(member: discord.Member):
    start_time = datetime.utcnow()
    tracking_tasks[member.id]["start_time"] = start_time
    tracking_tasks[member.id]["voice_channel"] = member.voice.channel
    print(f"[TRACKING START] {member} started tracking at {start_time} in {member.voice.channel}")

    try:
        #Warning
        await asyncio.sleep(WARNING_TIME)
        if member.id not in tracking_tasks:
            return
        await send_warning(member)
        tracking_tasks[member.id]["warned"] = True
        print(f"[WARNING] {member} warned after {WARNING_TIME} seconds muted.")

        #  Timeout
        await asyncio.sleep(FINAL_TIME - WARNING_TIME)
        if member.id not in tracking_tasks:
            return
        await apply_timeout(member)
    finally:
        if member.id in tracking_tasks:
            tracking_tasks.pop(member.id, None)
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        print(f"[TRACKING END] {member} tracking ended after {duration:.1f} seconds.")


@client.event
async def on_voice_state_update(member, before, after):
    if member.bot or has_bypass_role(member):
        return
    if after.channel and after.channel.id in AFK_CHANNEL_IDS:
        return

    # User left VC
    if before.channel and not after.channel:
        task_data = tracking_tasks.pop(member.id, None)
        if task_data:
            task_data["task"].cancel()
            duration = (datetime.utcnow() - task_data["start_time"]).total_seconds()
            print(f"[LEFT VC] {member} left VC after {duration:.1f} seconds muted.")
        return

 
    if after.channel and after.self_mute and member.id not in tracking_tasks:
        task = asyncio.create_task(track_user(member))
        tracking_tasks[member.id] = {"task": task, "warned": False, "start_time": None, "voice_channel": None}
        return


    if before.self_mute and not after.self_mute:
        task_data = tracking_tasks.pop(member.id, None)
        if task_data:
            task_data["task"].cancel()
            duration = (datetime.utcnow() - task_data["start_time"]).total_seconds()
            print(f"[UNMUTED] {member} unmuted after {duration:.1f} seconds muted.")
        return


    if not before.self_mute and after.self_mute and member.id not in tracking_tasks:
        task = asyncio.create_task(track_user(member))
        tracking_tasks[member.id] = {"task": task, "warned": False, "start_time": None, "voice_channel": None}
        return


@tasks.loop(seconds=1)
async def print_tracking_table():
    if not tracking_tasks:
        return
    print("\n--- Current VC Tracking ---")
    print(f"{'USER':<20}{'VC CHANNEL':<20}{'MUTED TIME':<12}{'WARNED?':<8}")
    now = datetime.utcnow()
    for user_id, data in tracking_tasks.items():
        member = client.get_user(user_id)
        if not member:
            continue
        vc_name = data.get("voice_channel").name if data.get("voice_channel") else "Unknown"
        muted_time = (now - data["start_time"]).total_seconds() if data["start_time"] else 0
        warned = "Yes" if data.get("warned") else "No"
        print(f"{str(member):<20}{vc_name:<20}{int(muted_time):<12}{warned:<8}")
    print("----------------------------\n")


@client.event
async def on_ready():
    GUILD_ID =   # your server ID
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)  
    print(f"Logged in as {client.user}")
    print_tracking_table.start()


# Set warning time
@tree.command(name="set_warning_time", description="Set warning time in seconds")
@app_commands.checks.has_permissions(administrator=True)
async def set_warning_time(interaction: discord.Interaction, seconds: int):
    global WARNING_TIME
    WARNING_TIME = seconds
    await interaction.response.send_message(f"Warning time set to {seconds}s")

@tree.command(name="set_timeout_time", description="Set total mute time before timeout")
@app_commands.checks.has_permissions(administrator=True)
async def set_timeout_time(interaction: discord.Interaction, seconds: int):
    global FINAL_TIME
    FINAL_TIME = seconds
    await interaction.response.send_message(f"Total mute time before timeout set to {seconds}s")

# Add bypass role
@tree.command(name="add_bypass_role", description="Add a role to bypass tracking")
@app_commands.checks.has_permissions(administrator=True)
async def add_bypass_role(interaction: discord.Interaction, role: discord.Role):
    if role.id not in BYPASS_ROLE_IDS:
        BYPASS_ROLE_IDS.append(role.id)
    await interaction.response.send_message(f"Role {role.name} added to bypass list")

# Remove bypass role
@tree.command(name="remove_bypass_role", description="Remove a bypass role")
@app_commands.checks.has_permissions(administrator=True)
async def remove_bypass_role(interaction: discord.Interaction, role: discord.Role):
    if role.id in BYPASS_ROLE_IDS:
        BYPASS_ROLE_IDS.remove(role.id)
    await interaction.response.send_message(f"Role {role.name} removed from bypass list")

# Mute status check
@tree.command(name="mutestatus", description="Check how long a user has been muted in VC")
@app_commands.checks.has_permissions(administrator=True)
async def mutestatus(interaction: discord.Interaction, member: discord.Member):
    data = tracking_tasks.get(member.id)
    if not data:
        await interaction.response.send_message(f"{member} is not currently tracked (not muted).")
        return
    muted_time = (datetime.utcnow() - data["start_time"]).total_seconds()
    await interaction.response.send_message(f"{member} has been muted for {int(muted_time)} seconds in VC {data['voice_channel']}.")

client.run(TOKEN)
