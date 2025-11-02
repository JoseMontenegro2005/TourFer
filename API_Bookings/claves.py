from flask_bcrypt import Bcrypt

# No necesitamos una app de Flask, solo la librería
bcrypt = Bcrypt()

# Lista de las contraseñas en texto plano de tus usuarios de prueba
passwords_planas = [
    'password123',   # para Ana
    'securepass456', # para Juan
    'mypassword789', # para Lucía
    'mfpass',        # para Manuel
    'sqpass'         # para Stefanny
]

print("--- Hashes de Contraseña para seed.sql ---")

for pw in passwords_planas:
    # Genera el hash y lo decodifica a texto para poder copiarlo
    hash_generado = bcrypt.generate_password_hash(pw).decode('utf-8')
    print(f"Password: {pw}\nHash: {hash_generado}\n")

print("--- Copia y pega los hashes en tu archivo seed.sql ---")