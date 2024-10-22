class HttpRequest:
    def __init__(self, http_request):

        self._http_request = http_request
        self._request_length = len(http_request)
        self._headers = {}
        self._request_type = None
        self._file_path = None

        # TODO: make more robust to bad HTTP requests
        if self._request_length > 0:
            request_segments = http_request.split('\r\n')
            # request_line = [TYPE] [PATH] [HTTP/1.1]
            request_line = request_segments[0]
            self._request_type = request_line.split(' ')[0]
            self._file_path = request_line.split(' ')[1][1:]


            # Parse headers
            for header in request_segments[1:]:
                if ":" in header:
                    key, value = header.split(':', 1)
                    self._headers[key.strip()] = value.strip()

    def get_request_length(self):
        return self._request_length

    def get_request_type(self):
        return self._request_type

    def get_file_path(self):
        return self._file_path

    def get_headers(self):
        return self._headers