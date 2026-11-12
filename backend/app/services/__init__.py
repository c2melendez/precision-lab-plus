"""Application services package."""

# Install EC-H-10 hyperbolic tangent range hook at import time.
try:
    from app.services.hyperbolic_range import install_tanh_range_hook

    install_tanh_range_hook()
except Exception:
    # Never block application startup if the optional hook fails to load.
    pass
