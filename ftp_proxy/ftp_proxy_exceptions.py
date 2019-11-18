class ProxyException(Exception):
    """Proxy returned an error."""
    def __init__(self, message='Proxy returned an error.'):
        # Call the base class constructor with the parameters it needs
        super(ProxyException, self).__init__(message)

