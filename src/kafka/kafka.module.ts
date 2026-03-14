import { Module } from "@nestjs/common";
import { kafkaProducerProvider } from "./kafka.provider";
import { KafkaService } from "./kafka.service";

@Module({
    providers: [kafkaProducerProvider, KafkaService],
    exports: [KafkaService]
})

export class KafkaModule {}