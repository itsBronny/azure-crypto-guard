from fastapi import FastAPI, HTTPException
import requests
import os
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

app = FastAPI()

COSMOS_URL = "https://cosmos-cryptoguardas001.documents.azure.com:443/"
DATABASE_NAME = "CryptoDb"
CONTAINER_NAME = "PriceHistory"

@app.get("/")
def read_root():
    return {
        "status": "CryptoGuard Active", 
        "endpoints": ["/price (Live)", "/history (Database)"],
        "auth": "Managed Identity for DB access"
    }

@app.get("/price")
def get_price():
    """Legacy Endpoint: Fetches live from CoinGecko"""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {"bitcoin_price": data['bitcoin']['eur']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    """Secure Endpoint: Fetches the last 10 records from Cosmos DB using Managed Identity"""
    try:
        # Connect Securely
        credential = DefaultAzureCredential()

        # Connect to Cosmos DB using Managed Identity
        client = CosmosClient(url=COSMOS_URL, credential=credential)
        container = client.get_database_client(DATABASE_NAME).get_container_client(CONTAINER_NAME)
        
        # Query 
        query = "SELECT TOP 10 c.price_eur, c.timestamp, c.source FROM c ORDER BY c.timestamp DESC"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        return {"last_10_checks": items}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")