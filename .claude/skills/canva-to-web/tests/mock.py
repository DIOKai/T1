#!/usr/bin/env python3
"""Tiny PostgREST/Supabase-Auth look-alike for testing backend.js against the real schema + RLS.
Only the calls backend.js makes. Not a full implementation."""
import json, re, subprocess, sys, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qsl

PGHOST, KEY = sys.argv[1], 'sb_publishable_test'
STAFF = {'staff@shop.test': ('pw123456', sys.argv[2])}
LOG = []

def run(sql, role, sub=None):
    pre = "begin; " + (f"set local request.jwt.claim.sub = '{sub}'; " if sub else "") + f"set local role {role}; "
    r = subprocess.run(['psql', '-h', PGHOST, '-p', '55432', '-U', 'postgres', '-d', 'shop', '-At', '-v', 'ON_ERROR_STOP=1',
                        '-c', pre + sql + "; commit;"], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l not in ('BEGIN', 'SET', 'COMMIT')]
    return r.returncode, "\n".join(lines), r.stderr

def lit(v): return "'" + str(v).replace("'", "''") + "'"

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'apikey, authorization, content-type, prefer')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, OPTIONS')
    def reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code); self.cors(); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(data)
    def do_OPTIONS(self):
        self.send_response(204); self.cors(); self.end_headers()
    def who(self):
        LOG.append((self.command, self.path, self.headers.get('apikey'), self.headers.get('Authorization')))
        if self.headers.get('apikey') != KEY: return None, None
        a = self.headers.get('Authorization', '')
        m = re.match(r'Bearer tok-([0-9a-f-]{36})$', a)
        if m: return 'authenticated', m.group(1)
        if a == 'Bearer ' + KEY: return 'anon', None
        if a: return 'bad', None
        return 'anon', None
    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return json.loads(self.rfile.read(n) or b'null')
    def pgerr(self, err):
        msg = re.search(r'ERROR:\s+(.*)', err).group(1).strip()
        if 'permission denied' in msg: return self.reply(401, {'code': '42501', 'message': msg})
        return self.reply(400, {'code': 'P0001', 'message': msg})
    def handle_call(self):
        u = urlparse(self.path)
        if u.path == '/__log': return self.reply(200, LOG)
        if u.path.startswith('/auth/v1/token'):
            if self.headers.get('apikey') != KEY: return self.reply(401, {'message': 'no apikey'})
            q = dict(parse_qsl(u.query)); b = self.body()
            if q.get('grant_type') == 'password':
                s = STAFF.get(b.get('email'))
                if b.get('email') == 'outsider@shop.test' and b.get('password') == 'pw123456':
                    return self.reply(200, {'access_token': 'tok-' + sys.argv[3], 'refresh_token': 'r-out', 'expires_in': 3600})
                if not s or s[0] != b.get('password'): return self.reply(400, {'error': 'invalid_grant'})
                return self.reply(200, {'access_token': 'tok-' + s[1], 'refresh_token': 'r-' + s[1], 'expires_in': 3600})
            return self.reply(400, {'error': 'unsupported'})
        role, sub = self.who()
        if role in (None, 'bad'): return self.reply(401, {'message': 'Invalid API key'})
        m = re.match(r'/rest/v1/(rpc/)?([a-z_]+)$', u.path)
        if not m: return self.reply(404, {})
        rpc, name = m.group(1), m.group(2)
        params = parse_qsl(u.query)
        if rpc:
            b = self.body() or {}
            args = ", ".join(f"{k} => {lit(json.dumps(v) if isinstance(v, (dict, list)) else v)}" for k, v in b.items())
            code, out, err = run(f"select to_jsonb(public.{name}({args}))", role, sub)
            return self.pgerr(err) if code else self.reply(200, json.loads(out) if out else None)
        where, order = [], ''
        for k, v in params:
            if k == 'select': continue
            if k == 'order':
                col, _, d = v.partition('.'); order = f" order by {col} {d or 'asc'}"; continue
            op, _, val = v.partition('.')
            where.append(f"{k} {'=' if op == 'eq' else '>='} {lit(val)}")
        w = (" where " + " and ".join(where)) if where else ''
        if self.command == 'GET':
            code, out, err = run(f"select coalesce(json_agg(t{order.replace(' order by ', ' order by t.') if order else ''}), '[]') from public.{name} t{w}", role, sub)
        else:
            b = self.body()
            # like PostgREST: JSON objects go to jsonb columns, JSON arrays to Postgres arrays
            def val(v):
                if v is None: return 'null'
                if isinstance(v, dict): return lit(json.dumps(v))
                if isinstance(v, list): return lit('{' + ','.join('"' + str(x) + '"' for x in v) + '}')
                return lit(v)
            sets = ", ".join(f"{k} = {val(v)}" for k, v in b.items())
            code, out, err = run(f"with u as (update public.{name} set {sets}{w} returning *) select coalesce(json_agg(u), '[]') from u", role, sub)
        return self.pgerr(err) if code else self.reply(200, json.loads(out))
    do_GET = do_POST = do_PATCH = handle_call

ThreadingHTTPServer(('127.0.0.1', 8766), H).serve_forever()
