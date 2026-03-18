import requests

def get_pr_files(repo, pr_number, headers):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files?per_page=100"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch PR files: {res.text}")
    return res.json()


def upsert_pr_comment(repo, pr_number, headers, body, tag):
    comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    res = requests.get(comments_url, headers=headers)

    existing_id = None

    if res.status_code == 200:
        for c in res.json():
            if tag in c["body"]:
                existing_id = c["id"]
                break

    data = {"body": body}

    if existing_id:
        update_url = f"https://api.github.com/repos/{repo}/issues/comments/{existing_id}"
        requests.patch(update_url, headers=headers, json=data)
    else:
        requests.post(comments_url, headers=headers, json=data)