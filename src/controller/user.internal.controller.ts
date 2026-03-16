import { Controller, Post, Body, HttpCode, Get, Param, Query } from '@nestjs/common';
import { AddActivityScoreRequestDto } from 'src/dto/add-activity-score-request.dto';
import { UserResponseDto } from 'src/dto/user-response.dto';
import { UserService } from 'src/service/user.service';

@Controller('internal/users')
export class UserInternalController {
  constructor(private readonly userService: UserService) {}

  @Get(':userId')
  async getUser(@Param('userId') userId: string): Promise<UserResponseDto> {
    return this.userService.getUser(+userId);
  }

  @Get()
  async getUsersByIds(@Query('ids') ids: string[]): Promise<UserResponseDto[]> {
    const parsedIds = ids.map((id) => +id);
    return this.userService.getUsersByIds(parsedIds);
  }

  @Post('activity-score/add')
  @HttpCode(204)
  async addActivityScore(@Body() dto: AddActivityScoreRequestDto): Promise<void> {
    await this.userService.addActivityScore(dto);
  }
}
