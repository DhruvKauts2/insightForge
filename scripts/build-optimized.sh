#!/bin/bash

echo "🐳 Building Optimized Docker Images"
echo "===================================="
echo ""

# Build with no cache for production
echo "Building API..."
docker build --no-cache -t insightforge-api:latest ./api

echo ""
echo "Checking image sizes..."
docker images | grep insightforge

echo ""
echo "✅ Build complete!"
echo ""
echo "Image details:"
docker inspect insightforge-api:latest --format='{{.Size}}' | numfmt --to=iec-i --suffix=B
