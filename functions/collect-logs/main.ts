import { CloudWatchLogsClient, FilterLogEventsCommand, FilteredLogEvent, DescribeLogStreamsCommand } from '@aws-sdk/client-cloudwatch-logs';
import { APIGatewayProxyEvent, APIGatewayProxyResult, APIGatewayProxyHandler } from 'aws-lambda';

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

export async function getLogStreamLists(logGroupName: string): Promise<string[]> {
  const command = new DescribeLogStreamsCommand({
    logGroupName: logGroupName,
    orderBy: 'LastEventTime',
    descending: true
  });

  try {
    const response = await cloudwatchLogs.send(command);
    return (response.logStreams || []).map(stream => stream.logStreamName || '');
  } catch (error) {
    console.error('Error occurred while fetching log stream list:', error);
    throw error;
  }
}

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
    const body = JSON.parse(event.body || '{}');
    
    if (!body.logGroupName) {
      return {
        statusCode: 400,
        body: JSON.stringify({
          message: 'logGroupName is a required parameter'
        })
      };
    }

    const logStreamNames = await getLogStreamLists(body.logGroupName);
    
    if (logStreamNames.length === 0) {
      return {
        statusCode: 404,
        body: JSON.stringify({
          message: 'No log streams found in the specified log group'
        })
      };
    }

    const logs = await queryCloudwatchLogs({
      logGroupName: body.logGroupName,
      logStreamName: logStreamNames[0],
      startTime: Date.now() - (3 * 60 * 60 * 1000),
      endTime: Date.now(),
      filterPattern: ''
    });
    
    return {
      statusCode: 200,
      body: JSON.stringify({ 
        logs,
        logStreamName: logStreamNames[0]
      })
    };
  } catch (error) {
    if (error instanceof SyntaxError) {
      console.error('Invalid JSON format in request body:', error);
      return {
        statusCode: 400,
        body: JSON.stringify({
          message: 'Invalid JSON format in request body',
          error: error.message
        })
      };
    }
    
    console.error('Error occurred while querying logs:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: 'An error occurred while querying logs',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    };
  }
};
