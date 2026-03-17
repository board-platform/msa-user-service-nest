import { forwardRef, Module } from "@nestjs/common";
import { BoardCreatedEventConsumer } from "./board-created-event.consumer";
import { UserModule } from "src/user/user.module";

@Module({
  imports: [forwardRef(() => UserModule)],
    providers: [BoardCreatedEventConsumer],
    exports: [BoardCreatedEventConsumer],
  })
  export class ConsumerModule {}