import os
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
import python_shakaw
import python_uniotaku
import json
from datetime import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') #Edit .env file
owner_id = 1234 #Change to your account id 

bot = commands.Bot(command_prefix='g!')

goldens_shakaw = 0
goldens_uniotaku = 0

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="g!help"))

@bot.command(name='ayt', help='Check if the bot is online')
async def online(ctx):
    await ctx.send("<:yesir:902506562717896715>")

@bot.command(name='ping', help='Check latency')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms <:smugface:890265836076544081>')

@bot.command(name='start', help="Only bot's owner can use")
async def start(ctx, task='task'):
    if ctx.author.id == owner_id:
        if task.lower() == 'uniotaku' and not watch_golden_uniotaku.is_running():
            await ctx.send('Iniciando tarefa da Uniotaku')
            watch_golden_uniotaku.start()
            if watch_golden_uniotaku.is_running():
                await ctx.send('Tarefa da Uniotaku iniciada com sucesso!')
            else:
                await ctx.send('Falha ao iniciar a tarefa')
        elif task.lower() == 'shakaw' and not watch_golden_shakaw.is_running():
            await ctx.send('Iniciando tarefa da Shakaw')
            watch_golden_shakaw.start()
            if watch_golden_shakaw.is_running():
                await ctx.send('Tarefa da Shakaw iniciada com sucesso!')
            else:
                await ctx.send('Falha ao iniciar a tarefa')
        elif task.lower() == 'alicepantsu' and not watch_alicepantsu.is_running():
            await ctx.send('Iniciando tarefa da AlicePantsu')
            watch_alicepantsu.start()
            if watch_alicepantsu.is_running():
                await ctx.send('Tarefa da AlicePantsu iniciada com sucesso!')
            else:
                await ctx.send('Erro ao iniciar a tarefa')
        elif task.lower() != 'uniotaku' and task.lower() != 'shakaw' and task.lower() != 'alicepantsu':
            await ctx.send('Tarefa inválida')
        else:
            await ctx.send('Tarefa já está ativa')
    else:
        await ctx.send('Você não tem permissão para usar este comando <:nyanbaka:890259994786807899>\n' + ctx.author.mention)

@bot.command(name='stop', help="Only bot's owner can use")
async def stop(ctx, task='task'):
    if ctx.author.id == owner_id:
        if task.lower() == 'uniotaku' and watch_golden_uniotaku.is_running():
            await ctx.send('Parando tarefa da Uniotaku')
            watch_golden_uniotaku.cancel()
        elif task.lower() == 'shakaw' and watch_golden_shakaw.is_running():
            await ctx.send('Parando tarefa da Shakaw')
            watch_golden_shakaw.cancel()
        elif task.lower() == 'alicepantsu' and watch_alicepantsu.is_running():
            await ctx.send('Parando tarefa da AlicePantsu')
        elif task.lower() != 'uniotaku' and task.lower() != 'shakaw' and task.lower() != 'alicepantsu':
            await ctx.send('Tarefa inválida')
        else:
            await ctx.send('Tarefa já está inativa')
    else:
        await ctx.send('Você não tem permissão para usar este comando <:nyanbaka:890259994786807899>\n' + ctx.author.mention)

@bot.command(name='setup',  help='Setup channels for AlicePantsu, Uniotaku and Shakaw Goldens. Usage: g!setup shakaw, g!setup uniotaku, g!setup alicepantsu')
@commands.has_permissions(manage_messages=True)
async def setup(ctx, tracker='tracker'):
    with open('channels.json', 'r') as f:
        channel_file = json.load(f)
    if str(ctx.guild.id) not in channel_file:
        channel_file[str(ctx.guild.id)] = {}
        with open('channels.json', 'w') as f:
            json.dump(channel_file, f, indent=4)

    trackers = ['shakaw', 'uniotaku', 'alicepantsu']
    if tracker.lower() in trackers:
        with open ('channels.json', 'r') as f:
            channels = json.load(f)
        channels[str(ctx.guild.id)][tracker.lower()] = ctx.channel.id
        await ctx.send(f'Canal configurado para Goldens da {tracker.capitalize()}!')
        with open ('channels.json', 'w') as f:
            json.dump(channels, f, indent=4)
    else:
        await ctx.send('Usage: g!setup shakaw, g!setup uniotaku, g!setup alicepantsu')

@bot.command(name='remove',help='Remove Golden feed. Usage: g!remove shakaw, g!remove uniotaku, g!remove alicepantsu')
@commands.has_permissions(manage_messages=True)
async def remove(ctx, tracker='tracker'):
    trackers = ['shakaw', 'uniotaku', 'alicepantsu']
    if tracker.lower() in trackers:
        with open ('channels.json', 'r') as f:
            channels = json.load(f)
        if tracker.lower() in channels[str(ctx.guild.id)]:
            channels[str(ctx.guild.id)].pop(tracker.lower())
            await ctx.send(f'Feed de Goldens da {tracker.capitalize()} removido com sucesso!')
            with open ('channels.json', 'w') as f:
                json.dump(channels, f, indent=4)
        else:
            await ctx.send(f'Nenhum canal configurado para o tracker {tracker.capitalize()}')
    else:
        await ctx.send('Usage: g!remove shakaw, g!remove uniotaku, g!remove alicepantsu')

@bot.command(name='status', help='Status of Golden Tasks')
async def status_tasks(ctx):
    message_uni = 'Tarefa da Uniotaku está ativa\n' if watch_golden_uniotaku.is_running() else 'Tarefa da Uniotaku não está ativa\n'
    message_shakaw = 'Tarefa da Shakaw está ativa\n' if watch_golden_shakaw.is_running() else 'Tarefa da Shakaw não está ativa\n'
    message_alicepantsu = 'Tarefa da AlicePantsu está ativa\n' if watch_alicepantsu.is_running() else 'Tarefa da AlicePantsu não está ativa\n'
    await ctx.send(f'{message_uni}{message_shakaw}{message_alicepantsu}')

@bot.command(name='goldens', help='Display number of Goldens for each tracker')
async def num_goldens(ctx):
    if watch_golden_shakaw.is_running() and watch_golden_uniotaku.is_running():
        message_uni = 'Uniotaku: Nenhum Golden\n' if goldens_uniotaku == 0 else f'Uniotaku: {goldens_uniotaku}\n'
        message_shakaw = 'Shakaw :Nenhum Golden\n' if goldens_shakaw == 0 else f'Shakaw: {goldens_shakaw}\n'
        await ctx.send(message_uni + message_shakaw)
    else:
        await ctx.send('Inicie as tarefas para obter a quantidade de goldens')


@tasks.loop(minutes=12.0)
async def watch_golden_uniotaku():
        with open('uni.json', 'r') as file:
            uni_old = json.load(file)

        uni_new = python_uniotaku.torrents()

        global goldens_uniotaku
        goldens_uniotaku = len(uni_new)

        new_goldens = [ i for i in uni_new if not i in uni_old ]

        if new_goldens:

            with open(log_file(), 'a') as logf:
                logf.write(now() + f"[UniGoldens] {len(new_goldens)} Novos Goldens encontrados!\n")
                for i in new_goldens:
                    logf.write(now() + f'[UniGoldens] {i}: {uni_new[i]["Nome"]}\n')

            with open('channels.json', 'r') as f:
                json_file = json.load(f)
                channels = [ json_file[i]['uniotaku'] for i in json_file if 'uniotaku' in json_file[i] ]

            for i in new_goldens:

                embed_golden = discord.Embed(title=uni_new[i]["Nome"], url=uni_new[i]["Pagina"], color=discord.Color.from_rgb(41, 165, 219))  #(199, 138, 13))

                if uni_new[i]["Golden"]:
                    embed = embed_golden
                else:
                    embed = discord.Embed(title=uni_new[i]["Nome"], url=uni_new[i]["Pagina"], color=discord.Color.from_rgb(41, 165, 219))

                if uni_new[i]["Golden"]: embed.add_field(name="Golden até:", value=uni_new[i]["GoldenAte"], inline=False)

                embed.set_author(name="UniOtaku", icon_url="https://i.imgur.com/hlvOGyH.png")
                embed.add_field(name="Tamanho", value=uni_new[i]["Tamanho"], inline=False)
                embed.add_field(name="Categoria", value=uni_new[i]["Categoria"], inline=True)
                embed.add_field(name="Seeders / Leechers", value=f'{uni_new[i]["Seeders"]} / {uni_new[i]["Leechers"]}', inline=True)
                embed.add_field(name="Vezes Completado", value=uni_new[i]["Completado"], inline=True)
                embed.add_field(name="Fansub", value=uni_new[i]["Fansub"], inline=True)
                embed.add_field(name="Uploader", value=uni_new[i]["Uploader"], inline=True)
                embed.add_field(name="Download", value=str(uni_new[i]["Download"]), inline=False)
                embed.set_image(url=uni_new[i]["Imagem"])
                for i in channels:
                    channel = bot.get_channel(id=i)
                    await channel.send(embed=embed)
        else:
            with open(log_file(), 'a') as logf:
                logf.write(now() + f"[UniGoldens] Nenhum Golden Novo\n")


@tasks.loop(minutes=12.0)
async def watch_golden_shakaw():
        with open('shakaw.json', 'r') as file:
            shakaw_old = json.load(file)

        shakaw_new = python_shakaw.torrents()

        global goldens_shakaw
        goldens_shakaw = len(shakaw_new)

        new_goldens = [ i for i in shakaw_new if not i in shakaw_old ]

        if new_goldens:

            with open(log_file(), 'a') as logf:
                logf.write(now() + f"[ShakawGoldens] {len(new_goldens)} Novos Goldens encontrados!\n")
                for i in new_goldens:
                    logf.write(now() + f'[ShakawGoldens] {i}: {shakaw_new[i]["Nome"]}\n')

            with open('channels.json', 'r') as f:
                json_file = json.load(f)
                channels = [ json_file[i]['shakaw'] for i in json_file if 'shakaw' in json_file[i] ]

            for i in new_goldens:

                embed_golden=discord.Embed(title=shakaw_new[i]["Nome"], url=shakaw_new[i]["Pagina"], color=discord.Color.from_rgb(253, 253, 253))    #(199, 138, 13))

                if shakaw_new[i]["Golden"]:
                    embed = embed_golden
                    embed.add_field(name="Golden até:", value=shakaw_new[i]["GoldenAte"], inline=False)
                else:
                    embed = discord.Embed(title=shakaw_new[i]["Nome"], url=shakaw_new[i]["Pagina"], color=discord.Color.from_rgb(253, 253, 253))

                embed.set_author(name="Shakaw", icon_url="https://i.imgur.com/e7Vzwu5.png")
                embed.add_field(name="Tamanho", value=shakaw_new[i]["Tamanho"], inline=False)
                embed.add_field(name="Categoria", value=shakaw_new[i]["Categoria"], inline=False)
                embed.add_field(name="Arquivos", value=shakaw_new[i]["Arquivos"], inline=True)
                embed.add_field(name="Seeders / Leechers", value=f'{shakaw_new[i]["Seeders"]} / {shakaw_new[i]["Leechers"]}', inline=True)
                embed.add_field(name="Vezes Completado", value=shakaw_new[i]["Completado"], inline=True)
                embed.add_field(name="Fansub", value=shakaw_new[i]["Fansub"], inline=True)
                embed.add_field(name="Uploader", value=shakaw_new[i]["Uploader"], inline=True)
                embed.add_field(name="Download", value=str(shakaw_new[i]["Download"]), inline=False)
                embed.set_image(url=shakaw_new[i]["Imagem"])
                for i in channels:
                    channel = bot.get_channel(id=i)
                    await channel.send(embed=embed)
        else:
            with open(log_file(), 'a') as logf:
                logf.write(now() + f"[ShakawGoldens] Nenhum Golden Novo\n")


@tasks.loop(minutes=12.0)
async def watch_alicepantsu():
        with open('alicepantsu.json', 'r') as file:
            alicepantsu_old = json.load(file)

        alicepantsu_new = python_alicepantsu.torrents()


        new_torrents = [ i for i in alicepantsu_new['pantsu'] if not i in alicepantsu_old['pantsu'] ]
        new_torrents += [ i for i in alicepantsu_new['nyan'] if not i in alicepantsu_old['nyan'] ]

        if new_torrents:

            with open(log_file(), 'a') as logf:
                logf.write(now() + f"[AlicePantsu] {len(new_torrents)} Novos Torrents encontrados!\n")
                for i in new_torrents:
                    logf.write(now() + f'[AlicePantsu] {i["id"]}: {i["anime_name"]}\n')

            with open('channels.json', 'r') as f:
                json_file = json.load(f)
                channels = [ json_file[i]['alicepantsu'] for i in json_file if 'alicepantsu' in json_file[i] ]

            for i in new_torrents:

                embed=discord.Embed(title=f'{i["anime_name"]} {i["qualidade"]}', url=i["download_link"].replace(' ', '%20'), color=discord.Color.from_rgb(250, 129, 110))

                embed.set_author(name="AlicePantsu", icon_url="https://i.imgur.com/GgvDeCZ.png")
                embed.add_field(name="Fansub", value=re.search('(?<=\[).*(?=\])', i["fansub"]).group(0), inline=True)
                embed.add_field(name="Download", value=str(i["download_link"].replace(' ', '%20')), inline=False)
                for i in channels:
                    channel = bot.get_channel(id=i)
                    await channel.send(embed=embed)
        else:
            with open(log_file(), 'a') as logf:
                logf.write(now() + f"[AlicePantsu] Nenhum Torrent Novo\n")

def now():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S ")

def log_file():
    return 'logs/' + datetime.now().strftime('%d-%m-%y') + '.log'

bot.run(TOKEN)