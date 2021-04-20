import requests
import re


def login():
    # 테라 펀딩 사이트 접근
    company_url = "https://www.terafunding.com/"
    res = requests.get(company_url)
    res.raise_for_status()

    # 로그인에 필요한 정보 가져오기
    script = re.findall('<script type="text/javascript" src="\S+</script>', res.text)
    src = re.findall('_nuxt/\S+.js', script[-1])

    url = company_url + src[0]
    res = requests.get(url)

    data = re.findall('client_id:"\S+",client_secret:"\S+",grant_type:"\S+",scope:\S+"}', res.text)
    data = data[0].split(',')

    client_id = data[0].replace('client_id:', "").replace('"', "")
    client_secret = data[1].replace('client_secret:', "").replace('"', "")
    grant_type = data[2].replace('grant_type:', "").replace('"', "")
    scope = data[3].replace('scope:', "").replace('"', "").replace("}", "")
    return [client_id, client_secret, grant_type, scope]



