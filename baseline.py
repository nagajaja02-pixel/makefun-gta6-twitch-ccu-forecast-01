"""House persistence formula, retained only as an independent comparison tool."""
import json
import math
import os
from pathlib import Path


def forecast(case):
    first = max(1, next(row['viewers'] for row in case['known'] if row['hour'] == 1))
    rows = []
    for hour in range(2, 25):
        values = []
        for z in (-1.645, -0.674, 0, 0.674, 1.645):
            value = first * math.exp(z * 0.15 * math.sqrt(hour - 1))
            values.append(math.floor(value * 100 + 0.5) / 100)
        rows.append({'hour': hour, 'q': values})
    return {'hours': rows}


if __name__ == '__main__':
    output = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', '/output'))
    output.mkdir(parents=True, exist_ok=True)
    for path in sorted(Path(os.environ.get('MAKEFUN_INPUT_DIR', '/input')).glob('*.in')):
        result = forecast(json.loads(path.read_text()))
        (output / (path.stem + '.out')).write_text(json.dumps(result, separators=(',', ':')) + '\n')
