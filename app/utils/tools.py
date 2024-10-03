import re


def check_url(url: str = "/api/v1/system-manage/roles/{role_id}/buttons", url2: str = "/api/v1/system-manage/roles/1/buttons") -> bool:
    pattern = re.sub(r'\{.*?}', '[^/]+', url)
    if re.match(pattern, url2):
        return True
    return False
