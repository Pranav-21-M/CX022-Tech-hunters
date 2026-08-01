from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "market_sales_dataset_200_rows.xlsx")

# Read Excel
df = pd.read_excel(file_path)

# Convert Date column if present
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")


def get_summary():
    summary = {}
    summary["total_sales"] = len(df)

    if "Revenue" in df.columns:
        summary["total_revenue"] = int(df["Revenue"].sum())

    if "Units_Sold" in df.columns:
        summary["total_units"] = int(df["Units_Sold"].sum())

    if "Unit_Price" in df.columns:
        summary["avg_price"] = round(df["Unit_Price"].mean(), 2)

    return summary


@app.route("/", methods=["GET", "POST"])
def index():

    columns = list(df.columns)

    x_col = columns[0]
    y_col = "Revenue" if "Revenue" in columns else columns[1]
    chart_type = "bar"

    chart_data = None

    if request.method == "POST":

        x_col = request.form.get("x_col")
        y_col = request.form.get("y_col")
        chart_type = request.form.get("chart_type")

        temp = df[[x_col, y_col]].copy()

        # Convert Y values to numeric
        temp[y_col] = pd.to_numeric(temp[y_col], errors="coerce")

        # Remove invalid rows
        temp = temp.dropna()

        # Group values
        grouped = temp.groupby(x_col)[y_col].sum().reset_index()

        chart_data = {
            "labels": grouped[x_col].astype(str).tolist(),
            "values": grouped[y_col].tolist(),
            "type": chart_type
        }

    return render_template(
        "index.html",
        columns=columns,
        chart_data=chart_data,
        summary=get_summary(),
        x_col=x_col,
        y_col=y_col,
        chart_type=chart_type
    )


if __name__ == "__main__":
    app.run(debug=True)