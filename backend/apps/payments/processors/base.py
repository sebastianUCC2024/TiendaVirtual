from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class PaymentIntentResult:
    payment_intent_id: str
    client_secret: str
    status: str
    amount: Decimal
    currency: str


@dataclass
class WebhookResult:
    event_type: str
    payment_intent_id: str
    status: str
    raw_event: dict


class PaymentProcessor(ABC):
    """
    Interfaz abstracta para procesadores de pago.
    Cualquier nueva pasarela debe implementar esta clase.
    """

    @abstractmethod
    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        metadata: Optional[dict] = None
    ) -> PaymentIntentResult:
        """Crea una intención de pago y retorna los datos necesarios para el frontend."""
        ...

    @abstractmethod
    def confirm_payment(self, payment_intent_id: str) -> dict:
        """Confirma el estado actual de un pago."""
        ...

    @abstractmethod
    def refund(self, payment_intent_id: str, amount: Optional[Decimal] = None) -> dict:
        """Realiza un reembolso total o parcial."""
        ...

    @abstractmethod
    def handle_webhook(self, payload: bytes, signature: str) -> WebhookResult:
        """Valida y procesa un evento webhook del proveedor."""
        ...
