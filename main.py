from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
import os
from urllib import request

from authlib.integrations.requests_client import AssertionSession
from gspread import Client


BOT_TOKEN = os.getenv('BOT_USER_OAUTH_TOKEN')
CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')
REMINDER_SHEET_ID = os.getenv('REMINDER_SPREADSHEET_ID')
USER_MYSELF = os.getenv('MENTION_USER_ID')


def create_assertion_session(conf_file, scopes, subject=None):
    with open(conf_file) as f:
        conf = json.load(f)

    token_url = conf['token_uri']
    issuer = conf['client_email']
    key = conf['private_key']
    key_id = conf.get('private_key_id')

    header = {'alg': 'RS256'}
    if key_id:
        header['kid'] = key_id
    
    claims = {'scope': ' '.join(scopes)}
    return AssertionSession(
        grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
        token_endpoint=token_url,
        issuer=issuer,
        audience=token_url,
        claims=claims,
        subject=subject,
        key=key,
        header=header,
    )


@dataclass
class Task:
    category: str
    description: str
    due_date: date
    is_important: bool


def create_task(data):
    due_datetime = datetime.strptime(data['期日'], '%Y/%m/%d')
    due_date = date(due_datetime.year, due_datetime.month, due_datetime.day)
    is_important = data['重要度'] != ''
    return Task(data['分類'], data['やること'], due_date, is_important)


def post_slack(channel, message):
    slack_url = 'https://slack.com/api/chat.postMessage'
    data = {
        'channel': channel,
        'text': message
    }
    jsoned = json.dumps(data).encode('utf-8')
    headers = {
        'Authorization': f"Bearer {BOT_TOKEN}",
        'Content-type': 'application/json'
    }
    req = request.Request(slack_url, data=jsoned, method='POST', headers=headers)
    request.urlopen(req)


def main_handler(event, context):
    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    session = create_assertion_session(CREDENTIALS_PATH, scopes)
    gc = Client(None, session)

    spread_sheet = gc.open_by_key(REMINDER_SHEET_ID)
    worksheet = spread_sheet.sheet1
    list_of_lists = worksheet.get_all_values()

    header = list_of_lists[0]
    rows = []
    for row in list_of_lists[1:]:
        data = {key: value for key, value in zip(header, row)}
        rows.append(data)

    undone_tasks = []
    for row in rows:
        if not row['達成']:
            task = create_task(row)
            undone_tasks.append(task)
    
    today = date.today()
    needs_notify_tasks = []
    for task in undone_tasks:
        due_date = task.due_date
        if task.is_important:
            if due_date - today <= timedelta(days=7):
                needs_notify_tasks.append(task)
        else:
            if due_date - today <= timedelta(days=3):
                needs_notify_tasks.append(task)
    
    message = f'<@{USER_MYSELF}> 仕掛け人さま、おはようございます\n'
    sorted_tasks = sorted(needs_notify_tasks, key=lambda d: d.due_date)
    if not sorted_tasks:
        message += '今日も一日、張り切ってまいりましょう'
    else:
        message += '本日のやることをお知らせしますね\n\n'
        for task in sorted_tasks:
            message += (
                f'[{task.category}]{task.description}'
                f' ({task.due_date:%m/%d}まで)\n'
            )
    
    post_slack('general', message)


if __name__ == '__main__':
    main_handler(None, None)
