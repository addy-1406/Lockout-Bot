# Lockout-Tournament Discord Bot
<img src="https://github.com/Ayush-721/Lockout-Tourney-Bot/assets/95296019/348642b7-22b7-44d8-afbc-d37b685ee12b" alt="Image" width="60%">

This is a [Python](https://www.python.org/) based Discord bot which helps to organise tournaments and conduct 1v1 programming matches. The bot can handle scheduling and organisation of the fixtures.</br>
We used the [Codeforces](https://codeforces.com/apiHelp) API for fetching questions and also check for submissions in real time while conducting the matches itself. We used  [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for web scraping to get the support of  [AtCoder](https://atcoder.jp/)  judge.
We tried to create a user-friendly interface, allowing participants get to validated and compete in tournaments. All of these features were integrated with the help of [discord.py](https://discordpy.readthedocs.io/en/stable/) library.

# Features
* <b>Competitive Programming Judges supported: </b>[Codeforces](https://codeforces.com/) and [Atcoder](https://atcoder.jp/).
* <b>Validation of Handles: </b> Validate a handle by making a request to the <b>"user.info"</b> method of the Codeforces API and checking the response for user information for Codeforces Handle Verification. Also no. of permissible accounts for a particular judge is limited by <b>1</b>.
* <b>Show ongoing Matches: </b> Provide user with the list of all ongoing matches in the particular tournament.
* <b>Start Match:</b> Starts a lockout based match between the users(if both are <b>registered</b>) and asks for a time in minutes in [10-180) for that round, and presents the users with a set of <b>5</b> questions which neither of them have previously attempted.
* <b>Match Updates:</b> Shows the status of problems solved and remaining time for the particular round.
* <b>Problems Presented:</b> Takes in an input value for the rating of the first problem for the user, and the problems presented are of rating <b>x, x+100, x+200, x+300, x+400</b> where <b>x</b> is the value input by the user.
* <b>Show Participants: </b> Gives the list of participants in a particular tournament along with their [Codeforces](https://codeforces.com/) and [Atcoder](https://atcoder.jp/) profile's max ratings.
* <b> Show Matches: </b> Provides user with the fixture of matches to be played in the ongoing tournament. This fixture is built by using the method of <b>Single Elimination Tournament</b> with byes given in case of an unsymetric number of participants in the particular round.

The commands for all these features can be retrieved by executing the ```!help``` command.

# How to Use:
The Lockout Bot can be installed locally by running the below command.

```git clone https://github.com/addy-1406/Lockout-Bot.git```

To use the bot install the required dependencies:

* [requests](https://requests.readthedocs.io/en/latest/user/install/)
* [asyncio](https://pypi.org/project/asyncio/)
* [bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)
* [discord](https://pypi.org/project/discord.py/)
* [pymongo](https://pypi.org/project/pymongo/)

To start the Bot , run the ``main.py`` file

# Bot in Action:

```!help``` command
</br></br>
![help](https://github.com/Ayush-721/Lockout-Tourney-Bot/assets/95296019/8cbaa040-fdc2-4206-8d75-03c46ff3df3d)

```User Validation```
</br></br>
![validation](https://github.com/Ayush-721/Lockout-Tourney-Bot/assets/95296019/8b766f03-8e24-4bf4-812a-0ed8f71601d7)

``` Start Match and Round Updates Popup```
</br></br>
![startMatchandupdate](https://github.com/Ayush-721/Lockout-Tourney-Bot/assets/95296019/1aa63d52-959b-4add-96fa-f200a7a7abaa)

``` !showParticipants command```
</br></br>
![showparticipants](https://github.com/Ayush-721/Lockout-Tourney-Bot/assets/95296019/266025d5-5623-4617-914e-2db3f79c21e7)

```Update in Problem Set on solving a problem```
</br></br>
![solveupdate](https://github.com/Ayush-721/Lockout-Tourney-Bot/assets/95296019/7aaa5038-ab80-427a-a094-f2d0c3fa30b1)

```End of a round```
</br></br>
![matchfinish](https://github.com/Ayush-721/Lockout-Tourney-Bot/assets/95296019/58618c05-8ab1-4d41-986c-f0a9538f3a49)

```!showTourneys command```
</br></br>
![showtourney](https://github.com/Ayush-721/Lockout-Tourney-Bot/assets/95296019/a8bd528b-0971-4131-9f29-b5229f25c3c9)

```!stalk command```
</br></br>
![stalk](https://github.com/Ayush-721/Lockout-Tourney-Bot/assets/95296019/d2def038-a719-4daf-a781-48698fccb201)

```When you ace the tournament```
</br></br>
![tournamentend](https://github.com/Ayush-721/Lockout-Tourney-Bot/assets/95296019/d6df9f55-d4b7-4da0-bd6f-5a60529b42ac)


# Team:

This project was made by:
* [Aditya Mandal](https://github.com/addy-1406)
* [Tanish](https://github.com/v-tanish012)
* [Shrivathsa P S](https://github.com/5hrivathsa)
* [Achintya Gupta](https://github.com/achintya7567)
* [Ayush Kumar](https://github.com/Ayush-721)
* [Riya Mittal](https://github.com/mit-riya)
* [Chandrashekar A. Giridharan](https://github.com/chandrashekar27)
