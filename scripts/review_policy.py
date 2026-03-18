MAX_TOTAL_DIFF = 5000

def should_skip_file(filename, file_diff, file):
    if not file_diff:
        return True
    if not file_diff.strip():
        return True
    if any(x in filename for x in ["node_modules", "dist", "build"]):
        return True
    if len(file_diff) > 2000:
        return True
    if file["status"] in ["removed", "renamed"]:
        return True
    if not filename.endswith((".ts", ".js", ".tsx")):
        return True
    if "test" in filename or "spec" in filename:
        return True
    return False


def exceed_diff_limit(current_total, diff_length):
    return current_total + diff_length > MAX_TOTAL_DIFF