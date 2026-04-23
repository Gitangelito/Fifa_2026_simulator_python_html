# ⚽ FIFA World Cup 2026 — Monte Carlo Predictor
### Predictor Monte Carlo — Copa Mundial FIFA 2026

<div align="center">

![FIFA World Cup 2026](https://img.shields.io/badge/FIFA%20World%20Cup-2026-gold?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![Monte Carlo](https://img.shields.io/badge/Monte%20Carlo-50%2C000%20sims-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-Personal%20%2F%20Educational-orange?style=for-the-badge)

**🇺🇸 English** · **🇪🇸 Español**

*Created by **Angel Luyo M** · For fun & learning · No commercial purpose*

</div>

---

## 🇺🇸 English

### What is this?

A statistical predictor for the **2026 FIFA World Cup** (USA 🇺🇸 · Canada 🇨🇦 · Mexico 🇲🇽) powered by:

- **Elo ratings** derived from official FIFA April 2026 rankings (France #1, Spain #2, Argentina #3)
- **894 real qualifying matches** parsed from AFC, CONMEBOL, UEFA, CAF, CONCACAF, and OFC qualifying campaigns (Oct 2023 – Mar 2026)
- **Dixon-Coles Poisson model** for statistically accurate score simulation
- **Monte Carlo simulation** — 50,000 full tournament runs to compute championship probabilities

The result is a fully interactive HTML app that shows win probabilities, group predictions, and a full knockout bracket — all recalculated live in your browser every time you hit **Run Simulation**.

---

### 📊 How It Works

#### 1. Elo Ratings
Starting from official **FIFA/Coca-Cola Elo points (April 1, 2026)**, each team's rating is updated by processing all 894 qualifying match results using the **World Football Elo** formula:

```
ΔElo = K × GDM × (W − Eₐ)
```

- `K = 40` (qualifying match importance weight)
- `GDM` = Goal Difference Multiplier (1.0 for draws/1-goal wins, up to 2.5 for large wins)
- `W` = actual result (1 = win, 0.5 = draw, 0 = loss)
- `Eₐ` = expected result based on Elo difference

#### 2. Dixon-Coles Poisson Goal Model
Each match generates a statistically realistic scoreline. Expected goals per team:

```
λ_A = 1.35 × exp(ΔElo / 1200)
λ_B = 1.35 × exp(-ΔElo / 1200)
```

The **Dixon-Coles correction** (ρ = −0.13) fixes the known over-representation of low-scoring outcomes (0-0, 1-0, 0-1, 1-1) in naive Poisson models — making score distributions match real international football data.

#### 3. Knockout Logic
- **90 minutes**: Poisson score simulation
- **Extra time**: If tied, ~60% goal rate (fatigue factor applied)
- **Penalties**: Near-random with tiny Elo tilt — `P(A wins) = 0.5 + (EloA − EloB) / 8000`

#### 4. Monte Carlo (50,000 runs)
Runs the entire 48-team tournament end-to-end 50,000 times:
- 12 group round-robins (3 matches each)
- Determine 32 qualifiers (top 2 per group + best 8 third-place teams)
- Round of 32 → Round of 16 → Quarter-finals → Semi-finals → Final

Final probabilities are aggregated frequencies across all runs — so a team's "win %" means they won the tournament in that percentage of all 50,000 simulations.

---

### 🚀 Installation & Usage

#### Option A — Just open the HTML (no install needed)
```bash
# Download and open in any browser — no server required
open wc2026_predictor.html
```

The HTML file is **fully self-contained** — all simulation logic runs in JavaScript in your browser. Click **▶ Run Simulation** to run fresh iterations on top of the pre-loaded 50,000-run Python baseline.

#### Option B — Run the Python engine locally
```bash
# Install dependencies
pip install numpy scipy

# Run Monte Carlo simulation (generates mc_stats.json)
python3 wc2026_montecarlo.py

# Generate fresh HTML report from results
python3 generate_html.py

# Open the output
open wc2026_predictor.html
```

Requirements: Python 3.8+ · numpy · scipy · `fifa_all_matches` data file

---

### 📁 File Structure

```
wc2026-predictor/
├── wc2026_predictor.html    # Standalone interactive app (open in browser)
├── wc2026_montecarlo.py     # Python Monte Carlo simulation engine
├── generate_html.py         # HTML report generator from Python results
├── fifa_all_matches         # Raw match data (894 qualifying games)
├── README.md                # This file
```

---

### 📈 Sample Results (50,000 simulations)

| 🏳️ Team | Win % | Final % | Semi % | Elo |
|---|---|---|---|---|
| 🇪🇸 Spain | 26.37% | 38.7% | 55.5% | 1877 |
| 🇫🇷 France | 22.73% | 34.4% | 50.8% | 1866 |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | 18.10% | 30.4% | 44.3% | 1843 |
| 🇲🇦 Morocco | 7.09% | 15.6% | 27.8% | 1771 |
| 🇦🇷 Argentina | 6.74% | 15.7% | 29.9% | 1767 |
| 🇳🇱 Netherlands | 4.97% | 11.6% | 23.9% | 1747 |
| 🇵🇹 Portugal | 3.72% | 9.9% | 22.1% | 1723 |

> Results vary with each simulation run — these are aggregate probabilities, not fixed predictions.

---

### ⚠️ Disclaimer

> **This project is for entertainment and educational purposes only.**
> It does not constitute professional sports analysis, betting advice, or official FIFA predictions.
> Results are purely probabilistic simulations based on publicly available data.
> Created for fun by **Angel Luyo M** — not affiliated with FIFA or any sports organization.
> **Do not use for gambling or wagering decisions.**

---

### 📜 License & Copyright

© 2026 **Angel Luyo M**. All rights reserved.

This project was created for **personal and educational use only**. Not for commercial redistribution.

- **FIFA®**, **World Cup®**, and all related marks are registered trademarks of FIFA
- This project is **independent** and is not affiliated with, endorsed by, or connected to FIFA or any national football federation
- Match data used from public sources for non-commercial analysis only
- FIFA ranking data sourced from [inside.fifa.com](https://inside.fifa.com/news/france-1st-fifa-coca-cola-world-ranking-april-2026)

---

### 🔗 Data Sources

- [FIFA/Coca-Cola Men's World Ranking — April 1, 2026](https://inside.fifa.com/news/france-1st-fifa-coca-cola-world-ranking-april-2026)
- [2026 FIFA World Cup — Wikipedia](https://en.wikipedia.org/wiki/2026_FIFA_World_Cup)
- [2026 FIFA World Cup Qualification — Wikipedia](https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification)
- [ESPN Soccer — FIFA Rankings](https://www.espn.com/soccer/story/_/id/46664763/fifa-mens-top-50-world-rankings)
- Raw qualifying match data: `fifa_all_matches` (894 matches, AFC/CONMEBOL/UEFA/CAF/CONCACAF/OFC)

---
---

## 🇪🇸 Español

### ¿Qué es esto?

Un predictor estadístico para la **Copa Mundial FIFA 2026** (EE.UU. 🇺🇸 · Canadá 🇨🇦 · México 🇲🇽) impulsado por:

- **Ratings Elo** derivados del ranking oficial de la FIFA de abril 2026 (Francia #1, España #2, Argentina #3)
- **894 partidos reales de clasificación** de AFC, CONMEBOL, UEFA, CAF, CONCACAF y OFC (oct. 2023 – mar. 2026)
- **Modelo Poisson de Dixon-Coles** para simulación estadísticamente precisa de resultados
- **Simulación Monte Carlo** — 50,000 torneos completos para calcular probabilidades de campeonato

El resultado es una app HTML completamente interactiva que muestra probabilidades de ganar, predicciones de grupos y un cuadro completo de eliminatorias — todo recalculado en vivo en tu navegador cada vez que presionas **Ejecutar Simulación**.

---

### 📊 Cómo Funciona

#### 1. Ratings Elo
Partiendo de los **puntos Elo oficiales de la FIFA/Coca-Cola (1 de abril de 2026)**, el rating de cada equipo se actualiza procesando los 894 partidos con la fórmula de **World Football Elo**:

```
ΔElo = K × MDF × (W − Eₐ)
```

- `K = 40` (peso de importancia de partido clasificatorio)
- `MDF` = Multiplicador de Diferencia de Goles (1.0 para empates/victorias por 1 gol, hasta 2.5 para victorias abultadas)
- `W` = resultado real (1 = victoria, 0.5 = empate, 0 = derrota)
- `Eₐ` = resultado esperado según la diferencia de Elo

#### 2. Modelo Poisson de Dixon-Coles
Cada partido genera un marcador estadísticamente realista. Goles esperados por equipo:

```
λ_A = 1.35 × exp(ΔElo / 1200)
λ_B = 1.35 × exp(-ΔElo / 1200)
```

La **corrección de Dixon-Coles** (ρ = −0.13) corrige la sobrerepresentación conocida de resultados de pocos goles (0-0, 1-0, 0-1, 1-1) en modelos de Poisson simples, haciendo que las distribuciones de marcadores coincidan con los datos reales del fútbol internacional.

#### 3. Lógica de Eliminatorias
- **90 minutos**: Simulación de marcador con Poisson
- **Tiempo extra**: Si hay empate, tasa de goles ~60% (factor de fatiga aplicado)
- **Penaltis**: Casi aleatorio con pequeño sesgo Elo — `P(A gana) = 0.5 + (EloA − EloB) / 8000`

#### 4. Monte Carlo (50,000 corridas)
Ejecuta el torneo completo de 48 equipos de principio a fin 50,000 veces:
- 12 grupos en fase de grupos (3 partidos cada uno)
- Determina 32 clasificados (mejores 2 por grupo + mejores 8 terceros)
- Ronda de 32 → Octavos → Cuartos → Semifinales → Final

Las probabilidades finales son frecuencias acumuladas en todas las corridas — el "%" de ganar de un equipo significa que ganaron el torneo en esa proporción de las 50,000 simulaciones.

---

### 🚀 Instalación y Uso

#### Opción A — Abrir el HTML directamente (sin instalación)
```bash
# Descarga y abre en cualquier navegador — no necesita servidor
open wc2026_predictor.html
```

El archivo HTML es **completamente autónomo** — toda la lógica de simulación corre en JavaScript en tu navegador. Haz clic en **▶ Ejecutar Simulación** para correr nuevas iteraciones sobre la base de 50,000 corridas del motor Python.

#### Opción B — Correr el motor Python localmente
```bash
# Instalar dependencias
pip install numpy scipy

# Correr simulación Monte Carlo (genera mc_stats.json)
python3 wc2026_montecarlo.py

# Generar reporte HTML fresco desde los resultados
python3 generate_html.py

# Abrir el resultado
open wc2026_predictor.html
```

Requisitos: Python 3.8+ · numpy · scipy · archivo de datos `fifa_all_matches`

---

### 📁 Estructura de Archivos

```
wc2026-predictor/
├── wc2026_predictor.html    # App interactiva autónoma (abrir en navegador)
├── wc2026_montecarlo.py     # Motor de simulación Monte Carlo en Python
├── generate_html.py         # Generador de reporte HTML desde resultados Python
├── fifa_all_matches         # Datos de partidos (894 partidos de clasificación)
├── README.md                # Este archivo
```

---

### 📈 Resultados de Ejemplo (50,000 simulaciones)

| 🏳️ Equipo | Campeón % | Final % | Semi % | Elo |
|---|---|---|---|---|
| 🇪🇸 España | 26.37% | 38.7% | 55.5% | 1877 |
| 🇫🇷 Francia | 22.73% | 34.4% | 50.8% | 1866 |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra | 18.10% | 30.4% | 44.3% | 1843 |
| 🇲🇦 Marruecos | 7.09% | 15.6% | 27.8% | 1771 |
| 🇦🇷 Argentina | 6.74% | 15.7% | 29.9% | 1767 |
| 🇳🇱 Países Bajos | 4.97% | 11.6% | 23.9% | 1747 |
| 🇵🇹 Portugal | 3.72% | 9.9% | 22.1% | 1723 |

> Los resultados varían con cada corrida — estas son probabilidades agregadas, no predicciones fijas.

---

### ⚠️ Aviso Legal

> **Este proyecto es solo para entretenimiento y fines educativos.**
> No constituye análisis deportivo profesional, asesoramiento de apuestas ni predicciones oficiales de la FIFA.
> Los resultados son simulaciones puramente probabilísticas basadas en datos de acceso público.
> Creado por diversión por **Angel Luyo M** — sin afiliación con la FIFA ni ninguna organización deportiva.
> **No utilizar para decisiones de apuestas o juegos de azar.**

---

### 📜 Licencia y Derechos de Autor

© 2026 **Angel Luyo M**. Todos los derechos reservados.

Este proyecto fue creado para **uso personal y educativo únicamente**. No para redistribución comercial.

- **FIFA®**, **World Cup®** y todas las marcas relacionadas son marcas registradas de la FIFA
- Este proyecto es **independiente** y no está afiliado, respaldado ni conectado con la FIFA ni con ninguna federación nacional de fútbol
- Datos de partidos utilizados de fuentes públicas solo para análisis no comercial
- Datos de ranking FIFA obtenidos de [inside.fifa.com](https://inside.fifa.com/news/france-1st-fifa-coca-cola-world-ranking-april-2026)

---

### 🔗 Fuentes de Datos

- [Ranking Mundial FIFA/Coca-Cola — 1 de abril de 2026](https://inside.fifa.com/news/france-1st-fifa-coca-cola-world-ranking-april-2026)
- [Copa Mundial FIFA 2026 — Wikipedia](https://en.wikipedia.org/wiki/2026_FIFA_World_Cup)
- [Clasificación Copa Mundial FIFA 2026 — Wikipedia](https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification)
- [ESPN Soccer — Rankings FIFA](https://www.espn.com/soccer/story/_/id/46664763/fifa-mens-top-50-world-rankings)
- Datos de partidos clasificatorios: `fifa_all_matches` (894 partidos, AFC/CONMEBOL/UEFA/CAF/CONCACAF/OFC)

---

<div align="center">

Made with ❤️ by **Angel Luyo M** · 2026

*For the love of the game / Por amor al fútbol* ⚽

</div>
