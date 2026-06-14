from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://icps:icps_secret@127.0.0.1:5432/icps_master"
    port: int = 8000

    mqtt_enabled: bool = True
    mqtt_broker: str = "207.246.121.211"
    mqtt_port: int = 1883
    mqtt_qos: int = 1
    mqtt_client_id: str = "icps-seller-sim"
    mqtt_subscribe_topic: str = "rfid/1514032003830/1514250054321/edi/850"
    mqtt_ack_topic: str = "rfid/1514250054321/1514032003830/edi/855"
    mqtt_asn_topic: str = "rfid/1514250054321/1514032003830/edi/856"

    seller_gln: str = "1514250054321"
    seller_name: str = "ICPS-Lab"
    buyer_gln: str = "1514032003830"
    buyer_name: str = "IoT-Lab"

    fulfillment_mode: str = "simulated"
    fulfillment_delay_seconds: int = 5
    default_carrier: str = "FedEx"
    mqtt_retry_attempts: int = 3
    mqtt_retry_delay_seconds: float = 1.0


settings = Settings()
