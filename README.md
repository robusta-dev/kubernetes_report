# Prometheus Reports Generator

## Example Report Output
The script generates a Prometheus alerts report in PDF format. An example report can be found here: [example_prometheus_alerts_report.pdf](example_prometheus_alerts_report.pdf).

The generated PDF includes:
1. **Alerts Over Time (Line Chart)**: Shows alert frequency trends.
<img width="1001" alt="Screen Shot 2025-02-02 at 14 05 00" src="https://github.com/user-attachments/assets/12cea63e-f28a-46b5-94f8-81750603c143" />

2. **Alert Distribution (Pie Chart)**: Displays the proportion of each alert type.
<img width="628" alt="Screen Shot 2025-02-02 at 14 08 14" src="https://github.com/user-attachments/assets/37908122-1f6b-4d58-8ef3-63a3342890ea" />

3. **Alert Summary Table**: Categorizes alerts based on their types and distributions.
4. **Enrichment Summary Table**: Shows how alerts are enriched and categorized.
<img width="648" alt="Screen Shot 2025-02-02 at 14 05 35" src="https://github.com/user-attachments/assets/ad47383c-e8e3-4d2d-9029-bfe50b9b1806" />

## How to Use
This script works by calling Robusta’s API, which stores historical data on Prometheus alerts. It fetches alert information and generates a detailed report.

### Installation
To install the required dependencies, run:

```sh
pip install -r requirements.txt
```

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

## Troubleshooting
- **No alerts appearing in the report?**
  - Ensure that `AUTH_TOKEN` and `ACCOUNT_ID` are correctly set.
  - Check if the Robusta API is returning data for the requested time range.
- **PDF generation issues?**
  - Ensure that `fpdf` is installed and the required fonts are available in the `imported/` directory.
  - Check if `matplotlib` and `pandas` are installed correctly.

## Contributing
If you'd like to improve this script, feel free to submit a pull request or open an issue.
