#!/bin/bash
# Example: Research e-commerce product category

python main.py "ergonomic office chair" \
  --reddit "homeoffice,WorkOnline,RemoteWork" \
  --amazon \
  --context "E-commerce store selling office furniture to remote workers experiencing back pain" \
  --format html
