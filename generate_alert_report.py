from fpdf import FPDF
from fpdf.enums import XPos, YPos  # For better alignment in `fpdf2`
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import requests
import io
import os

LINE_CHART_SCALE = float(os.getenv("LINE_CHART_SCALE", 0.8))  # Default: 100% scale
PIE_CHART_SCALE = float(os.getenv("PIE_CHART_SCALE", 0.8))  # Default: 100% scale
TABLE_FONT_SIZE = int(os.getenv("TABLE_FONT_SIZE", 8))  # Default: 10pt font

# Constants
API_URL = os.getenv("API_URL", "https://api.robusta.dev/api/query/report")  # Default to production URL
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
AUTH_HEADER = {"Authorization": f"Bearer {AUTH_TOKEN}"} if AUTH_TOKEN else {}
ACCOUNT_ID = os.getenv("ACCOUNT_ID", "")

MAX_DAYS_BACK = 30

LOGO_PATH = "imported/logo.png"  # Path to the logo
LOGO_X = 10  # X-coordinate for the logo
LOGO_Y = 10  # Y-coordinate for the logo
LOGO_WIDTH = 20  # Width of the logo

class PDFReport(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__("L", "mm", "A4")  # Set orientation to Landscape
        self.add_font("DejaVu", "", "imported/DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "imported/DejaVuSans-Bold.ttf", uni=True)
        self.set_font("DejaVu", size=10)

    def header(self):
        # Add the logo in the top-left corner
        if LOGO_PATH:  # Ensure the logo path is set
            self.image(LOGO_PATH, x=LOGO_X, y=LOGO_Y, w=LOGO_WIDTH)
        
        # Add the report title
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, "Robusta Alerts Report", border=0, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_section_title(self, title):
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(5)

    def add_paragraph(self, text):
        self.set_font("DejaVu", "", 10)
        self.multi_cell(0, 10, text)
        self.ln()

    def add_image(self, image, x=None, y=None, width=None):
        self.image(image, x=x, y=y, w=width)
        self.ln(10)

    def add_table_row(self, row, widths):
        self.set_font("DejaVu", "", TABLE_FONT_SIZE)  # Set font size dynamically
        for i, value in enumerate(row):
            self.cell(widths[i], 10, str(value), border=1, align="C")
        self.ln()

def fetch_alert_data_for_time_range(start_time, end_time):
    """Fetch alerts for a specific time range."""
    params = {
        "account_id": ACCOUNT_ID,
        "start_ts": start_time.isoformat() + "Z",
        "end_ts": end_time.isoformat() + "Z",
    }

    response = requests.get(API_URL, headers=AUTH_HEADER, params=params)
    response.raise_for_status()
    return response.json()

def fetch_alert_data(days_back):
    """Fetch alert data for the specified number of days, with 12-hour increments."""
    if not AUTH_TOKEN:
        raise ValueError("AUTH_TOKEN is not set. Please set the AUTH_TOKEN environment variable.")
    if not ACCOUNT_ID:
        raise ValueError("ACCOUNT_ID is not set. Please set the ACCOUNT_ID environment variable.")

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days_back)
    
    params = {
        "account_id": ACCOUNT_ID,
        "start_ts": start_time.isoformat() + "Z",
        "end_ts": end_time.isoformat() + "Z",
    }

    response = requests.get(API_URL, headers=AUTH_HEADER, params=params)
    response.raise_for_status()
    return response.json()

# New function to fetch alert data in 12-hour intervals
def fetch_alert_data_12_hour_intervals(days_back):
    if not AUTH_TOKEN:
        raise ValueError("AUTH_TOKEN is not set. Please set the AUTH_TOKEN environment variable.")
    if not ACCOUNT_ID:
        raise ValueError("ACCOUNT_ID is not set. Please set the ACCOUNT_ID environment variable.")

    end_time = datetime.utcnow()
    intervals = []
    for hours_back in range(0, days_back * 24, 12):
        start_time = end_time - timedelta(hours=hours_back + 12)
        interval_end_time = end_time - timedelta(hours=hours_back)

        params = {
            "account_id": ACCOUNT_ID,
            "start_ts": start_time.isoformat() + "Z",
            "end_ts": interval_end_time.isoformat() + "Z",
        }

        response = requests.get(API_URL, headers=AUTH_HEADER, params=params)
        response.raise_for_status()
        intervals.append({"start_time": start_time, "end_time": interval_end_time, "data": response.json()})

    return intervals



def generate_report(alert_data, days_back):
    df = pd.DataFrame(alert_data)
    df['alert_count'] = df['alert_count'].astype(int)
    total_alerts = df['alert_count'].sum()

    # Line chart: One line per alert
    df["date"] = [datetime.utcnow() - timedelta(days=i) for i in range(len(df))]
    # Using the 12-hour interval data for "Alerts Over Time" chart
    interval_data = fetch_alert_data_12_hour_intervals(days_back)
    all_intervals = []
    
    for interval in interval_data:
        for alert in interval["data"]:
            all_intervals.append({
                "start_time": interval["start_time"],
                "end_time": interval["end_time"],
                "aggregation_key": alert["aggregation_key"],
                "alert_count": int(alert["alert_count"])
            })
    
    interval_df = pd.DataFrame(all_intervals)

    # Creating "Alerts Over Time" chart
    plt.figure(figsize=(12, 6))
    for key in interval_df['aggregation_key'].unique():
        key_data = interval_df[interval_df['aggregation_key'] == key]
        plt.plot(
            key_data['start_time'], 
            key_data['alert_count'], 
            label=key
        )
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.title("Alerts Over Time (12-Hour Intervals)")
    plt.xlabel("Time")
    plt.ylabel("Alert Count")
    plt.xticks(rotation=45)
    chart_path = "alerts_over_time_chart.png"
    plt.savefig(chart_path, format="png", bbox_inches="tight")
    plt.close()


    # Pie chart with "OtherAlerts"
    df["percentage"] = (df["alert_count"] / total_alerts) * 100
    other_alerts = df[df["percentage"] < 3]
    other_count = other_alerts["alert_count"].sum()

    # Create the pie chart data, adding "OtherAlerts" only if the count is greater than 0
    if other_count > 0:
        pie_df = pd.concat([
            df[df["percentage"] >= 3],
            pd.DataFrame([{
                "aggregation_key": "OtherAlerts", 
                "alert_count": other_count, 
                "percentage": (other_count / total_alerts) * 100
            }])
        ], ignore_index=True)
    else:
        pie_df = df[df["percentage"] >= 2.3]

    # Plotting the pie chart
    plt.figure(figsize=(10, 6))
    wedges, texts, autotexts = plt.pie(
        pie_df["alert_count"],
        labels=pie_df["aggregation_key"],
        autopct='%1.1f%%',
        startangle=140
    )


    # Match label colors with the corresponding wedge colors
    for text, wedge in zip(texts, wedges):
        text.set_color(wedge.get_facecolor())  # Set label color to match wedge color

    # Adjust the position of the percentage labels
    for autotext in autotexts:
        autotext.set_position((1.4 * autotext.get_position()[0], 1.4 * autotext.get_position()[1]))
        autotext.set_fontsize(10)  # Optional: Adjust font size for better readability

    plt.title("Alert Distribution")
    pie_chart = "pie_chart.png"
    plt.savefig(pie_chart, format="png")
    plt.close()




    # Generate PDF
    pdf = PDFReport()
    # First page report details
    pdf.add_page()
    pdf.add_section_title("Robusta Alerts Report")
    pdf.set_font("Arial", "", 12)
    report_start_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    report_end_date = datetime.utcnow().strftime("%Y-%m-%d")
    pdf.add_paragraph(
        f"This report provides an analysis of Prometheus alerts "
        f"from {report_start_date} to {report_end_date} over the past {days_back} days."
    )


    # Add line chart
    pdf.add_section_title("Line Chart: Alerts Over Time")
    line_chart_width = 275 * LINE_CHART_SCALE  # Scale width for landscape
    pdf.add_image(chart_path, width=line_chart_width)

    # Add pie chart
    pdf.add_section_title("Pie Chart: Alert Distribution")
    pie_chart_width = 275 * PIE_CHART_SCALE  # Scale width for landscape
    pdf.add_image(pie_chart, width=pie_chart_width)

    # Table of all alerts with percentages
    # Add enrichment logic
    enriched_automatically = {
        'CPUThrottlingHigh', 'HostHighCpuLoad', 'HostOomKillDetected', 'KubeAggregatedAPIDown',
        'KubeCPUOvercommit', 'KubeContainerWaiting', 'KubeDaemonSetMisScheduled',
        'KubeDaemonSetRolloutStuck', 'KubeDeploymentReplicasMismatch', 'KubeHpaReplicasMismatch',
        'KubeJobCompletion', 'KubeJobFailed', 'KubeJobNotCompleted', 'KubeMemoryOvercommit',
        'KubeNodeNotReady', 'KubeNodeUnreachable', 'KubePodCrashLooping', 'KubePodNotReady',
        'KubeStatefulSetReplicasMismatch', 'KubeStatefulSetUpdateNotRolledOut', 'KubeVersionMismatch',
        'KubeletTooManyPods', 'KubernetesDaemonsetMisscheduled', 'KubernetesDeploymentReplicasMismatch',
        'NodeFilesystemAlmostOutOfSpace', 'NodeFilesystemSpaceFillingUp', 'PrometheusRuleFailures', 'TargetDown'
    }

    formatted_table = [
        ["Alert Name", "Count", "Percentage", "Enriched Automatically", "Recommended Enrichment", "Needs Customization"]
    ]

    for _, row in df.iterrows():
        auto_enrich = '✔' if row['aggregation_key'] in enriched_automatically else ' '
        recommended_enrich = (
            '✔' if ((
                'node' in row['aggregation_key'].lower() or 
                'pod' in row['aggregation_key'].lower() or 
                'deployment' in row['aggregation_key'].lower() or 
                'statefulset' in row['aggregation_key'].lower() or 
                'daemonset' in row['aggregation_key'].lower() or 
                'cpu' in row['aggregation_key'].lower() or 
                'memory' in row['aggregation_key'].lower() or 
                'job' in row['aggregation_key'].lower()
            )  and auto_enrich == ' ') else ' '
        )
        needs_customization = '✔' if auto_enrich == ' ' and recommended_enrich == ' ' else ' '
        name = row['aggregation_key']
        STRING_LIMIT = 20
        if len(row['aggregation_key']) > STRING_LIMIT :
            name = row['aggregation_key'][:STRING_LIMIT] + "..."
        formatted_table.append([
            name, row['alert_count'], f"{row['percentage']:.2f}%",
            auto_enrich, recommended_enrich, needs_customization
        ])

    # Add table to PDF
    pdf.add_section_title("Alert Summary Table with Enrichment")
    table_widths = [50, 30, 30, 50, 50, 50]  # Column widths
    for row in formatted_table:
        pdf.add_table_row(row, table_widths)


    # Calculate enrichment summary
    enrichment_summary = {
        "Enriched Automatically": {"count": 0, "percentage": 0},
        "Recommended Enrichment": {"count": 0, "percentage": 0},
        "Needs Customization": {"count": 0, "percentage": 0}
    }

    for _, row in df.iterrows():
        if row['aggregation_key'] in enriched_automatically:
            enrichment_summary["Enriched Automatically"]["count"] += row['alert_count']
        elif (
            'node' in row['aggregation_key'].lower() or 
            'pod' in row['aggregation_key'].lower() or 
            'deployment' in row['aggregation_key'].lower() or 
            'statefulset' in row['aggregation_key'].lower() or 
            'daemonset' in row['aggregation_key'].lower() or 
            'cpu' in row['aggregation_key'].lower() or 
            'memory' in row['aggregation_key'].lower() or 
            'job' in row['aggregation_key'].lower()
        ):
            enrichment_summary["Recommended Enrichment"]["count"] += row['alert_count']
        else:
            enrichment_summary["Needs Customization"]["count"] += row['alert_count']

    for key, values in enrichment_summary.items():
        values["percentage"] = (values["count"] / total_alerts) * 100

    pdf.add_page()
    # Add enrichment summary table to PDF
    pdf.add_section_title("Enrichment Summary Table")
    summary_widths = [60, 40, 40]  # Column widths
    summary_table = [
        ["Enrichment Type", "Alert Count", "Percentage"]
    ] + [
        [key, enrichment_summary[key]["count"], f"{enrichment_summary[key]['percentage']:.2f}%"]
        for key in enrichment_summary
    ]

    pdf.set_font("Arial", "B", 10)
    for row in summary_table:
        pdf.add_table_row(row, summary_widths)


    # Save PDF
    pdf_output = "prometheus_alerts_report.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Main Execution
days_back = 30  # Example: Can be changed to test different durations
alert_data = fetch_alert_data(days_back)
pdf_file = generate_report(alert_data, days_back)
print(f"Report generated: {pdf_file}")
