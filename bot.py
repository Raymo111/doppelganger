import discord
import re
import asyncio
import io
import aiohttp
import os
import json
print("hello world")

def jsonFromFile(filePath):
  with open(filePath,"r",encoding="utf8") as file:
    return json.loads(file.read())

emojis = jsonFromFile('emoji.json')
emoji_map = {}
for emoji in emojis['emoji']:
    emoji_name = emoji[emoji.index(':',0)+1:emoji.index(':',emoji.index(':',0)+1)]
    emoji_map[emoji_name] = emoji

def cacheFile(obj,filePath):
  with open(filePath,"w") as file:
    file.write(json.dumps(obj, indent=4))

emoji_page_msgs = {}

emoji_pages = []
def fill_pages():
    global emoji_pages
    emoji_pages = []
    cur_page = ''
    cnt = 0
    for cur_emoji in emojis['emoji']:
        if cnt < 26 and len(cur_page) < 1900:
            cur_page += cur_emoji
            cnt += 1
        else:
            emoji_pages.append(cur_page)
            cur_page = cur_emoji
            cnt = 1
    emoji_pages.append(cur_page)

fill_pages()

left_arrow = '⬅️'
right_arrow = '➡️'

emoji_send_regex = ':[A-z]{1,50}:'
multiple_emoji_send_regex = '(<?a?(:[A-z]{1,50}:)([0-9]{1,20}>)?){1,50}'

print(re.match(multiple_emoji_send_regex, ":orz:"))

emoji_render_regex = '<a?'+emoji_send_regex+'[0-9]{1,20}>'

print(emoji_map)
print(emojis)

servers = [779069894767542274]

def link(message):
  link = "https://discord.com/channels/"
  link += str(message.guild.id)+"/"
  link += str(message.channel.id)+"/"
  link += str(message.id)
  return link

archive = 779070940310274058
archiveDiscussion = 815794494174920744

client = discord.Client()
@client.event
async def on_ready():
    print("logged in as {0.user}".format(client))
    for guild in client.guilds:
        for channel in guild.channels:
            global archive
            global archiveDiscussion
            if(channel.id == archive):
                archive = channel
            if(channel.id == archiveDiscussion):
                archiveDiscussion = channel

cnt = {}
cache = open('cache.txt','r')
n = int(cache.readline())
for i in range(0,n):
  cur = cache.readline().strip().split()
  cnt[cur[0]] = int(cur[1])
cache.close()
print("ez")

def cache():
    cacheFile(emojis, 'emoji.json')
    cache = open('cache.txt','w')
    cache.write(str(len(cnt))+"\n")
    for emoji in cnt:
      cache.write(emoji+" "+str(cnt[emoji])+"\n")
    cache.close()

async def grabImage(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
          if resp.status != 200:
            print("oof")
          data = io.BytesIO(await resp.read())
          return discord.File(data, 'cool_image.png')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel == archive and message.author.bot and (not message.author == client.user):
      await message.delete()
      return
    if(message.channel == archive):
        if(len(message.attachments) != 0):
            e = discord.Embed(title="Archived", url=message.jump_url, description=message.content, color=0xff0ff)
            e.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            e.set_image(url=message.attachments[0].url)
            discussionLink = link(await archiveDiscussion.send(link(message),embed=e))
            await message.channel.send(content="Comments: "+discussionLink)
        else:
            await message.delete()
            empty = "https://cdn.discordapp.com/attachments/747090562661875763/816728774623625286/unknown.png"
            msg = await archive.send(file=await grabImage(empty),embed=discord.Embed(title="DELET",description="<:ree:779082002560974931>",color=0xff0000))
            await asyncio.sleep(10)
            await msg.delete()
    tokens = message.content.strip().split()
    emojis_list = re.findall(r'<:\w*:\d*>', message.content)
    for emoji in emojis_list:
        if emoji in cnt:
            cnt[emoji] = cnt[emoji]+1
        else:
            cnt[emoji] = 1
    cache()
    if message.content.strip()=="<:paopao:814288638359502908>":
        await message.channel.send("<:blobweary:779086866829279243>")
    if len(tokens) >= 1 and tokens[0] == "gimme":
        if len(tokens) >= 2 and tokens[1] == "help":
            print("help CALLED")
            e = discord.Embed(title="HELAPAMEEEEE REEE", description="yeet", color=0xff00ff)
            e.add_field(name="`gimme emoji usage`", value="gives you usage of the emojis", inline=True)
            e.add_field(name="`yo yo yo cache rq`", value="caches the emojis rq",inline=True)
            await message.channel.send(embed=e)
        elif len(tokens) >= 3 and tokens[1] == "emoji" and tokens[2] == "usage":
            print("emoji usage CALLED")
            e = discord.Embed(title="Emoji Usage", description="Usage of all emojis that have been used atleast once, ever since I felt like counting", color=0xff00ff)
            uses = {}
            keys = []
            serverEmojis = ["<:latiwow:814202957494353972>"]
            serverEmojisRaw = await message.guild.fetch_emojis()
            for emoji in serverEmojisRaw:
              serverEmojis.append("<:"+str(emoji.name)+":"+str(emoji.id)+">")
            for emoji in cnt:
                if not(emoji in serverEmojis):
                    continue
                if(cnt[emoji] in uses):
                    uses[cnt[emoji]].append(emoji)
                else:
                    keys.append(cnt[emoji])
                    uses[cnt[emoji]] = [emoji]
            keys.sort(reverse=True)
            rank = 1;
            for key in keys:
                start = True
                next = 0
                while(next < len(uses[key])):
                    cur = str(rank)+"."
                    if(start):
                        start = False
                    else:
                        cur += "(cont.)"
                    cur += " "
                    while(next < len(uses[key]) and len(cur)+len(uses[key][next]) < 256):
                        cur += uses[key][next]
                        next = next+1
                    val = ""
                    if key == 1:
                      val += "1 use"
                    else:
                      val += str(key)+" uses"
                    val = val+"\n"
                    e.add_field(name=cur, value=val, inline=True)
                rank = rank+1;
            if len(uses) == 0:
                e.add_field(name="lmao yall are boring asf", value="monke", inline=True)
            await message.channel.send(embed=e)
    elif len(tokens) >= 5 and tokens[0] == "yo" and tokens[1] == "yo" and tokens[2] == "yo" and tokens[3] == "cache" and tokens[4] == "rq":
        cache()
        await message.channel.send("cache me outside how bow dah")

    if message.author.bot:
        return

    msg = message
    ch = message.channel
    tokens = msg.content.strip().split()
    print(tokens)

    if len(tokens) >= 2 and tokens[:2] == ['scan','server']:
        for server_emoji in msg.guild.emojis:
            print(server_emoji)
            if server_emoji.is_usable():
                if server_emoji.name in emoji_map:
                    if emoji_map[server_emoji.name] != str(server_emoji):
                        await ch.send('The emoji name '+server_emoji.name+' is already registered as the following:')
                        await ch.send(emoji_map[server_emoji.name])
                        await ch.send('Change its name to something else if you wish to use it.')
                else:
                    #await ch.send('orz')
                    #await ch.send(str(server_emoji))
                    print(str(server_emoji.name))
                    emoji_map[server_emoji.name] = str(server_emoji)
                    emojis['emoji'].append(str(server_emoji))
        await ch.send('done')
        print(emoji_map)
        print(emojis)
        cache()
        fill_pages()

    if len(tokens) >= 2 and tokens[0] == 'view' and 'emoji' in tokens[1]:
        if len(emoji_pages) == 0:
            await ch.send('no emojis registered')
        else:
            emoji_page_msg = await ch.send(emoji_pages[0])
            emoji_page_msgs[str(emoji_page_msg.id)] = 0
            await asyncio.sleep(0.5)
            await emoji_page_msg.add_reaction(left_arrow)
            await emoji_page_msg.add_reaction(right_arrow)

    if len(tokens) >= 2 and "le" in tokens[0] and "me" in tokens[0] and "in" in tokens[1]:
        await ch.send("rrreeeeeeeeeeeeeeeeeeeeeeeeeeeee fiiiiiiiinnnnnnnneeeeeeeeee")
        await ch.send("<https://discord.com/api/oauth2/authorize?client_id=815267324973023234&permissions=8&scope=bot>")

    all_emoji = True
    for token in tokens:
        if not re.fullmatch(multiple_emoji_send_regex, token):
            all_emoji = False

    if all_emoji:
        text = ''
        for token in tokens:
            print(token)
            for emoji_key in re.findall(emoji_send_regex, token):
                print(emoji_key)
                cur_emoji = emoji_key[1:-1]
                print(cur_emoji)
                if cur_emoji in emoji_map:
                    text += emoji_map[cur_emoji]
            text += ' '

        text = text.strip()
        if len(text) > 0:
            await msg.delete()

            cur_member = (await msg.guild.query_members(message.author.name))[0]
            if cur_member.nick is None:
                hook_name = cur_member.name
            else:
                hook_name = cur_member.nick
            user_avatar = await msg.author.avatar_url.read()
            hook = await ch.create_webhook(name=hook_name, avatar=user_avatar)
            await hook.send(text)
            await hook.delete()

@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    msg = reaction.message
    if str(msg.id) in emoji_page_msgs:
        if str(reaction.emoji) == right_arrow:
            print('got right')
            emoji_page_msgs[str(msg.id)] += 1
            if emoji_page_msgs[str(msg.id)] >= len(emoji_pages):
                emoji_page_msgs[str(msg.id)] = 0
            await reaction.remove(user)

        elif str(reaction.emoji) == left_arrow:
            print('got left')
            emoji_page_msgs[str(msg.id)] -= 1
            if emoji_page_msgs[str(msg.id)] < 0:
                emoji_page_msgs[str(msg.id)] = len(emoji_pages)-1
            await reaction.remove(user)

        print('editing to '+emoji_pages[emoji_page_msgs[str(msg.id)]])
        await msg.edit(content=emoji_pages[emoji_page_msgs[str(msg.id)]])

client.run(os.environ['tok'])
