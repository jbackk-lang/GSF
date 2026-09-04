"""
scripts/fetch_gsf_data.py

Pobiera realne dane makro dla dashboardu GSF (dashboard/gsf_dashboard.html)
i zapisuje je do dashboard/data.json, ktory dashboard wczytuje przez
fetch() przy starcie strony.

ZRODLA (wszystkie zweryfikowane recznie w tej sesji, 4.09.2026 --
patrz komentarze przy kazdej serii):
  - FRED (St. Louis Fed) -- USA + EBC (rate). Wymaga darmowego klucza
    API (https://fred.stlouisfed.org/docs/api/api_key.html), podanego
    jako sekret repo GitHub `FRED_API_KEY`.
  - Frankfurter (frankfurter.dev, oparte o referencyjne kursy EBC) --
    EUR/USD i USD/CNY. Bez klucza, wolno uzywane w produkcji.

CZEGO TEN SKRYPT NIE POBIERA (jawnie, uczciwie): chinskiej stopy
procentowej (PBOC LPR), chinskiego dlugu/PKB, chinskiego rachunku
biezacego, unijnego dlugu/PKB i unijnego rachunku biezacego -- zadne z
tych nie ma darmowego, czystego API z jednoznacznym seria ID (w
przeciwienstwie do serii FRED ponizej, ktore zostaly rowno sprawdzone
pod katem istnienia i aktualnej wartosci przed napisaniem tego
skryptu). Te pola sa WPISYWANE RECZNIE w dashboardzie (patrz pola
edytowalne w gsf_dashboard.html, zapisywane w localStorage
przegladarki) -- data.json ma dla nich tylko wartosc-zalozenie z
ostatniego recznego researchu (patrz FALLBACK ponizej), nie zywe dane.

TREND: dla trzech serii o sensownej ciaglej dynamice (dlug/PKB USA,
rachunek biezacy USA, ropa Brent) skrypt liczy prosta regresje liniowa
(najmniejsze kwadraty) na ostatnich N obserwacjach i ekstrapoluje
JEDEN krok naprzod. To NIE jest model ekonometryczny (brak sezonowosci,
autokorelacji, testu istotnosci) -- jawnie oznaczone w JSON jako
"method": "naive_linear_extrapolation", zeby nikt nie pomylil tego z
prognoza banku centralnego.

UWAGA O WYKONANIU: napisany w sesji bez dostepu do sandboxa bash --
kazdy adres URL i series ID zostal zweryfikowany recznie przez
mcp__workspace__web_fetch na fred.stlouisfed.org i
api.frankfurter.dev PRZED napisaniem tego pliku (patrz historia
sesji), ale sam skrypt nie zostal jeszcze faktycznie uruchomiony --
uruchomi go po raz pierwszy GitHub Actions
(.github/workflows/update_gsf_data.yml), recznie (workflow_dispatch)
lub wg harmonogramu.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
FRANKFURTER_BASE = "https://api.frankfurter.dev/v1"

OUT_PATH = Path(__file__).parent.parent / "dashboard" / "data.json"

# Wartosci z recznego researchu 4.09.2026 -- fallback, gdyby dana seria
# FRED chwilowo nie odpowiedziala (np. przerwa w publikacji), zeby
# data.json nigdy nie zostal nadpisany pustym/uszkodzonym stanem.
FALLBACK = {
    "usa": {
        "fed_funds_upper": 3.75,
        "fed_funds_lower": 3.50,
        "debt_gdp": 122.59,
        "current_account_musd": -226828.0,
        "brent_usd_bbl": 96.02,
    },
    "eu": {
        "ecb_rate": 2.25,
        "eur_usd": 1.1603,
    },
    "china": {
        "usd_cny": 6.7191,
    },
    # pola bez darmowego API -- patrz naglowek modulu; edytowalne recznie
    # w dashboardzie, tu tylko jako punkt startowy
    "manual_defaults": {
        "china_lpr_1y": "3,0%",
        "china_lpr_5y": "3,5%",
        "china_debt_gdp": "~90,0% PKB",
        "china_current_account_musd": 184300.0,
        "eu_debt_gdp": "88,1% PKB",
        "eu_current_account_meur_2025": 261400.0,
    },
}


def fred_observations(series_id: str, limit: int = 12) -> list[dict]:
    """Zwraca do `limit` ostatnich obserwacji serii FRED, najnowsza pierwsza.
    Rzuca RuntimeError z czytelnym komunikatem przy braku klucza/bledzie API
    -- NIE cichnie po cichu, zeby awaria w Action byla widoczna w logach."""
    if not FRED_API_KEY:
        raise RuntimeError(
            "Brak FRED_API_KEY w zmiennych srodowiskowych -- ustaw sekret "
            "repo GitHub o tej nazwie (darmowy klucz: "
            "https://fred.stlouisfed.org/docs/api/api_key.html)."
        )
    url = (
        f"{FRED_BASE}?series_id={series_id}&api_key={FRED_API_KEY}"
        f"&file_type=json&sort_order=desc&limit={limit}"
    )
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            payload = json.load(resp)
    except urllib.error.URLError as e:
        raise RuntimeError(f"FRED request failed dla {series_id}: {e}") from e
    obs = [
        o for o in payload.get("observations", [])
        if o.get("value") not in (None, ".", "")
    ]
    return obs


def frankfurter_rate(base: str, target: str) -> float:
    url = f"{FRANKFURTER_BASE}/latest?from={base}&to={target}"
    with urllib.request.urlopen(url, timeout=20) as resp:
        payload = json.load(resp)
    return float(payload["rates"][target])


def linear_trend(values: list[float]) -> dict:
    """Regresja liniowa najmniejszych kwadratow na `values` (najstarsza
    pierwsza -- odwroc przed wywolaniem, jesli masz najnowsza-pierwsza z
    FRED), ekstrapolacja o 1 krok naprzod. n>=3 wymagane, inaczej zwraca
    method='insufficient_data'."""
    n = len(values)
    if n < 3:
        return {"method": "insufficient_data", "n": n}
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(values) / n
    num = sum((xs[i] - mean_x) * (values[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    slope = num / den if den else 0.0
    intercept = mean_y - slope * mean_x
    next_estimate = slope * n + intercept
    return {
        "method": "naive_linear_extrapolation",
        "n": n,
        "slope_per_step": round(slope, 4),
        "next_step_estimate": round(next_estimate, 4),
    }


def build_payload() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "generated_at": now,
        "generator": "scripts/fetch_gsf_data.py",
        "usa": {},
        "eu": {},
        "china": {},
        "manual_defaults": FALLBACK["manual_defaults"],
    }

    # --- USA: Fed funds target range ---------------------------------
    try:
        upper = fred_observations("DFEDTARU", limit=1)
        lower = fred_observations("DFEDTARL", limit=1)
        payload["usa"]["fed_funds_upper"] = float(upper[0]["value"])
        payload["usa"]["fed_funds_lower"] = float(lower[0]["value"])
        payload["usa"]["fed_funds_date"] = upper[0]["date"]
    except RuntimeError as e:
        print(f"UWAGA: {e}", file=sys.stderr)
        payload["usa"]["fed_funds_upper"] = FALLBACK["usa"]["fed_funds_upper"]
        payload["usa"]["fed_funds_lower"] = FALLBACK["usa"]["fed_funds_lower"]
        payload["usa"]["fed_funds_date"] = None
        payload["usa"]["fed_funds_source"] = "fallback"

    # --- USA: dlug/PKB (kwartalna, z trendem) -------------------------
    try:
        obs = fred_observations("GFDEGDQ188S", limit=8)
        values = [float(o["value"]) for o in reversed(obs)]  # najstarsza pierwsza
        payload["usa"]["debt_gdp"] = values[-1]
        payload["usa"]["debt_gdp_date"] = obs[0]["date"]
        payload["usa"]["debt_gdp_trend"] = linear_trend(values)
    except RuntimeError as e:
        print(f"UWAGA: {e}", file=sys.stderr)
        payload["usa"]["debt_gdp"] = FALLBACK["usa"]["debt_gdp"]
        payload["usa"]["debt_gdp_source"] = "fallback"

    # --- USA: rachunek biezacy (kwartalny, z trendem) -----------------
    try:
        obs = fred_observations("IEABC", limit=8)
        values = [float(o["value"]) / 1000.0 for o in reversed(obs)]  # mln -> mld USD
        payload["usa"]["current_account_busd"] = values[-1]
        payload["usa"]["current_account_date"] = obs[0]["date"]
        payload["usa"]["current_account_trend"] = linear_trend(values)
    except RuntimeError as e:
        print(f"UWAGA: {e}", file=sys.stderr)
        payload["usa"]["current_account_busd"] = FALLBACK["usa"]["current_account_musd"] / 1000.0
        payload["usa"]["current_account_source"] = "fallback"

    # --- USA (globalnie): ropa Brent (dzienna, z trendem) -------------
    try:
        obs = fred_observations("DCOILBRENTEU", limit=30)
        values = [float(o["value"]) for o in reversed(obs)]
        payload["usa"]["brent_usd_bbl"] = values[-1]
        payload["usa"]["brent_date"] = obs[0]["date"]
        payload["usa"]["brent_trend"] = linear_trend(values)
    except RuntimeError as e:
        print(f"UWAGA: {e}", file=sys.stderr)
        payload["usa"]["brent_usd_bbl"] = FALLBACK["usa"]["brent_usd_bbl"]
        payload["usa"]["brent_source"] = "fallback"

    # --- EU: stopa depozytowa EBC -------------------------------------
    try:
        obs = fred_observations("ECBDFR", limit=1)
        payload["eu"]["ecb_rate"] = float(obs[0]["value"])
        payload["eu"]["ecb_rate_date"] = obs[0]["date"]
    except RuntimeError as e:
        print(f"UWAGA: {e}", file=sys.stderr)
        payload["eu"]["ecb_rate"] = FALLBACK["eu"]["ecb_rate"]
        payload["eu"]["ecb_rate_source"] = "fallback"

    # --- FX: EUR/USD, USD/CNY (Frankfurter, bez klucza) ---------------
    try:
        payload["eu"]["eur_usd"] = frankfurter_rate("EUR", "USD")
    except Exception as e:  # noqa: BLE001 -- zewnetrzne API, chcemy dowolny blad
        print(f"UWAGA: Frankfurter EUR/USD failed: {e}", file=sys.stderr)
        payload["eu"]["eur_usd"] = FALLBACK["eu"]["eur_usd"]
        payload["eu"]["eur_usd_source"] = "fallback"

    try:
        payload["china"]["usd_cny"] = frankfurter_rate("USD", "CNY")
    except Exception as e:  # noqa: BLE001
        print(f"UWAGA: Frankfurter USD/CNY failed: {e}", file=sys.stderr)
        payload["china"]["usd_cny"] = FALLBACK["china"]["usd_cny"]
        payload["china"]["usd_cny_source"] = "fallback"

    return payload


def main() -> None:
    payload = build_payload()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Zapisano {OUT_PATH}")


if __name__ == "__main__":
    main()
