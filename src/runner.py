import subprocess
import sys
import re
import time
import tempfile
import os

def run_tests(test_ids, cwd=None):
    if not test_ids:
        return None

    # Test ID ieraksta pagaidu failā, jo Windows komandrindai ir garuma limits (~32 767 rakstzīmes)
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    for tid in test_ids:
        tmp.write(tid + "\n")
    tmp.close()

    # Pytest lasa test ID no faila ar @ prefiksu
    cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short", "--no-header", "-p", "no:warnings",
           f"@{tmp.name}"]

    start_time = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=cwd)
    os.unlink(tmp.name)
    total_time = time.time() - start_time

    output = proc.stdout + proc.stderr

    # Parsē katra testa statusu no pytest izvades.
    # Piemērs: "tests/test_auth.py::test_login FAILED  [ 25%]"
    results = {}
    status_pattern = re.compile(r"^(.+?)\s+(PASSED|FAILED|ERROR)", re.MULTILINE)
    for match in status_pattern.finditer(output):
        results[match.group(1)] = match.group(2)

    passed = sum(1 for s in results.values() if s == "PASSED")
    failed = sum(1 for s in results.values() if s == "FAILED")

    return {
        "results": results,
        "passed": passed,
        "failed": failed,
        "total": len(test_ids),
        "total_time": round(total_time, 3),
    }


# Aprēķina APFD (Average Percentage of Faults Detected) vērtību, kas parāda, cik ātri prioritizētā testu secībā tiek atklātas kļūdas.
def calc_apfd(test_ids, results):
    # Ja testu saraksts ir tukšs, atgriež None, jo APFD nav piemērojams
    n = len(test_ids)
    if n == 0:
        return None

    # Atrod testu pozīcijas, kurās ir kļūdas (FAILED)
    fault_positions = [
        i for i, tid in enumerate(test_ids, start=1)
        if results.get(tid) == "FAILED"
    ]
    m = len(fault_positions)

    # Ja nav nesekmīgu testu, APFD nav piemērojams un atgriež None
    if m == 0:
        return None

    # Aprēķina APFD vērtību
    apfd = 1 - sum(fault_positions) / (n * m) + 1 / (2 * n)
    return round(apfd, 3)
