<!-- <p align="center">
<img width="180" height="180" style="vertical-align:middle" src="https://github.com/WuJunde/werewolf_ai_agents/blob/main/werewolf_logo.png" />
</p> -->
<h1 align="center">
<span><i>CamelGym</i></span>
</h1>

<!-- <h3 align="center">
Train Agents to Play Werewolf
</h3> -->

<!-- <p align="center">
    <a href="https://discord.gg/DN4rvk95CC">
        <img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=flat&logoColor=white"/></a>
    <img src="https://img.shields.io/static/v1?label=license&message=GPL&color=white&style=flat" alt="License"/>
</p> -->
CamelGym provides environments to train LLM (Lange Language Model) based Agents. It is built upon multi-agent interaction framework [CAMEL](https://www.camel-ai.org). 

 ## Preparation

 Install the environment:
 ``conda env create -f environment.yml``

 ``conda activate camelgym``

Set the configuration

Create `~/config/config.yaml` 

Copy and paste the following in it:

```yaml
llm:
  api_type: "openai"  # or azure / ollama / open_llm etc. Check LLMType for more options
  model: "gpt-4-turbo-preview"  # or gpt-3.5-turbo-1106 / gpt-4-1106-preview
  base_url: "https://api.openai.com/v1"  # or forward url / other llm url
  api_key: "YOUR_API_KEY"
```

## Run

### Werewolf Game
AI v.s. AI environment playing [Werewolf Game](https://playwerewolf.co/pages/rules#gameplay). 
It is also a reproduction of papers [Language Agents with Reinforcement Learning for Strategic Play in the Werewolf Game](https://openreview.net/pdf?id=N1gmpVd4iE) and [Exploring Large Language Models for Communication Games: An Empirical Study on Werewolf](https://arxiv.org/abs/2309.04658)

Start the game:
```bash
python werewolf_game/start_game.py
```

### Pokemon
still building

