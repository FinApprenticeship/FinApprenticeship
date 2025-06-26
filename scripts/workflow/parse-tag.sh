#!/bin/bash

help() {
	echo "Usage: $0 <tag-name>"
	echo "Parses a tag name of the form <artifact>-<stage>-v<version> or <artifact>-v<version> and outputs key=value pairs."
	echo "  <artifact>   : Name of the artifact (e.g., streamlit)"
	echo "  <stage>      : Optional stage (e.g., beta, main). If missing, defaults to 'main'"
	echo "  <version>    : Version string (e.g., 1.0.0)"
	echo "Example: $0 streamlit-beta-v1.0.0"
	echo "         $0 streamlit-v1.0.0"
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
	help
	exit 0
fi

if [ -z "$1" ]; then
	echo "Error: Tag name argument missing."
	help
	exit 1
fi

TAG_NAME="$1"

# Check if tag contains a dash (required for valid format)
if [[ "$TAG_NAME" != *"-"* ]]; then
	echo "Error: Invalid tag format."
	help
	exit 1
fi

# Extract version (everything after the last dash)
VERSION=$(echo "$TAG_NAME" | sed 's/.*-v//')

# Validate that version was extracted successfully and is not the original tag
if [ -z "$VERSION" ] || [ "$VERSION" = "$TAG_NAME" ]; then
	echo "Error: VERSION required."
	help
	exit 2
fi

# Extract artifact (everything before the first dash)
ARTIFACT=$(echo "$TAG_NAME" | sed 's/-.*//')

# Validate that artifact was extracted successfully
if [ -z "$ARTIFACT" ]; then
	echo "Error: ARTIFACT required."
	help
	exit 3
fi

# Create capitalized version of artifact (first letter only)
ARTIFACT_CAPITALIZED=$(echo "$ARTIFACT" | sed 's/^./\U&/')

# Initialize stage with "main" and try to extract it from tag
STAGE="main"
# Try to extract stage by removing artifact and version parts
# First remove artifact part
REMAINING=$(echo "$TAG_NAME" | sed "s/^$ARTIFACT-//")
# Then remove version part (handle both -v and v formats)
EXTRACTED_STAGE=$(echo "$REMAINING" | sed "s/-*v$VERSION$//")
# If extracted stage is not empty, use it
if [ -n "$EXTRACTED_STAGE" ]; then
	STAGE="$EXTRACTED_STAGE"
fi

# Set output variables
echo "artifact=$ARTIFACT"
echo "artifact_capitalized=$ARTIFACT_CAPITALIZED"
echo "stage=$STAGE"
echo "version=$VERSION"
echo "tag_name=$TAG_NAME"
