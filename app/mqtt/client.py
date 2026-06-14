import json
import logging
import threading
import time
from typing import Callable

import paho.mqtt.client as mqtt

from app.config import settings

logger = logging.getLogger(__name__)


class MqttClientService:
    def __init__(self) -> None:
        self._client: mqtt.Client | None = None
        self._connected = False
        self._lock = threading.Lock()
        self._message_handler: Callable[[str, dict], None] | None = None

    @property
    def connected(self) -> bool:
        return self._connected

    def set_message_handler(self, handler: Callable[[str, dict], None]) -> None:
        self._message_handler = handler

    def start(self) -> None:
        if not settings.mqtt_enabled:
            logger.info("MQTT disabled; subscriber not started")
            return

        self._client = mqtt.Client(client_id=settings.mqtt_client_id, protocol=mqtt.MQTTv311)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.reconnect_delay_set(min_delay=1, max_delay=30)

        logger.info(
            "Connecting to MQTT broker",
            extra={"broker": settings.mqtt_broker, "port": settings.mqtt_port},
        )
        self._client.connect_async(settings.mqtt_broker, settings.mqtt_port, keepalive=60)
        self._client.loop_start()

    def stop(self) -> None:
        if self._client is None:
            return
        self._client.loop_stop()
        self._client.disconnect()
        self._client = None
        self._connected = False

    def publish_json(self, topic: str, payload: dict, retain: bool = False) -> None:
        if not settings.mqtt_enabled:
            logger.info("MQTT disabled; skipping publish to %s", topic)
            return

        if self._client is None:
            raise RuntimeError("MQTT client is not started")

        body = json.dumps(payload)
        last_error: Exception | None = None
        for attempt in range(1, settings.mqtt_retry_attempts + 1):
            try:
                result = self._client.publish(
                    topic,
                    body,
                    qos=settings.mqtt_qos,
                    retain=retain,
                )
                result.wait_for_publish(timeout=5)
                logger.info(
                    "Published MQTT message",
                    extra={
                        "topic": topic,
                        "message_id": payload.get("message_id"),
                        "attempt": attempt,
                    },
                )
                return
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "MQTT publish failed",
                    extra={"topic": topic, "attempt": attempt, "error": str(exc)},
                )
                time.sleep(settings.mqtt_retry_delay_seconds)

        raise RuntimeError(f"Failed to publish to {topic}: {last_error}")

    def _on_connect(self, client, _userdata, _flags, rc) -> None:
        if rc != 0:
            logger.error("MQTT connect failed", extra={"rc": rc})
            self._connected = False
            return

        self._connected = True
        client.subscribe(settings.mqtt_subscribe_topic, qos=settings.mqtt_qos)
        logger.info("MQTT connected and subscribed", extra={"topic": settings.mqtt_subscribe_topic})

    def _on_disconnect(self, _client, _userdata, rc) -> None:
        self._connected = False
        logger.warning("MQTT disconnected", extra={"rc": rc})

    def _on_message(self, _client, _userdata, msg) -> None:
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError as exc:
            logger.exception("Invalid MQTT JSON on topic %s: %s", topic, exc)
            return

        if self._message_handler is None:
            logger.warning("No MQTT message handler registered")
            return

        with self._lock:
            try:
                self._message_handler(topic, payload)
            except Exception:
                logger.exception("Error handling MQTT message on topic %s", topic)


mqtt_service = MqttClientService()
