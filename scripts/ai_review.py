import os
import subprocess
import requests
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# GitHub Actions 환경에서 diff 비교가 가능하도록 base 브랜치(master)를 fetch
subprocess.run(["git", "fetch", "origin", "master"], check=True)

# Pull Request에서 변경된 파일 목록 가져오기
files = subprocess.check_output(
    ["git", "diff", "--name-only", "origin/master...HEAD"]
).decode().splitlines()

reviews = []

for file in files:

    if not file.endswith((".ts", ".js")):
        continue

    # 현재 파일에 대한 git diff 가져오기
    file_diff = subprocess.check_output(
        ["git", "diff", "origin/master...HEAD", "--", file]
    ).decode()

    if not file_diff.strip():
        continue

    # 토큰 사용량이 과도해지는 것을 방지하기 위해 diff 길이 제한
    file_diff = file_diff[:4000]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
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

                    출력 형식 (반드시 지킬 것):

                    ### 🔍 주요 문제
                    - 발견된 문제를 bullet point로 설명

                    ### ⚠️ 개선 제안
                    - 코드 개선 방법 제안

                    ### 👍 긍정적인 부분
                    - 좋은 코드가 있다면 간단히 언급

                    다음은 Pull Request에서 변경된 파일입니다.

                    파일:
                    {file}

                    아래는 해당 파일의 git diff 입니다.

                    {file_diff}
                    '''
            }
        ],
    )

    review = response.content[0].text if response.content else "리뷰 생성 실패"
    reviews.append(f"### 📄 {file}\n{review}")

review_text = "\n\n".join(reviews) if reviews else "리뷰할 변경 사항이 없습니다."

repo = os.environ["GITHUB_REPOSITORY"]
token = os.environ["GITHUB_TOKEN"]
pr_number = os.environ["PR_NUMBER"]

url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

headers = {
    "Authorization": f"Bearer {token}",
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