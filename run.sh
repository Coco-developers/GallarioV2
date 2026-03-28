#!/bin/bash
docker run -d \
  --name gallario \
  --restart unless-stopped \
  -p 80:8000 \
  -v gallario_db:/app \
  gallario
