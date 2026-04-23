"""
Generate the final HTML report from Monte Carlo stats.
"""
import json, math

with open('/home/claude/mc_stats.json') as f:
    stats = json.load(f)

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

# Predicted group winner = team with highest 1st-place %
def predicted_standing(group):
    teams = GROUPS[group]
    return sorted(teams, key=lambda t: (
        stats[t]['pos1_pct'] if stats[t]['pos1_pct'] > 0 else 0,
        stats[t]['avg_pts']
    ), reverse=True)

# Most likely bracket path (deterministic single-sim based on Elo)
# Use predicted group winners for bracket display
bracket_q = {}
for g in GROUPS:
    ranked = predicted_standing(g)
    bracket_q[f'1{g}'] = ranked[0]
    bracket_q[f'2{g}'] = ranked[1]

third_place_teams = []
for g in GROUPS:
    ranked = predicted_standing(g)
    third_place_teams.append((g, ranked[2], stats[ranked[2]]['avg_pts'], stats[ranked[2]]['elo']))
third_place_teams.sort(key=lambda x: (x[2], x[3]), reverse=True)
third_slots = ['3ABCDF','3CDFGH','3BEFIJ','3AEHIJ','3CEFHI','3EHIJK','3EFGIJ','3DEIJL']
for i, (g, team, _, _) in enumerate(third_place_teams[:8]):
    bracket_q[third_slots[i]] = team

def resolve(slot):
    if slot in bracket_q: return bracket_q[slot]
    if slot.startswith('3'):
        for g in slot[1:]:
            if f'3{g}' in bracket_q: return bracket_q[f'3{g}']
    return third_place_teams[0][1]

def ko_winner(a, b):
    """Pick winner based on highest win probability (Elo)."""
    elo_a = stats[a]['elo']
    elo_b = stats[b]['elo']
    return a if elo_a >= elo_b else b

R32_SLOTS = [
    ('1E','3ABCDF'),('1I','3CDFGH'),('2A','2B'),('1F','2C'),
    ('2K','2L'),('1H','2J'),('1D','3BEFIJ'),('1G','3AEHIJ'),
    ('1C','2F'),('2E','2I'),('1A','3CEFHI'),('1L','3EHIJK'),
    ('1J','2H'),('2D','2G'),('1B','3EFGIJ'),('1K','3DEIJL'),
]

r32_pairs = [(resolve(a), resolve(b)) for a,b in R32_SLOTS]
r32_w = [ko_winner(a,b) for a,b in r32_pairs]
r16_pairs = [(r32_w[i], r32_w[i+1]) for i in range(0,16,2)]
r16_w = [ko_winner(a,b) for a,b in r16_pairs]
qf_pairs = [(r16_w[i], r16_w[i+1]) for i in range(0,8,2)]
qf_w = [ko_winner(a,b) for a,b in qf_pairs]
sf_pairs = [(qf_w[i], qf_w[i+1]) for i in range(0,4,2)]
sf_w = [ko_winner(a,b) for a,b in sf_pairs]
sf_l = [sf_pairs[i][1] if sf_w[i]==sf_pairs[i][0] else sf_pairs[i][0] for i in range(2)]
champion = ko_winner(sf_w[0], sf_w[1])
runner_up = sf_w[1] if champion==sf_w[0] else sf_w[0]
third_f = ko_winner(sf_l[0], sf_l[1])

def f(t): return FLAGS.get(t,'🏳')
def s(t): return stats.get(t, {})
def wp(t): return s(t).get('win_pct', 0)
def bar(pct, color='#e8b84b', max_w=100):
    w = min(pct/max_w*100, 100)
    return f'<div style="height:4px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden"><div style="height:4px;width:{w:.1f}%;background:{color};border-radius:2px"></div></div>'

def pct_color(p):
    if p >= 40: return '#3ecf8e'
    if p >= 25: return '#4f9ef8'
    if p >= 10: return '#e8b84b'
    return '#8a8f9e'

# ── Build HTML ──
html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FIFA World Cup 2026 — Monte Carlo Predictor</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{--bg:#0a0c10;--bg2:#111318;--bg3:#181b22;--border:rgba(255,255,255,0.08);--border2:rgba(255,255,255,0.15);--text:#f0f0f0;--text2:#8a8f9e;--text3:#555a68;--gold:#e8b84b;--gold2:#c99a35;--green:#3ecf8e;--blue:#4f9ef8;--red:#f06060;--teal:#2dd4bf;}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;min-height:100vh;}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 80% 50% at 20% 10%,rgba(232,184,75,.04) 0%,transparent 60%),radial-gradient(ellipse 60% 40% at 80% 90%,rgba(79,158,248,.04) 0%,transparent 60%);pointer-events:none;z-index:0;}
.wrap{max-width:1200px;margin:0 auto;padding:0 20px;position:relative;z-index:1;}
/* Hero */
.hero{padding:44px 0 28px;border-bottom:1px solid var(--border);margin-bottom:28px;}
.hero-inner{display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:14px;}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:clamp(44px,7vw,88px);line-height:.9;letter-spacing:2px;}
.hero-title span{color:var(--gold);}
.hero-meta{text-align:right;}
.hero-meta p{font-size:12px;color:var(--text2);line-height:1.9;}
.hero-meta strong{color:var(--text);}
.badge{display:inline-block;margin-top:6px;padding:3px 10px;background:rgba(232,184,75,.12);border:1px solid rgba(232,184,75,.25);border-radius:4px;font-size:11px;color:var(--gold);font-family:'DM Mono',monospace;}
/* Tabs */
.tabs{display:flex;gap:2px;margin-bottom:26px;background:var(--bg2);padding:4px;border-radius:8px;width:fit-content;border:1px solid var(--border);flex-wrap:wrap;}
.tab-btn{padding:7px 18px;background:transparent;color:var(--text2);border:none;border-radius:6px;font-size:13px;font-family:'DM Sans',sans-serif;font-weight:500;cursor:pointer;transition:all .15s;white-space:nowrap;}
.tab-btn.active{background:var(--bg3);color:var(--text);}
.tab-btn:hover:not(.active){color:var(--text);}
.panel{display:none;}.panel.active{display:block;}
/* Data note */
.note{background:rgba(232,184,75,.06);border:1px solid rgba(232,184,75,.15);border-radius:8px;padding:12px 16px;margin-bottom:22px;font-size:12px;color:var(--text2);line-height:1.75;}
.note strong{color:var(--gold);}
/* Groups */
.groups-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px;}
.gcard{background:var(--bg2);border:1px solid var(--border);border-radius:10px;overflow:hidden;transition:border-color .2s;}
.gcard:hover{border-color:var(--border2);}
.ghead{padding:9px 13px;background:var(--bg3);display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);}
.glabel{font-family:'Bebas Neue',sans-serif;font-size:18px;color:var(--gold);letter-spacing:1px;}
.gsub{font-size:10px;color:var(--text3);font-family:'DM Mono',monospace;}
.gtable{width:100%;border-collapse:collapse;}
.gtable th{padding:5px 11px;font-size:10px;color:var(--text3);font-weight:400;text-align:right;font-family:'DM Mono',monospace;border-bottom:1px solid var(--border);}
.gtable th:first-child{text-align:left;}
.gtable td{padding:6px 11px;font-size:11px;text-align:right;border-top:1px solid rgba(255,255,255,.04);}
.gtable td:first-child{text-align:left;}
.tcell{display:flex;align-items:center;gap:7px;}
.fl{font-size:15px;}
.tn{font-size:12px;}
.qdot{width:5px;height:5px;border-radius:50%;flex-shrink:0;}
.q1{background:var(--blue);}.q2{background:var(--teal);}.q3{background:var(--gold);opacity:.7;}
.qno{width:5px;}
.mono{font-family:'DM Mono',monospace;}
.grn{color:var(--green);}.blu{color:var(--blue);}.gld{color:var(--gold);}.dim{color:var(--text3);}
.leg{display:flex;gap:18px;margin-bottom:14px;flex-wrap:wrap;}
.li{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--text2);}
.ld{width:7px;height:7px;border-radius:50%;}
/* Odds */
.odds-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:8px;}
.orow{display:flex;align-items:center;gap:10px;background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:8px 13px;transition:border-color .15s;}
.orow:hover{border-color:var(--border2);}
.orank{font-family:'DM Mono',monospace;font-size:11px;color:var(--text3);width:20px;}
.oflag{font-size:17px;}
.oname{flex:1;font-size:13px;}
.owin{font-family:'DM Mono',monospace;font-size:13px;font-weight:500;color:var(--gold);min-width:50px;text-align:right;}
.opcts{display:flex;gap:8px;font-size:10px;color:var(--text3);font-family:'DM Mono',monospace;min-width:170px;justify-content:flex-end;}
.opct{display:flex;flex-direction:column;align-items:center;gap:1px;}
.opct span:first-child{font-size:9px;color:var(--text3);}
.opct span:last-child{color:var(--text2);}
/* Bracket */
.bscroll{overflow-x:auto;padding-bottom:12px;}
.brows{display:flex;gap:6px;min-width:880px;}
.rcol{display:flex;flex-direction:column;flex:1;min-width:125px;}
.rtit{font-size:9px;color:var(--text3);text-align:center;padding:0 4px 9px;border-bottom:1px solid var(--border);margin-bottom:7px;font-family:'DM Mono',monospace;letter-spacing:.05em;text-transform:uppercase;}
.rms{display:flex;flex-direction:column;justify-content:space-around;flex:1;gap:4px;padding:0 2px;}
.mc{background:var(--bg2);border:1px solid var(--border);border-radius:6px;padding:5px 8px;}
.mc.fin{border-color:rgba(232,184,75,.35);background:rgba(232,184,75,.04);}
.mr{display:flex;align-items:center;gap:4px;padding:2px 0;}
.mfl{font-size:11px;}.mn{flex:1;font-size:10px;color:var(--text2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.mn.w{color:var(--text);font-weight:600;}.mw{font-size:10px;color:var(--text3);min-width:36px;text-align:right;font-family:'DM Mono',monospace;font-size:9px;}
.mw.w{color:var(--gold);}
/* Winner */
.wbox{margin-top:22px;background:linear-gradient(135deg,rgba(232,184,75,.09) 0%,rgba(232,184,75,.02) 100%);border:1px solid rgba(232,184,75,.28);border-radius:12px;padding:26px;display:flex;align-items:center;gap:22px;flex-wrap:wrap;}
.wtroph{font-size:50px;}
.wtxt h2{font-family:'Bebas Neue',sans-serif;font-size:38px;color:var(--gold);letter-spacing:2px;line-height:1;}
.wtxt p{color:var(--text2);font-size:12px;margin-top:4px;}
.podium{display:flex;gap:20px;margin-left:auto;flex-wrap:wrap;}
.pm{text-align:center;}.pm-medal{font-size:22px;}.pm-name{font-size:11px;color:var(--text2);margin-top:3px;}.pm-pos{font-size:10px;color:var(--text3);}
/* Method */
.mgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:12px;}
.mcard{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:16px 18px;}
.micon{font-size:22px;margin-bottom:8px;}.mtit{font-size:13px;font-weight:600;color:var(--text);margin-bottom:5px;}
.mdesc{font-size:12px;color:var(--text2);line-height:1.75;}
.mdesc code{font-family:'DM Mono',monospace;background:rgba(255,255,255,.07);padding:1px 5px;border-radius:3px;font-size:11px;color:var(--teal);}
/* Footer */
.foot{margin-top:56px;padding:20px 0;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;}
.foot p{font-size:11px;color:var(--text3);}
.foot a{color:var(--text2);text-decoration:none;}
.foot a:hover{color:var(--gold);}
@media(max-width:600px){.hero-title{font-size:44px;}.groups-grid,.odds-grid,.mgrid{grid-template-columns:1fr;}.wbox{flex-direction:column;}.podium{margin-left:0;}}
</style>
</head>
<body>
<div class="wrap">
'''

# ── Hero
html += f'''
<header class="hero">
  <div class="hero-inner">
    <div>
      <div class="hero-title">FIFA WORLD<br>CUP <span>2026</span></div>
      <div style="margin-top:10px;font-size:13px;color:var(--text2)">Monte Carlo AI Predictor · 50,000 simulations</div>
    </div>
    <div class="hero-meta">
      <p><strong>48 teams</strong> · 12 groups · 104 matches</p>
      <p><strong>894 qualifying matches</strong> processed · Elo-adjusted</p>
      <p>FIFA Rankings: <strong>April 1, 2026</strong> (France #1, Spain #2, Argentina #3)</p>
      <p>Model: <strong>Dixon-Coles Poisson · Elo · Monte Carlo</strong></p>
      <div class="badge">🇺🇸🇨🇦🇲🇽 June 11 – July 19, 2026</div>
    </div>
  </div>
</header>

<div class="tabs">
  <button class="tab-btn active" onclick="showTab('odds')">🏅 Win Odds</button>
  <button class="tab-btn" onclick="showTab('groups')">📊 Groups</button>
  <button class="tab-btn" onclick="showTab('bracket')">🏆 Bracket</button>
  <button class="tab-btn" onclick="showTab('method')">🔬 Methodology</button>
</div>
'''

# ══════════════════════════════════
# PANEL: WIN ODDS
# ══════════════════════════════════
html += '<div class="panel active" id="panel-odds">'
html += '''<div class="note">
  <strong>Monte Carlo championship probabilities</strong> — based on 50,000 full tournament simulations using Elo ratings,
  Dixon-Coles Poisson goal model, and official FIFA April 2026 rankings.
  Probabilities reflect how often each team wins across all 50,000 runs.
  <strong>Spain leads</strong> at 26.4%, followed by France (22.7%) and England (18.1%).
</div>'''
html += '<div class="odds-grid">'
all_sorted = sorted(stats.items(), key=lambda x: -x[1]['win_pct'])
for i, (team, s) in enumerate(all_sorted):
    wp = s['win_pct']
    col = '#e8b84b' if wp >= 15 else '#4f9ef8' if wp >= 5 else '#3ecf8e' if wp >= 1 else '#555a68'
    maxwp = all_sorted[0][1]['win_pct']
    bw = min(wp/maxwp*100, 100)
    html += f'''<div class="orow">
      <span class="orank">{i+1}</span>
      <span class="oflag">{f(team)}</span>
      <span class="oname">{team}</span>
      <div style="flex:1;padding:0 8px">
        <div style="height:3px;background:rgba(255,255,255,.08);border-radius:2px;overflow:hidden">
          <div style="height:3px;width:{bw:.1f}%;background:{col};border-radius:2px"></div>
        </div>
      </div>
      <span class="owin" style="color:{col}">{wp:.2f}%</span>
      <div class="opcts">
        <div class="opct"><span>Final</span><span>{s["final_pct"]}%</span></div>
        <div class="opct"><span>Semi</span><span>{s["semi_pct"]}%</span></div>
        <div class="opct"><span>QF</span><span>{s["qf_pct"]}%</span></div>
        <div class="opct"><span>Elo</span><span>{s["elo"]:.0f}</span></div>
      </div>
    </div>'''
html += '</div></div>'

# ══════════════════════════════════
# PANEL: GROUPS
# ══════════════════════════════════
html += '<div class="panel" id="panel-groups">'
html += '''<div class="note">
  Group predictions use <strong>Monte Carlo 1st/2nd-place finish probabilities</strong> from 50,000 simulations.
  <strong>Avg Pts</strong> = average simulated group-stage points. Teams ordered by 1st-place probability.
  Blue dot = predicted 1st · Teal = predicted 2nd · Gold = possible 3rd-place qualifier.
</div>'''
html += '<div class="leg"><div class="li"><div class="ld" style="background:var(--blue)"></div>1st (advances)</div><div class="li"><div class="ld" style="background:var(--teal)"></div>2nd (advances)</div><div class="li"><div class="ld" style="background:var(--gold);opacity:.7"></div>3rd (best 8 advance)</div></div>'
html += '<div class="groups-grid">'
for g, teams in GROUPS.items():
    ranked = sorted(teams, key=lambda t: (stats[t]['pos1_pct'], stats[t]['avg_pts']), reverse=True)
    html += f'''<div class="gcard">
      <div class="ghead"><span class="glabel">Group {g}</span><span class="gsub">MC Prediction</span></div>
      <table class="gtable">
        <tr><th>Team</th><th>1st%</th><th>2nd%</th><th>AvgPts</th><th>Elo</th></tr>'''
    for i, team in enumerate(ranked):
        s2 = stats[team]
        dot = f'<div class="qdot q1"></div>' if i==0 else f'<div class="qdot q2"></div>' if i==1 else f'<div class="qdot q3"></div>' if i==2 else '<div class="qno"></div>'
        c1 = 'grn' if i==0 else 'blu' if i==1 else 'dim'
        html += f'''<tr>
          <td><div class="tcell">{dot}<span class="fl">{f(team)}</span><span class="tn">{team}</span></div></td>
          <td class="mono {c1}">{s2["pos1_pct"]}%</td>
          <td class="mono dim">{s2["pos2_pct"]}%</td>
          <td class="mono" style="color:var(--text2)">{s2["avg_pts"]:.1f}</td>
          <td class="mono dim">{s2["elo"]:.0f}</td>
        </tr>'''
    html += '</table></div>'
html += '</div></div>'

# ══════════════════════════════════
# PANEL: BRACKET
# ══════════════════════════════════
def mk_match(a, b, w, show_pct=True):
    def wp_str(t):
        if not show_pct: return ''
        return f'{stats[t]["win_pct"]:.1f}%' if stats[t]['win_pct'] >= 0.5 else ''
    wa = a==w; wb = b==w
    return f'''<div class="mc">
      <div class="mr"><span class="mfl">{f(a)}</span><span class="mn{" w" if wa else ""}">{a}</span><span class="mw{" w" if wa else ""}">{wp_str(a)}</span></div>
      <div class="mr"><span class="mfl">{f(b)}</span><span class="mn{" w" if wb else ""}">{b}</span><span class="mw{" w" if wb else ""}">{wp_str(b)}</span></div>
    </div>'''

def mk_final_match(a, b, w):
    wa = a==w; wb = b==w
    return f'''<div class="mc fin">
      <div class="mr"><span class="mfl">{f(a)}</span><span class="mn{" w" if wa else ""}">{a}</span><span class="mw{" w" if wa else ""}">{stats[a]["win_pct"]:.1f}%</span></div>
      <div class="mr"><span class="mfl">{f(b)}</span><span class="mn{" w" if wb else ""}">{b}</span><span class="mw{" w" if wb else ""}">{stats[b]["win_pct"]:.1f}%</span></div>
    </div>'''

html += '<div class="panel" id="panel-bracket">'
html += f'''<div class="note">
  Most likely bracket path based on <strong>highest Elo rating progression</strong>.
  Numbers next to teams = <strong>championship win probability</strong> from Monte Carlo.
  Predicted champion: <strong>{f(champion)} {champion}</strong> ({stats[champion]["win_pct"]:.1f}% win probability).
</div>'''

html += '<div class="bscroll"><div class="brows">'
# R32
html += '<div class="rcol"><div class="rtit">Round of 32 (16)</div><div class="rms">'
for a, b in r32_pairs:
    w = ko_winner(a,b)
    html += mk_match(a, b, w, show_pct=False)
html += '</div></div>'
# R16
html += '<div class="rcol"><div class="rtit">Round of 16 (8)</div><div class="rms">'
for a, b in r16_pairs:
    w = ko_winner(a,b)
    html += mk_match(a, b, w)
html += '</div></div>'
# QF
html += '<div class="rcol"><div class="rtit">Quarter-finals (4)</div><div class="rms">'
for a, b in qf_pairs:
    w = ko_winner(a,b)
    html += mk_match(a, b, w)
html += '</div></div>'
# SF
html += '<div class="rcol"><div class="rtit">Semi-finals (2)</div><div class="rms">'
for a, b in sf_pairs:
    w = ko_winner(a,b)
    html += mk_match(a, b, w)
html += '</div></div>'
# Final
html += '<div class="rcol"><div class="rtit">Final (1)</div><div class="rms">'
html += mk_final_match(sf_w[0], sf_w[1], champion)
html += '</div></div>'
html += '</div></div>'

html += f'''<div class="wbox">
  <div class="wtroph">🏆</div>
  <div class="wtxt">
    <h2>{f(champion)} {champion}</h2>
    <p>Predicted 2026 FIFA World Cup Champions · {stats[champion]["win_pct"]:.1f}% championship probability</p>
    <p style="margin-top:4px;font-size:11px;color:var(--text3)">Based on 50,000 Monte Carlo simulations · Dixon-Coles Poisson · Elo ratings</p>
  </div>
  <div class="podium">
    <div class="pm"><div class="pm-medal">🥈</div><div class="pm-name">{f(runner_up)} {runner_up}</div><div class="pm-pos">Runner-up · {stats[runner_up]["win_pct"]:.1f}%</div></div>
    <div class="pm"><div class="pm-medal">🥉</div><div class="pm-name">{f(third_f)} {third_f}</div><div class="pm-pos">3rd place · {stats[third_f]["win_pct"]:.1f}%</div></div>
  </div>
</div>
</div>'''

# ══════════════════════════════════
# PANEL: METHODOLOGY
# ══════════════════════════════════
html += '''<div class="panel" id="panel-method">
<div class="mgrid">
  <div class="mcard"><div class="micon">📐</div><div class="mtit">Elo Rating System</div>
  <div class="mdesc">Starting point: official FIFA/Coca-Cola Elo ratings, April 1 2026 (France #1 at 1,879 pts, Spain #2 at 1,876). Then updated by processing all 894 qualifying matches using the World Football Elo method: <code>ΔElo = K × GDM × (W − Eₐ)</code> where K=40 (qualifying), GDM = goal-difference multiplier (1.0–2.5), Eₐ = expected result. Each match moves Elo toward actual result weighted by upset size.</div></div>

  <div class="mcard"><div class="micon">🎯</div><div class="mtit">Dixon-Coles Poisson Model</div>
  <div class="mdesc">Goals are modeled as Poisson-distributed. Expected goals: <code>λA = 1.35 × exp(ΔElo/1200)</code>. The Dixon-Coles correction adjusts probabilities for low-scoring outcomes (0-0, 1-0, 0-1, 1-1) using correlation parameter ρ = −0.13, calibrated to international football. This prevents over-representation of draws and makes the score distribution more realistic than naive Poisson.</div></div>

  <div class="mcard"><div class="micon">🔁</div><div class="mtit">Monte Carlo (50,000 runs)</div>
  <div class="mdesc">Each of 50,000 simulations runs the full tournament: 12 groups (round-robin, 3 matches each), determines the 32 qualifiers (top 2 per group + best 8 third-place), then runs Round of 32 → R16 → QF → SF → Final. Knockout draws include extra time and penalty shootout logic. Final stats = aggregated frequency across all 50,000 runs.</div></div>

  <div class="mcard"><div class="micon">⚽</div><div class="mtit">Knockout Simulation</div>
  <div class="mdesc">Knockout matches use the same Poisson model for 90 minutes. If tied, extra time is simulated with ~60% of normal expected goals (fatigue factor). If still tied, penalties are decided by a coin flip with tiny Elo-based tilt: <code>P(A wins pens) = 0.5 + (EloA − EloB)/8000</code>. This means even a 200-point Elo gap only shifts penalty odds by ~2.5%.</div></div>

  <div class="mcard"><div class="micon">📂</div><div class="mtit">Match Data (894 games)</div>
  <div class="mdesc">Qualifying results parsed from uploaded file covering AFC (rounds 1–2), CONMEBOL Eliminatorias, UEFA Nations League + qualifying, CAF qualifying, CONCACAF, and OFC qualifying. Oct 2023 – March 2026. Used to update Elo from official FIFA starting points. Coverage: 45 of 48 WC teams have data; Mexico, USA, Canada start from FIFA ranking only (auto-qualified as hosts).</div></div>

  <div class="mcard"><div class="micon">⚠️</div><div class="mtit">Known Limitations</div>
  <div class="mdesc">No player-level data (injuries, suspensions, form). No host advantage modeled (USA/Canada/Mexico). European teams have fewer qualifying matches in dataset (only 6–8 games) vs South American/Asian teams (16–20), so Elo updates are asymmetric. Confederation calibration is simplified. Third-place tiebreakers use alphabetical fallback. Results are probabilistic, not deterministic.</div></div>
</div>
</div>'''

# Footer & tabs JS
html += f'''
<footer class="foot">
  <p>Data: <a href="https://inside.fifa.com/news/france-1st-fifa-coca-cola-world-ranking-april-2026" target="_blank">FIFA April 2026 Rankings</a> · 894 qualifying matches · <a href="https://en.wikipedia.org/wiki/2026_FIFA_World_Cup" target="_blank">Wikipedia</a></p>
  <p>Model: Elo + Dixon-Coles Poisson + Monte Carlo · Python (scipy, numpy) · For entertainment</p>
</footer>
</div>
<script>
function showTab(name) {{
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-'+name).classList.add('active');
  event.target.classList.add('active');
}}
</script>
</body>
</html>'''

with open('/home/claude/wc2026_predictor.html', 'w') as f:
    f.write(html)
print(f"HTML written: {len(html):,} chars")
