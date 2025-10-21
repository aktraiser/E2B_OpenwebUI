# CrewAI E2B - Production VPS Deployment

Production-ready CrewAI with E2B cloud sandboxes, optimized for VPS deployment with comprehensive cost control and monitoring.

## 🎯 Features

- ✅ **E2B Cloud Sandbox Integration** - Secure Python code execution
- ✅ **Resource Limits** - Concurrent and hourly sandbox limits
- ✅ **Cost Protection** - Rate limiting and budget controls
- ✅ **Error Handling** - Comprehensive error recovery and retries
- ✅ **Health Monitoring** - REST API endpoints for status checks
- ✅ **Metrics Tracking** - Detailed usage and performance metrics
- ✅ **Docker Deployment** - Containerized for easy VPS deployment
- ✅ **Production Logging** - Structured logging with file rotation

## 📋 Prerequisites

- **VPS**: 2GB+ RAM, 2 CPU cores minimum
- **Docker**: Docker and docker-compose installed
- **API Keys**:
  - Anthropic API key ([get here](https://console.anthropic.com/api))
  - E2B API key ([get here](https://e2b.dev/docs))

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd E2B
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Required in `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
E2B_API_KEY=e2b_your-key-here
```

### 3. Deploy

```bash
# Make deploy script executable (if needed)
chmod +x deploy.sh

# Deploy to VPS
./deploy.sh
```

### 4. Verify Deployment

```bash
# Check health
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics

# View logs
docker-compose logs -f crewai
```

## 📁 Project Structure

```
E2B/
├── config.py           # VPS configuration and limits
├── sandbox_pool.py     # E2B sandbox pool manager
├── tools.py            # CrewAI tool for Python execution
├── crew.py             # CrewAI agents and crew definition
├── main.py             # Application entry point
├── healthcheck.py      # FastAPI health/metrics endpoints
├── Dockerfile          # Docker image configuration
├── docker-compose.yml  # Docker orchestration
├── requirements.txt    # Python dependencies
├── deploy.sh           # Deployment script
├── .env                # Environment variables (create from .env.example)
├── .env.example        # Example environment configuration
└── logs/               # Application logs directory
```

## ⚙️ Configuration

Edit `.env` to adjust resource limits and behavior:

### Resource Limits (Cost Control)

```bash
MAX_CONCURRENT_SANDBOXES=2    # Max parallel sandboxes
MAX_SANDBOXES_PER_HOUR=20     # Hourly creation limit
```

### Timeouts

```bash
CODE_EXECUTION_TIMEOUT=30.0   # Max code execution time
REQUEST_TIMEOUT=60.0          # Max request time
SANDBOX_CREATION_TIMEOUT=120.0 # Max sandbox creation time
```

### Agent Configuration

```bash
MAX_ITERATIONS=3              # Max agent iterations
MAX_RPM=10                    # Max requests per minute
```

## 📊 Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "can_create_sandbox": true,
  "active_sandboxes": 1,
  "hourly_usage": "5/20",
  "failure_rate": "2.5%",
  "avg_execution_time": "1.23s"
}
```

### Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

Response includes:
- Total sandboxes created/failed
- Execution counts and timings
- Hourly usage tracking
- Configuration settings

### Logs

```bash
# Follow logs
docker-compose logs -f crewai

# View log file
tail -f logs/app.log

# View metrics file
cat logs/metrics.json
```

## 💰 Cost Management

### E2B Pricing

E2B sandboxes cost approximately **$0.01-0.05 per creation**.

With default limits:
- Max concurrent: 2 sandboxes
- Max hourly: 20 sandboxes
- **Estimated daily cost**: $10-25
- **Estimated monthly cost**: $300-750

### Cost Optimization Tips

1. **Reduce concurrent limit** if you don't need parallel execution
2. **Lower hourly limit** to control daily budget
3. **Monitor metrics** regularly via `/metrics` endpoint
4. **Set up alerts** for unusual usage patterns
5. **Review logs** to identify unnecessary executions

### Adjusting Limits

Edit `.env`:
```bash
# Conservative (lower cost)
MAX_CONCURRENT_SANDBOXES=1
MAX_SANDBOXES_PER_HOUR=10

# Standard (default)
MAX_CONCURRENT_SANDBOXES=2
MAX_SANDBOXES_PER_HOUR=20

# Aggressive (higher cost)
MAX_CONCURRENT_SANDBOXES=5
MAX_SANDBOXES_PER_HOUR=50
```

## 🔧 Usage

### Run Default Task

```bash
docker-compose up
```

This runs the example task: counting 'r' letters in 'strawberry'

### Custom Tasks

Edit [crew.py](crew.py):L49 to modify the task description:

```python
@task
def execute_task(self) -> Task:
    return Task(
        description="Your custom task here",
        agent=self.python_executor(),
        expected_output="Expected output format"
    )
```

Then redeploy:
```bash
./deploy.sh
```

## 🛠️ Troubleshooting

### "Cannot create sandbox: Max concurrent sandboxes reached"

**Cause**: Too many active sandboxes
**Solution**: Wait for current sandboxes to finish, or increase `MAX_CONCURRENT_SANDBOXES`

### "Hourly limit reached"

**Cause**: Hit the hourly creation limit
**Solution**:
- Wait for hourly reset (shown in error message)
- Or increase `MAX_SANDBOXES_PER_HOUR` (will increase costs)

### "Health check failed"

**Cause**: Service not starting properly
**Solution**:
```bash
# Check logs
docker-compose logs crewai

# Verify .env file
cat .env | grep API_KEY

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### High Costs

**Cause**: Too many sandbox creations
**Solution**:
1. Check metrics: `curl http://localhost:8000/metrics`
2. Review logs for unexpected executions
3. Reduce limits in `.env`
4. Restart: `docker-compose restart`

## 📚 Architecture

### Components

1. **config.py** - Centralized configuration with validation
2. **sandbox_pool.py** - Manages E2B sandbox lifecycle with:
   - Concurrent execution limits
   - Hourly rate limiting
   - Metrics tracking
   - Resource cleanup
3. **tools.py** - CrewAI tool with:
   - Code validation
   - Retry logic
   - Error handling
   - Result formatting
4. **crew.py** - CrewAI agents optimized for:
   - Cost-aware execution
   - Minimal sandbox usage
   - Clear task definitions
5. **main.py** - Entry point with logging setup
6. **healthcheck.py** - Monitoring API

### Execution Flow

```
User Request
    ↓
CrewAI Agent (crew.py)
    ↓
execute_python tool (tools.py)
    ↓
Sandbox Pool (sandbox_pool.py)
    ↓
E2B Cloud Sandbox
    ↓
Results + Metrics
```

## 🔒 Security

- ✅ Non-root Docker user
- ✅ Isolated E2B sandboxes
- ✅ Environment variable configuration
- ✅ Resource limits enforced
- ✅ Timeout protections
- ✅ Input validation

## 📝 Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=sk-...
export E2B_API_KEY=e2b_...

# Run locally
python main.py
```

### Running Tests

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test metrics
curl http://localhost:8000/metrics

# Test with custom input (edit crew.py first)
docker-compose restart
```

## 📖 Additional Resources

- [E2B Documentation](https://e2b.dev/docs)
- [CrewAI Documentation](https://docs.crewai.com)
- [Docker Documentation](https://docs.docker.com)

## 🤝 Support

For issues:
1. Check logs: `docker-compose logs crewai`
2. Verify configuration: `.env` file
3. Check health: `curl http://localhost:8000/health`
4. Review metrics: `curl http://localhost:8000/metrics`

## 📄 License

[Your License Here]

---

**Note**: This is a production-ready system with real costs. Monitor your E2B usage regularly and adjust limits according to your budget.
