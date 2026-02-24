"""
WealthHive - Plataforma Quantitativa de Investimentos
Autor: WealthHive Team
Versão: 16.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="WealthHive API",
    description="API para análise quantitativa e gestão de investimentos",
    version="16.0.0",
    contact={
        "name": "WealthHive Team",
        "url": "https://wealthhive.io",
        "email": "contact@wealthhive.io"
    }
)

# ... resto do código
