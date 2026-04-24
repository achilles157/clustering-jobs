from curl_cffi import requests
import json

# Minimal config for testing
COOKIES = {
    'session': 'Fe26.2**b89deca7cf137d23ec2ef497c60ad08f621b6d6e887f98780c2b64bd4cce1cc2*kkHrIr7Wk9_ggsXnAHovqg*AJ4WxhZCuZf1GBTp2dHq-gizuG6G67Cy1rEJjN6xJilnvea7uu4tBz0Z0rga1FBk**4d47cb9068861434bc2f6d18ecf0433815c945000a5b52e05ab8c5c7a3adfcec*n3H9n6mgEmudXxiRKC2SMRjwgKOvEc-UeW6tDZDU9kg',
}

HEADERS = {
    'content-type': 'application/json',
    'x-glints-country-code': 'ID',
}

QUERY = """
query searchJobsV3($data: JobSearchConditionInput!) {
  searchJobsV3(data: $data) {
    jobsInPage {
      id
      title
    }
  }
}
"""

def test_sort(sort_val):
    payload = {
        'operationName': 'searchJobsV3',
        'variables': {
            'data': {
                'CountryCode': 'ID',
                'sortBy': sort_val,
                'pageSize': 5,
                'page': 1,
            },
        },
        'query': QUERY
    }
    
    res = requests.post(
        'https://glints.com/api/v2-alc/graphql', 
        json=payload, 
        headers=HEADERS, 
        cookies=COOKIES,
        impersonate="chrome110"
    )
    print(f"Testing sortBy={sort_val}...")
    if res.status_code == 200:
        data = res.json()
        jobs = data.get('data', {}).get('searchJobsV3', {}).get('jobsInPage', [])
        for j in jobs:
            print(f"- {j['title']} (ID: {j['id']})")
    else:
        print(f"Error ({sort_val}): {res.status_code}")
        print(res.text[:300])

test_sort("LATEST")
test_sort("RELEVANCE")
test_sort("SALARY_DESC")
