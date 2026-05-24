def get_risk(changed_lines: dict, coverage_pct: float, affected_tests: int) -> str:
    score = 0

    # Saskaita kopējo mainīto rindiņu skaitu
    total_lines = sum(len(lines) for lines in changed_lines.values())

    # Piešķir riska punktus pēc izmaiņu apjoma
    if total_lines > 100:
        score += 3
    elif total_lines > 20:
        score += 1

    # Piešķir riska punktus pēc pārklājuma procenta
    if coverage_pct < 50:
        score += 3
    elif coverage_pct < 80:
        score += 1

    # Atgriež HIGH risku, ja neviens tests nav ietekmēts
    if affected_tests == 0:
        return "HIGH"

    # Atgriež riska līmeni pēc kopējā score
    if score >= 5:
        return "HIGH"
    elif score >= 2:
        return "MEDIUM"
    return "LOW"
