import { Controller, Post, Body, HttpCode } from '@nestjs/common';
import { LoginRequestDto } from 'src/dto/login-request.dto';
import { LoginResponseDto } from 'src/dto/login-response.dto';
import { SignUpRequestDto } from 'src/dto/sign-up-request.dto';
import { UserService } from 'src/service/user.service';

@Controller('api/users')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Post('sign-up')
  @HttpCode(204)
  async signUp(@Body() dto: SignUpRequestDto): Promise<void> {
    await this.userService.signUp(dto);
  }

  @Post('login')
  async login(@Body() dto: LoginRequestDto): Promise<LoginResponseDto> {
   return this.userService.login(dto);
  }
}
