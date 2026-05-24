from datetime import datetime

def generate_report(prioritized, risk, coverage_pct, affected_tests, total_tests, test_results, execution_time, apfd=None):
    # Definētas krāsas katram riska līmenim
    risk_colors = {"LOW": "green", "MEDIUM": "orange", "HIGH": "red"}
    risk_color = risk_colors.get(risk, "black")

    # Atskaites ģenerēšanas datums un laiks
    gen_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    # Atlasīto testu procents
    selected_pct = (affected_tests / total_tests * 100) if total_tests > 0 else 0

    # Prioritizēto testu tabula (sakārtota dilstošā secībā pēc score)
    sorted_tests = sorted(prioritized, key=lambda x: x[1], reverse=True)
    has_scored = any(score > 0 for _, score in sorted_tests)

    if has_scored:
        priority_rows = ""
        for test_id, score in sorted_tests:
            if score > 0:
                priority_rows += f"<tr><td>{test_id}</td><td>{score}</td></tr>\n"
        priority_section = (
            "<table><tr><th>Tests</th><th>Atbilstības vērtība</th></tr>\n"
            + priority_rows
            + "</table>"
        )
    else:
        priority_section = (
            "<p style=\"color:#555\">Neviens tests nepārklāj mainītās rindiņas. "
            "Tiek izpildīti visi testi.</p>"
        )

    # Izpildes rezultātu tabula, kur vispirms parādīti FAILED testi un pēc tam PASSED
    failed_tests = [name for name, status in test_results.items() if status == "FAILED"]
    passed_tests = [name for name, status in test_results.items() if status == "PASSED"]

    result_rows = ""
    for name in failed_tests:
        result_rows += (
            f"<tr><td>{name}</td>"
            f"<td style=\"color:red; font-weight:bold\">FAILED</td></tr>\n"
        )
    for name in passed_tests:
        result_rows += (
            f"<tr><td>{name}</td>"
            f"<td style=\"color:green; font-weight:bold\">PASSED</td></tr>\n"
        )

    # Passed/failed skaits no rezultātiem
    passed_count = len(passed_tests)
    failed_count = len(failed_tests)

    # APFD rinda kopsavilkumā — tikai ja risks ir HIGH
    apfd_row = ""
    if risk == "HIGH" and apfd is not None:
        apfd_row = f"<tr><td><b>APFD vērtība</b></td><td>{apfd}</td></tr>\n"

    # Saliek kopā visu HTML lapu
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Testu prioritizācijas atskaite</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; }}
    h1 {{ color: #333; }}
    h2 {{ border-bottom: 2px solid #ccc; padding-bottom: 4px; margin-top: 30px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
    th, td {{ padding: 8px 12px; border: 1px solid #ccc; text-align: left; }}
    th {{ background: #f0f0f0; }}
  </style>
</head>
<body>

<h1>Testu prioritizācijas atskaite</h1>
<p style="color:#666">Ģenerēts: {gen_time}</p>

<h2>Kopsavilkums</h2>
<table>
  <tr><td><b>Riska līmenis</b></td>
      <td><span style="color:{risk_color}; font-weight:bold">{risk}</span></td></tr>
  <tr><td><b>Pārklājuma procents</b></td><td>{coverage_pct:.1f}%</td></tr>
  <tr><td><b>Atlasītie testi</b></td>
      <td>{affected_tests} / {total_tests} ({selected_pct:.1f}%)</td></tr>
  <tr><td><b>Izpildes laiks</b></td><td>{execution_time:.3f} s</td></tr>
  <tr><td><b>Sekmīgi (Passed)</b></td><td style="color:green; font-weight:bold">{passed_count}</td></tr>
  <tr><td><b>Nesekmīgi (Failed)</b></td><td style="color:red; font-weight:bold">{failed_count}</td></tr>
  {apfd_row}</table>

<h2>Izpildes rezultāti</h2>
<table>
  <tr><th>Tests</th><th>Rezultāts</th></tr>
  {result_rows}</table>

<h2>Prioritizēto testu tabula</h2>
{priority_section}

</body>
</html>"""

    # Saglabā HTML failu
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\nReport saved as report.html")
