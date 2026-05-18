## gc-email-triage

A Python tool that ingests racing telemetry (lap times, sector splits) and
turns the time-degradation curve into a rough tire wear strategy — how many
laps you can push before the tires drop off enough that pitting becomes the
faster choice.


## Why this exists

I've always had a passion for motorsports, and I wanted a hands-on excuse to get comfortable with
pandas and matplotlib on data I actually cared about. Lap times are a nice
dataset for this: small enough to iterate quickly, structured enough to do
real analysis, and the domain has enough texture (compound choice, fuel
load, track evolution) that you can keep going deeper.

It's a personal learning project. It's not a strategy engine and it's not
trying to be one. However, the calculations are real: given a stint of laps, it'll
fit a degradation curve and tell you roughly where the crossover point is
between staying out and pitting.


## What it does

- Loads lap-time CSVs (one row per lap: lap number, time, compound, optional sector splits)
- Cleans out in/out laps and obvious outliers (safety car laps, mistakes)
- Fits a degradation model per stint — linear by default, with an option for
  a piecewise fit when you see a "cliff" rather than gradual fall-off
- Compares projected stint pace against a reference pit-loss value to find
  the optimal stint length
- Plots the whole thing so you can eyeball whether the model is sane


## Stack

- Python 3.10+
- pandas — data manipulation
- numpy — math
- matplotlib — plots
- scipy — curve fitting

Dependencies are pinned in `requirements.txt`.


## Setup

```bash
git clone https://github.com/jrlexineer/track-telemetry-analysis.git
cd track-telemetry-analysis
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Running it

There's a sample dataset in `data/sample_stint.csv` so you can try it without any setup:

```bash

python analyze.py --input data/sample_stint.csv --pit-loss 22.5

```

The `--pit-loss` flag is the time cost of a pit stop in seconds — entry, stop, and exit, minus what you'd lose driving past the pit lane. 22.5s is a rough average for a permanent circuit; street circuits run higher.

## What you'll see

You get two things back: a printed summary and a saved plot.

The summary looks something like this:
```
Stint summary: medium compound, 24 laps
Baseline pace (laps 3-5): 1:32.412
Degradation rate: 0.041 s/lap (linear fit, R² = 0.87)
Projected pace at lap 30: 1:33.640
Crossover with pit-loss 22.5s: lap 27
Recommendation: pit window opens lap 25, optimal stop lap 27
```

The plot shows lap times with the fitted degradation curve, the projection forward, and a vertical line at the crossover lap. Saved to `output/`.


## What I'd do differently if I rebuilt it today

A few things, in rough order of how much they bug me:

1. **The degradation model is too simple.** Linear fits are fine for medium compounds on most circuits, but real tire behavior has a thermal window — pace can actually *improve* over the first few laps as the tire gets up to temp, then degrade, then sometimes fall off a cliff. A three-phase model (warm-up, linear deg, cliff) would be more honest about what tires actually do.

2. **No fuel correction.** Cars get faster as they burn fuel — roughly 0.03s/lap in F1, varies by category. Right now that effect gets folded into the degradation rate, which makes the numbers a bit pessimistic for long stints. Splitting fuel effect from tire effect would be a real improvement.

3. **The CSV schema is too loose.** I let it accept "whatever columns are there" because I was iterating, and now I have to think every time about which sample files have sector splits and which don't. A proper schema with pydantic, even just for the input layer, would save future me.

4. **I'd reach for polars instead of pandas now** for the data layer. The datasets are small enough that it doesn't matter for performance, but the API is cleaner and I prefer it for new projects.

None of these are hard to add. They're just on the list, not in the repo.
