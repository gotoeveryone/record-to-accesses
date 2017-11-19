""" ソーシャルサイトへアクセスし、APIを利用して結果を更新する """
import json
import os
import api_client

ENDPOINT = os.environ.get('AWS_API_ENDPOINT')

if __name__ == '__main__':
    # GET
    res = api_client.get(ENDPOINT, {
        'dateOfAccess': '20171119',
    })
    print(json.dumps(res.json(), indent=4))

    # PUT
    res = api_client.put(ENDPOINT, {
        'dateOfAccess': '20171119',
        'result': {
            'slot': False,
            'roulette': {
                'count': 0,
                'success': False,
            },
            'scratch': False,
        }
    })
    print(json.dumps(res.json(), indent=4))
