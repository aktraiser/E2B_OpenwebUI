#!/usr/bin/env python3
"""
Test simple E2B connection
"""
import os
from e2b_code_interpreter import Sandbox

print("🧪 Testing E2B...")

try:
    with Sandbox.create() as sandbox:
        execution = sandbox.run_code("print('Hello E2B!'); 5+3")
        print(f"✅ Result: {execution.text}")
except Exception as e:
    print(f"❌ Error: {e}")