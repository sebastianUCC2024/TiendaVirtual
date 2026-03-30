class InsufficientStockError(Exception):
    """Stock insuficiente para completar la operación."""
    def __init__(self, product_name: str, available: int):
        self.product_name = product_name
        self.available = available
        super().__init__(f"Stock insuficiente para '{product_name}'. Disponible: {available}")


class EmptyCartError(Exception):
    """El carrito está vacío."""
    pass


class InvalidCouponError(Exception):
    """Cupón inválido o expirado."""
    pass


class OrderStatusError(Exception):
    """Transición de estado inválida."""
    pass
