import { Module } from "@nestjs/common";
import { kafkaProducerProvider } from "./producer.provider";
import { KafkaService } from "./kafka.service";
import { kafkaConsumerProvider } from "./consumer.provider";
import { KafkaConsumerRunner } from "./consumer.runner";

@Module({
    providers: [kafkaProducerProvider, kafkaConsumerProvider, KafkaConsumerRunner, KafkaService],
    exports: [KafkaService]
})

export class KafkaModule {}