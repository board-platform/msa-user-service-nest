import { forwardRef, Module } from "@nestjs/common";
import { UserController } from "./user.controller";
import { UserInternalController } from "./user.internal.controller";
import { UserService } from "./user.service";
import { KafkaModule } from "src/kafka/kafka.module";
import { PrismaModule } from "src/prisma/prisma.module";

@Module({
    imports: [forwardRef(() => KafkaModule), PrismaModule],
    controllers: [UserController, UserInternalController],
    providers: [UserService],
    exports: [UserService]
})

export class UserModule {}