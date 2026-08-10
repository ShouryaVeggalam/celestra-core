"""
Example: product apps import Celestra Core auth + monitoring.

    python examples/auth_and_monitoring.py
"""

from __future__ import annotations

from auth.passwords import hash_password, verify_password
from auth.tokens import create_access_token, decode_token
from monitoring.metrics import MetricsRegistry
from monitoring.tracing import start_trace, trace_headers


def main() -> None:
    # Passwords
    hashed = hash_password("demo-password")
    assert verify_password("demo-password", hashed)

    # JWT
    token = create_access_token(subject="user-123", secret_key="demo-secret-key-32chars-minimum!!")
    claims = decode_token(token, secret_key="demo-secret-key-32chars-minimum!!", expected_type="access")
    print("jwt.sub =", claims["sub"])

    # Tracing + metrics
    start_trace()
    print("trace headers =", trace_headers())
    metrics = MetricsRegistry(namespace="demo")
    metrics.observe_request(method="GET", path="/health", status=200, duration_seconds=0.002)
    body, _ = metrics.render_prometheus()
    print("metrics sample lines:")
    for line in body.decode().splitlines()[:5]:
        print(" ", line)


if __name__ == "__main__":
    main()
