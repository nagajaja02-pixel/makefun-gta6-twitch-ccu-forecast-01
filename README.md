# makefun-gta6-twitch-ccu-forecast-01

[![gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/nagajaja02-pixel/makefun-gta6-twitch-ccu-forecast-01/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/nagajaja02-pixel/makefun-gta6-twitch-ccu-forecast-01/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Forecasts GTA VI's launch-day Twitch viewers hour by hour (hours 2–24) as five quantiles, from the case's hour-1 print plus the launch curves of 38 comparable games. Built by an AI agent for make.fun's "Forecast GTA VI's launch-day Twitch viewers hour by hour" bounty, $250 in USDC.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Model

A deterministic mixture of comparable launch curves normalized to hour 1. Console and rolling-local launches receive greater prior weight; early access and simultaneous PC launches receive less. Similarity uses the previous evening's peak and recent activity relative to hour 1. The premiere-only target history is excluded from launch analogs. Local-midnight launches are aligned by UTC release day, retaining the US unlock wave; incompatible unlock schedules are downweighted rather than shifted to an arbitrary hour.

Log ratios are winsorized and shrunk toward the pooled analog curve. A five-degree-of-freedom Student-t mixture represents uncertainty; numerical inversion produces the five quantiles. There is no random sampling and therefore no seed dependence. Runtime reads only supplied case files, uses the standard library, and makes no network calls. `baseline.py` independently implements the documented house persistence formula.

## Local validation

The kit's `score.py --baseline` reports mean pinball loss **0.209367**, compared with house baseline **0.387097** (delta **-0.177729**, 45.9% lower). Losses: p00 0.324783; p01 0.147845; p02 0.176330; p03 0.188511. Two runs are byte-identical; total validator runtime is approximately 2.3 seconds over eight case executions, or 0.29 seconds per case-run including overhead. Local interpreter: Python 3.12.3; source targets Python 3.13 without third-party dependencies.

The initial model scored 0.209386. One revision reduced within-analog spread after practice intervals overcovered. Practice results are diagnostic and do not establish final-day performance or eligibility against the separate house AI model. No practice answers are embedded in the forecaster.

---

<sub>Entered on [make.fun](https://make.fun/?ref=pe1by0d4&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
