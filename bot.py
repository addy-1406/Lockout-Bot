import os
import discord
import time
import math
import string
import random
from discord.ext import commands
from pymongo import MongoClient
import requests
import json
import asyncio
from bs4 import BeautifulSoup


uri = os.environ.get("MONGO_URI")
token = os.environ.get("BOT_TOKEN")

try:
    cluster = MongoClient(uri)
    print("Connected successfully!!!")
except:  
    print("Could not connect to MongoDB")

class AcWeb:
    def __init__(self):
        self.url = 'https://atcoder.jp/contests/'

    def key_words(self, user_message):
        words = user_message.split()[1:]
        if words[0].lower == 'b':
            num = random.randint(0,250)
            keyword = f'abc{num}/tasks/abc{num}_'+words[1].lower()
        elif words[0].lower == 'r':
            num = random.randint(0,150)
            keyword = f'arc{num}/tasks/arc{num}_'+words[1].lower()
        return keyword
        

    def search(self, keywords):
        response = requests.get(self.url+keywords)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        Text = soup.body
        return Text

    def status(self, Text):
        main = Text.find('td',class_ = 'text-center')
        if main == None:
            ans = ans = 'No submissions'
        else:
            ans = main.text
        return ans




db = cluster['discord-bot']
servers = db['servers']
participantsList = db['participantsList']
tourney_status = db['tourney_status']
storage = db['storage']
current_round = db['current_round']
current_matches=db['current_matches']
intents = discord.Intents().all()
client = commands.Bot(command_prefix="!", intents=intents,help_command=None)
botName = "Tatakae"
ac_problemset = AcWeb()


@client.command()
async def help(ctx):
    embed = discord.Embed(
        title="COMMANDS :ledger:",
        color=0x3cddbc)

    embed.add_field(name="!registerMe <cf_handle>", value="To register your codeforces handles"+"\n\u200b", inline=False)
    embed.add_field(name="!ac_registerMe <ac_handle>", value="To register your atcoder handles"+"\n\u200b", inline=False)
    embed.add_field(name="!unregisterMe", value="To unregister yourself from the tournament"+"\n\u200b", inline=False)
    embed.add_field(name="!showParticipants", value="To display the participants"+"\n\u200b", inline=False)
    embed.add_field(name="!showMatches", value="Shows all the matches in the current round"+"\n\u200b", inline=False)
    embed.add_field(name="!show", value="Shows the current round number"+"\n\u200b", inline=False)
    embed.add_field(name="!roundStatus <roundnumber>", value="Shows the status of the current round"+"\n\u200b", inline=False)
    embed.add_field(name="!matchUpdates", value="Gives you the updates of the ongoing match in a channel"+"\n\u200b", inline=False)
    embed.add_field(name="!stalk <tag>", value="Shows details of a particular participant"+"\n\u200b", inline=False)
    embed.add_field(name="!flow", value="Shows the workflow"+"\n\u200b", inline=False)
    embed.add_field(name="!managerHelp", value="Shows the commands for tourney-managers"+"\n\u200b", inline=False)
    embed.add_field(name="!help", value="This message -_-", inline=False)
    

    await ctx.send(embed=embed)
    return

@client.command()
async def flow(ctx):
    embed = discord.Embed(
        title="FLOW OF EVENTS :ocean:",
        description=f"\n"
        "1. Register your cf handles(compulsary) followed by your ac handles(not compulsary)\n\n"
        "2. Contact your opponent of your current round to fix a match and inform one of the moderators\n\n"
        "3. Have your match for anytime between 10 to 180 mins on a cf/ac problemset\n\n"
        "4. Be the last one standing to become the LOCKOUT CHAMPION\n\n"
        ,
        color=0x3cddbc)

    await ctx.send(embed=embed)
    return



@client.command()
@commands.has_role('Tourney-manager')
async def managerHelp(ctx):
    embed = discord.Embed(
        title="MANAGER COMMANDS :saluting_face: ",
        color=0x3cddbc)

    disp = ""
    disp +=  "Start a match between two participants\n"
    disp += "-> To start a cf match give rating number\n"
    disp += "-> To start a ac match give toughness (easy, medium, hard)\n"

    embed.add_field(name="!channel <channel name>", value="To change the channel of tourney manager"+"\n\u200b", inline=False)
    embed.add_field(name="!startRegister <channel name> <tourneyname>", value="To register a tournament with a channel"+"\n\u200b", inline=False)
    embed.add_field(name="!matchChannel <channel name> <tourneyname>", value="To register a channel for match"+"\n\u200b", inline=False)
    embed.add_field(name="!unRegMatchChannel <channel name>", value="To unregister a channel for match"+"\n\u200b", inline=False)
    embed.add_field(name="!startTourney <tourneyname>", value="Start a tournament"+"\n\u200b", inline=False)
    embed.add_field(name="!stopTourney <tourneyname>", value="Stop a tournament"+"\n\u200b", inline=False)
    embed.add_field(name="!showTourneys", value="Shows the list of tournaments"+"\n\u200b", inline=False)
    embed.add_field(name="!startMatch <tag1> <tag2> <rating/toughness>", value=disp, inline=False)

    await ctx.send(embed=embed)
    return



##########################################################################################################################
#                                           ATCODER CODE                        
##########################################################################################################################

# sync functions

def sing_status(task,user):
    link1 = f"{task[:-2]}/submissions?f.Task={task}&f.LanguageName=&f.Status=&f.User={user}"
    msg1 = ac_problemset.search(link1)
    ans1 = ac_problemset.status(msg1)
    return ans1

def status(task,user1,user2):
    link1 = f"{task[:-2]}/submissions?f.Task={task}&f.LanguageName=&f.Status=&f.User={user1}"
    msg1 = ac_problemset.search(link1)
    ans1 = ac_problemset.status(msg1)
    link2 = f"{task[:-2]}/submissions?f.Task={task}&f.LanguageName=&f.Status=&f.User={user2}"
    msg2 = ac_problemset.search(link2)
    ans2 = ac_problemset.status(msg2)
    if ans1 == ans2 == 'No submissions':
        return False
    else:
        return True

def ac_probs(words,user1,user2):
    link = 'Error, Please try again!'
    if words[0].lower() == 'beginner':
        if words[1] in 'abcd':
            num = random.randint(42,250)
        else:
            num = random.randint(130,250)
        if 9<num<100:
            num = '0'+str(num)
        else:
            num = str(num)
        
    
        while status('abc_'+num+words[1],user1,user2):
            if words[1] in 'abcd':
                num = random.randint(42,250)
            else:
                num = random.randint(130,250)
            if 9<num<100:
                num = '0'+str(num)
            else:
                num = str(num)

        link = 'abc'+str(num)+'/tasks/abc'+str(num)+'_'+words[1].lower()


    elif words[0].lower() == 'regular':
        num = random.randint(104,150) #starts from 58 but 58 to 103 only have abcd
        if 9<num<100:
            num = '0'+str(num)
        else:
            num = str(num)
        while status('arc_'+num+words[1],user1,user2):
            num = random.randint(104,150) #starts from 58 but 58 to 103 only have abcd
            if 9<num<100:
                num = '0'+str(num)
            else:
                num = str(num)

        link = 'arc'+str(num)+'/tasks/arc'+str(num)+'_'+words[1].lower()
    
    elif words[0].lower() == 'grand':
        num = random.randint(1,59)
        if 0<num<10:
            num  = '00'+str(num)
        elif 9<num<100:
            num = '0'+str(num)
        else:
            num = str(num)
        while status('agc_'+num+words[1],user1,user2):
            num = random.randint(1,59)
            if 0<num<10:
                num  = '00'+str(num)
            elif 9<num<100:
                num = '0'+str(num)
            else:
                num = str(num)
        
        link = 'agc'+str(num)+'/tasks/agc'+str(num)+'_'+words[1].lower()
    
    return link

def ac_validate_acc(handle,string):
    startTime = time.time()
    uris = 'https://atcoder.jp/users/' + handle
    while True:
        response = requests.get(uris)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        Text = soup.body
        main = Text.find("table",class_ = "dl-table")
        if "Affiliation" not in main.text:
            continue
        index = main.text.index("Affiliation")
        aff = main.text[index+11:]
        s = str(aff)[:-1]

        # s = string
        # print(s,aff)
        if s == string:
            return True
        if time.time()-startTime > 60:
            return False
        time.sleep(10)


async def matchLive(ctx, str1, str2, dic, url, match_time):

    thisServer = servers.find_one({"_id": ctx.guild.id})
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == dic["channel_id"]:
            text_channel = x

    global tourneyName
    tourneyName = None
    for tournament in thisServer['tournaments']:
        if(text_channel.id in thisServer['tournaments'][tournament]['match_channels']):
            tourneyName = tournament

    print(text_channel.id)

    
    # await text_channel.send(embed=embed)
    # return


    print("hello")
    # match_time = 0
    while(True):
        flag = False
        match_list_now=current_matches.find_one({"server":ctx.guild.id})['matches'][tourneyName]
        for i in match_list_now:
            if(i["channel_id"] == text_channel.id):
                plt = i["platform"]
                problem_list = i["Problems"]
                score1 = i["Scores"][0]
                score2 = i["Scores"][1]
                pc1 = i["problem_rating"][0]
                pc2 = i["problem_rating"][1]
                player1  = i["player1"]
                player2 = i["player2"]
                hours_start = i["Start_Time"][0]
                minutes_start = i["Start_Time"][1]
                flag = True
                break
        
        if(flag == False):
            break
        print(text_channel.id)
        print(i["player1"]["cf_handle"])

        # score1=scores[0]
        # score2=scores[1]
        # pc1 = pc[0]
        # pc2 = pc[1]

        if plt == 'cf':
            url1=f"https://codeforces.com/api/user.status?handle={player1['cf_handle']}&from=1&count=10"
            url2=f"https://codeforces.com/api/user.status?handle={player2['cf_handle']}&from=1&count=10"
            
            response_API=requests.get(url1)
            data=response_API.text
            parse_json=json.loads(data)
            submissions=parse_json['result']
            index=1
            for x in problem_list:
                for y in submissions:
                    if(y['problem']['name']==x['name']and y['verdict']=="OK"and x['status']==0):
                        pc1 = max(pc1,index*100)
                        x['status']=1
                        score1=score1+100*index
                        embed = discord.Embed(
                            description=f"<@{str1}> has solved problem worth {100*index} points",
                            color=discord.Color.blue()
                        )
                        await text_channel.send(embed = embed)
                        embed = discord.Embed(
                            title="There's an update in the standings !",
                            description=f"<@{str1}> : {score1}   <@{str2}> : {score2}",
                            color=discord.Color.green()
                        )
                        value = ""
                        score = ""
                        idx=1
                        for xx in problem_list:
                            proburl = "https://codeforces.com/contest/" + str(xx['contestId']) + "/problem/" + str(xx['index'])
                            if(xx['status'] == 0):
                                value += f"[{xx['name']}]({proburl})" + "\n" 
                                score += str(idx*100) + "\n";
                            else:
                                value += "this problem has been solved" + "\n" 
                                score += str(idx*100) + "\n";
                            idx += 1
                        embed.add_field(name='Score', value = score, inline = True)
                        embed.add_field(name="Problem", value = value, inline=True)
                        embed.set_footer(text=f"Remaining Time : {match_time-time_elapsed} minutes")                   
                        await text_channel.send(embed = embed)
                        continue
                index = index + 1
            response_API=requests.get(url2)
            data=response_API.text
            parse_json=json.loads(data)
            submissions=parse_json['result']
            index=1
            for x in problem_list:
                for y in submissions:
                    if(y['problem']['name']==x['name']and y['verdict']=="OK"and x['status']==0):
                        pc2 = max(pc2,index*100)
                        x['status']=1
                        score2=score2 + 100*index
                        embed = discord.Embed(
                            description=f"<@{str2}> has solved problem worth {100*index} points",
                            color=discord.Color.blue()
                        )
                        await text_channel.send(embed = embed)
                        embed = discord.Embed(
                            title="There's an update in the standings !",
                            description=f"<@{str1}> : {score1}   <@{str2}> : {score2}",
                            color=discord.Color.green()
                        )
                        value = ""
                        score = ""
                        idx = 1
                        for xx in problem_list:
                            proburl = "https://codeforces.com/contest/" + str(xx['contestId']) + "/problem/" + str(xx['index'])
                            if(xx['status'] == 0):
                                value += f"[{xx['name']}]({proburl})" + "\n" 
                                score += str(idx*100) + "\n";
                            else:
                                value += "this problem has been solved" + "\n" 
                                score += str(idx*100) + "\n";
                            idx += 1
                        embed.add_field(name='Score', value = score, inline = True)
                        embed.add_field(name="Problem", value = value, inline=True)
                        embed.set_footer(text=f"Remaining Time : {match_time-time_elapsed} minutes")                   
                        await text_channel.send(embed = embed)
                        continue
                index=index+1
            dic.update({"platform": "cf"})
        else:
            index = 1
            for x in problem_list:
                # print(x[0][-8:])
                if sing_status(x[0][-8:],player1["ac_handle"]) == 'AC' and x[1] == 0:
                    x[1]=1
                    score1+=100*index
                    pc1 = max(pc1,100*index)
                    embed = discord.Embed(
                            description=f"<@{str1}> has solved problem worth {100*index} points",
                            color=discord.Color.blue()
                        )
                    await text_channel.send(embed = embed)

                    embed = discord.Embed(
                        title="There's an update in the standings !",
                        description=f"<@{str1}> : {score1}   <@{str2}> : {score2}",
                        color=discord.Color.green()
                    )
                    value = ""
                    score = ""

                    index = 1
                    for xx in problem_list:
                        if(xx[1] == 0):
                            value += f"[Task {index}]({url+str(xx[0])})"+"\n" 
                            score += str(index*100) + "\n";
                        else:
                            value += "this problem has been solved" + "\n" 
                            score += str(index*100) + "\n";
                        index+=1

                    embed.add_field(name='Score', value = score, inline = True)
                    embed.add_field(name="Problem", value = value, inline=True)
                    embed.set_footer(text=f"Remaining Time : {match_time-time_elapsed} minutes")                   
                    await text_channel.send(embed = embed)
                    continue
                index=index+1

            index=1
            for x in problem_list:
                if sing_status(x[0][-8:],player2["ac_handle"]) == 'AC' and x[1] == 0:
                    x[1]=1
                    score2+=100*index
                    pc2 = max(pc2,100*index)
                    embed = discord.Embed(
                            description=f"<@{str2}> has solved problem worth {100*index} points",
                            color=discord.Color.blue()
                        )
                    await text_channel.send(embed = embed)
                    embed = discord.Embed(
                        title="There's an update in the standings !",
                        description=f"<@{str1}> : {score1}   <@{str2}> : {score2}",
                        color=discord.Color.green()
                    )
                    value = ""
                    score = ""
                    index = 1
                    for xx in problem_list:
                        if(xx[1] == 0):
                            value += f"[Task {index}]({url+str(xx[0])})"+"\n"  
                            score += str(index*100) + "\n";
                        else:
                            value += "this problem has been solved" + "\n" 
                            score += str(index*100) + "\n";
                        index=index+1
                    embed.add_field(name='Score', value = score, inline = True)
                    embed.add_field(name="Problem", value = value, inline=True)
                    embed.set_footer(text=f"Remaining Time : {match_time-time_elapsed} minutes")                   
                    await text_channel.send(embed = embed)
                    continue
                index=index+1
            dic.update({"platform":"ac"})

        
        dic.update({"Problems":problem_list})
        dic.update({"Scores":[score1,score2]})
        dic.update({"problem_rating":[pc1,pc2]})
        scores = [score1,score2]
        pc = [pc1,pc2]
        current_time=time.ctime()[11:19]
        hours=int(current_time[0:2])
        minutes=int(current_time[3:5])
        seconds=int(current_time[6:8])
        time_elapsed=(hours-hours_start)*60+(minutes-minutes_start)

        if(time_elapsed > match_time-1):
            print(time_elapsed)
            print(match_time)
            embed = discord.Embed(
                title="Time over!",
                description="The match is finished",
                color=discord.Color.red()
            )
            await text_channel.send(embed = embed)
            await stopMatch(ctx)
            return

        matches = current_matches.find_one({"server":ctx.guild.id})['matches']
        arr = []
        for var in matches[tourneyName]:
            if(var['channel_id'] == text_channel.id):
                var['Scores'] = scores
                var['Problems'] = problem_list
                var['problem_rating'] = pc
                var['platform'] = plt
                arr.append(var)
            else:
                arr.append(var)

        matches[tourneyName] = arr
        current_matches.update_one({"server": ctx.guild.id},{"$set":{"matches": matches}})

        all_solved = True
        if plt == 'ac':
            for x in problem_list:
                if(x[1] == 0):
                    all_solved = False
        else:
            for x in problem_list:
                if(x['status'] == 0):
                    all_solved = False

        if(all_solved):
            embed = discord.Embed(
                title="All problems have been solved !",
                description="The match is finished",
                color=discord.Color.red()
            )
            await text_channel.send(embed = embed)
            await stopMatch(ctx)
            return

        await asyncio.sleep(30)



#async functions

#Participants can register using this command
@client.command()
async def ac_registerMe(ctx, ac_handle="--"):
    thisServer = servers.find_one({"_id": ctx.guild.id})
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == ctx.channel.id:
            text_channel = x

    global tourneyName
    tourneyName = None
    for tournament in thisServer['tournaments']:
        if(thisServer['tournaments'][tournament]['text_channel'] == text_channel.id):
            tourneyName = tournament

    if tourneyName == None:
        embed = discord.Embed(
            title="No Tourney",
            description=f"{ctx.author.mention} there is no ongoing tournament in this channel",
            color=discord.Color.gold()
        )
        await text_channel.send(embed=embed)
        return

    checkForStartTourney = thisServer['tournaments'][tourneyName]['tourney_status']

    if(ac_handle == "--"):
        embed = discord.Embed(
            title="Invalid command!",
            description="Please specify the ac handle.",
            color=discord.Color.gold()
        )
        await text_channel.send(embed=embed)
        return

    if checkForStartTourney == True:
        embed = discord.Embed(
            title="Tournament Already Started",
            description="Tounament has already started so nothing can be changed.",
            color=discord.Color.gold()
        )
        await text_channel.send(embed=embed)
        return

    flag = False
    participantsListTemp = participantsList.find_one({"server": ctx.guild.id})
    for x in participantsListTemp["contestants"][tourneyName]:
        if x['id'] == ctx.author.id:
            flag = True
        if x['ac_handle'] == ac_handle:
            embed = discord.Embed(
                title="Already Registered",
                description=f"{ctx.author.mention} This handle has already been registered by another person"
                "Please register using another perviously unregistered handle!",
                color=discord.Color.gold()
            )
            await text_channel.send(embed=embed)
            return
        if x['id'] == ctx.author.id and x['ac_handle'] != '--':
            embed = discord.Embed(
                title="Already Registered",
                description=f"{ctx.author.mention} you are already registered, please wait till tournament"
                            f" is started. If trying to change your"
                            f"seed then first unregister yourself then again register.",
                color=discord.Color.gold()
            )
            await text_channel.send(embed=embed)
            return
    if not flag:
        embed = discord.Embed(
                title="Invalid Command",
                description=f"{ctx.author.mention} Please register your cf_handle first and then register your "
                "ac_handle!",
                color=discord.Color.gold()
            )
        await text_channel.send(embed=embed)
        return


    maxR = 0
    uri = 'https://atcoder.jp/users/' + ac_handle
    response = requests.get(uri)
    soup = BeautifulSoup(response.content, 'html.parser')
    Text = soup.body
    main = Text.find("table",class_ = "dl-table mt-2")

    if main == None:
        embed = discord.Embed(
            title="Invalid ac handle!",
            description="Please check your ac handle.",
            color=discord.Color.gold()
        )
        await text_channel.send(embed=embed)
        return

    ## validate account
    embed = discord.Embed(
        title="Validate your account within 1 minute",
        description=f"{ctx.author.mention}",
        color=discord.Color.gold()
    )

    val_string = ''.join(random.choices(string.ascii_lowercase, k=10))
    embed.add_field(name="Please change your Affiliation", value=val_string)
    await text_channel.send(embed=embed)
    
    if not (ac_validate_acc(ac_handle, val_string)):
        embed = discord.Embed(
            title="Validation failed!",
            description=f"{ctx.author.mention}",
            color=discord.Color.gold()
        )
        embed.add_field(name="Please try to register again")
        await text_channel.send(embed=embed)
        return

    ind = main.text.index("Highest")
    s = ''
    for i in main.text[ind+len("Highest rating"):]:
        if i == '―':
            break
        s += i
    maxR = int(s)
    contestants_ = participantsList.find_one({"server": ctx.guild.id})['contestants']
    for i in contestants_[tourneyName]:
        if i["id"] == ctx.author.id:
            i["ac_handle"] = ac_handle
            i["ac_maxR"] = maxR
    participantsList.update_one({"server": ctx.guild.id},
                                {"$set": {"contestants": contestants_}})


    embed = discord.Embed(
        title="Registration successfull!",
        description=f"{ctx.author.mention}",
        color=discord.Color.gold()
    )
    embed.add_field(name="Ac_Handle", value=ac_handle, inline=True)
    embed.add_field(name="Max_Rating", value=maxR)
    embed.set_footer(text = "If the above details are incorrect, unregister yourself and then register again.")
    await text_channel.send(embed=embed)

###########################################################################################################################
#                                                CODEFORCES
###########################################################################################################################

#Give updates on the status of a match using discord command
@client.command()
async def matchUpdates(ctx):
    thisServer = servers.find_one({"_id": ctx.guild.id})
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == ctx.channel.id:
            text_channel = x

    global tourneyName
    tourneyName = None
    for tournament in thisServer['tournaments']:
        if(text_channel.id in thisServer['tournaments'][tournament]['match_channels']):
            tourneyName = tournament

    if(tourneyName == None):
        embed = discord.Embed(
            title="This channel is not registered for hosting any match!",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return
        

    matches = current_matches.find_one({"server": ctx.guild.id})["matches"][tourneyName]

    for match in matches:
        if(match["channel_id"] == text_channel.id):
            current_time=time.ctime()[11:19]
            hours=int(current_time[0:2])
            minutes=int(current_time[3:5])
            time_elapsed=(hours-match["Start_Time"][0])*60+(minutes-match["Start_Time"][1])
            score1,score2=match["Scores"][0],match["Scores"][1]
            id1,id2=match['player1']['id'],match['player2']['id']
            plt = match["platform"]
            embed=discord.Embed(
                title="Match_Updates",
                description=f"<@{id1}> : {score1}   <@{id2}> : {score2}",
                color=discord.Color.green()
            )
            index=1
            value = ""
            score = ""
            if plt == 'cf':
                for x in match["Problems"]:
                    proburl = "https://codeforces.com/contest/" + str(x['contestId']) + "/problem/" + str(x['index'])
                    if(x['status'] == 0):
                        value += f"[{x['name']}]({proburl})" + "\n" 
                        score += str(index*100) + "\n";
                    else:
                        value += "this problem has been solved" + "\n" 
                        score += str(index*100) + "\n";
                    index=index+1
            else:
                url = 'https://atcoder.jp/contests/'
                for x in match["Problems"]:
                    if(x[1] == 0):
                        value += f"[Task {index}]({url+str(x[0])})"+"\n" 
                        score += str(index*100) + "\n";
                    else:
                        value += "this problem has been solved" + "\n" 
                        score += str(index*100) + "\n";
                    index=index+1

            embed.add_field(name='Score', value = score, inline = True)
            embed.add_field(name="Problem", value = value, inline=True)
            embed.set_footer(text=f"Remaining Time : {match['Match_duration']-time_elapsed} minutes")
            await text_channel.send(embed=embed)
            return
    
    embed=discord.Embed(
        title="No live match in this channel !",
        color=discord.Color.red()
    )
    await text_channel.send(embed=embed)
    return
    
#Prepares the database for tournaments in a new server
@client.event
async def on_guild_join(guild):
    res = servers.find_one({"_id": guild.id})
    if res is None:
        text_channel = guild.text_channels[0]
        servers.insert_one({"_id": guild.id,
                            "tournaments": {},
                            "text_channel": text_channel.id})
        current_matches.insert_one({"server": guild.id,
                                    "matches": {}})
        participantsList.insert_one({"server": guild.id,
                                    "contestants": {}})
        storage.insert_one({"server": guild.id,
                            "storage": {}})            
        embed = discord.Embed(title="Lockout Bot Added Successfully ! :crossed_swords:",
                              description="You are now ready to organise tournaments", color=0xffa800)
        embed.set_thumbnail(
            url="https://cdn-icons-png.flaticon.com/512/1355/1355961.png")
        embed.add_field(name="Bot Name", value="Lockout Bot", inline=True)
        embed.add_field(name="Nick Name", value="Tatakae", inline=True)
        await text_channel.send(embed=embed)


@client.command()
@commands.has_role('Tourney-manager')
async def channel(ctx, text_channel: discord.TextChannel):
    global prev_channel
    prev = servers.find_one({"_id": ctx.guild.id})["text_channel"]
    servers.update_one({"_id": ctx.guild.id}, {"$set": {"text_channel": text_channel.id}})
    for x in ctx.guild.text_channels:
        if x.id == prev:
            prev_channel = x


    if prev == text_channel.id:
        embed = discord.Embed(
            title="Channel Changed",
            description=f"I am already in this channel",
            color=discord.Color.gold()
        )
        await text_channel.send(embed=embed)
        return

    embed = discord.Embed(
        title="Channel Changed",
        description=f"Bot's channel changed to {text_channel.mention}",
        color=discord.Color.gold()
    )
    embed2 = discord.Embed(
        title="Channel Changed",
        description=f"Bot's channel changed to {text_channel.mention}",
        color=discord.Color.gold()
    )
    await text_channel.send(embed=embed)
    await prev_channel.send(embed=embed2)


#Starts the registrations for a tournament
@client.command()
@commands.has_role('Tourney-manager')
async def startRegister(ctx, text_channel: discord.TextChannel, tourneyName = "--"):
    thisServer = servers.find_one({"_id": ctx.guild.id})
    text_channel_n = thisServer["text_channel"]
    global home_channel
    for x in ctx.guild.text_channels:
        if x.id == text_channel_n:
            home_channel = x

    if(ctx.channel.id != text_channel_n):
        embed = discord.Embed(
            title="Bot not registered in this channel !",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if(tourneyName == "--"):
        embed = discord.Embed(
            title="Invalid command! :x:",
            description="please specify tournament name",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)
        return

    flag = False
    tournaments =  servers.find_one({"_id": ctx.guild.id})['tournaments']
    for tournament in tournaments:
        if(tournaments[tournament]['text_channel'] == text_channel.id):
            embed = discord.Embed(
                title="Tournament already running in given channel !",
                description="you can start a new tournament only after current one ends",
                color=discord.Color.red()
            )
            await home_channel.send(embed=embed)
            return
        
        if(tournament == tourneyName):
            flag = True

    if(flag):
        embed = discord.Embed(
            title="Tournament name should be unique !",
            description="there exists a tournament with the same name so please try again with a new name",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)
        return

    tournaments[tourneyName] = {
        "text_channel": text_channel.id,
        "tourney_status": False,
        "current_round": None,
        "match_channels": []
    }

    servers.update_one({"_id": ctx.guild.id}, {
                        "$set": {"tournaments": tournaments}})


    parts_ = participantsList.find_one({"server": ctx.guild.id})['contestants']
    parts_[tourneyName] = []
    participantsList.update_one({"server": ctx.guild.id},
                                {"$set": {'contestants': parts_}})

    current_ = current_matches.find_one({"server": ctx.guild.id})['matches']
    current_[tourneyName] = []
    current_matches.update_one({"server": ctx.guild.id},
                                {"$set": {'matches': current_}})
    
    storage_ = storage.find_one({"server": ctx.guild.id})['storage']
    storage_[tourneyName] = []
    storage.update_one({"server": ctx.guild.id},
                        {"$set": {'storage': storage_}})

    embed = discord.Embed(
        title="Tournament Started :crossed_swords:",
        description=f"Participants can register their cf account with **!registerMe <cf_handle>** and ac account with **!ac_registerMe <ac_handle>**",
        color=discord.Color.gold()
    )

    embed2 = discord.Embed(
        title=f"Tournament **{tourneyName}** started :crossed_swords:",
        color=discord.Color.gold()
    )

    embed.set_author(name=botName)
    await text_channel.send(embed=embed)
    await home_channel.send(embed=embed2)



#Officially starts the tournament with matchups
@client.command()
@commands.has_role('Tourney-manager')
async def startTourney(ctx, tourneyName= "--"):

    thisServer = servers.find_one({"_id": ctx.guild.id})
    text_channel_n = thisServer["text_channel"]
    global home_channel
    for x in ctx.guild.text_channels:
        if x.id == text_channel_n:
            home_channel = x
        
    if(ctx.channel.id != text_channel_n):
        embed = discord.Embed(
            title="Tourney-manager not registered in this channel !",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if(tourneyName == "--"):
        embed = discord.Embed(
            title="Invalid command! :x:",
            description="please specify tournament name",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)
        return

    tournaments = thisServer['tournaments']
    global checkForStartTourney
    flag = False
    for i in tournaments:
        if(i == tourneyName):
            flag = True
            checkForStartTourney = tournaments[tourneyName]['tourney_status']

    if not flag:
        embed = discord.Embed( 
            title=f"Tournament {tourneyName} does not exist!",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)

    if checkForStartTourney == True:
        embed = discord.Embed( 
            title="Tournament Already Started",
            color=discord.Color.red()
        )
        embed.set_author(name=botName)
        await home_channel.send(embed=embed)
        return

    
    if len(participantsList.find_one({"server": ctx.guild.id})['contestants'][tourneyName]) == 0:
        embed = discord.Embed(
            title="No registrations",
            description="No participants registered, cannot start the Tourney. Participants can register their cf accont using !registerMe <cf_handle> and ac accound using !ac_registerMe <ac_handle>",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)
        return

    if len(participantsList.find_one({"server": ctx.guild.id})['contestants'][tourneyName]) == 1:
        embed = discord.Embed(
            title="Single registrant",
            description="Cannot start a tourney with a single participant.",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)
        return

    text_channel_n2 = thisServer['tournaments'][tourneyName]['text_channel']
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == text_channel_n2:
            text_channel = x

    tournaments[tourneyName]['tourney_status'] = True
    tournaments[tourneyName]['current_round'] = 1
    
    match_builder(ctx,tourneyName)

    servers.update_one({"_id": ctx.guild.id},{
                        "$set": {"tournaments": tournaments}})

    embed = discord.Embed(
        title=f"Tourney started :D",
        description=f"The tourney {tourneyName} has started.",
        color=discord.Color.green()
    )
    await text_channel.send(embed=embed)
    await home_channel.send(embed=embed)


@client.command()
@commands.has_role('Tourney-manager')
async def matchChannel(ctx, text_channel: discord.TextChannel, tourneyName= "--"):

    thisServer = servers.find_one({"_id": ctx.guild.id})
    text_channel_n = thisServer["text_channel"]
    global home_channel
    for x in ctx.guild.text_channels:
        if x.id == text_channel_n:
            home_channel = x
        
    if(ctx.channel.id != text_channel_n):
        embed = discord.Embed(
            title="Tourney-manager not registered in this channel !",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if(tourneyName == "--"):
        embed = discord.Embed(
            title="Invalid command! :x:",
            description="please specify tournament name",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)
        return

    tournaments = thisServer['tournaments']
    flag = False
    for i in tournaments:
        if(text_channel.id in tournaments[i]['match_channels'] or text_channel.id == tournaments[i]['text_channel']):
            flag = True

    if flag:
        embed = discord.Embed( 
            title=f"Channel already registered for tournament!",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)
        return

    flag = False
    for i in tournaments:
        if(i == tourneyName):
            flag = True

    if not flag:
        embed = discord.Embed( 
            title=f"Tournament {tourneyName} does not exist !",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)
        return


    tournaments =  servers.find_one({"_id": ctx.guild.id})['tournaments']
    tournaments[tourneyName]['match_channels'].append(text_channel.id)

    servers.update_one({"_id": ctx.guild.id}, {
                        "$set": {"tournaments": tournaments}})

    embed = discord.Embed(
        title="Channel registered for matches !",
        description=f"Tournament : {tourneyName}",
        color=discord.Color.gold()
    )

    embed2 = discord.Embed(
        title=f"Channel #{text_channel} registered for tournament {tourneyName} !",
        color=discord.Color.gold()
    )

    await text_channel.send(embed=embed)
    await home_channel.send(embed=embed2)


@client.command()
@commands.has_role('Tourney-manager')
async def unRegMatchChannel(ctx, text_channel: discord.TextChannel):

    thisServer = servers.find_one({"_id": ctx.guild.id})
    text_channel_n = thisServer["text_channel"]
    global home_channel
    for x in ctx.guild.text_channels:
        if x.id == text_channel_n:
            home_channel = x
        
    if(ctx.channel.id != text_channel_n):
        embed = discord.Embed(
            title="Tourney-manager not registered in this channel !",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    tournaments = thisServer['tournaments']
    global tourneyName
    flag = False
    for i in tournaments:
        if(text_channel.id in tournaments[i]['match_channels']):
            tourneyName = i
            flag = True

    if not flag:
        embed = discord.Embed( 
            title=f"Channel not registered for any tournament match!",
            color=discord.Color.gold()
        )
        await home_channel.send(embed=embed)
        return

    tournaments =  servers.find_one({"_id": ctx.guild.id})['tournaments']
    tournaments[tourneyName]['match_channels'].remove(text_channel.id)

    servers.update_one({"_id": ctx.guild.id}, {
                        "$set": {"tournaments": tournaments}})

    embed = discord.Embed(
        title="Channel unregistered !",
        description=f"you can register the given channel for new tournament matches",
        color=discord.Color.green()
    )

    await home_channel.send(embed=embed)


@client.command()
@commands.has_role('Tourney-manager')
async def stopTourney(ctx, tourneyName= "--"):

    thisServer = servers.find_one({"_id": ctx.guild.id})
    text_channel_n = thisServer["text_channel"]
    global home_channel
    for x in ctx.guild.text_channels:
        if x.id == text_channel_n:
            home_channel = x
        
    if(ctx.channel.id != text_channel_n):
        embed = discord.Embed(
            title="Tourney-manager not registered in this channel !",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if(tourneyName == "--"):
        embed = discord.Embed(
            title="Invalid command! :x:",
            description="please specify tournament name",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)
        return

    tournaments = thisServer['tournaments']
    flag = False
    for i in tournaments:
        if(i == tourneyName):
            flag = True

    if not flag:
        embed = discord.Embed( 
            title=f"Tournament {tourneyName} does not exist !",
            color=discord.Color.red()
        )
        await home_channel.send(embed=embed)
        return

    text_channel_n2 = thisServer['tournaments'][tourneyName]['text_channel']
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == text_channel_n2:
            text_channel = x

    if thisServer['tournaments'][tourneyName]["current_round"] != "finished":
        embed = discord.Embed(
            title="Tourney stopped :(",
            description=f"The tourney **{tourneyName}** has been stopped.",
            color=discord.Color.red()
        )

    else:
        round = storage.find_one({"server": ctx.guild.id})['storage'][tourneyName]
        last_match = round[-1]["matches"]
        part = participantsList.find_one({"server": ctx.guild.id})['contestants'][tourneyName]
        var = None
        avatar = None
        for i in part:
            if(i == last_match[0]["winner"]):
                var = i["id"]
                avatar = i["avatar"]
        embed = discord.Embed(
            title="Tournament finished :first_place:",
            description=f"Congratulations! <@{var}> you have won the tournament GG",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url = avatar)
    
    await text_channel.send(embed=embed)
    embed2 = discord.Embed(
        title=f"Tourney {tourneyName} stopped!",
        color=discord.Color.dark_purple()
    )
    await home_channel.send(embed=embed2)


    server_ = servers.find_one({"_id": ctx.guild.id})['tournaments']
    del server_[tourneyName]
    servers.update_one({"_id": ctx.guild.id}, {"$set": {"tournaments": server_}})

    storage_ = storage.find_one({"server": ctx.guild.id})['storage']
    del storage_[tourneyName]
    storage.update_one({"server":ctx.guild.id},{"$set":{"storage": storage_}})

    part_ = participantsList.find_one({"server": ctx.guild.id})['contestants']
    del part_[tourneyName]
    participantsList.update_one({"server":ctx.guild.id},{"$set":{"contestants": part_}})

    current_ = current_matches.find_one({"server": ctx.guild.id})['matches']
    del current_[tourneyName]
    current_matches.update_one({"server": ctx.guild.id},{"$set":{"matches": current_}})



@client.command()
async def show(ctx):
    thisServer = servers.find_one({"_id": ctx.guild.id})
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == ctx.channel.id:
            text_channel = x

    global tourneyName
    for tournament in thisServer['tournaments']:
        if(thisServer['tournaments'][tournament]['text_channel'] == text_channel.id or text_channel.id in thisServer['tournaments'][tournament]['match_channels']):
            tourneyName = tournament

    if(tourneyName == None):
        embed = discord.Embed(
            title="This channel is not registered with any tournament",
            color=discord.Color.gold()
        )
        await text_channel.send(embed=embed)
        
 
    current_round = thisServer['tournaments'][tourneyName]["current_round"]


    if(current_round == None):
        embed = discord.Embed(
            title="Tournament has not started yet !",
            color=discord.Color.purple()
        )
    else:
        embed = discord.Embed(
            title=f"Tournament: {tourneyName} ",
            description=f"Current round: **{current_round}**",
            color=discord.Color.purple()
        )
    
    await text_channel.send(embed=embed)





#Player match maker, matches the players based on different criteria
def match_builder(ctx,tourneyName):
    part_ = participantsList.find_one({"server": ctx.guild.id})['contestants'][tourneyName]
    participants = sorted(part_, key=lambda d: (-1)*d['maxRating'])
    player_count = len(participants)

    var = int(math.log2(player_count))
    temp = player_count - 2**var
    lista = []
    for j in range(2**var - temp):
        lista.append([participants[j]])
    for j in range(2**var - temp + 1, 2**var + 1):
        if(j%2 == 0):
            lista.append([[participants[player_count-j+2**var - temp],participants[j-1]]])
        else:
            lista.append([[participants[j-1],participants[player_count-j+2**var - temp]]])
    while(len(lista) != 1):
        templist = []
        for j in range(int(len(lista)/2)):
            templist.append(lista[j] + lista[-j - 1][::-1])
        lista = templist
    lista = lista[0]
    for i in lista:
        if(len(i) == 2):
            print(i[0]['cf_handle'],i[1]['cf_handle'])
        else:
            print(i['cf_handle'])


    matches_ = []
    if(temp > 0):
        
        playersone = []
        matchesone = []
        for i in range(len(lista)):
            if(len(lista[i]) == 2):
                playersone.append(lista[i][0])
                playersone.append(lista[i][1])
                matchesone.append({"next_index": i})

        for i in range(int(len(playersone)/2)):
            matchesone[i]['player1'] = playersone[2*i]
            matchesone[i]['player2'] = playersone[2*i + 1]
            matchesone[i]['winner'] = None
            matchesone[i]['status'] = False
        
        matches_.append({"players": playersone, "matches": matchesone})
        print(matches_)

        playersone = []
        matchesone = []
        for i in range(len(lista)):
            if(len(lista[i]) == 2):
                playersone.append("TBD")
            else:
                playersone.append(lista[i])
        
        for i in range(int(len(playersone)/2)):
            dic = {}
            dic['player1'] = playersone[2*i]
            dic['player2'] = playersone[2*i + 1]
            dic['winner'] = None
            dic['status'] = False
            dic['next_index'] = i
            matchesone.append(dic)
        
        matches_.append({"players": playersone, "matches": matchesone})

        for i in range(1,var):
            c = 2**(var - i)
            playersone = []
            matchesone = []
            for j in range(c):
                playersone.append("TBD")
            for j in range(int(c/2)):
                dic = {}
                dic['player1'] = playersone[2*j]
                dic['player2'] = playersone[2*j + 1]
                dic['winner'] = None
                dic['status'] = False
                dic['next_index'] = i
                matchesone.append(dic)
            
        matches_.append({"players": playersone, "matches": matchesone})



    else:
        matches_ = []

        playersone = []
        matchesone = []
        for i in range(len(lista)):
            playersone.append(lista[i])

        for i in range(int(len(lista)/2)):
            dic = {}
            dic['player1'] = playersone[2*i]
            dic['player2'] = playersone[2*i + 1]
            dic['winner'] = None
            dic['status'] = False
            dic['next_index'] = i
            matchesone.append(dic)

        matches_.append({"players": playersone, "matches": matchesone})

        for i in range(1,var):
            c = 2**(var - i)
            playersone = []
            matchesone = []
            for j in range(c):
                playersone.append("TBD")
            for j in range(int(c/2)):
                dic = {}
                dic['player1'] = playersone[2*j]
                dic['player2'] = playersone[2*j + 1]
                dic['winner'] = None
                dic['status'] = False
                dic['next_index'] = i
                matchesone.append(dic)
            
            matches_.append({"players": playersone, "matches": matchesone})

    storage_ = storage.find_one({"server": ctx.guild.id})['storage']
    storage_[tourneyName] = matches_
    storage.update_one({"server": ctx.guild.id},{"$set":{"storage":storage_}})




#Start a match between two players
#Only if they have a match in the current round

@client.command()
@commands.has_role('Tourney-manager')
async def startMatch(ctx, player_1, player_2, rting: str):
    thisServer = servers.find_one({"_id": ctx.guild.id})
    for x in ctx.guild.text_channels:
        if x.id == ctx.channel.id:
            text_channel = x

    global tourneyName
    tourneyName = None
    for tournament in thisServer['tournaments']:
        if(text_channel.id in thisServer['tournaments'][tournament]['match_channels']):
            tourneyName = tournament

    if(tourneyName == None):
        embed = discord.Embed(
            title="This channel is not registered for hosting any match!",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    cr = thisServer['tournaments'][tourneyName]['current_round']

    if(cr == "finished"):
        embed = discord.Embed(
            title="The tournament is already over !",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return
    

    match_list=current_matches.find_one({"server":ctx.guild.id})['matches'][tourneyName]
    dic={}

    str1 = player_1[2:len(player_1)-1]
    str2 = player_2[2:len(player_2)-1]
    player1 = None
    player2 = None
    participants = participantsList.find_one({"server": ctx.guild.id})["contestants"][tourneyName]

    for i in participants:
        if(str1 == str(i["id"])):
            player1 = i
        if(str2 == str(i["id"])):
            player2 = i
        
    dic.update({"player1": player1})
    dic.update({"player2": player2})

    if player1 == None or player2 == None:
        embed = discord.Embed(
            title="Unregistered User!",
            description="One or both of the above users haven't even been registered for the tournament",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    if(player1['id']==player2['id']):
        embed = discord.Embed(
            title="Error!",
            description="Both Players can't be same",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    flag=False
    ac_check = True
    curr_round = servers.find_one({"_id": ctx.guild.id})['tournaments'][tourneyName]["current_round"]
    current_round_matches=storage.find_one({"server": ctx.guild.id})["storage"][tourneyName][curr_round - 1]["matches"]

    for match in current_round_matches:
        if((player1==match["player1"] and player2==match["player2"]) or (player1==match["player2"] and player2==match["player1"])):
            if player1["ac_handle"] == '--' or player2["ac_handle"] == '--':
                ac_check = False
            flag=True
            break

    if(flag==False):
        embed = discord.Embed(
            title="Error!",
            description="Mentioned Players don't have a match in current round, check again",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    flag=False
    xd = current_matches.find_one({"server":ctx.guild.id})["matches"][tourneyName]
    newxd = []
    for match in xd:
        if((player1==match["player1"] and player2==match["player2"]) or (player1==match["player2"] and player2==match["player1"])):
            flag=True
            # print(1)
        else:
            newxd.append(match)
            # print(2)

    if(flag):
        mat = current_matches.find_one({"server":ctx.guild.id})["matches"]
        print(newxd)
        # if(len(newxd) == 0):
        #     mat[tourneyName] = []
        # else:
        #     mat[tourneyName] = newxd
        del mat[tourneyName]
        mat[tourneyName] = newxd
        match_list = newxd
        # mat.update({tourneyName: newxd})
            
        current_matches.update_one({"server":ctx.guild.id},{"$set":{"matches":mat}})
        print(10)

    if not ac_check and not(rting.isdigit()):
        embed=discord.Embed(
        title="Inavlid Command",
        description=f"One or both of the players do not have their ac_handle registered. Please have your contest on a codeforces problemset:) ",
        color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    #set time for match
    match_time = 0
    embed=discord.Embed(
        title="Please enter duration of match in minutes [10 - 180]:",
        color=discord.Color.green()
        )
    await text_channel.send(embed=embed)

    def check(msg):
        return (msg.channel == text_channel and ctx.message.author == msg.author)

    try:
        reply_message = await client.wait_for('message', check=check, timeout=15)
    except asyncio.TimeoutError:
        await text_channel.send('You ran out of time to answer!')
        return
    else:
        if reply_message.content.isnumeric():
            mins = int(reply_message.content)
            if not (mins>=10 and mins<=180):
                await text_channel.send('Invalid duration. Please enter a number between 10 and 180.')
                return
            else:
                match_time = mins
        else:
            await text_channel.send('Invalid format. Please enter a number next time.')
            return

    if rting.isdigit():
        rating = int(rting)
        tags=["implementation","dp","graphs","constructive algorithms","greedy","math","binary search","number theory","sortings"]
        random.shuffle(tags)
        url = f"https://codeforces.com/api/problemset.problems?{tags[0]}"
        # url = f"https://codeforces.com/api/problemset.problems?implementation"

        response_API = requests.get(url)
        data = response_API.text
        parse_json = json.loads(data)
        if(parse_json['status'] != "OK"):
            embed=discord.Embed(
                title="CF API caused an error",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        problems = parse_json['result']['problems']

        random.shuffle(problems)
        problem_list = []
        scores = [0,0]
        pc = [0,0]
        c = 0
        for i in problems:  
            if(i.get('rating') == rating and unsolved_checker(i["contestId"], i["index"], player1['cf_handle']) and unsolved_checker(i["contestId"], i["index"], player2['cf_handle']) ):
                i['status']=0
                problem_list.append(i)
                rating += 100
                c += 1
            if(c == 5):
                break
        embed = discord.Embed(
            title="Problem for this match",
            description=f"<@{str1}> : 0  vs <@{str2}> : 0",
            color=discord.Color.green()
        )
        index=1
        value = ""
        score = ""
        for x in problem_list:
            proburl = "https://codeforces.com/contest/" + str(x['contestId']) + "/problem/" + str(x['index'])
            if(x['status'] == 0):
                value += f"[{x['name']}]({proburl})" + "\n" 
                score += str(index*100) + "\n"
            else:
                value += "this problem has been solved" + "\n" 
                score += str(index*100) + "\n"
            index=index+1
        dic.update({"platform": "cf"})
    else:
        url = 'https://atcoder.jp/contests/'
        diff = rting
        x = 'beginner'
        if diff.lower() == 'easy':
            x = 'beginner'
        elif diff.lower() == 'medium':
            x = 'regular'
        elif diff.lower() == 'hard':
            x = 'grand'

        problem_list = []
        scores = [0,0]
        pc = [0,0]

        for i in 'abcde':
            words = [x,i]
            link = ac_probs(words,player1['ac_handle'],player2['ac_handle'])
            problem_list.append([link,0])

        embed = discord.Embed(
            title="Problem for this match",
            description=f"<@{str1}> : 0  vs <@{str2}> : 0",
            color=discord.Color.green()
        )

        index=1
        value = ""
        score = ""
        for x in problem_list:
            if(x[1] == 0):
                value += f"[Task {index}]({url+str(x[0])})"+"\n" 
                score += str(index*100) + "\n";
            else:
                value += "this problem has been solved" + "\n" 
                score += str(index*100) + "\n";
            index=index+1
        dic.update({"platform":"ac"})
        
    embed.add_field(name='Score', value = score, inline = True)
    embed.add_field(name="Problem", value = value, inline=True)               
    embed.set_footer(text=f"You have {match_time} minutes to solve the questions :)")
    dic.update({"Problems":problem_list})
    dic.update({"Scores":scores})
    dic.update({"channel_id": ctx.channel.id})
    dic.update({"status": "live"})
    dic.update({"problem_rating": pc})
    print(text_channel)
    start_time=time.ctime()[11:19]
    hours_start=int(start_time[0:2])
    minutes_start=int(start_time[3:5])
    seconds_start=int(start_time[6:8])
    dic.update({"Start_Time":[hours_start,minutes_start,seconds_start]})
    dic.update({"Match_duration":match_time})
    match_list.append(dic)

    curr_ = current_matches.find_one({"server": ctx.guild.id})['matches']
    curr_[tourneyName] = match_list
    current_matches.update_one({"server":ctx.guild.id},{"$set":{"matches":curr_}})
    await ctx.send(embed=embed)

    task1 = asyncio.create_task(matchLive(ctx,str1,str2,dic,url,match_time))
    await task1  
    

#Display the list of participants 
@client.command()
async def showParticipants(ctx):
    thisServer = servers.find_one({"_id": ctx.guild.id})
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == ctx.channel.id:
            text_channel = x

    global tourneyName
    tourneyName = None
    for tournament in thisServer['tournaments']:
        if(thisServer['tournaments'][tournament]['text_channel'] == text_channel.id):
            tourneyName = tournament

    if(tourneyName == None):
        embed = discord.Embed(
            title="This channel is not registered for any tournament updates!",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    p_list=participantsList.find_one({"server":ctx.guild.id})['contestants'][tourneyName]

    if(len(p_list) == 0):
        embed = discord.Embed(
            title="No participants registered yet!",
            color=discord.Color.purple()
        )
        await text_channel.send(embed=embed)
        return

    embed=discord.Embed(title=f"Tournament : **{tourneyName}**",description=f"Total participants : {len(p_list)}",color=discord.Color.purple())
    tags = ""
    cfids = ""
    maxratings = ""
    acfids = ""
    for i in range(min(20,len(p_list))):
        tags += f"<@{str(p_list[i]['id'])}>" + "\n"
        cfids += f"{p_list[i]['cf_handle']} ({p_list[i]['maxRating']})" + "\n"
        acfids += f"{p_list[i]['ac_handle']}  ({p_list[i]['ac_maxR']})" + "\n"

    embed.add_field(name=" Tag",value=tags,inline=True)
    embed.add_field(name="Codeforces",value=cfids,inline=True)
    embed.add_field(name="Atcoder",value=acfids,inline=True)
    await text_channel.send(embed=embed)


#Stops the match when a moderator gives the command to do so
@client.command()
@commands.has_role('Tourney-manager')
async def stopMatch(ctx):
    thisServer = servers.find_one({"_id": ctx.guild.id})
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == ctx.channel.id:
            text_channel = x

    global tourneyName
    tourneyName = None
    for tournament in thisServer['tournaments']:
        if(text_channel.id in thisServer['tournaments'][tournament]['match_channels']):
                tourneyName = tournament

    if(tourneyName == None):
        embed = discord.Embed(
            title="This channel is not registered for hosting any match!",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    global home_channel
    for x in ctx.guild.text_channels:
        if x.id == thisServer['tournaments'][tourneyName]['text_channel']:
            home_channel = x

    match_list=current_matches.find_one({"server": ctx.guild.id})['matches'][tourneyName]

    flag = False
    for i in match_list:
        if(i['channel_id'] == text_channel.id):
            flag = True

    if not flag:
        embed = discord.Embed(
            title="No live match in this channel !",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    player1 = None
    player2 = None

    for i in match_list:
        if(i["channel_id"] ==text_channel.id):
            player1,player2 = i['player1'],i['player2']

    winner = None
    temp = []
    for i in match_list:
        if(i['player1'] == player1 and i['player2'] == player2):
            if(i["Scores"][0] > i["Scores"][1]):
                winner = player1
            elif(i["Scores"][0] == 0 and i["Scores"][1] == 0):
                if(player1['maxRating'] > player2['maxRating']):
                    winner = player1
                else:
                    winner = player2
            elif(i["Scores"][0] ==  i["Scores"][1]):
                if(i["problem_rating"][0] > i["problem_rating"][1]):
                    winner = player1
                else:
                    winner = player2
            else:
                winner = player2

        elif(i['player1'] == player2 and i['player2'] == player1):
            if(i["Scores"][0] > i["Scores"][1]):
                winner = player2
            elif(i["Scores"][0] == 0 and i["Scores"][1] == 0):
                if(player1['maxRating'] > player2['maxRating']):
                    winner = player1
                else:
                    winner = player2
            elif(i["Scores"][0] ==  i["Scores"][1]):
                if(i["problem_rating"][0] < i["problem_rating"][1]):
                    winner = player1
                else:
                    winner = player2
            else:
                winner = player1
        else:
            temp.append(i)

    curr_ = current_matches.find_one({"server": ctx.guild.id})['matches']
    curr_[tourneyName] = temp
    current_matches.update_one({"server": ctx.guild.id}, {"$set":{"matches": curr_}})


    curr_round = servers.find_one({"_id": ctx.guild.id})['tournaments'][tourneyName]['current_round']

    rounds = storage.find_one({"server": ctx.guild.id})["storage"][tourneyName]

    embed = None

    if(curr_round == len(rounds)):
        
        embed = discord.Embed(
            title="Congratulations ! :first_place:",
            description=f"<@{winner['id']}> you have won this round",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        emb = discord.Embed(
                title=f"Round {curr_round} has finished !",
                color=discord.Color.purple(),
        )

        await text_channel.send(embed = emb)
        await home_channel.send(embed = emb)
        

        rounds[-1]["matches"][0]["status"] = True
        rounds[-1]["matches"][0]["winner"] = winner

        storage_ = storage.find_one({"server": ctx.guild.id})['storage']
        storage_[tourneyName] = rounds
        storage.update_one({"server": ctx.guild.id}, {"$set":{"storage": storage_}})

        tournaments = servers.find_one({"_id": ctx.guild.id})['tournaments']
        tournaments[tourneyName]['current_round'] = "finished"
        servers.update_one({"_id": ctx.guild.id},{"$set":{'tournaments': tournaments}})

        curr_ = current_matches.find_one({"server": ctx.guild.id})['matches']
        curr_[tourneyName] = []
        current_matches.update_one({"server": ctx.guild.id},{"$set":{"matches": curr_}})

        await roundStatus(ctx, curr_round)

    
    else:
        embed = discord.Embed(
            title="Congratulations ! :first_place: ",
            description=f"<@{winner['id']}> you have won this round",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        matches = rounds[curr_round-1]["matches"]
        for i in range(len(matches)):
            if((matches[i]["player1"] == player1 and matches[i]["player2"] == player2) or ((matches[i]["player1"] == player2 and matches[i]["player2"] == player1))):
                rounds[curr_round-1]["matches"][i]["status"] = True
                rounds[curr_round-1]["matches"][i]["winner"] = winner
                nextIndex = rounds[curr_round-1]["matches"][i]["next_index"]
                rounds[curr_round]["players"][nextIndex] = winner
                rounds[curr_round]["matches"][int(nextIndex/2)]["player" + str(nextIndex%2 + 1)] = winner

                storage_ = storage.find_one({"server": ctx.guild.id})['storage']
                storage_[tourneyName] = rounds
                storage.update_one({"server": ctx.guild.id}, {"$set":{"storage": storage_}})
                break
            

        all_status = True
        for i in matches:
            if(i["status"] == False):
                all_status = False
        
        if(all_status):
            emb = discord.Embed(
                title=f"Round {curr_round} has finished !",
                color=discord.Color.dark_green(),
            )
            await text_channel.send(embed = emb)
            await home_channel.send(embed = emb)

            tournaments = servers.find_one({"_id": ctx.guild.id})['tournaments']
            tournaments[tourneyName]['current_round'] = curr_round + 1
            servers.update_one({"_id": ctx.guild.id},{"$set":{'tournaments': tournaments}})
    
            # match_builder(ctx,tourneyName,curr_round + 1)

            await roundStatus(ctx, curr_round)

#Displays the list of ongoing matches with their status
@client.command()
async def showMatches(ctx):
    thisServer = servers.find_one({"_id": ctx.guild.id})
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == ctx.channel.id:
            text_channel = x

    global tourneyName
    tourneyName = None
    for i in thisServer['tournaments']:
        if(thisServer['tournaments'][i]['text_channel'] == text_channel.id or text_channel.id in thisServer['tournaments'][i]['match_channels']):
            tourneyName = i

    if(tourneyName == None):
        embed = discord.Embed(
            title="No ongoing tournament in this channel !",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    curr_round = thisServer['tournaments'][tourneyName]['current_round']

    if(curr_round == None):
        embed = discord.Embed(
            title="Tournament has not started yet !",
            color=discord.Color.purple()
        )
        await text_channel.send(embed=embed)
        return
    
    if(curr_round == "finished"):
        embed = discord.Embed(
            title="All matches are finished !",
            color=discord.Color.purple()
        )
        await text_channel.send(embed=embed)
        return


    current_round_matches=storage.find_one({"server": ctx.guild.id})["storage"][tourneyName][curr_round - 1]["matches"]
    current_matchlist = current_matches.find_one({"server": ctx.guild.id})["matches"][tourneyName]
    

    embed=discord.Embed(
        title=f"Current Round : {curr_round} ",
        color=discord.Color.purple()
    )

    sr = ""
    match_players = ""
    match_status = ""

    count=1
    for match in current_round_matches:
        
        player1 = match['player1']
        player2 = match['player2']

        match_players += f"<@{player1['id']}> vs <@{player2['id']}>" + "\n"

        if(match["status"] == False):
            match_={}
            flag = False
            for match in current_matchlist:
                if((match['player1'] == player1 and match['player2'] == player2) or (match['player1'] == player2 and match['player2'] == player1)):
                    flag=True
                    match_=match
                    break
            if(flag):
                 current_time=time.ctime()[11:19]
                 hours=int(current_time[0:2])
                 minutes=int(current_time[3:5])
                 time_elapsed=(hours-match_["Start_Time"][0])*60+(minutes-match_["Start_Time"][1])
                 match_status += f"{match['Match_duration'] - time_elapsed} mins left" + "\n"
            else:
                match_status += "pending" + "\n"

            

        elif(match["status"] == True):
            match_status += f"<@{match['winner']['id']}>" + "\n"

        sr += str(count) + "\n"
        count+=1
    
    embed.add_field(name="Sr.", value=sr,inline=True)
    embed.add_field(name="Match", value=match_players, inline=True)
    embed.add_field(name="Status/Winner", value=match_status, inline=True)
    await text_channel.send(embed=embed)
    return



#Shows all the matches in the current round (remaining, ongoing and finished)
@client.command()
async def roundStatus(ctx,round = -1):
    thisServer = servers.find_one({"_id": ctx.guild.id})
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == ctx.channel.id:
            text_channel = x

    global tourneyName
    tourneyName = None
    for i in thisServer['tournaments']:
        if(thisServer['tournaments'][i]['text_channel'] == text_channel.id or text_channel.id in thisServer['tournaments'][i]['match_channels']):
            tourneyName = i

    if(tourneyName == None):
        embed = discord.Embed(
            title="No ongoing tournament in this channel !",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return
    

    if(round == -1):
        embed = discord.Embed(
            title="Invalid command!",
            description="Please specify the round.",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return
    
    current_round = servers.find_one({"_id": ctx.guild.id})["tournaments"][tourneyName]['current_round']
    
    if(current_round == None):
        embed = discord.Embed(
            title="Tournament has not started yet !",
            color=discord.Color.purple()
        )
        await text_channel.send(embed=embed)
        return
        
    storage_ = storage.find_one({"server": ctx.guild.id})["storage"][tourneyName]
    total_rounds = len(storage_)
    
    if(round > total_rounds):
        embed = discord.Embed(
            title="Invalid round number",
            description="Given round exceeds total rounds in this tournament :/",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    elif(round <= 0):
        embed = discord.Embed(
            title="Invalid round number",
            description="Round number should be greater than 0 :/",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return
            
    elif(current_round != "finished" and int(current_round) < round):
        embed = discord.Embed(
            title="Invalid round number",
            description="Given round has not started yet :/",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    
    current_round_matches=storage.find_one({"server": ctx.guild.id})["storage"][tourneyName][round - 1]["matches"]
    current_matchlist = current_matches.find_one({"server": ctx.guild.id})["matches"][tourneyName]

    desc = None
    if(current_round == round):
        desc = "Active"
    else:
        desc = "Finished"

    embed=discord.Embed(
        title=f"Round : {round} ",
        description=f"Status : {desc}",
        color=discord.Color.purple()
    )

    sr = ""
    match_players = ""
    match_status = ""

    count=1
    for match in current_round_matches:
        
        player1 = match['player1']
        player2 = match['player2']

        match_players += f"<@{player1['id']}> vs <@{player2['id']}>" + "\n"

        if(match["status"] == False):
            match_={}
            flag = False
            for match in current_matchlist:
                if((match['player1'] == player1 and match['player2'] == player2) or (match['player1'] == player2 and match['player2'] == player1)):
                    flag=True
                    match_=match
                    break
            if(flag):
                 current_time=time.ctime()[11:19]
                 hours=int(current_time[0:2])
                 minutes=int(current_time[3:5])
                 time_elapsed=(hours-match_["Start_Time"][0])*60+(minutes-match_["Start_Time"][1])
                 match_status += f"{match['Match_duration'] - time_elapsed} mins left" + "\n"
            else:
                match_status += "pending" + "\n"

            

        elif(match["status"] == True):
            match_status += f"<@{match['winner']['id']}>" + "\n"

        sr += str(count) + "\n"
        count+=1
    
    embed.add_field(name="Sr.", value=sr,inline=True)
    embed.add_field(name="Match", value=match_players, inline=True)
    embed.add_field(name="Status/Winner", value=match_status, inline=True)
    await text_channel.send(embed=embed)
    return
    



#Helps check if the players have solved a problem so that it is not given in the match
def unsolved_checker(contest_id, p_index, handle):
    if(len(p_index) > 1):
        return False
    problem_index = ord(p_index) - ord("A")
    uri = "https://codeforces.com/api/contest.standings?contestId="+str(contest_id)+"&from=1&count=5&showUnofficial=true&handles=" + handle

    response_API = requests.get(uri)
    data = response_API.text
    parse_json = json.loads(data)['result']['rows']

    if(len(parse_json) == 0):
        return True
    else:
        points = parse_json[0]['problemResults'][problem_index]['points']
        rejected_attempt = parse_json[0]['problemResults'][problem_index]['rejectedAttemptCount']


        if(points > 0 or rejected_attempt > 0):
            return False
        else:
            return True



def validate_acc(handle,string):
    startTime = time.time()
    uris = 'https://codeforces.com/api/user.info?handles=' + handle
    while True:
        response = requests.get(uris)
        #print(handle, response.json())
        parse_json = response.json()
        parse_store = parse_json['result'][0]
        if 'firstName' not in parse_store:
            continue
        firstName = parse_store['firstName']
        #print(firstName, time.time()-startTime)
        # firstName = string #to be commented out later
        if firstName == string:
            return True
        if time.time()-startTime > 60:
            return False
        time.sleep(10)



#Participants can register using this command
@client.command()
async def registerMe(ctx, cf_handle="--"):

    thisServer = servers.find_one({"_id": ctx.guild.id})
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == ctx.channel.id:
            text_channel = x

    global tourneyName
    tourneyName = None
    for tournament in thisServer['tournaments']:
        if(thisServer['tournaments'][tournament]['text_channel'] == text_channel.id):
            tourneyName = tournament

    if tourneyName == None:
        embed = discord.Embed(
            title="No Tourney",
            description=f"{ctx.author.mention} there is no ongoing tournament in this channel",
            color=discord.Color.gold()
        )
        await text_channel.send(embed=embed)
        return

    if(cf_handle == "--"):
        embed = discord.Embed(
            title="Invalid command!",
            description="Please specify the cf handle.",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    checkForStartTourney = thisServer['tournaments'][tourneyName]['tourney_status']

    if checkForStartTourney == True:
        embed = discord.Embed(
            title="Tournament Already Started !",
            description="Tounament has already started so nothing can be changed.",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    participantsListTemp = participantsList.find_one({"server": ctx.guild.id})
    for x in participantsListTemp["contestants"][tourneyName]:
        if x['id'] == ctx.author.id:
            embed = discord.Embed(
                title="Already Registered",
                description=f"{ctx.author.mention} you are already registered, please wait till tournament"
                            f" is started. If trying to change your"
                            f"seed then first unregister yourself then again register.",
                color=discord.Color.gold()
            )
            await text_channel.send(embed=embed)
            return
        elif x['id'] != ctx.author.id and x['cf_handle'] == cf_handle:
            embed = discord.Embed(
                title="Already Registered",
                description=f"{ctx.author.mention} This handle has already been registered with some other user. Please register with another handle.",
                color=discord.Color.gold()
            )
            await text_channel.send(embed=embed)
            return

    maxR = 0;
    uri = 'https://codeforces.com/api/user.info?handles=' + cf_handle
    response_API = requests.get(uri)
    data = response_API.text
    parse_json = json.loads(data)
    print(parse_json)
    if(parse_json['status'] == 'FAILED'):
        embed = discord.Embed(
            title="Invalid cf handle!",
            description="Please check your cf handle.",
            color=discord.Color.red()
        )
        await text_channel.send(embed=embed)
        return

    ## validate account
    embed = discord.Embed(
        title="Validate your account within 1 minute",
        description=f"{ctx.author.mention}",
        color=discord.Color.gold()
    )
    val_string = ''.join(random.choices(string.ascii_lowercase, k=10))
    embed.add_field(name="Please change your first name to", value=val_string)
    await text_channel.send(embed=embed)
    
    if not (validate_acc(cf_handle, val_string)):
        embed = discord.Embed(
            title="Validation failed!",
            description=f"{ctx.author.mention}",
            color=discord.Color.gold()
        )
        embed.add_field(name="Please try to register again", value=":-/")
        await text_channel.send(embed=embed)
        return

    maxR = parse_json['result'][0]['maxRating']
    avatar = parse_json['result'][0]['avatar']

    contestants_ = participantsList.find_one({"server": ctx.guild.id})['contestants']
    contestants_[tourneyName].append(
        {"id": ctx.author.id, "cf_handle": cf_handle.lower(), "maxRating": maxR, "avatar": avatar,"ac_handle":'--', "ac_maxR": '--'}
    )
    participantsList.update_one({"server": ctx.guild.id},
                                {"$set": {"contestants": contestants_}})


    embed = discord.Embed(
        title="Registration successfull!",
        description=f"{ctx.author.mention}",
        color=discord.Color.gold()
    )

    embed.add_field(name="Cf_Handle", value=cf_handle, inline=True)
    embed.add_field(name="Max_Rating", value=maxR)
    embed.set_footer(text = "If the above details are incorrect, unregister yourself and then register again.")
    await text_channel.send(embed=embed)


@client.command()
async def unregisterMe(ctx):
    thisServer = servers.find_one({"_id": ctx.guild.id})
    # global text_channel
    for x in ctx.guild.text_channels:
        if x.id == ctx.channel.id:
            text_channel = x

    global tourneyName
    tourneyName = None
    for tournament in thisServer['tournaments']:
        if(thisServer['tournaments'][tournament]['text_channel'] == text_channel.id):
            tourneyName = tournament

    if tourneyName == None:
        embed = discord.Embed(
            title="No Tourney",
            description=f"{ctx.author.mention} there is no ongoing tournament in this channel",
            color=discord.Color.gold()
        )
        await text_channel.send(embed=embed)
        return

    checkForStartTourney = thisServer['tournaments'][tourneyName]['tourney_status']

    if checkForStartTourney == True:
        embed = discord.Embed(
            title="Tournament Already Started",
            description="Tounament has already started so nothing can be changed.",
            color=discord.Color.gold()
        )
        await text_channel.send(embed=embed)
        return

    contestants_ = participantsList.find_one({"server": ctx.guild.id})['contestants']

    found = False
    ix = 0
    for i in range(len(contestants_[tourneyName])):
        if contestants_[tourneyName][i]["id"] == ctx.author.id:
            found = True
            ix = i

    if found:
        contestants_[tourneyName] = contestants_[tourneyName][:ix] + contestants_[tourneyName][ix+1:]
        participantsList.update_one({"server": ctx.guild.id},{"$set":{"contestants": contestants_}})

        embed = discord.Embed(
            title="Unregistered",
            description=f"{ctx.author.mention} you are now unregistered.",
            color=discord.Color.gold()
        )
        await text_channel.send(embed=embed)
        return

    embed = discord.Embed(
        title="Couldn't Unregister",
        description=f"{ctx.author.mention} you are not part of tournament **{tourneyName}** right now.",
        color=discord.Color.gold()
    )

    await text_channel.send(embed=embed)



@client.command()
async def stalk(ctx, userId):
    part_ = participantsList.find_one({"server": ctx.guild.id})['contestants']
    participant = None
    for i in part_:
        for j in part_[i]:
            if(str(j['id']) == str(userId)[2:len(userId)-1]):
                participant = j
    if(participant == None):
        embed = discord.Embed(
            title="Participant not found!",
            description=f"No such participant registered for any of the tournaments in the given server",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="Participant details :",
        color=discord.Color.gold()
    )
    embed.add_field(name=f"CF : {participant['cf_handle']}   ", value=f"Max Rating  : {participant['maxRating']}   ",inline=False)
    embed.add_field(name=f"AC : {participant['ac_handle']}   ", value=f"Max Rating  : {participant['ac_maxR']}   ",inline=False)
    embed.set_thumbnail(url = participant['avatar'])
    await ctx.send(embed=embed)
    return

@client.command()
@commands.has_role('Tourney-manager')
async def showTourneys(ctx):
    thisServer = servers.find_one({"_id": ctx.guild.id})['tournaments']

    if(len(thisServer) == 0):
        embed = discord.Embed(
            title="No tournaments ongoing!",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
        return

    tourneys = ""
    for i in thisServer:
        tourneys += f"{i}" + "\n"

    embed = discord.Embed(
        title="Tournaments :",
        color=discord.Color.gold()
    )
    embed.add_field(name="Name",value=tourneys,inline=True)
    await ctx.send(embed=embed)
    return

@client.command()
async def get_user(ctx,handle = '--'):
    if handle == '--':
        embed = discord.Embed(
            title= "Invalid Handle",
            description="Please enter a valid handle",
            color = discord.Color.red())
        await ctx.send(embed = embed)
        return

    tag = None
    part = participantsList.find_one({"server": ctx.guild.id})['contestants']
    for i in part:
        for j in part[i]:
            if j['cf_handle'] == handle:
                tag = j['id']
                break

    if tag == None:
        embed = discord.Embed(
            title= "User Not Found",
            description="There is no user registered with this handle :(",
            color = discord.Color.gold())
        await ctx.send(embed = embed)
        return
    else:
        embed = discord.Embed(
            title= "User",
            description= f"<@{str(tag)}>",
            color = discord.Color.green()
        )
        await ctx.send(embed = embed)
        return

client.run(token)