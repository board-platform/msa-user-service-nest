import { Injectable, NotFoundException, UnauthorizedException } from "@nestjs/common";
import { AddActivityScoreRequestDto } from "src/dto/add-activity-score-request.dto";
import { LoginRequestDto } from "src/dto/login-request.dto";
import { LoginResponseDto } from "src/dto/login-response.dto";
import { SignUpRequestDto } from "src/dto/sign-up-request.dto";
import { UserResponseDto } from "src/dto/user-response.dto";
import { UserSignedUpEvent } from "src/event/user-signed-up.event";
import { KafkaService } from "src/kafka/kafka.service";
import { PrismaService } from "src/prisma/prisma.service";
import * as jwt from "jsonwebtoken";

@Injectable()
export class UserService {
    constructor(
        private readonly prisma: PrismaService,
        private readonly kafkaService: KafkaService,
    ) {}
    
    async signUp(dto: SignUpRequestDto): Promise<void> {
        const savedUser = await this.prisma.user.create({ 
            data: {
                email: dto.email,
                name: dto.name,
                password: dto.password
            }
        });

        const event: UserSignedUpEvent = new UserSignedUpEvent();
        event.userId = savedUser.userId;
        event.name = savedUser.name;

        await this.kafkaService.send('user.signed-up', event);
    }

    async getUser(userId: number): Promise<UserResponseDto> {
        const user = await this.prisma.user.findUnique({ where: { userId } });

        if (!user) {
            throw new NotFoundException('사용자를 찾을 수 없습니다.');
        }

        return {
            userId: user.userId,
            email: user.email,
            name: user.name
        }
    }

    async getUsersByIds(ids: number[]): Promise<UserResponseDto[]> {
        const users = await this.prisma.user.findMany({ where: { userId: { in: ids} } });

        return users.map((user) => ({
            userId: user.userId,
            email: user.email,
            name: user.name,
        }));
    }

    async addActivityScore(dto: AddActivityScoreRequestDto): Promise<void> {
        try {
            await this.prisma.user.update({
                where: {
                    userId: dto.userId,
                },
                data: {
                    activityScore: {
                        increment: dto.score
                    }
                }
            });
        } catch (error) {
            throw new NotFoundException('사용자를 찾을 수 없습니다.');
        }
    }

    async login(dto: LoginRequestDto): Promise<LoginResponseDto> {
        const user = await this.prisma.user.findUnique({
            where: {
                email: dto.email
            }
        });

        if (!user) {
            throw new NotFoundException('사용자를 찾을 수 없습니다.');
        }

        if (user.password !== dto.password) {
            throw new UnauthorizedException('비밀번호가 일치하지 않습니다,');
        }

        const token = jwt.sign(
            { sub: user.userId.toString() },
            process.env.JWT_SECRET as string
        );

        return {
            token
        };
    }

    async brokenMethod(dto: any): Promise<any> {
        // ❌ null 가능성
        const user = await this.prisma.user.findUnique({
            where: { email: dto.email }
        });
    
        // ❌ null 체크 없음
        if (user.password === dto.password) {
    
            // ❌ await 없음 (DB 업데이트 안 될 수도 있음)
            this.prisma.user.update({
                where: { userId: user.userId },
                data: { name: dto.name }
            });
    
            // ❌ Kafka await 없음
            this.kafkaService.send('user.updated', {
                userId: user.userId
            });
    
            // ❌ 하드코딩 secret + 타입 문제
            const token = jwt.sign(
                { sub: user.userId }, // number 그대로
                "hardcoded-secret"
            );
    
            // ❌ 비밀번호 그대로 반환 (보안 문제)
            return {
                token,
                password: user.password
            };
        }
    
        // ❌ 잘못된 예외 처리
        throw new Error("로그인 실패"); // Nest 예외 안씀
    }
}