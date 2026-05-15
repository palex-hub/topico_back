from mangum import Mangum
from app.main import app

handler = Mangum(app)

# Comentario de control para forzar el empaquetado nativo con Podman en Fedora