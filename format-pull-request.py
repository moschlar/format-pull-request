#!/usr/bin/env python

# Defaults:
SMTP_HOST = None
SMTP_PORT = None
SMTP_SSL = False
SMTP_USER = ""
SMTP_PASS = ""

MAIL_FROM = ""
MAIL_TO = ""

import sys
import requests
#import json
import smtplib
from email.mime.text import MIMEText


class SMTP_DUMMY(object):
    def sendmail(self, from_, to, msg, *args, **kw):
        print from_
        print to
        print msg


def get_json(url, *args, **kwargs):
    r = requests.get(url, *args, **kwargs)
    if r.ok:
        #return json.loads(r.text or r.content)
        try:
            return r.json()
        except Exception as e:
            raise Exception('Response payload could not be read as json', e)
    else:
        raise Exception('Response status is not ok', r.status_code)


if SMTP_HOST:
    if SMTP_SSL:
        s = smtplib.SMTP_SSL()
    else:
        s = smtplib.SMTP()

    s.connect(SMTP_HOST, SMTP_PORT)
    if SMTP_USER and SMTP_PASS:
        s.login(SMTP_USER, SMTP_PASS)
else:
    s = SMTP_DUMMY()


def format_pull_request(owner, repo, pull_id):
    r = requests.get('https://api.github.com/repos/%s/%s/pulls/%d' % (owner, repo, pull_id))

    if not r.ok: raise
    j = json.loads(r.text or r.content)

    title, body = j['title'], j['body']
    p = requests.get(j['patch_url'])

    if not p.ok: raise
    patch = p.text or p.content

    msg = MIMEText(body + '\n\n' + patch)

    msg['Subject'] = '[%s/%s/pulls/%d] %s' % (owner, repo, pull_id, title)
    msg['From'] = MAIL_FROM
    msg['To'] = MAIL_TO

    #print msg.as_string()

    s.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())


if __name__ == '__main__':
    owner, repo = sys.argv[1:3]

    if len(sys.argv) > 3:
        pull_id = int(sys.argv[3])
    else:
        raise NotImplementedError

    format_pull_request(owner, repo, pull_id)


s.close()

