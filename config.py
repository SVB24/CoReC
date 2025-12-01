"""
Production Configuration and Deployment Guide
For deploying the Career Planning Agent in production environments
"""

import os
import logging
from typing import Optional
from enum import Enum


class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Config:
    """Base configuration class"""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    # API Rate Limiting
    MAX_REQUESTS_PER_MINUTE = 60  # Free tier limit
    REQUEST_TIMEOUT_SECONDS = 30
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 2
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'career_planning.log'
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 5
    
    # Output Configuration
    OUTPUT_DIR = 'outputs'
    METRICS_DIR = 'metrics'
    REPORTS_DIR = 'reports'
    
    # Performance Configuration
    PARALLEL_AGENTS_MAX_WORKERS = 3
    BATCH_SIZE = 10  # Students per batch
    
    # Error Handling
    CONTINUE_ON_AGENT_FAILURE = False
    COLLECT_ERROR_METRICS = True


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    MAX_REQUESTS_PER_MINUTE = 60
    CONTINUE_ON_AGENT_FAILURE = True


class StagingConfig(Config):
    """Staging environment configuration"""
    DEBUG = False
    TESTING = True
    LOG_LEVEL = 'INFO'
    MAX_REQUESTS_PER_MINUTE = 60
    PARALLEL_AGENTS_MAX_WORKERS = 3


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    MAX_REQUESTS_PER_MINUTE = 600  # Paid tier limit
    PARALLEL_AGENTS_MAX_WORKERS = 5
    MAX_RETRIES = 5


def get_config(environment: Optional[str] = None) -> Config:
    """Get configuration for specified environment"""
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'staging': StagingConfig,
        'production': ProductionConfig
    }
    
    config_class = configs.get(environment.lower(), DevelopmentConfig)
    return config_class()


def setup_logging(config: Config) -> logging.Logger:
    """Setup logging with configuration"""
    import logging.handlers
    
    # Create logger
    logger = logging.getLogger('CareerPlanningApp')
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.MAX_LOG_FILE_SIZE,
        backupCount=config.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def validate_configuration(config: Config) -> bool:
    """Validate configuration is complete and valid"""
    logger = logging.getLogger('ConfigValidator')
    
    issues = []
    
    # Check API key
    if not config.GEMINI_API_KEY:
        issues.append("GEMINI_API_KEY not set")
    
    # Check model
    if not config.GEMINI_MODEL:
        issues.append("GEMINI_MODEL not set")
    
    # Check directories can be created
    for dir_name in [config.OUTPUT_DIR, config.METRICS_DIR, config.REPORTS_DIR]:
        try:
            os.makedirs(dir_name, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create directory {dir_name}: {str(e)}")
    
    # Check timeout value
    if config.REQUEST_TIMEOUT_SECONDS < 10:
        issues.append("REQUEST_TIMEOUT_SECONDS too low (min 10)")
    
    # Check max workers
    if config.PARALLEL_AGENTS_MAX_WORKERS < 1:
        issues.append("PARALLEL_AGENTS_MAX_WORKERS must be >= 1")
    
    if issues:
        for issue in issues:
            logger.error(f"Configuration issue: {issue}")
        return False
    
    logger.info("Configuration validation passed")
    return True


def setup_environment() -> Config:
    """Complete environment setup"""
    # Get configuration
    config = get_config()
    
    # Setup logging
    logger = setup_logging(config)
    logger.info(f"Initialized in {os.getenv('ENVIRONMENT', 'development')} environment")
    
    # Validate configuration
    if not validate_configuration(config):
        raise RuntimeError("Configuration validation failed")
    
    # Create required directories
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.METRICS_DIR, exist_ok=True)
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    
    logger.info("Environment setup completed successfully")
    
    return config


# Deployment Checklist
DEPLOYMENT_CHECKLIST = """
╔════════════════════════════════════════════════════════════════╗
║            PRODUCTION DEPLOYMENT CHECKLIST                      ║
╚════════════════════════════════════════════════════════════════╝

PRE-DEPLOYMENT
  □ Run full test suite: python test_suite.py
  □ Review all logs for errors
  □ Test with sample student data
  □ Verify metrics collection working
  □ Check HTML dashboard generation
  □ Review error handling
  □ Validate API key setup
  □ Ensure rate limiting configured

DEPLOYMENT
  □ Set ENVIRONMENT=production
  □ Set GEMINI_API_KEY (production key)
  □ Verify Python 3.8+ installed
  □ Install dependencies: pip install -r requirements.txt
  □ Run setup script: ./setup.sh
  □ Verify database/storage access
  □ Setup log rotation and monitoring
  □ Configure backup strategy

POST-DEPLOYMENT
  □ Monitor application logs
  □ Track error rates and performance
  □ Verify API rate limiting
  □ Test user workflows end-to-end
  □ Check output file generation
  □ Monitor resource usage
  □ Setup alerts for failures
  □ Document any issues/resolutions

MONITORING
  □ Setup log aggregation
  □ Configure performance alerts
  □ Monitor API quota usage
  □ Track execution times
  □ Monitor error rates
  □ Review metrics regularly
  □ Setup automated backups

SECURITY
  □ Use environment variables for secrets
  □ Rotate API keys regularly
  □ Audit access logs
  □ Encrypt sensitive data
  □ Implement rate limiting
  □ Add request validation
  □ Monitor for abuse
  □ Keep dependencies updated
"""

# API Rate Limiting Strategy
RATE_LIMITING_STRATEGY = """
╔════════════════════════════════════════════════════════════════╗
║            API RATE LIMITING STRATEGY                           ║
╚════════════════════════════════════════════════════════════════╝

Free Tier (60 requests/minute):
  - Process 1 student per minute
  - Use batch processing: 10 students per 10 minutes
  - Add delays between requests: time.sleep(1)
  - Cache recommendations when possible

Paid Tier (Higher limits):
  - Increase max_workers for parallel agents
  - Batch process multiple students
  - Reduce delays between requests

Implementation:
  import time
  import requests
  
  def rate_limited_request(delay: float = 1.0):
      def decorator(func):
          def wrapper(*args, **kwargs):
              result = func(*args, **kwargs)
              time.sleep(delay)
              return result
          return wrapper
      return decorator
"""

# Scaling Recommendations
SCALING_RECOMMENDATIONS = """
╔════════════════════════════════════════════════════════════════╗
║            SCALING RECOMMENDATIONS                              ║
╚════════════════════════════════════════════════════════════════╝

Single Machine:
  - Process: 1-10 students per hour
  - Memory: 256 MB minimum
  - Storage: 1 GB for logs/reports
  - Bottleneck: API rate limits

Horizontal Scaling:
  1. Use message queue (Redis/RabbitMQ)
  2. Multiple worker processes
  3. Distribute student processing
  4. Aggregate results
  5. Cost: Linear with API usage

Docker Deployment:
  FROM python:3.9-slim
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt
  CMD ["python", "main.py"]

Kubernetes:
  - Horizontal Pod Autoscaling
  - Shared metrics collection
  - Load balancing
  - Persistent storage for reports

Cloud Platforms:
  - AWS Lambda: Serverless execution
  - Google Cloud Run: Container-based
  - Azure Functions: Event-driven
  - Cost: Pay per execution
"""

# Monitoring and Alerting
MONITORING_SETUP = """
╔════════════════════════════════════════════════════════════════╗
║            MONITORING & ALERTING SETUP                          ║
╚════════════════════════════════════════════════════════════════╝

Metrics to Track:
  1. API requests per minute (rate limiting)
  2. Average response time per agent
  3. Error rate per agent type
  4. Parallel execution efficiency
  5. Report generation success rate
  6. Total processing time per student
  7. Storage usage (logs + reports)
  8. API quota usage

Alert Thresholds:
  - Error rate > 5%: Critical
  - API response time > 60s: Warning
  - Storage > 80% capacity: Warning
  - Failed workflows: Immediate alert

Log Aggregation:
  - Centralized logging service
  - Real-time log streaming
  - Historical log analysis
  - Searchable metadata

Dashboard Metrics:
  - Current request queue
  - Processing success rate
  - Average execution time
  - Resource utilization
  - Error trends
"""

def print_deployment_checklist():
    """Print deployment checklist"""
    print(DEPLOYMENT_CHECKLIST)

def print_rate_limiting_strategy():
    """Print rate limiting strategy"""
    print(RATE_LIMITING_STRATEGY)

def print_scaling_recommendations():
    """Print scaling recommendations"""
    print(SCALING_RECOMMENDATIONS)

def print_monitoring_setup():
    """Print monitoring setup"""
    print(MONITORING_SETUP)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "checklist":
            print_deployment_checklist()
        elif command == "rate-limiting":
            print_rate_limiting_strategy()
        elif command == "scaling":
            print_scaling_recommendations()
        elif command == "monitoring":
            print_monitoring_setup()
        elif command == "validate":
            config = setup_environment()
            print("✓ Configuration validated successfully")
        else:
            print("Unknown command")
    else:
        # Default: run validation
        config = setup_environment()
        print("✓ Environment setup complete")
