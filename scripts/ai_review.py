import os
import requests
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

repo = os.environ["GITHUB_REPOSITORY"]
token = os.environ["GITHUB_TOKEN"]
pr_number = os.environ["PR_NUMBER"]
commit_id = os.environ.get("PR_HEAD_SHA")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

# GitHub PR files API로 변경된 파일 목록과 patch(diff) 가져오기
files_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files?per_page=100"
files_response = requests.get(files_url, headers=headers)

if files_response.status_code != 200:
    print("PR 파일 목록을 가져오지 못했습니다:", files_response.text)
    exit(1)

files_data = files_response.json()

# PR 변경 파일이 너무 많으면 AI 리뷰 스킵 (비용 폭주 방지)
if len(files_data) > 5:
    print(f"PR changed files: {len(files_data)}, skip AI review to avoid cost explosion")
    exit(0)

reviews = []

for file in files_data:
    filename = file["filename"]
    file_diff = file.get("patch")

    # patch가 없는 경우 (binary 파일 등) 스킵
    if not file_diff:
        continue

    if not filename.endswith((".ts", ".js", ".tsx")):
        continue

    if "test" in filename or "spec" in filename:
        continue

    # 토큰 사용량이 과도해지는 것을 방지하기 위해 diff 길이 제한
    file_diff = file_diff[:1500]

    response = client.messages.create(
        model="claude-haiku",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f'''
                    당신은 10년 경력의 시니어 백엔드 엔지니어입니다.
                    NestJS 및 TypeScript 기반 서버 코드를 리뷰한다고 가정하고 리뷰를 수행하세요.

                    목표:
                    - 실제 코드 리뷰어처럼 **구체적이고 실용적인 리뷰**를 작성합니다.
                    - 단순한 칭찬은 하지 말고 **문제점 중심으로 리뷰**합니다.
                    - 문제가 없다면 "특별한 문제는 발견되지 않았습니다."라고 작성합니다.

                    리뷰 기준:
                    1. 버그 가능성 (Null 처리, async/await 누락, race condition 등)
                    2. 성능 문제 (불필요한 연산, 비효율 로직, 반복 호출)
                    3. 보안 문제 (입력 검증 누락, 민감정보 노출 가능성)
                    4. 코드 가독성 및 유지보수성
                    5. NestJS / TypeScript 관점의 개선 사항

                    출력 형식 (JSON 배열로 반환):

                    [
                      {{
                        "line": <문제가 발생한 라인 번호>,
                        "comment": "<리뷰 내용>"
                      }}
                    ]

                    주의사항:
                    - 문제가 있는 라인만 반환합니다.
                    - 문제가 없다면 빈 배열 [] 을 반환합니다.
                    - line 값은 diff의 변경 라인을 기준으로 작성합니다.

                    다음은 Pull Request에서 변경된 파일입니다.

                    파일:
                    {filename}

                    아래는 해당 파일의 git diff 입니다.

                    {file_diff}
                    '''
            }
        ],
    )

    review = response.content[0].text if response.content else "리뷰 생성 실패"

    import json

    try:
        line_reviews = json.loads(review)
    except Exception:
        # JSON 파싱 실패 시 일반 리뷰로 fallback
        reviews.append(f"### 📄 {filename}\n{review}")
        continue

    for item in line_reviews:
        line = item.get("line")
        comment = item.get("comment")

        if not line or not comment:
            continue

        review_comment_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"

        review_data = {
            "body": comment,
            "commit_id": commit_id,
            "path": filename,
            "position": line,
        }

        requests.post(review_comment_url, headers=headers, json=review_data)

review_text = "\n\n".join(reviews) if reviews else "리뷰할 변경 사항이 없습니다."

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}

data = {
    "body": f"## 🤖 AI Code Review\n\n{review_text}"
}

# 기존 PR 댓글 목록 조회
comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
comments_response = requests.get(comments_url, headers=headers)

existing_comment_id = None

if comments_response.status_code == 200:
    comments = comments_response.json()
    for comment in comments:
        if "🤖 AI Code Review" in comment["body"]:
            existing_comment_id = comment["id"]
            break

# 기존 AI 댓글이 있으면 업데이트
if existing_comment_id:
    update_url = f"https://api.github.com/repos/{repo}/issues/comments/{existing_comment_id}"
    update_response = requests.patch(update_url, headers=headers, json=data)

    if update_response.status_code == 200:
        print("AI review comment updated")
    else:
        print("Failed to update comment:", update_response.text)

# 없으면 새 댓글 생성
else:
    create_response = requests.post(comments_url, headers=headers, json=data)

    if create_response.status_code == 201:
        print("AI review comment created")
    else:
        print("Failed to create comment:", create_response.text)