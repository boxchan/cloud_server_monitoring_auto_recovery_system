# cloud_server_monitoring_auto_recovery_system


# Cloud-Based Server Monitoring Auto-Recovery System

## Project Overview

This project is a **cloud-based server monitoring and auto-recovery system** developed to ensure stable server operation in the AWS cloud environment. Utilizing various AWS services and technologies such as AWS CloudWatch, AWS Lambda, Python, and Bash scripts, it aims to minimize system downtime and ensure service stability by real-time monitoring of key server metrics, automatically sending notifications upon anomaly detection, and performing recovery operations.

This project was conducted as a personal project to improve IT support/service desk operational efficiency and enhance cloud technology skills.

## Key Features and Characteristics

## Key Features and Characteristics

*   **Real-time Server Metric Monitoring:** Real-time collection and monitoring of key server metrics such as CPU utilization, memory utilization, and network traffic using AWS CloudWatch.
*   **User-Definable Warning Thresholds:** Warning thresholds can be defined by users for each metric, enabling flexible warning settings tailored to specific situations (e.g., warning when CPU utilization exceeds 80%). **Threshold for CPU utilization is configurable via environment variable.**
*   **Configurable Metric and Log Group:** **Now supports monitoring of different metrics and log groups.** The metric to monitor (e.g., CPUUtilization, MemoryUtilization) and the CloudWatch Log Group name can be easily configured using environment variables, making the system more versatile.
*   **Automatic Notification Function:** Upon exceeding warning thresholds, immediate notifications are sent via AWS SNS (Simple Notification Service) to email or Slack, enabling administrators to promptly recognize and respond to situations. **Notification subject and message prefix are also configurable.**
*   **Automatic Recovery Function (Example):** In case of specific events (e.g., sustained CPU overload), pre-defined recovery scripts (Bash) are automatically executed to automatically recover the system (e.g., service restart, process termination - recovery scripts are user-definable).
*   **Robust Error Handling and Logging:** **Improved error handling to gracefully manage issues like invalid log data or missing configurations.** Enhanced logging provides more detailed information for debugging and monitoring the system's operation.
*   **JSON Log Parsing:** **The system is designed to parse JSON-formatted log messages,** allowing for structured metric extraction.
*   **Scalability and Flexibility:** Built on the AWS cloud, it is flexibly scalable according to server environment changes, and the system can be enhanced by adding various monitoring metrics and recovery actions.
*   **Infrastructure as Code (IaC) (Planned):** Aiming for efficient system management by managing infrastructure as code using AWS CloudFormation or Terraform and establishing automated deployment (CI/CD). (Planned for future addition)

## Technology Stack

* **AWS Cloud Services:**
    * **AWS CloudWatch:** Server metric monitoring, alarm configuration
    * **AWS Lambda:** Metric data processing, notification sending, recovery script execution (Python runtime)
    * **AWS SNS (Simple Notification Service):** Notification sending (email, Slack, etc.)
    * **(Optional) AWS CloudFormation / Terraform:** Infrastructure automation and management (IaC)
* **Programming Languages & Scripting:**
    * **Python:** AWS Lambda function development (CloudWatch metric processing, logic implementation)
    * **Bash:** Server recovery script writing (example: service restart)

## Project Structure

cloud-server-monitoring-auto-recovery-system/
├── lambda_functions/
│ └── metric_processor.py # AWS Lambda function (Python) - CloudWatch metric processing and alarm/recovery trigger
├── scripts/
│ └── restart_service.sh # Bash script - Service restart (example recovery script)
└── README.md # Project description file (this file)


## Installation and Setup (Brief Guide)

This project should be configured in the AWS cloud environment. Basic setup steps are as follows:

1. **AWS Account and IAM Configuration:** Prepare an AWS account and create an IAM role with access permissions to necessary AWS services such as Lambda function execution role, CloudWatch, and SNS.
2. **AWS Lambda Function Deployment:** Deploy the `lambda_functions/metric_processor.py` file to AWS Lambda. Consider the following when configuring the Lambda function:
    * **Runtime:** Python 3.x
    * **Handler:** `metric_processor.lambda_handler`
    * **Environment Variables:** `ALARM_THRESHOLD_CPU`, `RECOVERY_SCRIPT_PATH`, `SNS_TOPIC_ARN`, etc. (add as needed)
    * **Memory and Timeout:** Set appropriate values (considering the server environment to be monitored and recovery script execution time)
    * **VPC Settings (if necessary):** If the server to be monitored is within a VPC, place the Lambda function in the same VPC.
    * **Layers (Optional):** Deploy the Bash recovery script (`restart_service.sh`) or necessary libraries as Lambda Layers (configured to access the `/opt/` path).
3. **AWS CloudWatch Configuration:**
    * **CloudWatch Logs Configuration:** Configure the server to be monitored to send metric data (e.g., CPU utilization logs) to CloudWatch Logs. (CloudWatch Agent installation and configuration required)
    * **CloudWatch Alarm Configuration:** Create a CloudWatch Alarm and set warning conditions (e.g., if CPU utilization metric exceeds the threshold in a specific log group). Set the Lambda function deployed above to be triggered as an alarm action.
4. **AWS SNS Topic Configuration (when using notification feature):** Create an AWS SNS topic and configure subscription settings for email addresses or Slack Webhook URLs to receive notifications. Set the SNS topic ARN in the Lambda function environment variables.
5. **Recovery Script Configuration (when using auto-recovery feature):** Include the `scripts/restart_service.sh` (example) file in the Lambda Layer or `/opt/` path, and set the path in the Lambda function environment variable `RECOVERY_SCRIPT_PATH`. The recovery script should be modified according to the actual server environment and recovery operations.

**Caution:** The above setup guide is a basic example, and the setup method may vary depending on the actual environment. Please refer to the AWS official documentation for settings appropriate for your environment.

## How to Use

Once the system is configured correctly, it operates as follows:

1. **Server Metric Data Collection:** The CloudWatch Agent collects metric data (e.g., CPU utilization) from the server to be monitored and sends it to CloudWatch Logs.
2. **CloudWatch Logs Monitoring and Alarm Trigger:** CloudWatch Logs monitors the collected log data, and if the configured CloudWatch Alarm condition (e.g., CPU utilization threshold exceeded) is met, it triggers an alarm.
3. **Lambda Function Execution:** The Lambda function (`metric_processor.py`) is automatically executed by the CloudWatch Alarm.
4. **Metric Data Processing and Notification/Recovery:** The Lambda function receives CloudWatch Logs event data, extracts the CPU utilization metric value, and checks if the threshold is exceeded.
    * **If Alert Occurs:** Sends notifications via SNS Topic and executes the configured recovery script (`restart_service.sh`) to attempt automatic recovery.
    * **Normal State:** Continues monitoring without any action.
5. **Notification Reception:** Administrators receive server CPU utilization warning notifications via SNS to email or Slack, etc.
6. **Automatic Recovery (if successful):** If the recovery script executes successfully, the server issue is automatically resolved, minimizing system downtime.

## Project Results and Achievements

Through this project, the following benefits can be expected:

* **Reduced System Downtime:** By promptly responding to server failures through automatic monitoring and auto-recovery functions, system downtime can be minimized and service availability improved.
* **Improved Operational Efficiency:** Reduces the time and effort required to manually monitor server status and respond to failures, increasing operational efficiency.
* **Proactive Problem Detection and Response:** Real-time metric monitoring enables proactive detection and prevention of potential issues, establishing a stable system operation environment.
* **Enhanced IT Support/Service Desk Capabilities:** Experience in building cloud-based automation systems enhances IT support and service desk work capabilities and improves expertise.

## Future Improvements (To-Do)

* **Addition of More Diverse Metric Monitoring:** Expand to monitor various server metrics in addition to CPU utilization, such as memory utilization, disk utilization, and network traffic.
* **More Sophisticated Warning Conditions and Recovery Actions:** Improve warning accuracy and reduce false positives by applying advanced analysis techniques such as trend analysis and anomaly detection, in addition to simple threshold-based warnings. Diversify recovery actions (e.g., scale-out, Auto Scaling integration, etc.).
* **Addition of Log Analysis and Dashboard Features:** Build a dashboard to visualize and analyze collected metric data (e.g., Grafana integration, AWS QuickSight utilization) and enhance log analysis capabilities (e.g., ELK Stack integration).
* **IaC (Infrastructure as Code) Application:** Automate infrastructure deployment and management (CI/CD pipeline establishment) using AWS CloudFormation or Terraform, etc.
* **Testing and Stability Enhancement:** Add various scenario-based test cases and enhance system stability and fault recovery capabilities.


## Contact

For project-related inquiries, please contact [coolsu92@gmail.com](mailto:coolsu92@gmail.com).

(https://github.com/boxchan/cloud_server_monitoring_auto_recovery_system)

