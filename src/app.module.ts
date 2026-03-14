import { Module } from '@nestjs/common';
import { HealthCheckController } from './controller/health-check.controller';
import { UserController } from './controller/user.controller';
import { UserInternalController } from './controller/user.internal.controller';
import { ClientModule } from './client/client.module';
import { UserService } from './service/user.service';
import { ConfigModule } from '@nestjs/config';
import { PrismaService } from './prisma/prisma.service';
import { KafkaModule } from './kafka/kafka.module';

@Module({
  imports: [ClientModule, ConfigModule.forRoot({ isGlobal: true }), KafkaModule],
  controllers: [HealthCheckController, UserController, UserInternalController],
  providers: [UserService, PrismaService],
})
export class AppModule {}
