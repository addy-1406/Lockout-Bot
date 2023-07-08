
# Lockout Bot



## Commands:
- `!!trivia`
  - The bot will give you a trivia question to answer related to anime.

- `!!character`
  - The bot will give you an image of an anime character and you must guess the character's name

- `!!stats`
  - The bot will present the ranking list of the top ten in the server along with their points

- `!!help`
  - To get list of all commands available


## FILES

### Python Files
  - main.py
  - commands.py 
  - database_functions.py

### JSON Files
  - anime_characters.json 
  - trivia_questions.json
  - database_json
  - config.json

### Requirements
  - requirements.txt


## Run Locally

Clone the project

```bash
  git clone https://github.com/soumyadeep-p/AnimeQuiz
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Conenct to your Discord Bot by adding TOKEN in config.json


Run the Bot

```bash
  Run the python main.py file
```


## Acknowledgements

 - [MyAnimeList](https://myanimelist.net/) for Anime characters and Pictures
 - [MalScrapper](https://github.com/Kylart/MalScraper/tree/master) for MyAnimeList API 
 - [GuessTheAnime bot by Bratah123](https://github.com/Bratah123/GuessTheAnime#guesstheanime)
