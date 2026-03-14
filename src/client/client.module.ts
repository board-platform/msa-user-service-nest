import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { PointClient } from './point.client';

@Module({
  imports: [HttpModule],
  providers: [PointClient],
  exports: [PointClient],
})
export class ClientModule {}