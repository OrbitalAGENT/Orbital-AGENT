// orbital-agent/src/messaging/kafka.go
package messaging

import (
    "context"
    "log"
    
    "github.com/segmentio/kafka-go"
)

type KafkaProducer struct {
    writer *kafka.Writer
}

func NewProducer(brokers []string, topic string) *KafkaProducer {
    return &KafkaProducer{
        writer: &kafka.Writer{
            Addr:     kafka.TCP(brokers...),
            Topic:    topic,
            Balancer: &kafka.Hash{},
        },
    }
}

func (p *KafkaProducer) SendMessage(ctx context.Context, key []byte, value []byte) error {
    return p.writer.WriteMessages(ctx,
        kafka.Message{
            Key:   key,
            Value: value,
        },
    )
}

type KafkaConsumer struct {
    reader *kafka.Reader
}

func NewConsumer(brokers []string, topic string, groupID string) *KafkaConsumer {
    return &KafkaConsumer{
        reader: kafka.NewReader(kafka.ReaderConfig{
            Brokers: brokers,
            Topic:   topic,
            GroupID: groupID,
        }),
    }
}

func (c *KafkaConsumer) Poll(ctx context.Context) (kafka.Message, error) {
    return c.reader.ReadMessage(ctx)
}
