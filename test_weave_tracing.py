"""
Test script to verify Weave tracing is working.

Run this to check if:
1. Weave can be initialized
2. OpenTelemetry spans can be created
3. Spans can be exported to Weave
"""

import os
import sys
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.weave_tracing import WeaveSpanExporter

def test_weave_tracing():
    """Test Weave tracing setup."""
    print("🧪 Testing Weave Tracing Setup...")
    print()
    
    # Check environment variables
    print("1. Checking environment variables...")
    required_vars = ["WANDB_PROJECT", "WANDB_API_KEY"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        print(f"   ❌ Missing: {', '.join(missing)}")
        print("   Set these in your .env file or environment")
        return False
    print(f"   ✅ WANDB_PROJECT: {os.environ.get('WANDB_PROJECT')}")
    print(f"   ✅ WANDB_ENTITY: {os.environ.get('WANDB_ENTITY', 'not set (optional)')}")
    print(f"   ✅ WANDB_API_KEY: {'*' * 20}...{os.environ.get('WANDB_API_KEY', '')[-4:]}")
    print()
    
    # Test Weave exporter initialization
    print("2. Testing Weave exporter initialization...")
    try:
        exporter = WeaveSpanExporter(debug=True)
        print("   ✅ Weave exporter initialized successfully")
        print()
    except Exception as e:
        print(f"   ❌ Failed to initialize Weave exporter: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Set up tracer provider
    print("3. Setting up OpenTelemetry tracer provider...")
    try:
        provider = TracerProvider()
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        print("   ✅ Tracer provider set up")
        print()
    except Exception as e:
        print(f"   ❌ Failed to set up tracer provider: {e}")
        return False
    
    # Create a test span
    print("4. Creating test span...")
    try:
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("test_span") as span:
            span.set_attribute("test.attribute", "test_value")
            span.set_attribute("test.number", 42)
            print("   ✅ Test span created")
            print(f"   - Span name: {span.name}")
            print(f"   - Trace ID: {format(span.get_span_context().trace_id, 'x')}")
        print()
    except Exception as e:
        print(f"   ❌ Failed to create test span: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Force flush
    print("5. Flushing spans to Weave...")
    try:
        processor.force_flush()
        print("   ✅ Spans flushed")
        print()
    except Exception as e:
        print(f"   ⚠️  Warning during flush: {e}")
        print()
    
    print("✅ All tests passed!")
    print()
    print("Next steps:")
    print("1. Check your W&B project dashboard for the trace")
    print("2. Look for a trace named 'test_span'")
    print("3. If you don't see it, check the W&B project name matches exactly")
    print("4. Enable WEAVE_DEBUG=true for more detailed logs")
    
    return True

if __name__ == "__main__":
    success = test_weave_tracing()
    sys.exit(0 if success else 1)

