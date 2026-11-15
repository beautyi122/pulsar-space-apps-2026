#!/usr/bin/env python3
"""Run Pulsar locally. Only binds 127.0.0.1; locally uploaded CSV is not stored."""
import json, os, sys
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
ROOT=Path(__file__).resolve().parent
APP=ROOT/'app'
sys.path.insert(0,str(ROOT/'research'))
from AnalyzeCSV import analyze_text, ALLOWED_ACTIVITY

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(APP),**kwargs)
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        super().end_headers()
    def do_GET(self):
        if self.path=='/':self.path='/index.html'
        super().do_GET()
    def do_POST(self):
        path=urlparse(self.path)
        if path.path!='/api/analyze':return self.reply(404,{'error':'Unknown API endpoint'})
        try:
            n=int(self.headers.get('Content-Length',0))
            if n<=0 or n>2000000:raise ValueError('Expected a CSV smaller than 2 MB')
            activity=parse_qs(path.query).get('activity',['walk'])[0]
            if activity not in ALLOWED_ACTIVITY:raise ValueError('Activity unsupported')
            content=self.rfile.read(n).decode('utf-8-sig')
            result=analyze_text(content,activity)
            return self.reply(200,result)
        except (UnicodeDecodeError, ValueError) as e:return self.reply(400,{'error':str(e)})
        except Exception as e:
            print('Analysis error:',str(e),file=sys.stderr)
            return self.reply(500,{'error':'Local analysis failed; review terminal for details.'})
    def reply(self,status,result):
        content=json.dumps(result,allow_nan=False).encode('utf8')
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content)
    def log_message(self,fmt,*args):pass

if __name__=='__main__':
    import argparse,webbrowser
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--port',type=int,default=8765)
    args=ap.parse_args()
    if not 1024<=args.port<=65535:raise ValueError('Use an unprivileged port between 1024 and 65535')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'Pulsar local console: http://127.0.0.1:{args.port}/',flush=True)
    print('Research demonstration, not medical monitoring. No network server or file storage.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
