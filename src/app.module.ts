import { Module } from '@nestjs/common';
import { HealthCheckController } from './health-check/health-check.controller';
import { UserController } from './user/user.controller';
import { UserInternalController } from './user/user.internal.controller';
import { ClientModule } from './client/client.module';
import { UserService } from './user/user.service';
import { ConfigModule } from '@nestjs/config';
import { PrismaService } from './prisma/prisma.service';
import { KafkaModule } from './kafka/kafka.module';
import { UserModule } from './user/user.module';
import { HealthCheckModule } from './health-check/health-check.module';

@Module({
  imports: [ClientModule, ConfigModule.forRoot({ isGlobal: true }), KafkaModule, HealthCheckModule, UserModule],
})
export class AppModule {}
