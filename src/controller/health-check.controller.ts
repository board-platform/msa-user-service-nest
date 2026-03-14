import { Controller, Get } from '@nestjs/common';

@Controller('actuator')
export class HealthCheckController {

  @Get('health')
  health() {
    return {
      status: 'ok'
    };
  }

}
