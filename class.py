import psutil
import time
from pymongo import MongoClient
import matplotlib.pyplot as plt
import config
import datetime

class Power:
    client = MongoClient(config.MONGODB_CONNECTION_STRING)
    col = MongoClient(config.MONGODB_CONNECTION_STRING)["power_stats"]["logs"]

    def __init__(self):
        self.cpu_percent = None
        self.ram_total = None
        self.ram_used = None
        self.timestamp = None

    def update_stats(self):
        # Update CPU percentage
        self.cpu_percent = psutil.cpu_percent()

        # Update RAM statistics
        mem = psutil.virtual_memory()
        self.ram_total = mem.total / (1024 * 1024 * 1024)  # Convert to GB
        self.ram_used = mem.used / (1024 * 1024 * 1024)  # Convert to GB

        # Update timestamp
        self.timestamp = time.time()

    def save_to_database(self):
        # Save power statistics to MongoDB database
        client = MongoClient(config.MONGODB_CONNECTION_STRING)
        db = client['power_stats']
        collection = db['logs']
        
        log = {
            'cpu_percent': self.cpu_percent,
            'ram_total': self.ram_total,
            'ram_used': self.ram_used,
            'timestamp': self.timestamp
        }
        collection.insert_one(log)
        client.close()

    @staticmethod
    def delete_old_logs():
        # Delete old logs from the database if the count exceeds 10000
        col = Power.col
        count = col.count_documents({})
        if count > 10000:
            oldest_logs = col.find().sort('timestamp', 1).limit(count - 10000)
            for log in oldest_logs:
                col.delete_one({'_id': log['_id']})
        Power.client.close()

    @staticmethod
    def plot_graph():
        # Plot power statistics grap
        client = MongoClient(config.MONGODB_CONNECTION_STRING)
        db = client['power_stats']
        collection = db['logs']
        data = collection.find()

        timestamps = []
        cpu_percent = []
        ram_total = []
        ram_used = []

        for log in data:
            timestamps.append(log['timestamp'])
            cpu_percent.append(log['cpu_percent'])
            ram_total.append(log['ram_total'])
            ram_used.append(log['ram_used'])

        client.close()

        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, cpu_percent, label='CPU %')
        plt.plot(timestamps, ram_total, label='RAM Total')
        plt.plot(timestamps, ram_used, label='RAM Used')
        plt.xlabel('Timestamp')
        plt.ylabel('Percentage / GB')
        plt.title('Power Statistics')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == '__main__':
    power = Power()

    while True:
        power.update_stats()
        power.save_to_database()
        power.delete_old_logs()
        print("works")
        time.sleep(1)  # Wait for 1 second before updating again
