import boto3
import os
import json
import base64
import gzip

# --- Environment Variable Configuration (Set in Lambda Environment Settings) ---
ALARM_THRESHOLD_CPU = float(os.environ.get('ALARM_THRESHOLD_CPU', 80))  # CPU Utilization Alarm Threshold (%)
RECOVERY_SCRIPT_PATH = os.environ.get('RECOVERY_SCRIPT_PATH', '/opt/restart_service.sh') # Recovery Script Path
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN') # SNS Topic ARN for notifications
LOG_GROUP_NAME = os.environ.get('LOG_GROUP_NAME', 'ServerMetricsLogGroup') # CloudWatch Log Group Name (configurable)
METRIC_NAME_TO_MONITOR = os.environ.get('METRIC_NAME_TO_MONITOR', 'CPUUtilization') # Metric Name to Monitor (configurable)
NOTIFICATION_SUBJECT = os.environ.get('NOTIFICATION_SUBJECT', '[Warning] High Server Metric Alert') # Notification Subject
NOTIFICATION_MESSAGE_PREFIX = os.environ.get('NOTIFICATION_MESSAGE_PREFIX', 'Server Metric Alert: ') # Notification Message Prefix

# --- Initialize AWS Clients ---
cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')
logs_client = boto3.client('logs') # CloudWatch Logs client for more detailed log retrieval (optional, for future enhancement)

def lambda_handler(event, context):
    """
    Lambda function to process CloudWatch Logs events for server metric monitoring and auto-recovery.
    """
    print("Lambda function started")
    print("Event:", event)

    try:
        # --- 1. Decode and Decompress CloudWatch Logs Data ---
        compressed_payload = base64.b64decode(event['awslogs']['data'])
        uncompressed_payload = gzip.decompress(compressed_payload)
        log_data = json.loads(uncompressed_payload)

        log_events = log_data['logEvents']
        if not log_events:
            print("No log events received in this batch.")
            return { 'statusCode': 200, 'body': 'No log events to process' } # Exit gracefully if no logs

        print(f"Processing {len(log_events)} log events...")

        # --- 2. Extract Metric Value from Log Events ---
        metric_value = extract_metric_value_from_logs(log_events, METRIC_NAME_TO_MONITOR) # Pass Metric Name

        if metric_value is not None: # Check if metric value was successfully extracted
            print(f"Monitored Metric ({METRIC_NAME_TO_MONITOR}) Value: {metric_value}")

            # --- 3. Check Alarm Threshold and Trigger Actions ---
            if metric_value >= ALARM_THRESHOLD_CPU:
                print(f"**Alarm Triggered! Metric ({METRIC_NAME_TO_MONITOR}) exceeds threshold ({ALARM_THRESHOLD_CPU}%): {metric_value}%**")
                trigger_alarm_actions(metric_value)
            else:
                print(f"Metric ({METRIC_NAME_TO_MONITOR}) is within normal range.")
        else:
            print(f"Warning: Could not extract metric ({METRIC_NAME_TO_MONITOR}) value from log events.") # Log warning if extraction fails

    except KeyError as e:
        print(f"**KeyError processing event data:** {e}. Check event structure and environment variables.")
        # More specific error handling for common issues
        log_error(f"KeyError: {e}. Event data structure issue. Event: {event}")
        return { 'statusCode': 400, 'body': f'Error: KeyError - {e}. Check event data structure.' } # Return error status

    except json.JSONDecodeError as e:
        print(f"**JSONDecodeError:** {e}. Could not decode log data. Check CloudWatch Logs data format.")
        log_error(f"JSONDecodeError: {e}. Could not decode log data. Event: {event}")
        return { 'statusCode': 400, 'body': f'Error: JSONDecodeError - {e}. Check log data format.' } # Return error status

    except Exception as e:
        print(f"**Unexpected error:** {e}")
        log_error(f"Unexpected error: {e}. Event: {event}") # Log full exception details
        return { 'statusCode': 500, 'body': f'Error: Unexpected error - {e}. Check function logs.' } # Return error status

    print("Lambda function finished")
    return { 'statusCode': 200, 'body': 'CloudWatch Metric Processing Completed' }


def extract_metric_value_from_logs(log_events, metric_name):
    """
    Extracts the metric value from CloudWatch Logs events.
    - Assumes log events are in JSON format and contain the metric name as a key.
    - Adapt this function based on your actual log format.
    """
    for log_event in log_events:
        try:
            message_json = json.loads(log_event['message']) # Parse log message as JSON
            if metric_name in message_json: # Check if metric name exists in JSON
                metric_value = float(message_json[metric_name]) # Get metric value and convert to float
                return metric_value
            else:
                print(f"Warning: Metric name '{metric_name}' not found in log message: {log_event['message']}") # Log warning if metric name is missing
        except json.JSONDecodeError:
            print(f"Warning: Log message is not in JSON format: {log_event['message']}") # Log warning for non-JSON logs
        except ValueError:
            print(f"Warning: Metric value is not a valid number in log message: {log_event['message']}") # Log warning for invalid metric values
        except Exception as e:
            print(f"Warning: Error parsing log message: {log_event['message']} - Error: {e}") # General parsing error logging

    return None # Return None if metric value could not be extracted from any log event


def trigger_alarm_actions(metric_value):
    """
    Triggers alarm actions: send notification and execute recovery script.
    """
    send_notification(metric_value)
    execute_recovery_script()


def send_notification(metric_value):
    """
    Sends notification via SNS Topic.
    """
    if SNS_TOPIC_ARN:
        try:
            subject = NOTIFICATION_SUBJECT  # Use configurable notification subject
            message = f"{NOTIFICATION_MESSAGE_PREFIX}{METRIC_NAME_TO_MONITOR} exceeds threshold ({ALARM_THRESHOLD_CPU}%): {metric_value}%" # Use configurable prefix and metric name
            response = sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=subject,
                Message=message,
            )
            print("SNS notification sent successfully:", response)
            log_info(f"SNS notification sent. Subject: '{subject}', Message: '{message}'") # Log notification details
        except Exception as e:
            print("SNS notification sending failed:", e)
            log_error(f"SNS notification sending failed: {e}") # Log SNS sending errors
    else:
        print("SNS_TOPIC_ARN not configured. Skipping notification.")
        log_warning("SNS_TOPIC_ARN not configured, skipping notification.") # Log warning about missing SNS config


def execute_recovery_script():
    """
    Executes the recovery script (Bash script example).
    """
    if os.path.exists(RECOVERY_SCRIPT_PATH):
        try:
            print(f"Executing recovery script: {RECOVERY_SCRIPT_PATH}")
            log_info(f"Executing recovery script: {RECOVERY_SCRIPT_PATH}") # Log recovery script execution start
            import subprocess
            result = subprocess.run([RECOVERY_SCRIPT_PATH], capture_output=True, text=True, timeout=15) # Increased timeout to 15s
            print(f"Recovery script finished (Return Code: {result.returncode})")
            if result.returncode != 0:
                error_message = f"Recovery script error (stderr):\n{result.stderr}"
                print(error_message)
                log_error(error_message) # Log recovery script errors
            else:
                output_message = f"Recovery script output (stdout):\n{result.stdout}"
                print(output_message)
                log_info(output_message) # Log recovery script output

        except FileNotFoundError:
            error_message = f"Error: Recovery script not found at path: {RECOVERY_SCRIPT_PATH}"
            print(error_message)
            log_error(error_message) # Log file not found error
        except subprocess.TimeoutExpired:
            error_message = "Error: Recovery script execution timed out (15 seconds)"
            print(error_message)
            log_error(error_message) # Log timeout error
        except Exception as e:
            error_message = f"Error executing recovery script: {e}"
            print(error_message)
            log_error(error_message) # Log general recovery script execution errors
    else:
        warning_message = f"Warning: Recovery script path does not exist: {RECOVERY_SCRIPT_PATH}. Skipping recovery."
        print(warning_message)
        log_warning(warning_message) # Log warning about missing recovery script


# --- Logging Helper Functions (Using print for Lambda logs, can be enhanced with proper logging library) ---
def log_info(message):
    print(f"INFO: {message}")

def log_warning(message):
    print(f"WARNING: {message}")

def log_error(message):
    print(f"ERROR: {message}")