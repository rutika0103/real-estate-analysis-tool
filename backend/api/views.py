# api/views.py
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pathlib import Path

# Path to your Excel file
EXCEL_PATH = r"C:\Users\sarje\Downloads\interview project\preload\data.xlsx"

# Helper: candidate names for the "area" column (lowercased)
AREA_CANDIDATES = [
    "area", "location", "final location", "final_location", "city", "place", "name", "region"
]

# Helper: candidate price-like numeric columns (lowercased)
PRICE_CANDIDATES = [
    "price", "flat - weighted average rate", "office - weighted average rate",
    "shop - weighted average rate", "total_sales - igr", "total sales - igr", "total_sales"
]

@api_view(['POST'])
def analyze_area(request):
    # Get requested area from POST JSON
    area = request.data.get("area") or request.data.get("query") or ""
    area = str(area).strip()
    if not area:
        return Response({"error": "Please POST JSON with an 'area' field, e.g. {\"area\":\"Pune\"}"}, status=400)

    # Load Excel into DataFrame
    try:
        df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    except Exception as e:
        return Response({"error": f"Failed to load Excel at {EXCEL_PATH}: {str(e)}"}, status=500)

    # Normalize column names map: lower -> original
    col_map = {str(c).strip().lower(): c for c in df.columns}

    # Find best area column
    area_col = None
    for cand in AREA_CANDIDATES:
        if cand in col_map:
            area_col = col_map[cand]
            break

    # If not found by candidate names, try heuristic: any column that contains 'city' or 'location' substring
    if area_col is None:
        for lower_name, orig in col_map.items():
            if "city" in lower_name or "location" in lower_name or "final" in lower_name:
                area_col = orig
                break

    # If still not found, fallback to first column and warn
    if area_col is None:
        area_col = list(df.columns)[0]

    # Filter rows where area_col contains the requested area (case-insensitive)
    try:
        filtered = df[df[area_col].astype(str).str.contains(area, case=False, na=False)]
    except Exception as e:
        return Response({"error": f"Failed to filter by column '{area_col}': {str(e)}", "available_columns": list(df.columns)}, status=500)

    if filtered.empty:
        return Response({"summary": f"No rows found for '{area}' using column '{area_col}'", "available_columns": list(df.columns), "filtered_count": 0})

    # Find price column for chart (choose first candidate that exists)
    price_col = None
    for cand in PRICE_CANDIDATES:
        if cand in col_map:
            price_col = col_map[cand]
            break

    # If price_col not found, try to find any numeric column (other than year) to use
    if price_col is None:
        numeric_cols = filtered.select_dtypes(include=["number"]).columns.tolist()
        # prefer columns that contain 'price' or 'rate' in name
        pref = [c for c in numeric_cols if ("price" in c.lower() or "rate" in c.lower() or "sales" in c.lower())]
        price_col = pref[0] if pref else (numeric_cols[0] if numeric_cols else None)

    # Chart: average price per year if 'year' exists and price_col exists
    chart = []
    year_col = None
    for k in col_map:
        if k == "year":
            year_col = col_map[k]
            break
    if year_col is not None and price_col is not None:
        try:
            grp = (
                filtered[[year_col, price_col]]
                .dropna(subset=[year_col, price_col])
                .groupby(year_col)[price_col]
                .mean()
                .reset_index()
                .sort_values(by=year_col)
            )
            # convert rows to list-of-dicts with simple keys
            chart = [{ "year": int(r[year_col]), "value": float(r[price_col]) } for _, r in grp.iterrows()]
        except Exception:
            chart = []

    # Prepare minimal summary
    summary = f"Found {len(filtered)} rows for '{area}' using column '{area_col}'."
    if price_col:
        summary += f" Using price column '{price_col}' for chart."

    # Prepare rows (convert NaN -> empty string)
    rows = filtered.fillna("").to_dict(orient="records")

    return Response({
        "summary": summary,
        "area_column_used": area_col,
        "price_column_used": price_col,
        "chart": chart,
        "rows": rows
    })
