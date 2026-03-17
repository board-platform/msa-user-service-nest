import { Module } from "@nestjs/common";
import { kafkaProducerProvider } from "./producer.provider";
import { KafkaService } from "./kafka.service";
import { kafkaConsumerProvider } from "./consumer.provider";
import { KafkaConsumerRunner } from "./consumer.runner";
import { ConsumerModule } from "src/consumer/consumer.module";

@Module({
    imports: [ConsumerModule],
    providers: [kafkaProducerProvider, kafkaConsumerProvider, KafkaConsumerRunner, KafkaService],
    exports: [KafkaService]
})

export class KafkaModule {}