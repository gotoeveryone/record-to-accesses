""" ソーシャルサイトへアクセスし、APIを利用して結果を更新する """
import datetime
import os
from os.path import join, dirname
import pathlib
import sys
from dotenv import load_dotenv
import api_client
import crawler
import json
import model
import utils

# .envから環境変数を取得
DOTENV_PATH = join(dirname(__file__), '.env')
load_dotenv(DOTENV_PATH)

START = datetime.datetime.now()
WORK_DATE = START.strftime('%Y-%m-%d')
# ENDPOINT = os.environ.get('AWS_API_ENDPOINT')

MAIL_TEMPLATE = """
-----%s 処理結果-----
　スロット：%s
　ルーレット：%s (%d回実施)
　スクラッチ：%s

　結果の格納：%s
"""

if __name__ == '__main__':
    # ロガー
    utils.LOGGER = utils.get_logger('record_to_social.log')
    utils.LOGGER.info('%s 処理開始' % WORK_DATE)

    # GET
    response = api_client.call_lambda('accessToSocial', {
        'dateOfAccess': WORK_DATE,
    })
    crawler.RESULTS = model.Result(json.loads(
        response['Payload'].read().decode('utf-8'))['result'])

    if crawler.RESULTS.is_cleared():
        utils.LOGGER.info('%s 処理終了（処理済み）' % WORK_DATE)
        sys.exit()

    # スクリーンショット保存ディレクトリ生成
    SAVE_DIR = '%s/%s/%s' % (os.environ.get('SCREENSHOT_DIR'),
                             START.strftime('%Y-%m'), START.strftime('%Y-%m-%d'))
    pathlib.Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)

    crawler.access_to_sp(SAVE_DIR)

    # PUT
    response = api_client.call_lambda('putSocial', {
        'dateOfAccess': WORK_DATE,
        'result': crawler.RESULTS.fields(),
    })
    put_success = True if response['ResponseMetadata']['HTTPStatusCode'] == 200 else False

    MAIL_BODY = MAIL_TEMPLATE % (
        WORK_DATE,
        '成功' if crawler.RESULTS.slot.get('success') else '失敗',
        '成功' if crawler.RESULTS.roulette.get('success') else '失敗',
        crawler.RESULTS.roulette.get(
            'count') if crawler.RESULTS.roulette.get('count') else 0,
        '成功' if crawler.RESULTS.scratch.get('success') else '失敗',
        '成功' if put_success else '失敗',
    )
    utils.send_mail(START, os.environ.get('MAIL_TO_ADDRESS'),
                    'ソーシャル関連ページアクセス結果通知', MAIL_BODY)

    utils.LOGGER.info('%s 処理終了' % WORK_DATE)
