"""
conftest.py raíz del proyecto – registra los pytest markers personalizados
para evitar PytestUnknownMarkWarning.
"""
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "unit: pruebas unitarias rápidas sin dependencias externas")
    config.addinivalue_line("markers", "integration: pruebas de integración por microservicio (in-memory)")
    config.addinivalue_line("markers", "e2e: flujo completo de extremo a extremo usando fakes")
    config.addinivalue_line("markers", "real: pruebas contra infraestructura real (RabbitMQ, etc.)")
