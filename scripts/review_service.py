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
                        당신은 시니어 백엔드 엔지니어입니다.
                        코드 리뷰를 수행하세요.

                        파일: {filename}
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