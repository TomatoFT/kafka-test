# Partitioning Strategies

Kafka provides different strategies for distributing messages across partitions within a topic. The partitioning strategy defines how Kafka determines which partition a message will be sent to. Kafka has several ways to do this, and each can be controlled via producer configuration.

Here are the key strategies used by Kafka to distribute messages into partitions:

### 1. **Round-robin (Default)**
- **Description**: The `round-robin` strategy simply sends messages to partitions in a sequential, cyclic manner. If you have 3 partitions, the first message goes to partition 0, the second to partition 1, the third to partition 2, and the fourth goes back to partition 0, and so on.
- **Use Case**: This is useful when you want an even distribution of messages across partitions, without considering the message content.
  
#### Example (Round-robin):
```python
from confluent_kafka import Producer

def on_delivery(err, msg):
    if err:
        print(f"Error delivering message: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition}] at offset {msg.offset()}")

# Configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'partitioner': 'roundrobin'  # This ensures round-robin partitioning
}

producer = Producer(conf)

# Produce a few messages to see round-robin partitioning
for i in range(10):
    producer.produce('example-topic', key=f'key-{i}', value=f'Message {i}', callback=on_delivery)

producer.flush()
```
In this case, messages will be evenly distributed across the available partitions in a cyclic order.

### 2. **Key-based (Hashing)**
- **Description**: Kafka can also determine the partition based on the **message key**. When a message is produced, Kafka will hash the key and assign the message to a partition based on the hash. This ensures that all messages with the same key will always be sent to the same partition.
- **Use Case**: This is useful when you need to ensure that all messages for a specific key (e.g., customer, user, order) are processed by the same consumer for consistency.
  
#### Example (Key-based):
```python
from confluent_kafka import Producer

def on_delivery(err, msg):
    if err:
        print(f"Error delivering message: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition}] at offset {msg.offset()}")

# Configuration
conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(conf)

# Produce a few messages with keys to see partitioning by key
for i in range(10):
    key = f'key-{i % 3}'  # Key will repeat every 3 messages to show key-based partitioning
    producer.produce('example-topic', key=key, value=f'Message {i}', callback=on_delivery)

producer.flush()
```
In this case, messages with the same key (e.g., `key-0`, `key-1`, or `key-2`) will always be sent to the same partition, ensuring messages for the same key are grouped together.

### 3. **Custom Partitioning Strategy**
- **Description**: Kafka allows you to implement a custom partitioner if the default partitioning strategies don’t meet your requirements. A custom partitioner lets you define your logic for how to map messages to partitions.
- **Use Case**: This is useful when you want more control over how messages are assigned to partitions, for example, based on business logic or advanced distribution patterns.
  
#### Example (Custom Partitioning):
```python
from confluent_kafka import Producer

class CustomPartitioner:
    def __init__(self):
        pass
    
    def __call__(self, key, all_partitions, available):
        # Simple custom logic: partition based on the length of the key
        return len(key) % len(all_partitions)

def on_delivery(err, msg):
    if err:
        print(f"Error delivering message: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition}] at offset {msg.offset()}")

# Configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'partitioner': CustomPartitioner()  # Use the custom partitioner
}

producer = Producer(conf)

# Produce a few messages to test custom partitioning
for i in range(10):
    key = f'key-{i % 3}'  # Repeat keys to see custom partitioning
    producer.produce('example-topic', key=key, value=f'Message {i}', callback=on_delivery)

producer.flush()
```
In this case, the custom partitioner uses the length of the key to decide which partition to assign the message to. You can replace the logic with whatever you need.

### 4. **Sticky Partitioner (Kafka 2.4 and above)**
- **Description**: The `sticky` partitioner aims to minimize rebalancing. It tries to stick messages to the same partition that a message with the same key was previously sent to. If a consumer group rebalances, the sticky assignor minimizes partition reassignments.
- **Use Case**: Best suited for cases where you want to preserve partition assignments as much as possible, especially when consumers join or leave a consumer group.
  
#### Example (Sticky Partitioner):
```python
from confluent_kafka import Producer

def on_delivery(err, msg):
    if err:
        print(f"Error delivering message: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition}] at offset {msg.offset()}")

# Configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'partition.assignment.strategy': 'sticky'  # Sticky partitioner strategy
}

producer = Producer(conf)

# Produce a few messages to test sticky partitioning
for i in range(10):
    key = f'key-{i % 3}'  # Repeated keys will stick to the same partition
    producer.produce('example-topic', key=key, value=f'Message {i}', callback=on_delivery)

producer.flush()
```
With sticky partitioning, Kafka will try to keep messages with the same key assigned to the same partition across consumer group rebalances.

---

### Summary of Partitioning Strategies

1. **Round-robin**:
   - Messages are distributed evenly across partitions in a cyclic fashion.
   - **Use case**: When you don’t need to preserve any order, just need to distribute messages evenly.

2. **Key-based (Hashing)**:
   - Messages are assigned to partitions based on the hash of their keys.
   - **Use case**: When you need to ensure that messages with the same key go to the same partition, which is useful for related message processing (e.g., processing all messages for a user in the same partition).

3. **Custom Partitioner**:
   - You can define your own logic for partitioning.
   - **Use case**: When you need complex or custom logic to determine which partition a message should go to.

4. **Sticky Partitioner**:
   - Kafka will try to keep messages with the same key assigned to the same partition, minimizing partition reassignments during consumer group rebalances.
   - **Use case**: When you need to minimize rebalancing overhead and maintain partition consistency across consumers.

Let me know if you need further clarification!