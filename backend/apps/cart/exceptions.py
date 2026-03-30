class InsufficientStockError(Exception):
    def __init__(self, product_name: str, available: int):
        self.product_name = product_name
        self.available = available
        super().__init__(f"Stock insuficiente para '{product_name}'. Disponible: {available}")


class ProductNotAvailableError(Exception):
    pass
