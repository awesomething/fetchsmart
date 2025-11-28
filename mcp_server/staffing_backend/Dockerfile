# mcp_server/staffing_backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy staffing backend code
COPY . .

# Expose port 8100
EXPOSE 8100

# Set environment variables
ENV PORT=8100
ENV HOST=0.0.0.0

# Run the MCP server
CMD ["python", "mcpstaffingagent.py"]

