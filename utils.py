""" ユーティリティ """
import codecs
import logging
import os
import smtplib
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

# ロガー
LOGGER = None


def get_logger(filename: str):
    """
    ロガーインスタンス取得
    """
    log_dir = os.environ.get('LOG_DIR')
    log_level = os.environ.get('LOG_LEVEL', logging.INFO)
    log_format = '%(asctime)s  %(levelname)s  %(message)s'

    # 標準出力も設定
    logging.basicConfig(level=log_level, format=log_format)

    # ファイル出力
    if log_dir and log_dir.endswith('/'):
        log_dir += '/'
    handler = logging.StreamHandler(codecs.open('%s%s' % (log_dir, filename),
                                                mode='a', encoding='utf-8'))
    handler.setFormatter(logging.Formatter(log_format))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(log_level)

    return logger


def send_mail(start, to_addresses, subject, body):
    """
    メール送信を行います。
    :param start datetime
    :param to_address str|array
    :param subject str
    :param body str
    """

    if not isinstance(to_addresses, list):
        to_addresses = [to_addresses]

    user = os.environ.get('MAIL_USER')
    password = os.environ.get('MAIL_PASSWORD')

    # 本文にヘッダを付与
    header = u'開始時間：%s | 終了時間：%s\n\n' % \
        (start.strftime("%Y/%m/%d %H:%M:%S"),
         datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    body = header + body

    # 本文
    msg = MIMEText(body.encode("utf-8"), _charset="utf-8")

    # 件名、宛先
    subject = u'【自動通知】%s_%s' % (start.strftime('%Y%m%d'), subject)
    to_str = ','.join(to_addresses)

    # ヘッダ
    msg['Subject'] = subject
    user_name = os.environ.get('MAIL_FROM_NAME').encode('utf-8')
    msg['From'] = formataddr((str(Header(user_name, 'utf-8')), user))
    msg['To'] = to_str

    logger = logging.getLogger(__name__)
    try:
        host = os.environ.get('MAIL_HOST').encode('utf-8')
        port = os.environ.get('MAIL_PORT').encode('utf-8')
        smtp = smtplib.SMTP(host=host, port=port)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(user, password)
        smtp.sendmail(os.environ.get('MAIL_FROM_ADDRESS'),
                      to_str, msg.as_string())
        smtp.quit()
        logger.info(u'メールを送信しました。')
        return True
    except smtplib.SMTPException as exception:
        logger.exception(u'メール送信に失敗しました。例外の型【%s】, 詳細【%s】',
                         type(exception), str(exception))
        logger.error(u'件名：%s', msg['Subject'])
        logger.error(u'本文：%s', body)
        return False
