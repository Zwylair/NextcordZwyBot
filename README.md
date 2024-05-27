<h1 align="center">
    NextcordZwyBot
</h1>

<p align="center">
    <img src="https://img.shields.io/badge/python-3.11-green?logo=python&logoColor=white&style=for-the-badge">
    <img src="https://img.shields.io/badge/LICENSE-MIT-green?style=for-the-badge">
    <img src="https://img.shields.io/github/languages/code-size/Zwylair/NextcordZwyBot?style=for-the-badge">
</p>

Discord bot made with [nextcord](https://docs.nextcord.dev/en/stable/api.html) lib and with Zwy's needed features.

#### Features:
* Create private temporary voice channels to talk with your buddies alone
* Make events announce it in certain channel, save it as templates to use it in future
* Administrator commands:
* * `caps checker`
* * `role edit` (edit color and name); `role move`; `role revoke`; `role give`
* `dice` command, that allows to throw **n** dices
* And some dev commands:
* * `guilds_info` which provides a small info-card of the guilds the bot is a member of
* * `extract_emojis` extracts server emojis to webhook/bot tag (`<(a):name:id>`)

# Setup and Dependencies
Clone the repository:
```
git clone https://github.com/Zwylair/NextcordZwyBot
```

## Install dependencies

#### Linux
```bash
python3 -m pip install -r requirements.txt
```

#### Windows
```bash
py -m pip install -r requirements.txt
```

## Running

#### Linux
```bash
python3 main.py
```

#### Windows
```bash
py main.py
```

## License

This project is under the [MIT license](./LICENSE).
