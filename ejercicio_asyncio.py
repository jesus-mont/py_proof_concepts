import asyncio
import time
from typing import Any

# ==========================================
# 1. CLIENTES ASÍNCRONOS MOCK (I/O)
# ==========================================
async def fetch_user_data(user_id: str) -> dict[str, Any]:
    await asyncio.sleep(0.3)
    return {"id": user_id, "name": "Ivan Montaño"}

async def fetch_orders(user_id: str) -> list[dict[str, Any]]:
    await asyncio.sleep(0.5)
    return [{"order_id": 101, "total": 150.0}]

async def fetch_notifications_count(user_id: str) -> int:
    await asyncio.sleep(0.2)
    return 5


# ==========================================
# 2. AGGREGATOR CONCURRENTE
# ==========================================
async def build_user_profile(user_id: str) -> dict[str, Any]:
    start_time = time.perf_counter()

    # TODO: Usar asyncio.gather(...) para ejecutar las 3 corrutinas en paralelo y desempaquetar sus resultados
    user_info, orders, unread_notifications = await asyncio.gather(fetch_user_data('1'),
                                                                   fetch_orders('1'),
                                                                   fetch_notifications_count('1'),
                                                                   return_exceptions=True)

    elapsed = time.perf_counter() - start_time
    print(f"⏱️ Perfil construido en: {elapsed:.2f} segundos")

    return {
        "user": user_info,
        "orders": orders,
        "unread_notifications": unread_notifications
    }


# ==========================================
# 3. EVENT LOOP RUNNER
# ==========================================
if __name__ == "__main__":
    # TODO: ¿Cómo se ejecuta una corrutina principal desde el punto de entrada síncrono en Python?
    asyncio.run(build_user_profile('1'))
    pass