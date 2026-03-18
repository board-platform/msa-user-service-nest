import { Inject, Injectable, OnModuleInit } from "@nestjs/common";
import { BoardCreatedEventConsumer } from "src/consumer/board-created-event.consumer";

@Injectable()
export class KafkaConsumerRunner implements OnModuleInit {
  constructor(
    @Inject('KAFKA_CONSUMER')
    private readonly consumer,
    private readonly boardCreatedEventConsumer: BoardCreatedEventConsumer,
  ) {}

  async onModuleInit() {
    await this.consumer.subscribe({
      topic: 'board.created',
      fromBeginning: false,
    });

    await this.consumer.run({
      eachMessage: async ({ message, topic }) => {
        const value = message.value?.toString();
        if (!value) return;

        if (topic === 'board.created') {
          await this.boardCreatedEventConsumer.consume(value);
        }
      },
    });
  }
}