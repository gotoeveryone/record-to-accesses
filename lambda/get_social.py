""" Get result from DynamoDB """
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    """ main handler """
    return {
        'date_of_access': event['dateOfAccess'],
        'result': get_results(event),
    }


def get_results(event):
    """ 結果オブジェクトの返却 """

    # DynamoDBから結果オブジェクトを取得
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('access_to_socials')

    date_of_access = event['dateOfAccess']
    result = table.get_item(Key={
        'date_of_access': date_of_access
    })
    return result['Item']['result'] if 'Item' in result else {}
