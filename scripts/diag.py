"""Diagnostic temporaire : compare les façons de lire Yahoo (branche de test, jamais sur main)."""
import datetime as dt
import yfinance as yf
print("yfinance", yf.__version__, "UTC", dt.datetime.utcnow().isoformat())
S = ["^N225", "^HSI", "000001.SS", "^NSEI", "^KS11", "^AXJO", "^FCHI", "^GSPC"]
df = yf.download(S, period="6mo", interval="1d", group_by="ticker", auto_adjust=False, progress=False, threads=True)
print("index lot :", type(df.index).__name__, df.index.tz, list(df.index[-4:]))
for s in S:
    print("\n==", s)
    print("lot    :", [(str(d)[:10], None if v != v else round(float(v), 2)) for d, v in df[s]["Close"].tail(4).items()])
    t = yf.Ticker(s)
    h = t.history(period="10d", interval="1d", auto_adjust=False)
    print("seul   :", [(str(d)[:16], round(float(v), 2)) for d, v in h["Close"].tail(4).items()])
    m = t.history_metadata or {}
    print("meta   :", {k: m.get(k) for k in ("regularMarketPrice", "regularMarketTime", "chartPreviousClose", "previousClose", "exchangeTimezoneName", "currency")})
    try:
        fi = t.fast_info
        print("fast   :", fi["lastPrice"], fi["previousClose"], fi["regularMarketPreviousClose"])
    except Exception as e:
        print("fast   : erreur", e)
print("\n== candidats pour l'ETF d'État zone euro")
for s in ["IEGA.L", "EUNH.DE", "IEGA.AS", "IEGA.MI", "IEGA.SW", "SEGA.L", "IBGS.AS", "VETY.AS", "EUNH.F", "CBE7.AS"]:
    try:
        t = yf.Ticker(s); h = t.history(period="10d", interval="1d", auto_adjust=False); m = t.history_metadata or {}
        print(s, len(h), None if h.empty else round(float(h["Close"].iloc[-1]), 3), m.get("currency"), m.get("longName") or m.get("shortName"))
    except Exception as e:
        print(s, "erreur", str(e)[:80])
