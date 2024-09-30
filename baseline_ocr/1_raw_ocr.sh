#!/bin/bash

INPUT_DIR="corpus/images"
OUTPUT_DIR="ocr_results/raw_tessdata"

mkdir -p "$OUTPUT_DIR"

for IMAGE in "$INPUT_DIR"/*; do
    BASENAME=$(basename "$IMAGE" | cut -d. -f1)
    
    tesseract "$IMAGE" "$OUTPUT_DIR/$BASENAME" -l ron --psm 12 --tessdata-dir /opt/homebrew/share/tessdata --dpi 300
done

