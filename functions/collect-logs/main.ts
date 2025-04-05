import { CloudWatchLogsClient, FilterLogEventsCommand, FilteredLogEvent } from '@aws-sdk/client-cloudwatch-logs';
import { APIGatewayProxyEvent, APIGatewayProxyResult, APIGatewayProxyHandler } from 'aws-lambda';

interface LogQueryParams {
  logGroupName: string;
  logStreamName: string;
  startTime: number;
  endTime: number;
  filterPattern?: string;
}

interface LogEvent {
  timestamp?: number;
  message?: string;
  logStreamName?: string;
}

interface QueryCloudwatchLogsParams {
  logGroupName: string;
  logStreamName: string;
  startTime: number;
  endTime: number;
  filterPattern: string;
}

const cloudwatchLogs = new CloudWatchLogsClient({ region: process.env.AWS_REGION || 'us-east-1' });

export async function queryCloudwatchLogs({
  logGroupName,
  logStreamName,
  startTime,
  endTime,
  filterPattern
}: QueryCloudwatchLogsParams): Promise<LogEvent[]> {
  const query = new FilterLogEventsCommand({
    logGroupName,
    logStreamNames: [logStreamName],
    startTime,
    endTime,
    filterPattern
  });

  const queryResult = await cloudwatchLogs.send(query);

  return queryResult.events?.map((event: FilteredLogEvent) => ({
    timestamp: event.timestamp,
    message: event.message,
    logStreamName: event.logStreamName
  })) || [];
}

export const handler: APIGatewayProxyHandler = async function(
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> {
  try {
    const body = event.body ? JSON.parse(event.body) : {};
    const { logGroupName, logStreamName, startTime, endTime, filterPattern }: LogQueryParams = body;
    
    if (!logGroupName || !logStreamName || !startTime || !endTime) {
      return {
        statusCode: 400,
        body: JSON.stringify({
          message: '필수 파라미터가 누락되었습니다: logGroupName, logStreamName, startTime, endTime'
        })
      };
    }

    const logs = await queryCloudwatchLogs({
      logGroupName,
      logStreamName,
      startTime,
      endTime,
      filterPattern: filterPattern || ''
    });

    return {
      statusCode: 200,
      body: JSON.stringify({
        logs
      })
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: '로그 쿼리 중 오류가 발생했습니다',
        error: error instanceof Error ? error.message : '알 수 없는 오류'
      })
    };
  }
};
