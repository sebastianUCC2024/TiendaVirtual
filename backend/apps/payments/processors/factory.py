from .base import PaymentProcessor
from .stripe_adapter import StripeAdapter


class PaymentProcessorFactory:
    """
    Factory que instancia el procesador correcto según el proveedor.
    Para agregar una nueva pasarela: registrar la clase en _registry.
    """

    _registry: dict[str, type[PaymentProcessor]] = {
        'stripe': StripeAdapter,
        # 'mercadopago': MercadoPagoAdapter,  # ejemplo futuro
        # 'paypal': PayPalAdapter,
    }

    @classmethod
    def get_processor(cls, provider: str) -> PaymentProcessor:
        processor_class = cls._registry.get(provider.lower())
        if not processor_class:
            raise ValueError(f"Proveedor de pago no soportado: '{provider}'. "
                             f"Disponibles: {list(cls._registry.keys())}")
        return processor_class()

    @classmethod
    def register(cls, provider: str, processor_class: type[PaymentProcessor]) -> None:
        """Permite registrar nuevos proveedores en runtime."""
        cls._registry[provider.lower()] = processor_class
