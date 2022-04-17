from chalice.test import Client

from app import app


def api_method(default_expected_code=200):
    def my_decorator(func):
        def wrapped(self, *args, **kwargs):
            expected_code = kwargs.pop("expected_code", default_expected_code)
            response = func(self, *args, **kwargs)
            if response.status_code != expected_code:
                raise AssertionError("Expected status code: {} but was {}.".format(expected_code, response.status_code))
            return response
        return wrapped
    return my_decorator


class HttpApi:

    @property
    def base_url(self): return "/v1"

    @api_method()
    def get(self, url):
        full_url = self.base_url + url
        with Client(app) as client:
            return client.http.get(full_url)

    @api_method(default_expected_code=201)
    def post(self, url, headers, body):
        full_url = self.base_url + url
        with Client(app) as client:
            return client.http.post(path=full_url, headers=headers, body=body)

    @api_method()
    def put(self, url, headers, body):
        full_url = self.base_url + url
        with Client(app) as client:
            return client.http.put(path=full_url, headers=headers, body=body)

    @api_method(default_expected_code=204)
    def delete(self, url):
        full_url = self.base_url + url
        with Client(app) as client:
            return client.http.delete(full_url)
