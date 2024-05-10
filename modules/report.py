class Report():
    def __init__(self) -> None:
        pass



# Generate example data
# data = chartify.examples.example_data()

# # Sum price grouped by date
# price_by_date = data.groupby("date")["total_price"].sum(
# ).reset_index()  # Move 'date' from index to column
# print(price_by_date.head())

# # Plot the data
# ch = chartify.Chart(blank_labels=True, x_axis_type="datetime")
# ch.set_title("Line charts")
# ch.set_subtitle("Plot two numeric values connected by an ordered line.")
# ch.plot.line(
#     # Data must be sorted by x column
#     data_frame=price_by_date.sort_values("date"),
#     x_column="date",
#     y_column="total_price",
# )

# ch.save("char.png", "png")

# # Libraries
# from dotenv import load_dotenv
# import os

# # AutoPyPDF Lib
# from AutoPyPDF.generator import GenerateReport
# from AutoPyPDF.utils import getFileName, dates
# from AutoPyPDF.database import Database
# from AutoPyPDF.config import signature
# import time


# # ReportLab Libraries
# from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
# from reportlab.lib.styles import ParagraphStyle

# # Load .env vars
# load_dotenv()
# DEVELOPMENT = os.environ.get("DEVELOPMENT") == "True"

# def generalReport(db: Database, report: GenerateReport):
#     database.ranges = dates.get_last_month_range()

#     attackers = db.getAttackers()
#     top10Vulns = db.getTop10Vulns()
#     auditViolations = db.getAuditViolations()

#     # 1696132800000 # 'Sun Oct 01 2023 00:00:00 GMT-0400 (hora de Venezuela)'
#     # 1698811199000 # 'Tue Oct 31 2023 23:59:59 GMT-0400 (hora de Venezuela)'


# if __name__ == "__main__":
#     signature["title"] = "ENSA TI: Monitoreo con Logrhythm - Informe Mensual de Amenazas"

#     output = getFileName("{title} - {stime}")
#     report = GenerateReport(output, signature)
#     database = Database()
#     inch, colors = report.constants.values()

#     generalReport(database, report)

#     report.build()
