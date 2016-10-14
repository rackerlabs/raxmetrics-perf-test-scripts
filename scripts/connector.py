
try:
    from net.grinder.plugin.http import HTTPRequest
    from grinder_connector import GrinderConnector as Connector
except ImportError:
    from requests_connector import RequestsConnector as Connector
