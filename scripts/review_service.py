import time
import json

def review_file_with_ai(client, filename, file_diff):
    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                            당신은 10년 경력의 시니어 백엔드 엔지니어입니다.
                            NestJS 및 TypeScript 기반 서버 코드를 리뷰한다고 가정하고 리뷰를 수행하세요.

                            목표:
                            - 실제 코드 리뷰어처럼 구체적이고 실용적인 리뷰를 작성합니다.
                            - 단순한 칭찬은 하지 말고 문제점 중심으로 리뷰합니다.
                            - 문제가 없다면 빈 배열 []을 반환합니다.

                            리뷰 기준:
                            1. 버그 가능성 (Null 처리, async/await 누락, race condition 등)
                            2. 성능 문제 (불필요한 연산, 비효율 로직)
                            3. 보안 문제 (입력 검증 누락 등)
                            4. 코드 가독성 및 유지보수성
                            5. NestJS / TypeScript 관점 개선

                            출력 형식 (반드시 JSON 배열):
                            [
                            {{
                                "line": <문제가 발생한 라인 번호>,
                                "comment": "<리뷰 내용>"
                            }}
                            ]

                            주의사항:
                            - 문제가 있는 라인만 반환
                            - 문제가 없다면 반드시 [] 반환
                            - line은 diff 기준 라인

                            파일:
                            {filename}

                            diff:
                            {file_diff}
                            """
                    }
                ],
            )
            return response.content[0].text
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)


def parse_review(review_text):
    try:
        return json.loads(review_text)
    except:
        return None