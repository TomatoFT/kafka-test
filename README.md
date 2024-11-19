# KAFKA PARTITION ASSIGNORS 

### 1. **Range Assignor Strategy**

- **Description**: The `range` assignor strategy tries to allocate contiguous sets of partitions to each consumer in the group. Each consumer gets a contiguous block of partitions.
- **Best Use Case**: When you need to maintain an order or sequence of partitioned messages. This can be useful in scenarios where consumer order must be preserved (e.g., processing in sequence).
- **Example**: If you have a topic with 6 partitions and 3 consumers:
  - Consumer 1: Gets partitions 0, 1, 2
  - Consumer 2: Gets partitions 3, 4, 5
  - Consumer 3: Gets partitions 6, 7, 8

- **Pros**:
  - **Predictable allocation**: It maintains a consistent order across partitions.
  - **Even distribution**: Ensures a balanced distribution across consumers.
  
- **Cons**:
  - **Not efficient** when partitions are added or removed.

- **Example Configuration**:
  ```python
  from confluent_kafka import Consumer, KafkaException

  conf = {
      'bootstrap.servers': 'localhost:9092',  # Kafka broker
      'group.id': 'range-consumer-group',  # Consumer group
      'auto.offset.reset': 'earliest',  # Start reading from the beginning
      'partition.assignment.strategy': 'range'  # Partition assignor strategy
  }

  consumer = Consumer(conf)

  def consume_messages():
      consumer.subscribe(['example-topic'])

      try:
          while True:
              msg = consumer.poll(timeout=1.0)
              
              if msg is None:
                  continue
              if msg.error():
                  if msg.error().code() == KafkaError._PARTITION_EOF:
                      print(f'End of partition reached: {msg.topic()} [{msg.partition}] at offset {msg.offset()}')
                  else:
                      raise KafkaException(msg.error())
              else:
                  print(f'Received message: {msg.value().decode("utf-8")}')
      finally:
          consumer.close()

  consume_messages()
  ```

### 2. **Round-robin Assignor Strategy**

- **Description**: The `roundrobin` assignor strategy allocates partitions to consumers in a cyclic manner, ensuring each consumer in the group gets a fair share of partitions. This method doesn’t maintain order across partitions.
- **Best Use Case**: Suitable for topics with a larger number of partitions or where a load-balanced, dynamic distribution of partitions is required.
- **Example**: If you have 6 partitions and 3 consumers:
  - Consumer 1: Gets partitions 0, 3
  - Consumer 2: Gets partitions 1, 4
  - Consumer 3: Gets partitions 2, 5
  - If a new consumer joins, partitions are evenly distributed again.

- **Pros**:
  - **Evenly distributed partitions**: No consumer ends up with significantly more or fewer partitions.
  - **Scalable**: Works well for large numbers of consumers and partitions.

- **Cons**:
  - **No consideration of order**: May not respect message ordering within partitions.
  - **Frequent rebalancing**: New partitions or consumers joining or leaving may lead to frequent reassignments.

- **Example Configuration**:
  ```python
  from confluent_kafka import Consumer, KafkaException

  conf = {
      'bootstrap.servers': 'localhost:9092',
      'group.id': 'roundrobin-consumer-group',
      'auto.offset.reset': 'earliest',
      'partition.assignment.strategy': 'roundrobin'
  }

  consumer = Consumer(conf)

  def consume_messages():
      consumer.subscribe(['example-topic'])

      try:
          while True:
              msg = consumer.poll(timeout=1.0)

              if msg is None:
                  continue
              if msg.error():
                  if msg.error().code() == KafkaError._PARTITION_EOF:
                      print(f'End of partition reached: {msg.topic()} [{msg.partition}] at offset {msg.offset()}')
                  else:
                      raise KafkaException(msg.error())
              else:
                  print(f'Received message: {msg.value().decode("utf-8")}')
      finally:
          consumer.close()

  consume_messages()
  ```

### 3. **Sticky Assignor Strategy**

- **Description**: The `sticky` assignor tries to keep as many partitions assigned to consumers as they were previously. It minimizes partition rebalancing overhead when consumers join or leave the group. 
- **Best Use Case**: Useful when you want to preserve the assignment of partitions as much as possible, particularly when stability is important or the number of partitions is small.
- **Example**: If you have 6 partitions and 3 consumers:
  - Consumer 1: Gets partitions 0, 1, 2
  - Consumer 2: Gets partitions 3, 4
  - Consumer 3: Gets partition 5
  - If a consumer joins or leaves, the assignor tries to preserve existing assignments as much as possible.

- **Pros**:
  - **Minimizes partition rebalancing**: Reduces the number of changes when consumers join or leave.
  - **Stable distribution**: Keeps the distribution relatively stable even when the number of partitions or consumers fluctuates.

- **Cons**:
  - **Can result in uneven load distribution**: May not distribute partitions as evenly as `roundrobin`.
  - **Rebalancing still occurs**: Only maintains stability where existing assignments don’t have to be changed.

- **Example Configuration**:
  ```python
  from confluent_kafka import Consumer, KafkaException

  conf = {
      'bootstrap.servers': 'localhost:9092',
      'group.id': 'sticky-consumer-group',
      'auto.offset.reset': 'earliest',
      'partition.assignment.strategy': 'sticky'
  }

  consumer = Consumer(conf)

  def consume_messages():
      consumer.subscribe(['example-topic'])

      try:
          while True:
              msg = consumer.poll(timeout=1.0)

              if msg is None:
                  continue
              if msg.error():
                  if msg.error().code() == KafkaError._PARTITION_EOF:
                      print(f'End of partition reached: {msg.topic()} [{msg.partition}] at offset {msg.offset()}')
                  else:
                      raise KafkaException(msg.error())
              else:
                  print(f'Received message: {msg.value().decode("utf-8")}')
      finally:
          consumer.close()

  consume_messages()
  ```

---

### Explanation for the "Dumb":

- **Range**:
  - Think of this as a sequence or a block of contiguous numbers. Each consumer gets assigned a group of partitions one after another. 
  - If partitions are reordered or removed, consumers may need to reassign the blocks of numbers.
  - Example: If you have `[0, 1, 2]` as partitions and three consumers `[A, B, C]`, they might be assigned `[0, 1, 2]` (A), `[3, 4, 5]` (B), `[6, 7]` (C).

- **Round-robin**:
  - This is like distributing tasks evenly among a group of people. Each consumer gets assigned a new partition sequentially. 
  - No special order or grouping, just a cycle through the partitions.
  - Example: If you have `[0, 1, 2, 3, 4, 5]` as partitions and three consumers `[A, B, C]`, they would get `[0, 3]` (A), `[1, 4]` (B), `[2, 5]` (C) with each new consumer addition leading to an even distribution.

- **Sticky**:
  - This strategy tries to keep the existing assignments as much as possible and only reassign partitions when absolutely necessary (e.g., consumers join or leave). 
  - It tries to maintain an already "sticky" state for consumers without frequent rebalancing.
  - Example: If partitions `[0, 1, 2]` belong to `[A, B, C]` and you add or remove a consumer, the `sticky` strategy tries to keep these groups relatively stable.

---

### Summary

- **`range`**: Useful for preserving an ordering, but can lead to more frequent rebalancing when new consumers join or leave.
- **`roundrobin`**: Best for even distribution of partitions across consumers, but doesn’t respect partition order.
- **`sticky`**: Minimizes the number of rebalancing operations, which can be useful for stability but might result in uneven partition distribution.

Let me know if you need further clarification or additional examples!