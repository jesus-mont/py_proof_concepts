import datetime
from typing import Protocol, Literal, Any, Callable, ParamSpec, TypeVar
import time
from functools import wraps
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_camel

# ==========================================
# 1. DECORADOR DE TIEMPO DE EJECUCIÓN
# ==========================================
P = ParamSpec("P")
R = TypeVar("R")

def log_execution_time(threshold_ms: float = 50.0):
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            inicio = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result

            finally:
                fin = time.perf_counter()
                duration = (fin - inicio) * 1000
                if duration > threshold_ms:
                    print(f" ALERTA: Ejecución lenta en {func.__name__}: {duration:.2f}ms")

        return wrapper
    return decorator

# ==========================================
# 2. DTOs CON PYDANTIC V2 (camelCase)
# ==========================================
class CamelBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True
    )

class AuditEventDTO(CamelBaseModel):
    event_id: str
    user_id: str
    ip_address: str
    payload: dict[str, Any]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    @field_validator("ip_address")
    @classmethod
    def sanitize_coupon(cls, ip_address: str | None) -> str | None:
        if ip_address is not None:
            return ip_address.strip()
        return None

    @model_validator(mode="after")
    def check_payload(self):
        if self.severity == "CRITICAL" and not self.payload:
            raise ValueError("Payload cannot be empty when severity is CRITICAL")
        return self

class AuditProcessedResponseDTO(CamelBaseModel):
    event_id: str
    status: str
    processed_at: str

# ==========================================
# 3. PROTOCOL & IMPLEMENTACIÓN
# ==========================================
class EventPublisher(Protocol):
    def publish(self, event: AuditEventDTO) -> bool:
        ...

class MockEventPublisher:
    def publish(self, event: AuditEventDTO) -> bool:
        if event.severity == 'CRITICAL':
          print(" Evento crítico publicado")
        else:
            print(" Evento normal publicado")
        return True


# ==========================================
# 4. SERVICIO DE NEGOCIO
# ==========================================
class AuditProcessorService:
    def __init__(self, publisher: EventPublisher) -> None:
        self._publisher = publisher

    @log_execution_time(threshold_ms=10.0)
    def process_event(self, event: AuditEventDTO) -> AuditProcessedResponseDTO:
         self._publisher.publish(event)

         return AuditProcessedResponseDTO(
             event_id=event.event_id,
             status = 'PUBLISHED',
             processed_at = datetime.now(datetime.timezone.utc).isoformat(),
         )
