# Robusta Alerts Report Generator

## Overview
This Python script fetches alert data from the Robusta API and generates a detailed Prometheus alerts report in PDF format. The report includes:
- Alert counts over time (line chart)
- Alert distribution breakdown (pie chart)
- A table summarizing alerts with enrichment recommendations

## Installation
To install the required dependencies, run:

```sh
pip install -r requirements.txt
```

## Usage

### Set Required Environment Variables
Before running the script, you must set the following environment variables:

```sh
export AUTH_TOKEN="your_auth_token"
export ACCOUNT_ID="your_account_id"
```

### Run the Script
To generate a report for the last 30 days:

```sh
python generate_alert_report.py 30
```

You can adjust the number of days as needed.

### Example Report Output
The script generates a Prometheus alerts report in PDF format. An example report can be found here: [example_prometheus_alerts_report.pdf](example_prometheus_alerts_report.pdf).

The generated PDF includes:
1. **Alerts Over Time (Line Chart)**: Shows alert frequency trends.
2. **Alert Distribution (Pie Chart)**: Displays the proportion of each alert type.
3. **Alert Summary Table**: Lists alerts with their count, percentage, and enrichment status.
4. **Enrichment Summary Table**: Categorizes alerts based on whether they are automatically enriched by Robusta, can be enriched using built-in playbooks, or require custom playbooks for enrichment.

## Troubleshooting
- **No alerts appearing in the report?**
  - Ensure that `AUTH_TOKEN` and `ACCOUNT_ID` are correctly set.
  - Check if the Robusta API is returning data for the requested time range.
- **PDF generation issues?**
  - Ensure that `fpdf` is installed and the required fonts are available in the `imported/` directory.
  - Check if `matplotlib` and `pandas` are installed correctly.

## Contributing
If you'd like to improve this script, feel free to submit a pull request or open an issue.

