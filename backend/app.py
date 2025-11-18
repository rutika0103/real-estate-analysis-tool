# backend/app.py
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
from pathlib import Path
import io
import traceback

app = Flask(__name__)
CORS(app)

# Location: project_root/preload/data.xlsx
BASE_DIR = Path(__file__).resolve().parents[1]  # one level up from backend folder
PRELOAD_DIR = BASE_DIR / "preload"
PRELOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = PRELOAD_DIR / "data.xlsx"

# In-memory dataframe (loaded from DATA_FILE if present)
df = None

def safe_read_excel(path):
    try:
        return pd.read_excel(path, engine="openpyxl")
    except Exception:
        # fallback to any engine
        return pd.read_excel(path)

def load_dataset():
    global df
    if DATA_FILE.exists():
        try:
            df = safe_read_excel(DATA_FILE)
        except Exception as e:
            print("Error reading preload data:", e)
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

# load at startup
load_dataset()

def find_best_columns(df):
    """
    Heuristic to find year, price, demand, area columns.
    Returns dict like {'year': colname, 'price': colname, 'demand': colname, 'area': colname}
    """
    cols = [c.lower() for c in df.columns]
    mapping = {}
    # approximate matches
    for c in df.columns:
        lc = c.lower()
        if 'year' in lc or 'date' in lc:
            mapping.setdefault('year', c)
        if 'price' in lc or 'rate' in lc or 'avg_price' in lc or 'amount' in lc:
            mapping.setdefault('price', c)
        if 'demand' in lc or 'interest' in lc or 'queries' in lc:
            mapping.setdefault('demand', c)
        if 'area' in lc or 'locality' in lc or 'location' in lc or 'neighbour' in lc or 'local' in lc:
            mapping.setdefault('area', c)
        if 'size' in lc or 'sqft' in lc or 'area_size' in lc:
            mapping.setdefault('size', c)
    return mapping

def make_summary(subdf, area_name=None):
    """
    Create a concise natural-language summary from subset dataframe.
    """
    if subdf.empty:
        return "No data available for the requested area or query."
    cols = find_best_columns(subdf)

    price_col = cols.get('price')
    demand_col = cols.get('demand')
    year_col = cols.get('year')

    lines = []
    if area_name:
        lines.append(f"Analysis for **{area_name}**:")

    # Price summary
    if price_col:
        try:
            mean_price = subdf[price_col].dropna().astype(float).mean()
            median_price = subdf[price_col].dropna().astype(float).median()
            recent = None
            if year_col:
                # most recent year row value
                recent_year = int(subdf[year_col].dropna().astype(int).max())
                recent_rows = subdf[subdf[year_col] == recent_year]
                if not recent_rows.empty:
                    recent = float(recent_rows[price_col].dropna().astype(float).mean())
            if recent:
                lines.append(f"Average price (most recent year) ≈ {recent:.0f}. Overall mean ≈ {mean_price:.0f} and median ≈ {median_price:.0f}.")
            else:
                lines.append(f"Average price ≈ {mean_price:.0f} and median ≈ {median_price:.0f}.")
        except Exception:
            pass

    # Demand summary
    if demand_col:
        try:
            mean_demand = subdf[demand_col].dropna().astype(float).mean()
            lines.append(f"Average demand score ≈ {mean_demand:.1f}.")
        except Exception:
            pass

    # Trend summary using grouping by year
    if year_col and price_col:
        try:
            grp = (
                subdf[[year_col, price_col]]
                .dropna(subset=[year_col, price_col])
                .groupby(year_col)[price_col]
                .mean()
                .reset_index()
                .sort_values(by=year_col)
            )
            if len(grp) >= 2:
                first = float(grp.iloc[0,1])
                last = float(grp.iloc[-1,1])
                pct = ((last - first) / first) * 100 if first != 0 else 0
                if pct > 5:
                    trend = "rising"
                elif pct < -5:
                    trend = "falling"
                else:
                    trend = "stable"
                lines.append(f"Price trend over the period is {trend} ({pct:.1f}% change from first to last recorded year).")
        except Exception:
            pass

    # final recommendation-like sentence
    lines.append("Recommendation: this locality shows " +
                 ("positive" if (price_col and year_col and not subdf.empty and 'rising' in " ".join(lines)) else "mixed") +
                 " signals for investment — combine with on-ground checks.")

    return " ".join(lines)

def build_chart_data(subdf):
    cols = find_best_columns(subdf)
    year_col = cols.get('year')
    price_col = cols.get('price')
    demand_col = cols.get('demand')

    chart = {}
    if year_col and price_col:
        try:
            grp = (
                subdf[[year_col, price_col]]
                .dropna(subset=[year_col, price_col])
                .groupby(year_col)[price_col]
                .mean()
                .reset_index()
                .sort_values(by=year_col)
            )
            chart['price_trend'] = [{"year": int(r[year_col]), "value": float(r[price_col])} for _, r in grp.iterrows()]
        except Exception:
            chart['price_trend'] = []
    if year_col and demand_col:
        try:
            grp = (
                subdf[[year_col, demand_col]]
                .dropna(subset=[year_col, demand_col])
                .groupby(year_col)[demand_col]
                .mean()
                .reset_index()
                .sort_values(by=year_col)
            )
            chart['demand_trend'] = [{"year": int(r[year_col]), "value": float(r[demand_col])} for _, r in grp.iterrows()]
        except Exception:
            chart['demand_trend'] = []

    return chart

@app.route("/")
def health():
    return jsonify({"status":"ok","message":"Real-estate analysis API (Flask)"}), 200

@app.route("/upload", methods=["POST"])
def upload():
    """
    Accepts a multipart/form-data file upload (key='file') and replaces the current dataset.
    Returns success/failure.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"ok":False,"error":"No file provided. Use form key 'file'."}), 400
        f = request.files['file']
        if f.filename == "":
            return jsonify({"ok":False,"error":"Empty filename."}), 400
        # Save to PRELOAD_DIR/data.xlsx
        content = f.read()
        # Try to load into pandas to validate
        try:
            temp_df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        except Exception:
            temp_df = pd.read_excel(io.BytesIO(content))
        # Save file
        with open(DATA_FILE, "wb") as fh:
            fh.write(content)
        # update in-memory
        global df
        df = temp_df
        return jsonify({"ok":True,"message":"File uploaded and dataset replaced.","rows":len(df)}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok":False,"error":str(e)}), 500

@app.route("/analyze", methods=["GET"])
def analyze():
    """
    Query params:
    - area: name of locality to analyze (case-insensitive substring match)
    - limit: optional integer to limit results
    Returns JSON:
    { summary: str, chart: {...}, table: [ {...}, ... ] }
    """
    try:
        if df is None:
            return jsonify({"ok":False,"error":"No dataset loaded."}), 500
        area = request.args.get("area","").strip()
        limit = int(request.args.get("limit", "200"))
        if area == "":
            return jsonify({"ok":False,"error":"Please provide 'area' query param."}), 400

        # case-insensitive substring match on area column(s)
        cols_map = find_best_columns(df)
        area_col = cols_map.get('area')
        if not area_col:
            # try to find any column with string values
            candidates = [c for c in df.columns if df[c].dtype == object]
            if candidates:
                area_col = candidates[0]
            else:
                return jsonify({"ok":False,"error":"No area-like column found in dataset."}), 500

        filtered = df[df[area_col].astype(str).str.lower().str.contains(area.lower(), na=False)]
        if filtered.empty:
            return jsonify({"ok":True,"summary":"No records found for the specified area.","chart":{},"table":[]})

        # limit rows
        table_rows = filtered.head(limit).to_dict(orient="records")
        summary = make_summary(filtered, area_name=area)
        chart = build_chart_data(filtered)

        return jsonify({"ok":True,"summary":summary,"chart":chart,"table":table_rows})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok":False,"error":str(e)}), 500

@app.route("/compare", methods=["GET"])
def compare():
    """
    Compare multiple areas.
    Query params:
    - areas: comma-separated list, e.g. areas=Wakad,Aundh
    Returns:
    { ok:true, comparisons: { area1: { chart:..., summary:..., table: [...] }, area2: {...} } }
    """
    try:
        if df is None:
            return jsonify({"ok":False,"error":"No dataset loaded."}), 500
        raw = request.args.get("areas","").strip()
        if not raw:
            return jsonify({"ok":False,"error":"Please provide 'areas' query param (comma-separated)."}), 400
        areas = [a.strip() for a in raw.split(",") if a.strip()]
        cols_map = find_best_columns(df)
        area_col = cols_map.get('area')
        if not area_col:
            candidates = [c for c in df.columns if df[c].dtype == object]
            if candidates:
                area_col = candidates[0]
            else:
                return jsonify({"ok":False,"error":"No area-like column found in dataset."}), 500

        out = {}
        for a in areas:
            filtered = df[df[area_col].astype(str).str.lower().str.contains(a.lower(), na=False)]
            out[a] = {
                "summary": make_summary(filtered, area_name=a),
                "chart": build_chart_data(filtered),
                "table": filtered.head(200).to_dict(orient="records")
            }
        return jsonify({"ok":True,"comparisons":out})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok":False,"error":str(e)}), 500

@app.route("/download", methods=["GET"])
def download():
    """
    Download current dataset file (preload data.xlsx)
    """
    if DATA_FILE.exists():
        return send_file(str(DATA_FILE), as_attachment=True, download_name="data.xlsx")
    return jsonify({"ok":False,"error":"No preload dataset present."}), 404

if __name__ == "__main__":
    # run local dev
    app.run(host="0.0.0.0", port=8000, debug=True)
