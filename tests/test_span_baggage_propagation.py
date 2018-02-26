
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest import TestCase
import socket

from equals import any_dict, any_string
from opentracing_instrumentation.interceptors import OpenTracingInterceptor
import requests


class GalileoClientInterceptor(OpenTracingInterceptor):

    def process(self, request, span):
        span.set_baggage_item('x-baggage', 'foober')


class MockServerRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        expected_dict = {
            'uber-trace-id': any_string,
            'uberctx-x-baggage': 'foober'
        }

        try:
            assert self.headers == any_dict.containing(**expected_dict)
            self.send_response(requests.codes.ok)
        except Exception:
            self.send_response(requests.codes.bad)

        self.end_headers()


class TestRequestsAgainstMockServer(TestCase):

    def _get_free_port(self):
        s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        s.bind(('localhost', 0))
        address, port = s.getsockname()
        s.close()
        return port
