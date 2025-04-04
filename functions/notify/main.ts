import { Handler } from "aws-lambda";
import { WebClient } from "@slack/web-api";

interface NotificationEvent {
    Records: any[];
}

interface NotificationResult {
    statusCode: number;
    body: string;
}

// Validate required environment variables
const SLACK_BOT_TOKEN = process.env.SLACK_BOT_TOKEN;
const SLACK_CHANNEL_ID = process.env.SLACK_CHANNEL_ID;

if (!SLACK_BOT_TOKEN || !SLACK_CHANNEL_ID) {
    throw new Error("Missing required environment variables: SLACK_BOT_TOKEN or SLACK_CHANNEL_ID");
}

const slack = new WebClient(SLACK_BOT_TOKEN);

export const handler: Handler<NotificationEvent, NotificationResult> = async (
    event,
    context,
) => {
    //
    // Sends a new slack message to the channel defined in the environment variable
    // The message is the body of the event
    // including the message "Anaylzation has been completed" and the expceted cause of the error.
    //
    try {
        console.log("Received event:", JSON.stringify(event, null, 2));

        const { Records } = event;
        const { body } = Records[0];
        const { message } = JSON.parse(body);

        // Slack에 메시지 전송
        await slack.chat.postMessage({
            channel: SLACK_CHANNEL_ID,
            text: message,
            blocks: [
                {
                    type: "section",
                    text: {
                        type: "mrkdwn",
                        text: message,
                    },
                },
            ],
        });

        return {
            statusCode: 200,
            body: JSON.stringify({
                message: "Notification processed successfully",
            }),
        };
    } catch (error) {
        console.error("Error:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                message: "Error processing notification",
                error: error.message,
            }),
        };
    }
};
