import { Injectable } from "@nestjs/common";
import { AddActivityScoreRequestDto } from "src/dto/add-activity-score-request.dto";
import { BoardCreatedEvent } from "src/event/board-created.event";
import { UserService } from "src/user/user.service";

@Injectable()
export class BoardCreatedEventConsumer {
    constructor(private readonly userService: UserService) {}

    async consume(message: string): Promise<void> {
        const event: BoardCreatedEvent = JSON.parse(message);

        const dto = new AddActivityScoreRequestDto();
        dto.userId = event.userId;
        dto.score = 10;

        await this.userService.addActivityScore(dto);
        console.log('활동 점수 적립 완료');
    }
}