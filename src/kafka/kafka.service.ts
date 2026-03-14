import { Inject, Injectable, Module } from "@nestjs/common";
import { Producer } from "kafkajs";

@Injectable()
export class KafkaService {
    constructor(
        @Inject('KAFKA_PRODUCER')
        private readonly kafkaProducer: Producer
    ) {}

    async send(topic: string, payload: unknown) {
        this.kafkaProducer.send({
            topic,
            messages: [
                {
                    value: JSON.stringify(payload)
                }
            ]
        });
    }
}