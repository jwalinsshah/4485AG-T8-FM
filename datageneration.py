import random
import pandas as pd
from faker import Faker

fake = Faker()

def generate_5g_data(num_records):
    data = []
    for _ in range(num_records):
        record = {
            'device_id': random.randint(1000, 9999),
            'device_type': random.choice(['smartphone', 'IoT device', 'router']),
            'os': random.choice(['Android', 'iOS', 'Windows']),
            'manufacturer': random.choice(['Samsung', 'Apple', 'Huawei', 'Nokia', 'Sony']),
            'network_operator': random.choice(['Verizon', 'AT&T', 'T-Mobile', 'Vodafone']),
            'user_id': random.randint(1, 10000),
            'name': fake.name(),
            'age': random.randint(18, 80),
            'location': (fake.latitude(), fake.longitude()),
            'data_usage': round(random.uniform(0.1, 50.0), 2),  # in GB
            'network_speed': round(random.uniform(10.0, 1000.0), 2),  # in Mbps
            'connection_duration': random.randint(10, 7200),  # in seconds
            'session_start_time': fake.date_time_this_year(),
            'cell_id': random.randint(1, 1000),
            'signal_strength': round(random.uniform(-120.0, -40.0), 2),  # in dBm
            'latency': round(random.uniform(1.0, 100.0), 2),  # in milliseconds
            'jitter': round(random.uniform(0.1, 50.0), 2),  # in milliseconds
            'packet_loss': round(random.uniform(0.0, 5.0), 2),  # in percentage
        }
        data.append(record)
    return data

# Generate 1000 records
dataset = generate_5g_data(1000)

# Convert the dataset to a DataFrame using Pandas
df = pd.DataFrame(dataset)

# Save the DataFrame to a CSV file
df.to_csv('5g_data_analytics_pandas.csv', index=False)

print("Data saved to 5g_data_analytics_pandas.csv")


# Read the CSV file into a DataFrame
df = pd.read_csv('5g_data_analytics_pandas.csv')

# Display the first 5 rows of the DataFrame
print(df.head())
