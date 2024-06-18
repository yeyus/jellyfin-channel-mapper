from requests.auth import AuthBase


class JellyfinAPITokenAuth(AuthBase):
    def __init__(self, apiToken):
        self.apiToken = apiToken

    def __call__(self, r):
        r.headers['Authorization'] = f"MediaBrowser Token=\"{self.apiToken}\""
        return r
