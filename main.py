import argparse
import json
from src.git_analyzer import get_changed_lines
from src.prioritizer import get_prioritized_tests
from src.risk_scorer import get_risk
from src.runner import run_tests, calc_apfd
from src.reporter import generate_report

# --risk parametrs manuālai riska līmeņa izmainīšanai
parser = argparse.ArgumentParser()
parser.add_argument("--risk", choices=["LOW", "MEDIUM", "HIGH"], default=None)
args = parser.parse_args()

# Iegūst mainītās rindiņas no pēdējā commit
changed_lines = get_changed_lines()

# Prioritizē testus pēc mainītajām rindiņām
prioritized = get_prioritized_tests(changed_lines, "coverage_by_test.json")

# Aprēķina kopējo mainīto rindiņu skaitu
total_changed = sum(len(lines) for lines in changed_lines.values())

data = json.load(open("coverage_by_test.json"))

# Iegūst kopu ar tām mainītajām rindiņām, kuras tiek pārklātas ar testiem.
covered = set()
for file_path, lines in changed_lines.items():
    for test_id, _ in prioritized:
        if file_path in data.get(test_id, {}):
            covered.update(set(data[test_id][file_path]) & set(lines))

# Aprēķina testu pārklājuma procentu
coverage_pct = (len(covered) / total_changed * 100) if total_changed > 0 else 0.0

# Iegūst ietekmēto testu skaitu (testi ar score > 0)
affected_tests = sum(1 for _, score in prioritized if score > 0)

# Aprēķina riska līmeni
risk = get_risk(changed_lines, coverage_pct, affected_tests)
if args.risk:
    risk = args.risk

if risk != "HIGH":
    tests_to_run = [test_id for test_id, score in prioritized if score > 0]
else:
    tests_to_run = [test_id for test_id, _ in prioritized]
    # Augsta riska gadījumā tiek izpildīti visi testi
    affected_tests = len(prioritized)

# Izvada rezultātus komandrindā
print(f"Risk level: {risk}")
print(f"Coverage: {coverage_pct:.1f}%")
print(f"Affected tests: {affected_tests}")
print()
print("Prioritized tests:")
matching = [(test_id, score) for test_id, score in prioritized if score > 0]
if matching:
    for test_id, score in matching:
        print(f"  {score:3}  {test_id}")
else:
    print("  (no tests matched the changed lines)")

# Palaiž testus
print(f"\nStarting pytest execution ({len(tests_to_run)} tests)...")
results = run_tests(tests_to_run, cwd="../httpx")

if results is None:
    print("No tests were executed.")
    exit()

if risk == "HIGH":
    apfd = calc_apfd(tests_to_run, results["results"])
else:
    apfd = None

print()
print("Execution results:")
print(f"Total tests run: {results['total']}")
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
print(f"Execution time: {results['total_time']}s")

if risk == "HIGH":
    print(f"APFD: {apfd}")
else:
    total_tests = len(prioritized)
    selected = len(tests_to_run)
    selected_pct = (selected / total_tests * 100) if total_tests > 0 else 0

    print(f"Selected tests: {selected}/{total_tests} ({selected_pct:.2f}%)")

# Sagatavo testa rezultātu vārdnīcu priekš HTML atskaites
test_results = dict(results["results"])

# Ģenerē HTML atskaiti
generate_report(
    prioritized=prioritized,
    risk=risk,
    coverage_pct=coverage_pct,
    affected_tests=affected_tests,
    total_tests=len(prioritized),
    test_results=test_results,
    execution_time=results["total_time"],
    apfd=apfd,
)
