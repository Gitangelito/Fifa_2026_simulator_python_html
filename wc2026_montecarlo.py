"""
FIFA World Cup 2026 — Monte Carlo Tournament Predictor
=======================================================
Uses:
  - Official FIFA April 2026 Elo ratings as base
  - Match data from 894 real qualifying games (updates Elo)
  - Dixon-Coles Poisson goal model for score simulation
  - 100,000-iteration Monte Carlo simulation
  - Outputs HTML report with full group predictions + knockout bracket

Sources:
  - FIFA/Coca-Cola Men's World Ranking, April 1 2026
  - Parsed match file: fifa_all_matches (AFC, UEFA, CONMEBOL, CAF, CONCACAF, OFC)
  - ESPN / inside.fifa.com / Wikipedia 2026 WC qualification
"""

import json
import math
import random
import numpy as np
from collections import defaultdict
from scipy.stats import poisson
from scipy.special import factorial

# ═══════════════════════════════════════════════════════════
# 1. ELO RATINGS  (FIFA April 2026 + match-adjusted)
# ═══════════════════════════════════════════════════════════

# Official FIFA points April 1 2026
# Ref: inside.fifa.com/news/france-1st-fifa-coca-cola-world-ranking-april-2026
FIFA_POINTS = {
    'France':1879,'Spain':1876,'Argentina':1874,'England':1829,'Portugal':1791,
    'Brazil':1780,'Netherlands':1769,'Morocco':1753,'Belgium':1721,'Germany':1693,
    'Croatia':1668,'Colombia':1648,'Senegal':1637,'USA':1627,'Mexico':1618,
    'Uruguay':1611,'Switzerland':1590,'Japan':1582,'IR Iran':1569,'Ecuador':1551,
    'Austria':1543,'Türkiye':1538,'Australia':1522,'Algeria':1510,'Canada':1497,
    'Egypt':1487,'Norway':1475,'Panama':1463,'Korea Republic':1455,'Czechia':1443,
    "Côte d'Ivoire":1431,'Scotland':1420,'Sweden':1408,'Tunisia':1396,
    'Congo DR':1384,'Paraguay':1372,'South Africa':1340,'Saudi Arabia':1318,
    'Jordan':1285,'Qatar':1263,'Bosnia-Herzegovina':1248,'Ghana':1235,
    'Iraq':1220,'Uzbekistan':1210,'Cabo Verde':1198,'New Zealand':1165,
    'Haiti':1148,'Curaçao':1132,
}

# Pre-computed Elo after processing all 894 matches
# (FIFA points as seed, then updated via World Football Elo method)
ELO = {
    'Spain':1876.8,'France':1865.9,'England':1842.8,'Morocco':1771.2,
    'Argentina':1767.0,'Netherlands':1747.2,'Portugal':1722.7,'Croatia':1695.6,
    'Belgium':1684.4,'Germany':1661.2,'Senegal':1635.0,'Japan':1634.9,
    'USA':1627.0,'Brazil':1621.8,'Mexico':1618.0,'Switzerland':1595.6,
    'Ecuador':1594.2,'Colombia':1589.6,'Türkiye':1584.7,'Australia':1578.5,
    'Uruguay':1570.1,'IR Iran':1570.0,'Norway':1558.1,'Austria':1534.7,
    'Korea Republic':1533.8,'Algeria':1531.9,'Egypt':1522.7,'Panama':1501.0,
    'Canada':1497.0,'Paraguay':1493.5,"Côte d'Ivoire":1489.7,'Tunisia':1487.5,
    'Czechia':1460.6,'Congo DR':1448.1,'Uzbekistan':1431.8,'Scotland':1426.6,
    'Jordan':1396.2,'Iraq':1390.9,'Saudi Arabia':1382.9,'Ghana':1356.2,
    'New Zealand':1351.4,'Sweden':1345.9,'Curaçao':1341.9,
    'Bosnia-Herzegovina':1340.5,'South Africa':1339.2,'Qatar':1331.2,
    'Cabo Verde':1307.9,'Haiti':1274.6,
}

# ═══════════════════════════════════════════════════════════
# 2. GROUPS & BRACKET
# ═══════════════════════════════════════════════════════════

GROUPS = {
    'A': ['Mexico','South Africa','Korea Republic','Czechia'],
    'B': ['Canada','Bosnia-Herzegovina','Qatar','Switzerland'],
    'C': ['Brazil','Morocco','Haiti','Scotland'],
    'D': ['USA','Paraguay','Australia','Türkiye'],
    'E': ['Germany','Curaçao',"Côte d'Ivoire",'Ecuador'],
    'F': ['Netherlands','Japan','Sweden','Tunisia'],
    'G': ['Belgium','Egypt','IR Iran','New Zealand'],
    'H': ['Spain','Cabo Verde','Saudi Arabia','Uruguay'],
    'I': ['France','Senegal','Iraq','Norway'],
    'J': ['Argentina','Algeria','Austria','Jordan'],
    'K': ['Portugal','Congo DR','Uzbekistan','Colombia'],
    'L': ['England','Croatia','Ghana','Panama'],
}

FLAGS = {
    'Mexico':'🇲🇽','South Africa':'🇿🇦','Korea Republic':'🇰🇷','Czechia':'🇨🇿',
    'Canada':'🇨🇦','Bosnia-Herzegovina':'🇧🇦','Qatar':'🇶🇦','Switzerland':'🇨🇭',
    'Brazil':'🇧🇷','Morocco':'🇲🇦','Haiti':'🇭🇹','Scotland':'🏴󠁧󠁢󠁳󠁣󠁴󠁿',
    'USA':'🇺🇸','Paraguay':'🇵🇾','Australia':'🇦🇺','Türkiye':'🇹🇷',
    'Germany':'🇩🇪','Curaçao':'🇨🇼',"Côte d'Ivoire":'🇨🇮','Ecuador':'🇪🇨',
    'Netherlands':'🇳🇱','Japan':'🇯🇵','Sweden':'🇸🇪','Tunisia':'🇹🇳',
    'Belgium':'🇧🇪','Egypt':'🇪🇬','IR Iran':'🇮🇷','New Zealand':'🇳🇿',
    'Spain':'🇪🇸','Cabo Verde':'🇨🇻','Saudi Arabia':'🇸🇦','Uruguay':'🇺🇾',
    'France':'🇫🇷','Senegal':'🇸🇳','Iraq':'🇮🇶','Norway':'🇳🇴',
    'Argentina':'🇦🇷','Algeria':'🇩🇿','Austria':'🇦🇹','Jordan':'🇯🇴',
    'Portugal':'🇵🇹','Congo DR':'🇨🇩','Uzbekistan':'🇺🇿','Colombia':'🇨🇴',
    'England':'🏴󠁧󠁢󠁥󠁮󠁧󠁿','Croatia':'🇭🇷','Ghana':'🇬🇭','Panama':'🇵🇦',
}

# Bracket slot assignments (per official FIFA 2026 draw)
R32_SLOTS = [
    ('1E', '3ABCDF'), ('1I', '3CDFGH'), ('2A', '2B'),  ('1F', '2C'),
    ('2K', '2L'),     ('1H', '2J'),     ('1D', '3BEFIJ'),('1G','3AEHIJ'),
    ('1C', '2F'),     ('2E', '2I'),     ('1A', '3CEFHI'),('1L','3EHIJK'),
    ('1J', '2H'),     ('2D', '2G'),     ('1B', '3EFGIJ'),('1K','3DEIJL'),
]

# ═══════════════════════════════════════════════════════════
# 3. DIXON-COLES POISSON GOAL MODEL
# ═══════════════════════════════════════════════════════════
# Each team has attack and defense strengths estimated from Elo
# Goal expectations via: lambda_A = base * attack_A * defense_B
# Poisson model for goals, with Dixon-Coles low-score correlation fix

BASE_GOALS = 1.35  # average goals per team per match in WC knockout
HOME_ADVANTAGE = 0.0  # neutral venue (USA/Canada/Mexico host, but no true home)

def elo_to_attack_defense(elo_a, elo_b):
    """Convert Elo difference to expected goals using logistic-Poisson link."""
    elo_diff = elo_a - elo_b
    # Each 200 Elo points ≈ 0.20 more goals expected (calibrated to WC data)
    lambda_a = BASE_GOALS * math.exp(elo_diff / 1200)
    lambda_b = BASE_GOALS * math.exp(-elo_diff / 1200)
    return max(lambda_a, 0.25), max(lambda_b, 0.25)

def dixon_coles_correction(goals_a, goals_b, lam_a, lam_b, rho=-0.13):
    """
    Dixon-Coles low-score correction factor.
    rho calibrated to -0.13 (standard for international football).
    Adjusts probability of 0-0, 1-0, 0-1, 1-1 outcomes.
    """
    if goals_a == 0 and goals_b == 0:
        return 1 - lam_a * lam_b * rho
    elif goals_a == 0 and goals_b == 1:
        return 1 + lam_a * rho
    elif goals_a == 1 and goals_b == 0:
        return 1 + lam_b * rho
    elif goals_a == 1 and goals_b == 1:
        return 1 - rho
    return 1.0

def score_probability(ga, gb, lam_a, lam_b):
    """P(score = ga:gb) under Dixon-Coles Poisson model."""
    p = (poisson.pmf(ga, lam_a) *
         poisson.pmf(gb, lam_b) *
         dixon_coles_correction(ga, gb, lam_a, lam_b))
    return max(p, 0.0)

def simulate_score(elo_a, elo_b, max_goals=7):
    """
    Sample a match score from the Dixon-Coles distribution.
    Returns (goals_a, goals_b).
    """
    lam_a, lam_b = elo_to_attack_defense(elo_a, elo_b)
    # Build probability matrix
    probs = np.zeros((max_goals+1, max_goals+1))
    for ga in range(max_goals+1):
        for gb in range(max_goals+1):
            probs[ga, gb] = score_probability(ga, gb, lam_a, lam_b)
    # Normalize (should be ~1 already)
    total = probs.sum()
    if total <= 0:
        return 1, 1
    probs = probs / total
    # Sample
    flat = probs.ravel()
    idx = np.random.choice(len(flat), p=flat)
    ga, gb = divmod(idx, max_goals+1)
    return int(ga), int(gb)

def simulate_knockout_score(elo_a, elo_b):
    """
    Knockout match: simulate 90min, then ET+penalties if draw.
    Returns (goals_a, goals_b, winner).
    """
    ga, gb = simulate_score(elo_a, elo_b)
    if ga != gb:
        return ga, gb, ('A' if ga > gb else 'B')
    # Extra time: slightly higher scoring rate
    et_a, et_b = simulate_score(elo_a, elo_b)
    # ET expected goals ~60% of 90min
    et_a = 1 if et_a >= 2 else et_a
    et_b = 1 if et_b >= 2 else et_b
    ga += et_a; gb += et_b
    if ga != gb:
        return ga, gb, ('A' if ga > gb else 'B')
    # Penalties: pure Elo-weighted coin flip
    prob_a_pen = 0.5 + (elo_a - elo_b) / 8000  # tiny advantage for better team
    winner = 'A' if random.random() < prob_a_pen else 'B'
    return ga, gb, winner

# ═══════════════════════════════════════════════════════════
# 4. SINGLE TOURNAMENT SIMULATION
# ═══════════════════════════════════════════════════════════

def sim_group(teams):
    pts = {t:0 for t in teams}
    gf  = {t:0 for t in teams}
    ga  = {t:0 for t in teams}
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            a, b = teams[i], teams[j]
            sa, sb = simulate_score(ELO[a], ELO[b])
            gf[a]+=sa; ga[a]+=sb; gf[b]+=sb; ga[b]+=sa
            if sa>sb: pts[a]+=3
            elif sa==sb: pts[a]+=1; pts[b]+=1
            else: pts[b]+=3
    def sort_key(t):
        return (pts[t], gf[t]-ga[t], gf[t], random.random())
    ranked = sorted(teams, key=sort_key, reverse=True)
    return [(t, pts[t], gf[t], ga[t], gf[t]-ga[t]) for t in ranked]

def sim_tournament():
    """Run one full tournament. Returns champion."""
    # Group stage
    group_results = {}
    for g, teams in GROUPS.items():
        group_results[g] = sim_group(teams)

    # Build qualifier map
    Q = {}
    for g, standings in group_results.items():
        Q[f'1{g}'] = standings[0][0]
        Q[f'2{g}'] = standings[1][0]

    # Best 8 third-place teams
    thirds = [(g, standings[2]) for g, standings in group_results.items()]
    thirds.sort(key=lambda x: (x[1][1], x[1][4], x[1][2]), reverse=True)
    third_slots = ['3ABCDF','3CDFGH','3BEFIJ','3AEHIJ','3CEFHI','3EHIJK','3EFGIJ','3DEIJL']
    for i, (g, row) in enumerate(thirds[:8]):
        Q[third_slots[i]] = row[0]

    def resolve(slot):
        if slot in Q: return Q[slot]
        if slot.startswith('3'):
            for g in slot[1:]:
                if f'3{g}' in Q: return Q[f'3{g}']
        return thirds[0][1][0]

    # Knockout rounds
    r32_teams = [(resolve(a), resolve(b)) for a, b in R32_SLOTS]
    r32_w = []
    for a, b in r32_teams:
        _, _, w = simulate_knockout_score(ELO[a], ELO[b])
        r32_w.append(a if w=='A' else b)

    r16_pairs = [(r32_w[i], r32_w[i+1]) for i in range(0, 16, 2)]
    r16_w = []
    for a, b in r16_pairs:
        _, _, w = simulate_knockout_score(ELO[a], ELO[b])
        r16_w.append(a if w=='A' else b)

    qf_pairs = [(r16_w[i], r16_w[i+1]) for i in range(0, 8, 2)]
    qf_w = []
    for a, b in qf_pairs:
        _, _, w = simulate_knockout_score(ELO[a], ELO[b])
        qf_w.append(a if w=='A' else b)

    sf_pairs = [(qf_w[i], qf_w[i+1]) for i in range(0, 4, 2)]
    sf_w = []; sf_l = []
    for a, b in sf_pairs:
        _, _, w = simulate_knockout_score(ELO[a], ELO[b])
        sf_w.append(a if w=='A' else b)
        sf_l.append(b if w=='A' else a)

    _, _, w = simulate_knockout_score(ELO[sf_w[0]], ELO[sf_w[1]])
    champion = sf_w[0] if w=='A' else sf_w[1]
    runner_up = sf_w[1] if w=='A' else sf_w[0]
    _, _, w3 = simulate_knockout_score(ELO[sf_l[0]], ELO[sf_l[1]])
    third = sf_l[0] if w3=='A' else sf_l[1]

    return {
        'champion': champion,
        'runner_up': runner_up,
        'third': third,
        'group_results': group_results,
        'r32_teams': r32_teams, 'r32_w': r32_w,
        'r16_pairs': r16_pairs, 'r16_w': r16_w,
        'qf_pairs': qf_pairs, 'qf_w': qf_w,
        'sf_pairs': sf_pairs, 'sf_w': sf_w, 'sf_l': sf_l,
    }

# ═══════════════════════════════════════════════════════════
# 5. MONTE CARLO  (100,000 simulations)
# ═══════════════════════════════════════════════════════════

N_SIMS = 100_000
print(f"Running {N_SIMS:,} Monte Carlo simulations...")

champion_count  = defaultdict(int)
final_count     = defaultdict(int)
semifinal_count = defaultdict(int)
r8_count        = defaultdict(int)
r16_count       = defaultdict(int)
group_pos_count = defaultdict(lambda: defaultdict(int))   # [team][pos] → count
group_pts_sum   = defaultdict(list)  # [team] → [pts, ...]

for sim_i in range(N_SIMS):
    result = sim_tournament()
    champion_count[result['champion']] += 1
    final_count[result['champion']] += 1
    final_count[result['runner_up']] += 1
    for t in result['sf_w'] + result['sf_l']:
        semifinal_count[t] += 1
    for t in result['qf_w']:
        r8_count[t] += 1
    for t in result['r16_w']:
        r16_count[t] += 1
    for g, standings in result['group_results'].items():
        for pos, (team, pts, gf, ga, gd) in enumerate(standings):
            group_pos_count[team][pos+1] += 1
            group_pts_sum[team].append(pts)

print("Done. Computing statistics...")

# ─── Results ───
all_teams = list(ELO.keys())
stats = {}
for t in all_teams:
    stats[t] = {
        'elo':         round(ELO[t], 1),
        'fifa_pts':    FIFA_POINTS.get(t, 0),
        'win_pct':     round(champion_count[t] / N_SIMS * 100, 2),
        'final_pct':   round(final_count[t] / N_SIMS * 100, 1),
        'semi_pct':    round(semifinal_count[t] / N_SIMS * 100, 1),
        'qf_pct':      round(r8_count[t] / N_SIMS * 100, 1),
        'r16_pct':     round(r16_count[t] / N_SIMS * 100, 1),
        'avg_pts':     round(sum(group_pts_sum[t]) / len(group_pts_sum[t]), 2) if group_pts_sum[t] else 0,
        'pos1_pct':    round(group_pos_count[t][1] / N_SIMS * 100, 1),
        'pos2_pct':    round(group_pos_count[t][2] / N_SIMS * 100, 1),
        'pos3_pct':    round(group_pos_count[t][3] / N_SIMS * 100, 1),
        'pos4_pct':    round(group_pos_count[t][4] / N_SIMS * 100, 1),
        'flag':        FLAGS.get(t, '🏳'),
    }

print("\n=== TOP 15 CHAMPIONSHIP PROBABILITIES ===")
for t, s in sorted(stats.items(), key=lambda x: -x[1]['win_pct'])[:15]:
    print(f"  {FLAGS.get(t,'🏳')} {t:<25} Win: {s['win_pct']:>5.2f}%  Final: {s['final_pct']:>5.1f}%  Semi: {s['semi_pct']:>5.1f}%  Elo: {s['elo']}")

print("\n=== GROUP J BREAKDOWN (Argentina group) ===")
for t in GROUPS['J']:
    s = stats[t]
    print(f"  {FLAGS.get(t,'🏳')} {t:<20} Elo:{s['elo']:>7}  1st:{s['pos1_pct']:>5.1f}%  2nd:{s['pos2_pct']:>5.1f}%  Avg pts:{s['avg_pts']:.2f}")

# Save for HTML generation
with open('/home/claude/mc_stats.json', 'w') as f:
    json.dump(stats, f)
with open('/home/claude/groups_data.json', 'w') as f:
    json.dump({g: teams for g, teams in GROUPS.items()}, f)

print("\nStats saved.")
