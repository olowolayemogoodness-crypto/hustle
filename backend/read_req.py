#!/usr/bin/env python3
import sys

# Read requirements.txt with UTF-16 encoding
with open('requirements.txt', 'r', encoding='utf-16') as f:
    content = f.read()
    lines = content.split('\n')
    
print(f"Total lines: {len(lines)}")
print("\nLast 15 lines:")
for i, line in enumerate(lines[-15:], 1):
    print(f"{i}: {repr(line)}")

# Now append ML dependencies
ml_deps = [
    "numpy>=1.26,<2.0",
    "pandas>=2.0,<3.0", 
    "scikit-learn>=1.3,<2.0",
    "joblib>=1.3,<2.0"
]

# Filter out empty lines at the end
while lines and lines[-1].strip() == '':
    lines.pop()

# Add dependencies
lines.extend(ml_deps)

# Write back
with open('requirements.txt', 'w', encoding='utf-16') as f:
    f.write('\n'.join(lines))

print("\n✓ Updated requirements.txt with ML dependencies")
print("Added:")
for dep in ml_deps:
    print(f"  - {dep}")
