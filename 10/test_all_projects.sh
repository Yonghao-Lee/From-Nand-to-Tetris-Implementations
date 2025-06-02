#!/bin/bash

# Set the path to TextComparer
TEXT_COMPARER="../../tools/TextComparer.sh"

echo "Testing ExpressionLessSquare Project..."
echo "======================================"

# Test ExpressionLessSquare files
EXPR_DIR="ExpressionLessSquare"
for jack_file in "${EXPR_DIR}"/*.jack; do
    if [ -f "$jack_file" ]; then
        filename=$(basename "$jack_file" .jack)
        your_xml="${EXPR_DIR}/${filename}.xml"
        reference_xml="${EXPR_DIR}/${filename}T.xml"  # Assuming T.xml are reference files
        
        if [ -f "$your_xml" ] && [ -f "$reference_xml" ]; then
            echo "Comparing: $filename"
            $TEXT_COMPARER "$your_xml" "$reference_xml"
            echo ""
        else
            echo "Missing files for $filename"
            echo "  Your XML: $your_xml (exists: $([ -f "$your_xml" ] && echo "yes" || echo "no"))"
            echo "  Reference: $reference_xml (exists: $([ -f "$reference_xml" ] && echo "yes" || echo "no"))"
            echo ""
        fi
    fi
done

echo ""
echo "Testing ArrayTest Project..."
echo "==========================="

# Test ArrayTest files
ARRAY_DIR="ArrayTest"
for jack_file in "${ARRAY_DIR}"/*.jack; do
    if [ -f "$jack_file" ]; then
        filename=$(basename "$jack_file" .jack)
        your_xml="${ARRAY_DIR}/${filename}.xml"
        reference_xml="${ARRAY_DIR}/${filename}T.xml"  # Assuming T.xml are reference files
        
        if [ -f "$your_xml" ] && [ -f "$reference_xml" ]; then
            echo "Comparing: $filename"
            $TEXT_COMPARER "$your_xml" "$reference_xml"
            echo ""
        else
            echo "Missing files for $filename"
            echo "  Your XML: $your_xml (exists: $([ -f "$your_xml" ] && echo "yes" || echo "no"))"
            echo "  Reference: $reference_xml (exists: $([ -f "$reference_xml" ] && echo "yes" || echo "no"))"
            echo ""
        fi
    fi
done

echo "Testing complete!"
