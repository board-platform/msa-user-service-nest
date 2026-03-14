import { Kafka } from "kafkajs"
import { ConfigService } from "@nestjs/config"
import { Provider } from "@nestjs/common";

export const kafkaProducerProvider: Provider = {
    provide: 'KAFKA_PRODUCER',
    inject: [ConfigService],
    useFactory: async (configService: ConfigService) => {
        const kafka = new Kafka({
            clientId: 'user-service',
            brokers: configService.get<string>('KAFKA_BOOTSTRAP_SERVERS')?.split(',') ?? ['localhost:9092']
        });

        const producer = kafka.producer();
        await producer.connect();

        return producer;
    }
}