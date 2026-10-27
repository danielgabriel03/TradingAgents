# TradingAgents · Deutsche Anleitung

Dieser Fork von [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
ist für **Claude** und **deutsche Berichte** voreingestellt. Sonst entspricht er dem Original.

TradingAgents ist ein **Forschungswerkzeug**: Es erstellt Analysen und eine Handelsempfehlung,
platziert aber **keine echten Orders**. Freigegebene Trades landen nur in einer simulierten Börse.
Die Ergebnisse sind keine Anlageberatung.

## Wie das Team arbeitet

1. **Analysten** (parallel): Markt und Technik (`market`), Stimmung in sozialen Medien
   (`social`), Nachrichten und Makro (`news`), Unternehmenszahlen (`fundamentals`).
2. **Researcher**: Ein bullischer und ein bärischer Agent debattieren die Berichte;
   der Research Manager fasst zusammen.
3. **Trader**: leitet daraus einen konkreten Handelsvorschlag ab.
4. **Risiko-Team**: Eine aggressive, eine neutrale und eine vorsichtige Stimme prüfen den Plan.
5. **Portfolio Manager**: gibt den Vorschlag frei oder lehnt ihn ab.

Voreingestellte Modelle:

| Aufgabe                                          | Modell              | Preis je 1 Mio. Tokens (Ein-/Ausgabe) |
| ------------------------------------------------ | ------------------- | ------------------------------------- |
| Research Manager, Portfolio Manager              | `claude-opus-5-5`   | 4 $ / 20 $                            |
| Analysten, Researcher, Trader, Risiko-Team       | `claude-sonnet-5-5` | 2 $ / 10 $                            |

## Einrichten

Voraussetzungen: Git und Docker mit Compose.

```bash
git clone https://github.com/danielgabriel03/TradingAgents.git
cd TradingAgents
cp .env.example .env
```

In `.env` den Schlüssel aus der [Claude Console](https://platform.claude.com/) eintragen
(Settings → API keys; der Schlüssel wird nur einmal angezeigt):

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

Die `.env` bleibt lokal: Git und Docker ignorieren sie. Den Schlüssel nie in andere Dateien schreiben.

Optional, ebenfalls in `.env`:

- `FRED_API_KEY`: kostenloser Schlüssel für US-Makrodaten.
- `SEC_EDGAR_USER_AGENT=Vorname Nachname mail@example.com`: Kontaktangabe für US-Unternehmensdaten.

Kursdaten, Nachrichten und Stimmung (Yahoo Finance, StockTwits, Reddit) brauchen keinen Schlüssel.

## Starten

```bash
mkdir -p data
echo "TRADINGAGENTS_DATA_DIR=./data" >> .env
docker compose run --rm tradingagents
```

Das CLI fragt nach Ticker, Datum, Analysten, Analysetiefe und Effort; Anbieter, Modelle und
Sprache kommen aus der `.env`. Ohne Rückfragen:

```bash
docker compose run --rm tradingagents --ticker NVDA --date 2026-10-23 \
  --analysts market,news,fundamentals --save --no-show
```

Ticker im Yahoo-Format: `NVDA`, `SAP.DE`, `0700.HK`, für Krypto `BTC-USD`.

Gespeicherte Berichte liegen danach in `data/logs/reports/<TICKER>_<Zeitstempel>/`, mit
`complete_report.html` als Gesamtbericht; Laufprotokolle in `data/logs/<TICKER>/<DATUM>/`.
Ohne `TRADINGAGENTS_DATA_DIR` landen sie im Docker-Volume `tradingagents_data`.

Nach Änderungen am Code oder einem Update das Image neu bauen: `docker compose build`.

### Ohne Docker

Python 3.11 oder neuer:

```bash
python -m venv .venv && source .venv/bin/activate
pip install .
tradingagents
```

Die `.env` im Projektordner wird automatisch gelesen. Ergebnisse liegen dann unter
`~/.tradingagents/logs/` (Berichte in `reports/`).

## Kosten im Griff behalten

Ein Lauf ruft die Modelle viele Male auf; die Kosten hängen vor allem von der Zahl der
Analysten, den Debattenrunden und dem Effort ab.

- Mit **einem Lauf**, wenigen Analysten und der niedrigsten Analysetiefe beginnen und den
  Verbrauch in der Anthropic Console prüfen.
- Effort `low` oder `medium` ist deutlich günstiger als `high`. Fest einstellen mit
  `TRADINGAGENTS_ANTHROPIC_EFFORT=medium`.
- Debattenrunden fest einstellen: `TRADINGAGENTS_MAX_DEBATE_ROUNDS=1` und
  `TRADINGAGENTS_MAX_RISK_ROUNDS=1`.
- `TRADINGAGENTS_TEMPERATURE` **nicht setzen**: Claude 5.5 lehnt den Parameter ab.

## Anderen Anbieter verwenden

In `.env` den Schlüssel des Anbieters eintragen (z. B. `OPENAI_API_KEY`, `GOOGLE_API_KEY`)
und die Voreinstellungen oben anpassen, etwa:

```bash
TRADINGAGENTS_LLM_PROVIDER=openai
TRADINGAGENTS_DEEP_THINK_LLM=gpt-6-sol
TRADINGAGENTS_QUICK_THINK_LLM=gpt-6-luna
```

Werden die drei Zeilen auskommentiert, fragt das CLI Anbieter und Modelle interaktiv ab.
Lokal ohne Schlüssel: `docker compose --profile ollama run --rm tradingagents-ollama`.
Alle Anbieter und Optionen stehen in der englischen [README](README.md) und in `.env.example`.

## Sprache

`TRADINGAGENTS_OUTPUT_LANGUAGE=German` lässt alle Agenten auf Deutsch schreiben. Die Zeilen,
die das Programm selbst auswertet („**Rating**:“ und „FINAL TRANSACTION PROPOSAL:“), bleiben
absichtlich englisch, damit die Entscheidung zuverlässig erkannt wird.

## Updates vom Original übernehmen

```bash
git remote add upstream https://github.com/TauricResearch/TradingAgents.git   # einmalig
git fetch upstream
git merge upstream/main
docker compose build
```

Alternativ auf GitHub im Fork „Sync fork“ wählen. Die Anpassungen dieses Forks sind bewusst
klein gehalten, damit Updates ohne Konflikte durchgehen: `.env.example`, diese Anleitung,
Sonnet 5.5 im Modellkatalog und native strukturierte Ausgaben für Claude-Modelle ohne
erzwungene Tool-Aufrufe (Opus 5.5, Sonnet 5.5, Fable 5.1) in
`tradingagents/llm_clients/anthropic_client.py`.
