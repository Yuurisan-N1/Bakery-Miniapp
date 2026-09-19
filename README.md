<div align="center">

<img width="100%" alt="header" src="https://capsule-render.vercel.app/api?type=waving&height=210&text=Bakery%20Rush%20Bot&fontAlign=50&fontAlignY=36&fontSize=56&desc=Bake%20Cycles%20%7C%20Storage%20Boost%20%7C%20Ad%20Partners%20%7C%20Task%20Hub%20%7C%20Multi-Account&descAlign=50&descAlignY=58"/>

<img alt="typing" src="https://readme-typing-svg.demolab.com?font=Inter&size=18&duration=3000&pause=650&center=true&vCenter=true&width=900&lines=Bake+Cycle+%7C+Start+%26+Collect+Per+Account;Bake+Storage+%7C+Ad+Boost+Extends+The+Cap;Ad+Partners+%7C+Every+Slot+Read+From+Server;Task+Hub+%7C+Daily+Reward+%26+Knowledge+Round;Multi-Account+%7C+Proxy+%26+Live+Countdown"/>

<p>
  <img alt="python" src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white"/>
  <img alt="platform" src="https://img.shields.io/badge/Platform-Bakery%20Rush%20Miniapp-111111"/>
  <img alt="multi-account" src="https://img.shields.io/badge/Multi--Account-Supported-111111"/>
  <img alt="proxy" src="https://img.shields.io/badge/Proxy-Supported-111111"/>
  <img alt="author" src="https://img.shields.io/badge/by-Yuurisandesu-111111"/>
</p>

<p>
  <b>Bakery Rush Bot</b> is a full automation bot for the Bakery Rush Telegram Miniapp.<br/>
  It handles the complete daily cycle: running the bake cycle, extending the bake storage with an ad, claiming every rewarded ad slot offered by the server, claiming the community tasks, the daily protocol reward, the wheel spin, the scratch card and the knowledge round, all running automatically across multiple accounts with a per-account session bootstrap, proxy support, and a live countdown between cycles.<br/>
  Built and distributed by <b>Yuurisandesu</b>.
</p>

</div>

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Bot](#running-the-bot)
- [Features](#features)
- [File Structure](#file-structure)
- [Disclaimer](#disclaimer)

---

## Requirements

- Python `3.12+`
- Git

---

## Installation

**Clone the repository:**

```bash
git clone https://github.com/Yuurisan-N1/Bakery-Miniapp.git
cd Bakery-Miniapp
```

**Install dependencies:**

```bash
pip install aiohttp yuurisan
```

---

## Configuration

### 1. Accounts (data.txt)

Fill `data.txt` with Telegram WebApp `initData` for each account, one per line:

```
user=%7B%22id%22...&hash=abc123
user=%7B%22id%22...&hash=def456
```

> `initData` can be obtained from the browser DevTools when opening Bakery Rush on Telegram Web.

> An optional `|address` suffix is tolerated and ignored, because no phase in this bot needs a wallet address.

### 2. Proxy (proxy.txt)

Fill `proxy.txt` with proxies, one per line (optional, leave empty to run without proxy):

```
host:port
host:port:user:pass
http://user:pass@host:port
```

Proxies are assigned to accounts by index in round-robin order.

### 3. Bot Settings (config.json)

`sleep_seconds` controls how many seconds the bot waits between cycles. If `config.json` is missing, it is created automatically with a default of `3600` seconds.

---

## Running the Bot

```bash
python bot.py
```

Press `Ctrl+C` at any time to stop the bot cleanly.

---

## Features

### Auto Bake Cycle
The bake cycle is driven by one server call that both starts a cycle and collects it. When the server reports a started cycle, that is logged as is. When it reports a collected amount, the credited amount and the balance it returned are logged. A cycle whose storage has not filled up yet is reported instead of being forced.

### Auto Storage Boost
The storage boost is requested as its own ad purpose, and the session id the server returns is used for the follow up call after the server wait gate. The added hours, the storage cap it produced and the number of boosts left on the account are all read from that response, so only a server confirmed extension is logged.

### Auto Ad Partners
The ad slot list is read from the server, and every active slot it offers is claimed on its own: the reward, the daily cap and the provider label come from the server, and the claim is sent with the provider id the session belongs to. The reward, the credited balance and the ad counter are logged straight from the claim response. When a slot returns its allowance as used up, that slot stops for the round instead of hammering the endpoint.

### Auto Community Tasks
Every task the server lists is claimed with its own task id, and the credited reward plus the balance it returned are logged per task. A task that genuinely needs a real channel join is reported with that server reason rather than being retried in a loop.

### Auto Daily Protocol Reward
The daily state is read from the daily hub first, and the claim is only sent when the server still offers the day. The credited amount and the streak day count are logged, and an already claimed day is reported with the current streak instead of being retried.

### Auto Wheel, Scratch Card and Knowledge Round
The wheel spin, the scratch card and the knowledge round are each claimed through their own endpoint, and each credited amount is read from the claim response so only a real credit is logged. A round that is not ready yet is reported instead of being polled.

### Auto Referral State
The referral friend count is read from the account state, and the invite link is derived from the referral code in the bot configuration.

### Multi Account
All accounts in `data.txt` are processed sequentially within every cycle. Each account signs in with its own `initData`, and the balance plus the credited amount per phase are logged per account. The cycle number is tracked and logged at the start of each round.

### Proxy Support
Proxies are loaded from `proxy.txt` and assigned to accounts by position in round-robin order. Proxy credentials are masked in log output. Running without proxies is fully supported.

### Auto Countdown
After all accounts complete a cycle, the bot displays a live `HH:MM:SS` countdown until the next cycle starts.

---

## File Structure

```text
BakeryRushBot-Miniapp/
├── bot.py          # Main bot, full daily cycle automation
├── config.json     # Sleep duration between cycles
├── data.txt        # Account initData, one per line
├── proxy.txt       # Proxy list, one per line (optional)
├── LICENSE         # License file
└── utils/
    └── banner.py   # Banner using yuurisan module
```

---

## Disclaimer

This tool is built for educational and technical exploration purposes. Use it wisely and at your own responsibility.

---

<div align="center">
<img width="100%" alt="footer" src="https://capsule-render.vercel.app/api?type=waving&height=120&section=footer"/>
</div>
