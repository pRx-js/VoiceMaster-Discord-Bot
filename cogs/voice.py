import discord
import math
import asyncio
import aiohttp
import json
import datetime
from discord.ext import commands
import traceback
import sqlite3
from urllib.parse import quote
import validators
from discord.ext.commands.cooldowns import BucketType
from time import gmtime, strftime


class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        guildID = member.guild.id
        c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
        voice=c.fetchone()
        if voice is None:
            pass
        else:
            voiceID = voice[0]
            try:
                if after.channel.id == voiceID:
                    c.execute("SELECT * FROM voiceChannel WHERE userID = ?", (member.id,))
                    cooldown=c.fetchone()
                    if cooldown is None:
                        pass
                    else:
                        await member.send("Çok hızlı kanal oluşturuyorsunuz! **15** Saniye zaman aşımına uğratıldınız.")
                        await asyncio.sleep(15)
                    c.execute("SELECT voiceCategoryID FROM guild WHERE guildID = ?", (guildID,))
                    voice=c.fetchone()
                    c.execute("SELECT channelName, channelLimit FROM userSettings WHERE userID = ?", (member.id,))
                    setting=c.fetchone()
                    c.execute("SELECT channelLimit FROM guildSettings WHERE guildID = ?", (guildID,))
                    guildSetting=c.fetchone()
                    if setting is None:
                        name = f"{member.name}'in Odası"
                        if guildSetting is None:
                            limit = 0
                        else:
                            limit = guildSetting[0]
                    else:
                        if guildSetting is None:
                            name = setting[0]
                            limit = setting[1]
                        elif guildSetting is not None and setting[1] == 0:
                            name = setting[0]
                            limit = guildSetting[0]
                        else:
                            name = setting[0]
                            limit = setting[1]
                    categoryID = voice[0]
                    id = member.id
                    category = self.bot.get_channel(categoryID)
                    channel2 = await member.guild.create_voice_channel(name,category=category)
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(self.bot.user, connect=True,read_messages=True)
                    await channel2.edit(name= name, user_limit = limit)
                    c.execute("INSERT INTO voiceChannel VALUES (?, ?)", (id,channelID))
                    conn.commit()
                    def check(a,b,c):
                        return len(channel2.members) == 0
                    await self.bot.wait_for('voice_state_update', check=check)
                    await channel2.delete()
                    await asyncio.sleep(3)
                    c.execute('DELETE FROM voiceChannel WHERE userID=?', (id,))
            except:
                pass
        conn.commit()
        conn.close()

    @commands.command()
    async def yardım(self, ctx):
        embed = discord.Embed(title="Yardım", description="",color=0x7289da)
        embed.set_author(name="Börü Özel Sohbet Yardım menüsü",url="https://steamcommunity.com/groups/borugamingg", icon_url="https://cdn.discordapp.com/avatars/702441843333529630/19fc69e335e3115bec14c4caf5f7d254.png?size=2048")
        embed.add_field(name=f'**Komutlar**', value=f'**Kanalı Kilitlemek İçin:**\n\n`.voice kilit`\n\n------------\n\n'
                        f'**Kiliti Açmak İçin:**\n\n`.voice kilitaç`\n\n------------\n\n'
                        f'**Kanalınızın İsmini Değiştirmek İçin:**\n\n`.voice isim <isim>`\n\n**Örnek:** `.voice isim gays`\n\n------------\n\n'
                        f'**Kanalınızın Limitini Değiştirmek İçin:**\n\n`.voice limit <sayı>`\n\n**Örnek:** `.voice limit 3`\n\n------------\n\n'
                        f'**Başka Kullanıcılara Odanıza Katılım İzni Vermek İçin:**\n\n`.voice izinver @kişi`\n\n**Örnek:** `.voice izinver @pRx`\n\n------------\n\n'
                        f'**Odanın Sahibi Odadan Çıkmış İse Sahipliği Almak İçin:**\n\n`.voice sahipol`\n\n**Örnek:** `.voice sahipol`\n\n------------\n\n'
f'**Odanın Sahibi Odadan Çıkmış İse Sahipliği Almak İçin:**\n\n`.voice sahipol`\n\n**Örnek:** `.voice sahipol`\n\n------------\n\n'
                        f'**Başka Kullanıcılardan Katılım İznini Almak İçin:**\n\n`.voice izinal @kişi`\n\n**Example:** `.voice izinal @pRx`\n\n', inline='false')
        await ctx.channel.send(embed=embed)

    @commands.group()
    async def voice(self, ctx):
        pass

    @voice.command(aliases=["setup"])
    async def kurulum(self, ctx):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        guildID = ctx.guild.id
        id = ctx.author.id
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id == 385001389119504384:
            def check(m):
                return m.author.id == ctx.author.id
            await ctx.channel.send("**Her Bir Soruyu Cevaplamak İçin 60 Saniyeniz Var.**")
            await ctx.channel.send(f"**Kanalların Oluşturulacağı Kategorinin İsmini Giriniz (ör. Özel Sohbet)**")
            try:
                category = await self.bot.wait_for('message', check=check, timeout = 60.0)
            except asyncio.TimeoutError:
                await ctx.channel.send('Cevap vermek çok uzun sürdü!')
            else:
                new_cat = await ctx.guild.create_category_channel(category.content)
                await ctx.channel.send('**Özel Oda Oluşturmak İçin Girilmesi Gereken Ses Kanalının İsmini Giriniz (ör. Özel Oda Oluştur)**')
                try:
                    channel = await self.bot.wait_for('message', check=check, timeout = 60.0)
                except asyncio.TimeoutError:
                    await ctx.channel.send('Cevap vermek çok uzun sürdü!')
                else:
                    try:
                        channel = await ctx.guild.create_voice_channel(channel.content, category=new_cat)
                        c.execute("SELECT * FROM guild WHERE guildID = ? AND ownerID=?", (guildID, id))
                        voice=c.fetchone()
                        if voice is None:
                            c.execute ("INSERT INTO guild VALUES (?, ?, ?, ?)",(guildID,id,channel.id,new_cat.id))
                        else:
                            c.execute ("UPDATE guild SET guildID = ?, ownerID = ?, voiceChannelID = ?, voiceCategoryID = ? WHERE guildID = ?",(guildID,id,channel.id,new_cat.id, guildID))
                        await ctx.channel.send("**Kurulum Tamamlandı!**")
                    except:
                        await ctx.channel.send("Kurulum tamamlanamadı.\nLütfen `.voice kurulum` ile tekrar kurulum başlatınız!")
        else:
            await ctx.channel.send(f"{ctx.author.mention} Sadece **Sunucu Sahibi** Kurulum Başlatabilir!")
        conn.commit()
        conn.close()

    @commands.command()
    async def varsayılanlimitayarla(self, ctx, num):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id == 151028268856770560:
            c.execute("SELECT * FROM guildSettings WHERE guildID = ?", (ctx.guild.id,))
            voice=c.fetchone()
            if voice is None:
                c.execute("INSERT INTO guildSettings VALUES (?, ?, ?)", (ctx.guild.id,f"{ctx.author.name}'s channel",num))
            else:
                c.execute("UPDATE guildSettings SET channelLimit = ? WHERE guildID = ?", (num, ctx.guild.id))
            await ctx.send("Varsayılan Kanal Limiti Değiştirildi!")
        else:
            await ctx.channel.send(f"{ctx.author.mention} Sadece **Sunucu Sahibi** Bu komutu ayarlayabilir.!")
        conn.commit()
        conn.close()

    @setup.error
    async def info_error(self, ctx, error):
        print(error)

    @voice.command(aliases=["lock"])
    async def kilit(self, ctx):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Bir kanala sahip değilsiniz!")
        else:
            channelID = voice[0]
            role = discord.utils.get(ctx.guild.roles, name='@everyone')
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False,read_messages=True)
            await ctx.channel.send(f'🔒 {ctx.author.mention} Özel Odanız **Kilitlendi!**')
        conn.commit()
        conn.close()

    @voice.command(aliases=["unlock"])
    async def kilitaç(self, ctx):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Bir kanala sahip değilsiniz!")
        else:
            channelID = voice[0]
            role = discord.utils.get(ctx.guild.roles, name='@everyone')
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True,read_messages=True)
            await ctx.channel.send(f'🔓 {ctx.author.mention} Özel Odanızın **Kiliti Açıldı!**')
        conn.commit()
        conn.close()

    @voice.command(aliases=["onayla"])
    async def izinver(self, ctx, member : discord.Member):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Bir kanala sahip değilsiniz!")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True)
            await ctx.channel.send(f'✅ {ctx.author.mention}, {member.name} Adlı kullanıcının özel odanıza erişmesine izin verdiniz.')
        conn.commit()
        conn.close()

    @voice.command(aliases=["reddet"])
    async def izinal(self, ctx, member : discord.Member):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        guildID = ctx.guild.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Bir kanala sahip değilsiniz!")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
                    voice=c.fetchone()
                    channel2 = self.bot.get_channel(voice[0])
                    await member.move_to(channel2)
            await channel.set_permissions(member, connect=False,read_messages=True)
            await ctx.channel.send(f'❌{ctx.author.mention}, {member.name} Adlı kullanıcının özel odanıza erişimini reddettiniz. ')
        conn.commit()
        conn.close()



    @voice.command(aliases=["kanallimiti"])
    async def limit(self, ctx, limit):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Bir kanala sahip değilsiniz!")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit = limit)
            await ctx.channel.send(f'{ctx.author.mention} Kanalınızın limiti başarıyla değiştirdiniz: '+ '{}!'.format(limit))
            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,))
            voice=c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id,f'{ctx.author.name}',limit))
            else:
                c.execute("UPDATE userSettings SET channelLimit = ? WHERE userID = ?", (limit, id))
        conn.commit()
        conn.close()


    @voice.command(aliases=["addeğiştir"])
    async def isim(self, ctx,*, name):
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        id = ctx.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice=c.fetchone()
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} Bir kanala sahip değilsiniz!")
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name = name)
            await ctx.channel.send(f'{ctx.author.mention} Kanalınızın ismini başarıyla değiştirdiniz: '+ '{}!'.format(name))
            c.execute("SELECT channelName FROM userSettings WHERE userID = ?", (id,))
            voice=c.fetchone()
            if voice is None:
                c.execute("INSERT INTO userSettings VALUES (?, ?, ?)", (id,name,0))
            else:
                c.execute("UPDATE userSettings SET channelName = ? WHERE userID = ?", (name, id))
        conn.commit()
        conn.close()

    @voice.command(aliases=["sahiplen"])
    async def sahipol(self, ctx):
        x = False
        conn = sqlite3.connect('voice.db')
        c = conn.cursor()
        channel = ctx.author.voice.channel
        if channel == None:
            await ctx.channel.send(f"{ctx.author.mention} bir ses kanalında değilsiniz.")
        else:
            id = ctx.author.id
            c.execute("SELECT userID FROM voiceChannel WHERE voiceID = ?", (channel.id,))
            voice=c.fetchone()
            if voice is None:
                await ctx.channel.send(f"{ctx.author.mention} Bu kanala sahip olamazsınız!")
            else:
                for data in channel.members:
                    if data.id == voice[0]:
                        owner = ctx.guild.get_member(voice [0])
                        await ctx.channel.send(f"{ctx.author.mention} Bu kanal zaten {owner.mention} tarafından sahiplenilmiş!")
                        x = True
                if x == False:
                    await ctx.channel.send(f"{ctx.author.mention} Kanalın sahipi değilsiniz")
                    c.execute("UPDATE voiceChannel SET userID = ? WHERE voiceID = ?", (id, channel.id))
            conn.commit()
            conn.close()


def setup(bot):
    bot.add_cog(voice(bot))
