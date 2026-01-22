#!/bin/bash
# Example: Research fitness products and services

python main.py "home workout equipment" \
  --reddit "homegym,bodyweightfitness,fitness" \
  --amazon \
  --youtube \
  --context "Targeting busy professionals aged 25-45 who want to workout at home but struggle with motivation and time" \
  --format all
