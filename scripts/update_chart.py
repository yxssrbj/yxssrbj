"""Build the profile's weekly contribution chart from GitHub GraphQL."""

import json
import os
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen


QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks { firstDay contributionDays { contributionCount } }
      }
    }
  }
}"""


def weekly_counts(payload):
    if payload.get("errors"):
        raise RuntimeError("GitHub GraphQL: " + json.dumps(payload["errors"]))
    try:
        weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        counts = [(week["firstDay"], sum(day["contributionCount"] for day in week["contributionDays"])) for week in weeks]
        for first_day, count in counts:
            date.fromisoformat(first_day)
            if count < 0:
                raise ValueError("negative contribution count")
        return counts
    except (KeyError, TypeError) as error:
        raise RuntimeError("GitHub GraphQL returned no contribution calendar") from error


def chart_svg(weeks):
    if not weeks:
        raise ValueError("no contribution weeks")
    width, height = 960, 380
    left, right, top, bottom = 72, 28, 66, 54
    plot_width, plot_height = width - left - right, height - top - bottom
    maximum = max(4, *(count for _, count in weeks))
    slot = plot_width / len(weeks)
    bar_width = slot * 0.68
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Contributions per week</title>',
        '<desc id="desc">Weekly GitHub contributions, with bars for actual counts and a four-week moving average trend.</desc>',
        '<rect width="960" height="380" rx="12" fill="#ffffff"/>',
        '<text x="72" y="34" fill="#1f2328" font-family="Arial,sans-serif" font-size="21" font-weight="700">Contributions per week</text>',
        '<rect x="72" y="45" width="11" height="11" rx="2" fill="#40c463"/>',
        '<text x="89" y="55" fill="#57606a" font-family="Arial,sans-serif" font-size="12">actual</text>',
        '<path d="M148 50 H171" stroke="#116329" stroke-width="3" fill="none"/>',
        '<text x="178" y="55" fill="#57606a" font-family="Arial,sans-serif" font-size="12">trend (4-week average)</text>',
    ]
    for tick in range(5):
        y = top + plot_height * (1 - tick / 4)
        parts.append(f'<path d="M{left} {y:.1f} H{width-right}" stroke="#eaeef2" stroke-width="1"/>')
        parts.append(f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" fill="#57606a" font-family="Arial,sans-serif" font-size="12">{round(maximum*tick/4):,}</text>')

    previous_month = None
    line = []
    for index, (first_day, count) in enumerate(weeks):
        day = date.fromisoformat(first_day)
        if count < 0:
            raise ValueError("negative contribution count")
        x = left + index * slot + (slot - bar_width) / 2
        bar_height = plot_height * count / maximum
        y = top + plot_height - bar_height
        parts.append(f'<rect class="bar" x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="1.5" fill="#40c463"><title>Week of {day.isoformat()}: {count} contributions</title></rect>')
        if day.month != previous_month:
            parts.append(f'<text x="{x:.1f}" y="{height-20}" fill="#57606a" font-family="Arial,sans-serif" font-size="12">{day.strftime("%b")}</text>')
            previous_month = day.month
        average = sum(value for _, value in weeks[max(0, index-3):index+1]) / min(index+1, 4)
        line.append(f'{"M" if index == 0 else "L"}{left + (index+0.5)*slot:.1f} {top + plot_height*(1-average/maximum):.1f}')
    parts.append(f'<path class="trend" d="{" ".join(line)}" stroke="#116329" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" fill="none"/>')
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def main():
    body = json.dumps({"query": QUERY, "variables": {"login": os.environ["GITHUB_REPOSITORY_OWNER"]}}).encode()
    request = Request("https://api.github.com/graphql", body, {
        "Authorization": "Bearer " + os.environ["GH_TOKEN"],
        "Content-Type": "application/json",
        "User-Agent": "weekly-contribution-chart",
    })
    with urlopen(request, timeout=20) as response:
        weeks = weekly_counts(json.load(response))
    output = Path("assets/contributions-per-week.svg")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(chart_svg(weeks), encoding="utf-8")


if __name__ == "__main__":
    main()
