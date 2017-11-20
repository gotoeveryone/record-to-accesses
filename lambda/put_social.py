""" Put to DynamoDB """
import datetime
import decimal
import json
import time
import boto3


def lambda_handler(event, context):
    """ main handler """
    return put_results(event)


def put_results(event):
    """ 結果オブジェクトの返却 """

    # DynamoDBから結果オブジェクトを取得
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('access_to_socials')

    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    date_of_access = event['dateOfAccess']
    item = json.loads(json.dumps({
        'date_of_access': date_of_access,
        'result': event['result'],
        'ttl': int(time.mktime(tomorrow.timetuple())),
    }), parse_float=decimal.Decimal)
    table.put_item(Item=item)
    return item
