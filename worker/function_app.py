import azure.functions as func
import logging
import requests
import os
import uuid
from datetime import datetime
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

app = func.FunctionApp()

COSMOS_URL = "https://cosmos-cryptoguardas001.documents.azure.com:443/"

@app.schedule(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=True) 
def PriceAuditor(myTimer: func.TimerRequest) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            price = response.json()['bitcoin']['eur']
            
            audit_record = {
                "id": str(uuid.uuid4()),
                "coin_id": "bitcoin",
                "price_eur": price,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "CoinGecko",
                "auth_method": "Managed Identity" 
            }

            # 3. Save to Database (Securely)
            try:
                credential = DefaultAzureCredential()
                client = CosmosClient(url=COSMOS_URL, credential=credential)
                
                container = client.get_database_client("CryptoDb").get_container_client("PriceHistory")
                container.create_item(body=audit_record)
                
                logging.info(f"SECURE AUDIT SUCCESS: Saved Price ${price} using Managed Identity.")
            except Exception as db_error:
                logging.error(f"Database Error: {str(db_error)}")
                
        else:
            logging.warning(f"AUDIT FAILED: API Status {response.status_code}")
            
    except Exception as e:
        logging.error(f"CRITICAL: Worker crashed - {str(e)}")