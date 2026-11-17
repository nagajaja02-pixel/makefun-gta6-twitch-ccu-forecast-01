"""Offline launch-curve analog mixture; Python 3.13, standard library only."""
import json
import math
import os
from datetime import datetime
from pathlib import Path

LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)


def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()


def hourly(rows, origin, key='from'):
    return {int(round((timestamp(r[key]) - origin) / 3600)): max(1, r['viewers'])
            for r in sorted(rows, key=lambda r: r[key]) if r.get('viewers') is not None}


def features(curve):
    """Relative pre-unlock activity avoids conflating audience size with maturity."""
    first = curve[0]
    evening = [curve[h] for h in range(-10, 0) if h in curve]
    recent = [curve[h] for h in range(-3, 0) if h in curve]
    return (math.log(max(evening, default=first) / first),
            math.log((sum(recent) / len(recent) if recent else first) / first))


def prior_weight(analog):
    description = analog['unlock'].lower()
    platforms = analog['platforms'].lower()
    if 'target-history' in description or 'not a launch' in description:
        return 0.0
    if 'early-access-contaminated' in description:
        return 0.08
    if 'single global' in description or 'simultaneous across' in description or 'pc only' in description:
        return 0.025
    if 'pc' not in platforms:
        return 1.0
    if 'midnight local' in description or 'rolling' in description:
        return 0.55
    return 0.08


def student_cdf(value):
    """Closed form Student-t CDF with five degrees of freedom."""
    theta = math.atan(value / math.sqrt(5))
    integral = 3 * theta / 8 + math.sin(2 * theta) / 4 + math.sin(4 * theta) / 32
    return min(1.0, max(0.0, 0.5 + 8 * integral / (3 * math.pi)))


def forecast(case):
    origin = timestamp(case['day_start'])
    observed = hourly(case['history_hourly'], origin)
    first = max(1, next(r['viewers'] for r in case['known'] if r['hour'] == 1))
    observed[0] = first
    target = features(observed)
    analogs = []
    for analog in sorted(case['comparables'], key=lambda a: (a['name'], a['day_start'])):
        prior = prior_weight(analog)
        if prior == 0:
            continue
        curve = hourly(analog['hourly'], timestamp(analog['day_start']))
        if 0 not in curve or sum(h in curve for h in range(24)) < 22:
            continue
        feat = features(curve)
        distance = ((feat[0] - target[0]) / 0.38) ** 2 + ((feat[1] - target[1]) / 0.28) ** 2
        # A pooled component prevents one nearest neighbor dominating.
        weight = prior * (0.06 + math.exp(-0.5 * distance))
        analogs.append((curve, weight))
    results = []
    for hour in range(2, 25):
        h = hour - 1
        components = []
        for curve, weight in analogs:
            if h in curve:
                ratio = max(-3.0, min(3.5, math.log(curve[h] / curve[0])))
                components.append((ratio, weight))
        if not components:
            components = [(0.0, 1.0)]
        total = sum(w for _, w in components)
        pooled = sum(m * w for m, w in components) / total
        # Shrink individual log ratios slightly toward the pooled curve.
        components = [(0.9 * m + 0.1 * pooled, w / total) for m, w in components]
        # Practice intervals overcovered; retain analog dispersion and tails,
        # but reduce the extra within-analog noise by roughly one fifth.
        scale = 0.10 + 0.020 * math.sqrt(h)
        quantiles = []
        for level in LEVELS:
            low, high = -12.0, 12.0
            for _ in range(48):
                mid = (low + high) / 2
                probability = sum(w * student_cdf((mid - m) / scale) for m, w in components)
                if probability < level:
                    low = mid
                else:
                    high = mid
            quantiles.append(round(max(0.001, min(1e9, first * math.exp((low + high) / 2))), 3))
        results.append({'hour': hour, 'q': quantiles})
    return {'hours': results}


def main():
    destination = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', '/output'))
    destination.mkdir(parents=True, exist_ok=True)
    for source in sorted(Path(os.environ.get('MAKEFUN_INPUT_DIR', '/input')).glob('*.in')):
        case = json.loads(source.read_text(encoding='utf-8'))
        output = json.dumps(forecast(case), separators=(',', ':'), allow_nan=False) + '\n'
        (destination / (source.stem + '.out')).write_text(output, encoding='utf-8')


if __name__ == '__main__':
    main()
