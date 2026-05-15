from app.database import Base
from app.modules.clientes.models import Cliente
from app.modules.ventas.models import Venta, DetalleVenta
from app.modules.compra.models import Compra, DetalleCompra
from app.modules.inventario.models import Producto, Categoria

__all__ = ["Base", "Cliente", "Venta", "DetalleVenta", "Compra", "DetalleCompra", "Producto", "Categoria"]