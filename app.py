from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# Load hospital dataset
DATA_FILE = "hospital_data.csv"


def load_data():
    df = pd.read_csv(DATA_FILE)

    # Convert date column
    df["Date"] = pd.to_datetime(df["Date"])

    return df


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/dashboard")
def dashboard_data():

    df = load_data()

    # -------------------------
    # KPI calculations
    # -------------------------

    total_patients = len(df)

    total_treatment_cost = float(df["Treatment Cost"].sum())

    average_age = round(float(df["Age"].mean()), 2)

    average_satisfaction = round(
        float(df["Satisfaction"].mean()), 2
    )

    inpatient_count = int(
        (df["Visit Type"] == "Inpatient").sum()
    )

    outpatient_count = int(
        (df["Visit Type"] == "Outpatient").sum()
    )

    # -------------------------
    # Patients by Department
    # -------------------------

    department_data = (
        df.groupby("Department")
        .size()
        .reset_index(name="Patients")
    )

    # -------------------------
    # Monthly Patient Trend
    # -------------------------

    df["Month"] = df["Date"].dt.strftime("%Y-%m")

    monthly_data = (
        df.groupby("Month")
        .size()
        .reset_index(name="Patients")
        .sort_values("Month")
    )

    # -------------------------
    # Diagnosis Distribution
    # -------------------------

    diagnosis_data = (
        df.groupby("Diagnosis")
        .size()
        .reset_index(name="Patients")
        .sort_values(
            "Patients",
            ascending=False
        )
    )

    # -------------------------
    # Gender Distribution
    # -------------------------

    gender_data = (
        df.groupby("Gender")
        .size()
        .reset_index(name="Patients")
    )

    # -------------------------
    # Treatment Cost
    # -------------------------

    cost_data = (
        df.groupby("Department")["Treatment Cost"]
        .sum()
        .reset_index()
    )

    # -------------------------
    # Return JSON
    # -------------------------

    return jsonify({

        "kpis": {
            "total_patients": total_patients,
            "total_treatment_cost": total_treatment_cost,
            "average_age": average_age,
            "average_satisfaction": average_satisfaction,
            "inpatient_count": inpatient_count,
            "outpatient_count": outpatient_count
        },

        "department": department_data.to_dict(
            orient="records"
        ),

        "monthly": monthly_data.to_dict(
            orient="records"
        ),

        "diagnosis": diagnosis_data.to_dict(
            orient="records"
        ),

        "gender": gender_data.to_dict(
            orient="records"
        ),

        "cost": cost_data.to_dict(
            orient="records"
        )
    })


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )