# mcp_server/recruitment_backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies from requirements.txt
# Note: No system dependencies needed (unlike purchase order server which needs OpenCV/PaddleOCR)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all recruitment_backend files
COPY . .

# Expose port 8200 (recruitment backend port - separate from staffing:8100)
EXPOSE 8200
ENV PORT=8200
ENV HOST=0.0.0.0

# Run the recruitment backend server
CMD ["python", "server.py"]

