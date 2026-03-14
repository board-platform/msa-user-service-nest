import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class PointClient {
  constructor(private readonly httpService: HttpService) {}

  async addPoints(userId: bigint, amount: number): Promise<void> {
    const body = {
      userId,
      amount,
    };

    await firstValueFrom(
      this.httpService.post(
        `${process.env.POINT_SERVICE_URL}/internal/points/add`,
        body,
      ),
    );
  }
}