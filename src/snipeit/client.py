from snipeit import endpoints


class SnipeItClient:

    class Endpoints:
        def __init__(self):
            self.endpoints = {}

        def __getattr__(self, name):
            try:
                return self.endpoints[name]
            except KeyError:
                raise AttributeError(name)

    def __init__(self, base_url, jwt, verify_https=True):
        self.base_url = base_url
        self.jwt = jwt
        self.verify_https = verify_https

        self.endpoints = self.Endpoints()
        self.register_endpoint('list_hardware', endpoints.ListHardware)
        self.register_endpoint(
            'get_hardware_bytag',
            endpoints.GetHardwareByTag
        )

    def register_endpoint(self, name, endpoint_class):
        setattr(self.endpoints, name, endpoint_class(client=self))
