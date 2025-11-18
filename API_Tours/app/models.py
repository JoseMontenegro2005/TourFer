from spyne import ComplexModel, Integer, Unicode, Float

class TourModel(ComplexModel):

    id = Integer
    nombre = Unicode
    destino = Unicode
    precio = Float
    cupos_disponibles = Integer
    duracion_horas = Float
    descripcion_corta = Unicode 


