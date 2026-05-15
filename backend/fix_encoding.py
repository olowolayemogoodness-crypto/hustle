#!/usr/bin/env python3
"""Convert requirements_new.txt to UTF-16 and replace requirements.txt"""
from pathlib import Path

backend_dir = Path(__file__).parent
new_file = backend_dir / "requirements_new.txt"
target_file = backend_dir / "requirements.txt"

# Read the new file as UTF-8
content = new_file.read_text(encoding='utf-8')

# Write to requirements.txt as UTF-16
target_file.write_text(content, encoding='utf-16')

print("✓ Successfully updated requirements.txt with UTF-16 encoding")
print(f"  File: {target_file}")
print(f"  Size: {target_file.stat().st_size} bytes")

# Clean up temp file
new_file.unlink()
print("✓ Cleaned up temporary file")
