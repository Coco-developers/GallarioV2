#!/bin/bash
docker run -d \
  --name Gallario \
  --restart unless-stopped \
  -p 80:8000 \
  -v gallario_db:/app \
  gallario
