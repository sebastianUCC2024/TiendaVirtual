class PaymentException(Exception):
    """Error durante el procesamiento de un pago."""
    pass


class WebhookException(Exception):
    """Error al validar o procesar un webhook."""
    pass
