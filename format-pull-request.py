#!/usr/bin/env python

print 'This software is:'
print ' +++ ALPHA +++ ' * 5

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

    def close(self):
        pass


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
    pull_uri = 'https://api.github.com/repos/%s/%s/pulls/%d' % (owner, repo, pull_id)
    pull = get_json(pull_uri)

    title, body = pull['title'], pull['body']

    commits = get_json(pull_uri + '/commits')
    commit_uri = pull['head']['repo']['commits_url']

    for commit in commits:
        commit['uri'] = commit_uri.replace('{/sha}', '/%s' % commit['sha'])
        print get_json(commit['uri'])
        commit['diff'] = requests.get(commit['uri'], headers={'Accept': 'application/vnd.github.beta.diff'}).text
        commit['patch'] = requests.get(commit['uri'], headers={'Accept': 'application/vnd.github.beta.patch'}).text

        s.sendmail(MAIL_FROM, MAIL_TO, commit['patch'])


if __name__ == '__main__':
    owner, repo = sys.argv[1:3]

    if len(sys.argv) > 3:
        pull_id = int(sys.argv[3])
    else:
        raise NotImplementedError

    format_pull_request(owner, repo, pull_id)


s.close()

