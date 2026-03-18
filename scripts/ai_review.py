import os
from anthropic import Anthropic

from github_client import (
    get_pr_files,
    upsert_pr_comment,
)
from review_policy import should_skip_file, exceed_diff_limit
from review_service import review_file_with_ai, parse_review

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

repo = os.environ["GITHUB_REPOSITORY"]
token = os.environ["GITHUB_TOKEN"]
pr_number = os.environ["PR_NUMBER"]
commit_id = os.environ.get("PR_HEAD_SHA")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

AI_REVIEW_TAG = "<!-- AI_REVIEW_COMMENT -->"

files = get_pr_files(repo, pr_number, headers)

current_total = 0
reviews = []
reviewed_count = 0
partial = False

for file in files:
    filename = file["filename"]
    diff = file.get("patch")

    if should_skip_file(filename, diff, file):
        continue

    if exceed_diff_limit(current_total, len(diff or "")):
        partial = True
        break

    current_total += len(diff)

    review = review_file_with_ai(client, filename, diff[:1500])
    parsed = parse_review(review)

    if not parsed:
        reviews.append(f"### 📄 {filename}\n{review}")
        continue

    reviewed_count += 1

    file_comments = []

    for item in parsed:
        line = item.get("line")
        comment = item.get("comment")

        if not line or not comment:
            continue

        file_comments.append(f"- line {line}: {comment}")

    if file_comments:
        reviews.append(
            f"### 📄 {filename}\n" + "\n".join(file_comments)
        )


# 최종 메시지
if reviews:
    final = "\n\n".join(reviews)
elif reviewed_count > 0:
    final = "특별한 문제는 발견되지 않았습니다. 👍"
else:
    final = "리뷰 대상 코드가 없습니다."

if partial:
    final += "\n\n⚠️ 일부 파일만 리뷰되었습니다 (diff 제한 초과)"

body = f"{AI_REVIEW_TAG}\n## 🤖 AI Code Review\n\n{final}"

upsert_pr_comment(repo, pr_number, headers, body, AI_REVIEW_TAG)