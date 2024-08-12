#!/bin/bash
docker exec kong-api kong config db_export /var/lib/kong/kong.yaml
docker cp kong-api:/var/lib/kong/kong.yaml ./backup/kong.yaml
git add ./backup/kong.yaml
git commit -m "Kong configuration backup"
git push origin kong-configuration
