import discord
from discord.ext import commands
import asyncio
import random
import datetime
import requests

client = commands.Bot(command_prefix="$", intents=discord.Intents.all())
client.remove_command("help")

giveaways = {}
winners_chosen = set()

start_time = datetime.datetime.now()

welcome_goodbye_channel_id = 1170136792150839399

def convert_to_seconds(duration: str) -> int:
    seconds = 0
    parts = duration.split()
    for part in parts:
        if part[-1] == 's':
            seconds += int(part[:-1])
        elif part[-1] == 'm':
            seconds += int(part[:-1]) * 60
        elif part[-1] == 'h':
            seconds += int(part[:-1]) * 3600
        elif part[-1] == 'd':
            seconds += int(part[:-1]) * 86400
    return seconds

@client.command()
@commands.has_permissions(administrator=True)
async def live(ctx):
    embed=discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="", value=f"**>>> I'm live now! Watch it on my twitch!**", inline=False)
    await ctx.send("@everyone", embed=embed)
    await ctx.send("https://www.twitch.tv/xerzez1")

@client.command()
async def version(ctx):
    embed=discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="**Mewo! :3**", value=f"**>>> Version: 1.0!**", inline=False)
    await ctx.send(embed=embed)

@client.command()
async def help(ctx):
    embed = discord.Embed(title="Command List", description="Here are the available commands:", color=0xff9adc)
    
    embed.add_field(name=f">>> Moderation Commands", value="```\n$warn <member> <reason>\n$ban <member> <reason>\n$unban <user id>\n$kick <member> <reason>\n$mute <member> <reason>\n$unmute <member>```", inline=False)
    embed.add_field(name=f">>> Giveaway Commands", value="```\n$startgiveaway <duration> <prize>\n$endgiveaway <message id>```", inline=False)
    embed.add_field(name=f">>> Misc Commands", value="```\n$ping\n$date\n$time\n$version\n$uptime\n$userinfo <member>\n$avatar <member>```", inline=False)
    embed.add_field(name=f">>> Twitch Commands", value="```\n$live```", inline=False)
    await ctx.send(embed=embed)

@client.command(name="ping", description="Shows the bot's response time.")
async def ping(ctx):
    bot_latency = round(client.latency * 1000)

    embed=discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="", value=f">>> **Response**: {bot_latency}ms", inline=False)
    await ctx.send(embed=embed)

@client.command(name="clear", description="Deletes a specified number of messages from the channel.")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Please provide a positive number of messages to delete.")
        return

    await ctx.channel.purge(limit=amount + 1)
    embed=discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="", value=f"**Success!**\n>>> Deleted **{amount}** message(s).", inline=False)
    await ctx.send(content="", embed=embed)

@client.command(name="warn", description="Warns a server member from violating server rules or engaging in inappropriate behavior.")
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**Error!**\n>>> You cannot warn yourself silly.", inline=False)
        await ctx.send(content="", embed=embed)
        return
    
    if member is None:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**>>> Please provide a member to warn.**", inline=False)
        await ctx.send(content="", embed=embed)
        return

    if reason is None:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**>>> Please provide a reason for the warn.**", inline=False)
        await ctx.send(content="", embed=embed)
        return

    try:
        embed_dm = discord.Embed(title=f">>> You have been warned in {ctx.guild.name}", description=f"Reason: {reason}", color=discord.Color.orange())
        embed_dm.set_footer(text=f"Warned by {ctx.author}")
        
        await member.send(embed=embed_dm)
    except discord.Forbidden:
        await ctx.send(f"Failed to send a warning DM to {member.mention}. They may have DMs disabled.")
    except Exception as e:
        await ctx.send(f"An error occurred while sending a warning DM to {member.mention}: {e}")

    try:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value=f"**Success!**\n>>> **{member}** has been warned for: **{reason}**", inline=False)
        
        await ctx.send(content="", embed=embed)
    except discord.Forbidden:
        await ctx.send("Failed to send a confirmation message. Please check the bot's permissions.")
    except Exception as e:
        await ctx.send(f"An error occurred while sending a confirmation message: {e}")

@client.command(name="kick", description="Kicks a user from the server.")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, reason):
    await ctx.guild.kick(member)

    embed=discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="", value=f"**Success!**\n>>> Kicked {member} for: {reason}.", inline=False)
    await ctx.send(content="", embed=embed)

@client.command(name="unban", description="Unbans a previously banned user from the server.")
@commands.has_permissions(ban_members=True)
async def unban(ctx, member_id):
    user = discord.Object(id=member_id)
    await ctx.guild.unban(user)
    embed = discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="", value=f"**Success!**\n>>> {member_id} has been unbanned.", inline=False)
    await ctx.send(embed=embed)

@client.command(name="ban", description="Bans a server member for breaking the server rules.")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**Error!**\n>>> You cannot ban yourself.", inline=False)
        await ctx.send(content="", embed=embed)
        return
    
    if member is None:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**>>> Please provide a member to ban.**", inline=False)
        await ctx.send(content="", embed=embed)
        return

    if reason is None:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**>>> Please provide a reason for the ban.**", inline=False)
        await ctx.send(content="", embed=embed)
        return

    try:
        await member.ban(reason=reason)
        embed=discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value=f"**Success!**\n>>> Banned {member} for: {reason}.", inline=False)
        await ctx.send(content="", embed=embed)
    except discord.Forbidden:
        await ctx.send(f"Failed to ban {member.mention}. They may have higher permissions than the bot.")
    except Exception as e:
        await ctx.send(f"An error occurred while banning {member.mention}: {e}")

@client.command(name="mute", description="Mutes a member for breaking server rules.")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    if member == ctx.author:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**Error!**\n>>> You cannot mute yourself silly.", inline=False)
        await ctx.send(content="", embed=embed)
        return
    
    if not member:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**Error!**\nPlease mention a valid member to mute.", inline=False)
        await ctx.send(content="", embed=embed)
        return

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**Error!**\n>>> There is no 'Muted' role on this server. Please create one.", inline=False)
        await ctx.send(content="", embed=embed)
        return

    if muted_role in member.roles:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value=f"**Error!**\n>>> {member.mention} is already muted.", inline=False)
        await ctx.send(content="", embed=embed)
        return
    
    await member.add_roles(muted_role)
    embed = discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="", value=f"**Success!**\n>>> {member.mention} has been muted.", inline=False)
    await ctx.send(content="", embed=embed)

@client.command(name="unmute", description="Unmutes a server member.")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    if member == ctx.author:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**Error!**\n>>> You unmuted yourself... wait... if you sent the command, then how were you muted?", inline=False)
        await ctx.send(content="", embed=embed)
        return
    if not member:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**Error!**\nPlease mention a valid member to mute.", inline=False)
        await ctx.send(content="", embed=embed)
        return

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value="**Error!**\n>>> There is no 'Muted' role on this server. Please create one.", inline=False)
        await ctx.send(content="", embed=embed)
        return

    if muted_role not in member.roles:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value=f"**Error!**\n>>> {member.mention} is not muted.", inline=False)
        await ctx.send(content="", embed=embed)
        return

    await member.remove_roles(muted_role)
    embed = discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="", value=f"**Success!**\n>>> {member.mention} has been unmuted.", inline=False)
    await ctx.send(content="", embed=embed)

@client.command(name="startgiveaway", description="Starts a giveaway!")
async def startgiveaway(ctx, duration: str, *, prize: str):
    if ctx.author.guild_permissions.administrator:
        duration_seconds = convert_to_seconds(duration)
        if duration_seconds <= 0:
            await ctx.send("Please provide a valid duration for the giveaway.")
            return

        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="🎉 Giveaway 🎉", value=f"React with 🎉 to enter!\nPrize: <:gift:1223640610846806087> {prize}\nDuration: {duration}", inline=False)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")

        giveaways[msg.id] = {"prize": prize, "duration": duration_seconds, "participants": [], "author": ctx.author}

        await asyncio.sleep(duration_seconds)

        msg = await ctx.channel.fetch_message(msg.id)
        reactions = [reaction for reaction in msg.reactions if str(reaction.emoji) == "🎉"]
        users = []
        for reaction in reactions:
            async for user in reaction.users():
                if user != client.user:
                    users.append(user)
        winner = random.choice(users) if users else None

        if winner:
            embed = discord.Embed(title="", color=0xff9adc
)
            embed.add_field(name="🎉 Giveaway Winner 🎉", value=f"Congratulations {winner.mention}! You won! Prize: {prize}!", inline=False)
            await ctx.send(embed=embed)
            winners_chosen.add(msg.id)
        else:
            embed = discord.Embed(title="", color=0xff9adc
)
            embed.add_field(name="🎉 Giveaway 🎉", value="No one participated in the giveaway!", inline=False)
            await ctx.send(embed=embed)

        del giveaways[msg.id]
    else:
        await ctx.send("You don't have the required permissions to use this command.")

@client.command(name="endgiveaway", description="Ends a giveaway, no one wins.")
async def endgiveaway(ctx, msg_id: int):
    if ctx.author.guild_permissions.administrator:
        if msg_id in giveaways:
            try:
                giveaway_msg = await ctx.channel.fetch_message(msg_id)
                await giveaway_msg.delete()
            except discord.NotFound:
                pass

            embed = discord.Embed(title="", color=0xff9adc
)
            embed.add_field(name="Giveaway Ended", value="Giveaway ended and deleted.", inline=False)
            await ctx.send(embed=embed)

            del giveaways[msg_id]
        else:
            embed = discord.Embed(title="", color=0xff9adc
)
            embed.add_field(name="Error", value="Giveaway not found or already ended.", inline=False)
            await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have the required permissions to use this command.")

@client.command(name="userinfo", description="Gets basic info about the specified user.")
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    embed = discord.Embed(title="", color=0xff9adc)
    embed.set_thumbnail(url=member.avatar)
    embed.add_field(name="", value=f">>> **Name**: {member.name}\n**Nickname**: {member.display_name}\n**ID**: {member.id}\n**Top Role**: {member.top_role.mention}\n**Status**: {member.status}\n**Is Bot?** {member.bot}\n**Creation Date**: {member.created_at.__format__('%A, %d, %B, %Y @ %H:%M:%S')}", inline=False)
    await ctx.send(embed=embed)

@client.command(name="avatar", description="Get's user's avatars.")
async def avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    avatar_url = member.avatar.url

    embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=0xff9adc)
    embed.set_image(url=avatar_url)

    await ctx.send(embed=embed)

@client.command(name="time", description="Get's local time.")
async def time(ctx):
    now = datetime.datetime.now()
    embed = discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="", value=">>> <:clock:1223392595640848494> **Time**: <t:1711131060:T>", inline=False)
    await ctx.send(embed=embed)

@client.command(name="date", description="Get's todays date.")
async def date(ctx):
    now = datetime.datetime.now()
    embed = discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="", value=">>> <:date:1223392594206261310> **Date**: <t:1711131060:D>", inline=False)
    await ctx.send(embed=embed)

@client.command()
async def uptime(ctx):
    current_time = datetime.datetime.now()
    uptime = current_time - start_time
    seconds = uptime.total_seconds()
    days = seconds // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    uptime_str = "{:02}:{:02}:{:02}:{:02}".format(int(days), int(hours), int(minutes), int(seconds))
    embed = discord.Embed(title="", color=0xff9adc)
    embed.add_field(name="", value=f">>> **Uptime**: {uptime_str}", inline=False)
    await ctx.send(content="", embed=embed)

@kick.error
@warn.error
@clear.error
@ban.error
@unban.error
@mute.error
@unmute.error
@live.error
async def errors(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value=f"**Error!**\n>>> **You don't have the required permissions to use this command.**", inline=False)
        await ctx.send(content="", embed=embed)
    else:
        embed = discord.Embed(title="", color=0xff9adc)
        embed.add_field(name="", value=f"**Error!**\n>>> **An unexpected error occured.**\n```ansi\n[2;31m {error} [0m```", inline=False)
        await ctx.send(content="", embed=embed)

@client.event
async def on_member_join(member):
    welcome_goodbye_channel = client.get_channel(welcome_goodbye_channel_id)
    if welcome_goodbye_channel is not None:
            welcome_message = f"Welcome {member.mention} to our server! We're glad to have you here."
            embed = discord.Embed(title="", color=0xff9adc)
            embed.add_field(name="", value=f"**Welcome in!**\n>>> {welcome_message}", inline=False)
            await welcome_goodbye_channel.send(content="", embed=embed)

@client.event
async def on_member_remove(member):
    welcome_goodbye_channel = client.get_channel(welcome_goodbye_channel_id)
    if welcome_goodbye_channel is not None:
            leave_message = f"Goodbye **<@{member.id}>**! We're sad to see you leave."
            embed = discord.Embed(title="", color=0xff9adc)
            embed.add_field(name="", value=f"**Goodbye!**\n>>> {leave_message}", inline=False)
            await welcome_goodbye_channel.send(content="", embed=embed)

client.run("BOT TOKEN HERE")
