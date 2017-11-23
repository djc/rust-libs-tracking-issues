import requests, json, os

BASE = 'https://api.github.com'
ISSUES = '/repos/rust-lang/rust/issues'
EVENTS = '/repos/rust-lang/rust/issues/%s/events'

def get_links(rsp):
    links = {}
    if 'Link' not in rsp.headers:
        return links
    for link in rsp.headers['Link'].split(','):
        url, name = link.split(';')
        parts = name.split('"')
        links[parts[1]] = url[1:-1]
    return links

def collect(url):
    rsp = requests.get(url)
    if rsp.status_code != 200:
        raise Exception((url, rsp.status_code, rsp.json()))
    all = rsp.json()
    links = get_links(rsp)
    while 'next' in links:
        rsp = requests.get(links['next'])
        if rsp.status_code != 200:
            raise Exception((url, rsp.status_code, rsp.json()))
        all += rsp.json()
        links = get_links(rsp)
    return all

def cached(url, fn):
    if os.path.exists(fn):
        with open(fn) as f:
            data = json.load(f)
    else:
        data = collect(url)
        with open(fn, 'w') as f:
            json.dump(data, f, 2)
    return data

def get_issues():
    url = BASE + ISSUES + '?state=all&labels=T-libs,B-unstable'
    issues = cached(url, 'issues.json')
    return [i['number'] for i in issues]

def get_events(issue):
    events = cached(BASE + EVENTS % issue, '%s-events.json' % issue)
    print issue, [e for e in events if isinstance(e, basestring)]
    print json.dumps([e['event'] for e in events], indent=2)

def main():
    issues = get_issues()
    for issue in sorted(issues, reverse=True):
        events = get_events(issue)

if __name__ == '__main__':
    main()
