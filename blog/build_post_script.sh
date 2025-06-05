#!/bin/bash

# build-post.sh - Convert LaTeX files to HTML for math blog
# Usage: ./build-post.sh filename.tex
# or:    ./build-post.sh filename  (without .tex extension)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    print_error "Pandoc is not installed or not in PATH"
    echo "Install it from: https://pandoc.org/installing.html"
    exit 1
fi

# Check if filename provided
if [ $# -eq 0 ]; then
    print_error "No filename provided"
    echo "Usage: $0 <filename.tex> or $0 <filename>"
    echo "Examples:"
    echo "  $0 gradient-descent.tex"
    echo "  $0 gradient-descent"
    exit 1
fi

# Get filename and handle extension
INPUT_FILE="$1"
if [[ "$INPUT_FILE" != *.tex ]]; then
    INPUT_FILE="${INPUT_FILE}.tex"
fi

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    print_error "Input file '$INPUT_FILE' not found"
    exit 1
fi

# Get base filename without extension
BASE_NAME=$(basename "$INPUT_FILE" .tex)
OUTPUT_FILE="${BASE_NAME}.html"

print_status "Converting $INPUT_FILE to $OUTPUT_FILE"

# CSS file to use
CSS_FILE="math-blog.css"

# Optional analytics file
ANALYTICS_FILE="analytics.html"

# Build pandoc command
PANDOC_CMD="pandoc \"$INPUT_FILE\" -o \"$OUTPUT_FILE\" --mathjax --standalone"

# Add CSS if it exists
if [ -f "$CSS_FILE" ]; then
    PANDOC_CMD="$PANDOC_CMD --css \"$CSS_FILE\""
    print_status "Using CSS file: $CSS_FILE"
else
    print_warning "CSS file '$CSS_FILE' not found - using default styling"
fi

# Add analytics if file exists (for future use)
if [ -f "$ANALYTICS_FILE" ]; then
    PANDOC_CMD="$PANDOC_CMD -H \"$ANALYTICS_FILE\""
    print_status "Including analytics: $ANALYTICS_FILE"
fi

# Show the command being executed
print_status "Executing: $PANDOC_CMD"

# Execute pandoc
if eval $PANDOC_CMD; then
    print_success "Successfully converted $INPUT_FILE to $OUTPUT_FILE"
    
    # Show file size
    if command -v du &> /dev/null; then
        SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
        print_status "Output file size: $SIZE"
    fi
    
    # Optional: Open in browser (uncomment if desired)
    # if command -v open &> /dev/null; then  # macOS
    #     open "$OUTPUT_FILE"
    # elif command -v xdg-open &> /dev/null; then  # Linux
    #     xdg-open "$OUTPUT_FILE"
    # fi
    
else
    print_error "Pandoc conversion failed"
    exit 1
fi

print_status "Done! You can now view $OUTPUT_FILE in your browser"