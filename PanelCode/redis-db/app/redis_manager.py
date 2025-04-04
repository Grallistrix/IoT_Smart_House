import redis
import os
from datetime import datetime

class RedisManager:
    def __init__(self):
        self.r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=6379,
            db=0,
            decode_responses=True
        )

    def add_electricity_usage(self, date: str, time: str, price_per_hour: float):
        """
        Add electricity usage data to Redis.
        Key format: Electr_[Date in DD.MM.YYYY-HH.MM]
        Value structure: {"Day": "DD.MM.YYYY", "Time": "HH:MM", "PricePerHour": string (from float)}
        """
        key = f"Electr_{date}-{time}"
        value = {
            "Day": date,
            "Time": time,
            "PricePerHour": str(price_per_hour)
        }
        self.r.hmset(key, value)

    def add_sensor_data(self, sensor_number: int, date: str, time: str, temperature_value: int, humidity_value: float):
        """
        Add sensor data to Redis.
        Key format: Sensor-[Sensor Number]-[DD.MM.YYYY]-[HH.MM]
        Value structure: {"SensorNumber": int, "Day": "DD.MM.YYYY", "Time": "HH:MM", "TemperatureValue": string(from int), "HumidityValue": string(from float) }
        """
        key = f"Sensor-{sensor_number}-{date}-{time}"
        value = {
            "SensorNumber": str(sensor_number),
            "Day": date,
            "Time": time,
            "TemperatureValue": str(temperature_value),
            "HumidityValue": str(humidity_value)
        }
        self.r.hmset(key, value)
        
#======================================================================================================================

    def get_electricity_usage(self, date: str, time: str):
        key = f"Electr_{date}-{time}"
        return self.r.hgetall(key)

    def get_sensor_data(self, sensor_number: int, date: str, time: str):
        key = f"Sensor-{sensor_number}-{date}-{time}"
        return self.r.hgetall(key)

    def get_last_electricity_usage(self, num_values: int):
        keys = self.r.keys(f"Electr_*")
        keys.sort(reverse=True)  # Sorting keys to get the most recent ones
        last_values = []
        for key in keys[:num_values]:
            last_values.append(self.r.hgetall(key))
        return last_values

    def get_last_sensor_data(self, sensor_number: int, num_values: int):
        keys = self.r.keys(f"Sensor-{sensor_number}-*")
        keys.sort(reverse=True)  # Sorting keys to get the most recent ones
        last_values = []
        for key in keys[:num_values]:
            last_values.append(self.r.hgetall(key))
        return last_values