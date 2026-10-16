from decimal import Decimal
from typing import Protocol, Literal, Callable, ParamSpec, TypeVar
from functools import wraps
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

# ==========================================
# 1. DECORADOR DE REINTENTOS
# ==========================================
P = ParamSpec("P")
R = TypeVar("R")

def retry_on_exception(retries: int = 3):
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(retries):
                try:
                    # Intenta ejecutar la función original
                    return func(*args, **kwargs)
                except Exception as exc:
                    print(f"⚠️ Falló la ejecución (Intento {attempt + 1}/{retries}): {exc}")

                    # Si ya alcanzamos el límite de intentos, relanzamos el error
                    if attempt == retries - 1:
                        raise exc
        return wrapper
    return decorator

# ==========================================
# 2. MODELOS PYDANTIC V2 (camelCase)
# ==========================================
class CamelBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True
    )

class DiscountRequestDTO(CamelBaseModel):
    customer_id: str
    cart_total: Decimal = Field(..., gt=0)
    coupon_code: str | None = None

    @field_validator("coupon_code")
    @classmethod
    def sanitize_coupon(cls, coupon_code: str | None) -> str | None:
        if coupon_code is not None:
            return coupon_code.strip().upper()
        return None

class DiscountResponseDTO(CamelBaseModel):
    customer_id: str
    original_total: Decimal
    discount_amount: Decimal
    final_total: Decimal

# ==========================================
# 3. PROTOCOL (CONTRATO)
# ==========================================
class CouponRepository(Protocol):
    def get_discount_rate(self, code: str) -> Decimal:
        ...

class MockCouponRepository:
    def get_discount_rate(self, code: str) -> Decimal:
        # TODO: Si code es "WELCOME10", retorna Decimal("0.10").
        # De lo contrario, retorna Decimal("0.0").
        if code == "WELCOME10":
            return Decimal("0.10")
        else:
            return Decimal("0.0")


# ==========================================
# 4. SERVICIO DE NEGOCIO
# ==========================================
class DiscountService:
    def __init__(self, coupon_repo: CouponRepository) -> None:
        self._coupon_repo = coupon_repo

    @retry_on_exception(retries=2)
    def apply_discount(self, request: DiscountRequestDTO) -> DiscountResponseDTO:
        discount_rate = Decimal("0.0")
        if request.coupon_code:
            discount_rate = self._coupon_repo.get_discount_rate(request.coupon_code)

        discount_amount = request.cart_total * discount_rate
        final_total = request.cart_total - discount_amount

        return DiscountResponseDTO(
            customer_id=request.customer_id,
            original_total=request.cart_total,
            discount_amount=discount_amount,
            final_total=final_total,
        )
