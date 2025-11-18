import logging
from wsgiref.simple_server import make_server
from spyne import Application
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from app.service import TourService

APP_TNS = 'tourfer.soap.catalogo'

application = Application(
    [TourService],                      
    tns=APP_TNS,                        
    in_protocol=Soap11(validator='lxml'), 
    out_protocol=Soap11()                 
)

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    server_address = '127.0.0.1'
    server_port = 5003
    
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

    server = make_server(server_address, server_port, wsgi_application)
    
    print(f"Servidor SOAP corriendo en http://{server_address}:{server_port}")
    print(f"WSDL disponible en: http://{server_address}:{server_port}/?wsdl")
    
    server.serve_forever()

    