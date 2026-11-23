#!/usr/bin/env python3
"""Plan how to spend Claude plan usage before the weekly reset.

Reads rate-limit samples (5-hour and 7-day utilization) and your working hours, then
lays out each 5-hour window until the weekly reset: how much of it to use, what that
costs of the weekly limit, and a pace to hold (percent of the 5-hour window per hour).

  python3 usage_plan.py                                   # usage_samples.json next to this file
  python3 usage_plan.py --five 26 --week 54 --five-reset 14:40 --week-reset "+1 23:00"
  python3 usage_plan.py --work "13:20-23:00" "+1 18:00-23:00"

--five/--week come from Claude Code's /usage (or the rate_limit_event log in a cloud
session). Times are US Eastern; "+1 18:00" means tomorrow at 18:00.
"""
import argparse, json, os, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")
WINDOW = timedelta(hours=5)
HERE = os.path.dirname(os.path.abspath(__file__))


def at(spec, now):
    """'HH:MM' or '+N HH:MM' (N days from today) or epoch seconds -> aware datetime."""
    spec = str(spec).strip()
    if spec.isdigit():
        return datetime.fromtimestamp(int(spec), TZ)
    days = 0
    if spec.startswith("+"):
        d, spec = spec[1:].split(None, 1)
        days = int(d)
    h, m = map(int, spec.split(":"))
    return (now + timedelta(days=days)).replace(hour=h, minute=m, second=0, microsecond=0)


def intervals(specs, now):
    out = []
    for s in specs:
        prefix = ""
        if s.startswith("+"):
            prefix, s = s.split(None, 1)
            prefix += " "
        a, b = s.split("-")
        start, end = at(prefix + a, now), at(prefix + b, now)
        if end <= start:
            end += timedelta(days=1)
        start = max(start, now)
        if end > start:
            out.append((start, end))
    return sorted(out)


def overlap(a0, a1, ivs):
    return sum(max(0, (min(a1, b1) - max(a0, b0)).total_seconds()) for b0, b1 in ivs) / 3600


def first_work_after(t, ivs):
    for b0, b1 in ivs:
        if b1 > t:
            return max(t, b0)
    return None


def ratio_from(samples):
    """Weekly points per 5-hour point, from the change inside each 5-hour window."""
    groups = {}
    for s in samples:
        groups.setdefault(s["five_reset"], []).append(s)
    dw = df = 0.0
    n = 0
    for g in groups.values():
        g.sort(key=lambda s: s["t"])
        f = g[-1]["five"] - g[0]["five"]
        if f >= 0.05 and g[0]["week_reset"] == g[-1]["week_reset"]:
            dw += g[-1]["week"] - g[0]["week"]
            df += f
            n += 1
    if not df:
        return None
    # server rounds to 0.01, so each weekly difference is uncertain by +-0.01
    return dw / df, max(0.0, (dw - 0.01 * n) / df), (dw + 0.01 * n) / df


def observed_pace(samples):
    """5-hour points per hour over the latest stretch of steady use (last 90 min)."""
    s = sorted(samples, key=lambda s: s["t"])
    if not s:
        return None
    last = s[-1]
    tl = datetime.fromisoformat(last["t"].replace("Z", "+00:00"))
    recent = [x for x in s if x["five_reset"] == last["five_reset"]
              and tl - datetime.fromisoformat(x["t"].replace("Z", "+00:00")) <= timedelta(minutes=90)]
    if len(recent) < 2:
        return None
    t0 = datetime.fromisoformat(recent[0]["t"].replace("Z", "+00:00"))
    hours = (tl - t0).total_seconds() / 3600
    return (last["five"] - recent[0]["five"]) / hours if hours > 0.1 else None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--samples", default=os.path.join(HERE, "usage_samples.json"))
    p.add_argument("--five", type=float, help="5-hour window used, percent (overrides samples)")
    p.add_argument("--week", type=float, help="weekly used, percent (overrides samples)")
    p.add_argument("--five-reset", help="when the current 5-hour window resets, e.g. 14:40")
    p.add_argument("--week-reset", help='when the weekly limit resets, e.g. "+1 23:00"')
    p.add_argument("--work", nargs="+", default=["13:20-23:00"],
                   help='hours you will be working, e.g. "13:20-23:00" "+1 18:00-23:00"')
    p.add_argument("--ratio", type=float, help="weekly %% per full 5-hour window (default: fitted)")
    p.add_argument("--max-pace", type=float, default=35,
                   help="most of a 5-hour window you can usefully burn per hour, percent (default 35)")
    p.add_argument("--reserve", type=float, default=3, help="weekly %% to keep spare (default 3)")
    p.add_argument("--now", help="override the current time (HH:MM), for testing")
    a = p.parse_args()

    now = datetime.now(TZ)
    if a.now:
        now = at(a.now, now)
    samples = []
    if os.path.exists(a.samples):
        samples = json.load(open(a.samples))["samples"]
    last = max(samples, key=lambda s: s["t"]) if samples else {}

    five = a.five / 100 if a.five is not None else last.get("five")
    week = a.week / 100 if a.week is not None else last.get("week")
    five_reset = at(a.five_reset, now) if a.five_reset else (
        datetime.fromtimestamp(last["five_reset"], TZ) if last else None)
    week_reset = at(a.week_reset, now) if a.week_reset else (
        datetime.fromtimestamp(last["week_reset"], TZ) if last else None)
    if None in (five, week, five_reset, week_reset):
        sys.exit("need --five, --week, --five-reset and --week-reset (or a samples file)")
    if five_reset <= now:          # that window already ended; nothing used in a new one yet
        five, five_reset = 0.0, None

    fit = ratio_from(samples)
    if a.ratio is not None:
        ratio, lo, hi = a.ratio / 100, a.ratio / 100, a.ratio / 100
    elif fit:
        ratio, lo, hi = fit
    else:
        ratio, lo, hi = 0.13, 0.09, 0.17
    pace = observed_pace(samples)
    work = intervals(a.work, now)
    f = lambda d: d.strftime("%a %-I:%M%p").replace("AM", "am").replace("PM", "pm")

    print(f"Now {f(now)} ET")
    print(f"Weekly: {week:.0%} used, {1 - week:.0%} left, resets {f(week_reset)} "
          f"({(week_reset - now).total_seconds() / 3600:.1f} h away)")
    if five_reset:
        print(f"5-hour window: {five:.0%} used, resets {f(five_reset)}")
    print(f"One full 5-hour window costs about {ratio:.0%} of the weekly limit "
          f"(could be {lo:.0%}-{hi:.0%}: the server rounds to whole percents)")
    print(f"Weekly left = about {(1 - week) / ratio:.1f} full 5-hour windows")
    if pace is not None:
        print(f"Recent pace: {pace:.0%} of a 5-hour window per hour")
    print()

    # Walk the 5-hour windows from now to the weekly reset.
    rows, t, budget_week = [], now, max(0.0, 1 - week - a.reserve / 100)
    if five_reset:
        rows.append((now, five_reset, 1 - five, five_reset))
        t = five_reset
    while True:
        start = first_work_after(t, work)
        if start is None or start >= week_reset:
            break
        end = min(start + WINDOW, week_reset)
        rows.append((start, end, 1.0, start + WINDOW))
        t = start + WINDOW

    print(f"{'5-hour window':<28}{'work h':>7}{'use':>7}{'weekly':>8}{'weekly after':>14}{'pace/h':>8}")
    total_week, used_week = week, 0.0
    for start, end, cap, _ in rows:
        hrs = overlap(start, end, work)
        use = min(cap, hrs * a.max_pace / 100)
        use = min(use, max(0.0, budget_week - used_week) / ratio)
        cost = use * ratio
        used_week += cost
        total_week += cost
        pace_h = use / hrs if hrs else 0
        print(f"{f(start) + ' - ' + end.strftime('%-I:%M%p').lower():<28}{hrs:>7.1f}"
              f"{use:>7.0%}{cost:>8.0%}{total_week:>14.0%}{pace_h:>8.0%}")
    left = 1 - total_week
    print()
    print(f"Plan ends with {left:.0%} of the weekly limit unused (reserve {a.reserve:.0f}%).")
    if left > a.reserve / 100 + 0.02:
        print("Unused weekly: add working hours before the weekly reset (--work) to spend it.")
    if rows and five_reset and rows[0][2] > 0 and overlap(rows[0][0], rows[0][1], work) == 0:
        print("You are not working before the current window resets; its remainder is lost.")
    gaps = [r1[0] - r0[3] for r0, r1 in zip(rows, rows[1:])]
    if any(g > timedelta(minutes=10) for g in gaps):
        print("A new window starts at your first message after a reset: send one right at the reset "
              "to start the clock early.")


if __name__ == "__main__":
    main()
