import logging
import MySQLdb 
from spyne import rpc, ServiceBase, Integer, Unicode, Iterable, Float
from .models import TourModel

DB_HOST = 'localhost'
DB_USER = 'user_catalogo'
DB_PASS = 'tourpass123'
DB_NAME = 'catalogo_db'

class TourService(ServiceBase):
    
    @rpc(_returns=Iterable(TourModel))
    def listAllTours(ctx):
        db = None 
        try:
            db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
            cursor = db.cursor()
            query = "SELECT id, nombre, destino, precio, cupos_disponibles, duracion_horas, descripcion FROM tours"
            cursor.execute(query)
            tours_data = cursor.fetchall()
            cursor.close()
            results = []
            for row in tours_data:
                results.append(
                    TourModel(
                        id=row[0],
                        nombre=row[1],
                        destino=row[2],
                        precio=float(row[3]),
                        cupos_disponibles=row[4],
                        duracion_horas=float(row[5]),
                        descripcion_corta=str(row[6])[:100] + '...'
                    )
                )
            print(f"SOAP Service: Devolviendo {len(results)} tours.")
            return results
        except Exception as e:
            logging.error("Error en la consulta listAllTours: %s", e)
            return []
        finally:
            if db:
                db.close()
                
    @rpc(Integer, _returns=TourModel)
    def getTourById(ctx, tour_id):
        db = None 
        try:
            db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
            cursor = db.cursor()
            query = "SELECT id, nombre, destino, precio, cupos_disponibles, duracion_horas, descripcion FROM tours WHERE id = %s"
            cursor.execute(query, (tour_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                print(f"SOAP Service: Tour ID {tour_id} encontrado.")
                return TourModel(
                    id=row[0],
                    nombre=row[1],
                    destino=row[2],
                    precio=float(row[3]),
                    cupos_disponibles=row[4],
                    duracion_horas=float(row[5]),
                    descripcion_corta=str(row[6])[:100] + '...'
                )
            return None 
        except Exception as e:
            logging.error("Error en la consulta getTourById: %s", e)
            return None
        finally:
            if db:
                db.close()