def calculate_row_count(table: str) -> int:
    ROW_DELIMITERS = {"┼", "├", "┤", "─"}
    return sum(set(line) == ROW_DELIMITERS for line in table.split("\n"))
