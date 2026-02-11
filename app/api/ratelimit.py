from fastapi import Request, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from fastapi_limiter.limiter import FastAPILimiter

def tenant_rate_limiter(
    times: int,
    seconds: int,
):
    async def dependency(request: Request):
        user = request.state.user  # injected earlier
        tenant_id = user.tenant_id

        limiter = RateLimiter(
            times=times,
            seconds=seconds,
            identifier=lambda _: f"tenant:{tenant_id}",
        )

        await limiter(request)

    return dependency
