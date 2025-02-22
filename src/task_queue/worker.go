// orbital-agent/src/task_queue/worker.go
package taskqueue

import (
    "context"
    "log"
    "time"
    
    "github.com/redis/go-redis/v9"
)

type TaskWorker struct {
    redisClient *redis.Client
    queueName   string
}

func NewWorker(redisAddr string, queue string) *TaskWorker {
    return &TaskWorker{
        redisClient: redis.NewClient(&redis.Options{
            Addr:     redisAddr,
            Password: "",
            DB:       0,
        }),
        queueName: queue,
    }
}

func (w *TaskWorker) Start(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return
        default:
            task, err := w.redisClient.BLPop(ctx, 30*time.Second, w.queueName).Result()
            if err != nil {
                log.Printf("Error fetching task: %v", err)
                continue
            }
            
            // Process task
            log.Printf("Processing task: %s", task[1])
        }
    }
}
