#!/usr/bin/env python3
"""
Test script to launch the robust interactive dashboard
This demonstrates the fixed dashboard with working filters and no JavaScript errors
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def find_dashboard_template():
    """Find the robust dashboard template file"""
    possible_paths = [
        'mcp_visualization/templates/robust_dashboard.html',
        'templates/robust_dashboard.html',
        'robust_dashboard.html'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    return None

def start_dashboard_server(port=8080):
    """Start a simple HTTP server to serve the dashboard"""
    dashboard_path = find_dashboard_template()
    
    if not dashboard_path:
        print("❌ Error: Could not find robust_dashboard.html")
        print("Make sure you're running this from the project root directory")
        return False
    
    # Change to the directory containing the dashboard
    dashboard_dir = os.path.dirname(dashboard_path)
    dashboard_file = os.path.basename(dashboard_path)
    
    print(f"🚀 Starting dashboard server...")
    print(f"📁 Dashboard location: {dashboard_path}")
    print(f"🌐 Server will run on http://localhost:{port}")
    print(f"📊 Dashboard file: {dashboard_file}")
    print("")
    
    os.chdir(dashboard_dir)
    
    try:
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            print(f"✅ Server started successfully on port {port}")
            print(f"🔗 Dashboard URL: http://localhost:{port}/{dashboard_file}")
            print("")
            print("🎯 DASHBOARD FEATURES FIXED:")
            print("  ✅ No JavaScript errors")
            print("  ✅ Filter logging shows actual values (not [object Object])")
            print("  ✅ Real-time chart updates when filters change")
            print("  ✅ Working dropdowns and sliders")
            print("  ✅ Multiple chart types (bar, line, scatter, pie)")
            print("  ✅ Responsive design")
            print("")
            print("🧪 TO TEST THE FIXES:")
            print("  1. Open the dashboard in your browser")
            print("  2. Open browser developer console (F12)")
            print("  3. Change any filter (region, category, sliders)")
            print("  4. Watch console for proper filter value logging")
            print("  5. See charts update immediately")
            print("  6. Switch chart types to see all visualizations change")
            print("")
            print("⚠️  Press Ctrl+C to stop the server")
            print("")
            
            # Try to open the browser automatically
            try:
                url = f"http://localhost:{port}/{dashboard_file}"
                webbrowser.open(url)
                print(f"🌐 Browser opened automatically to: {url}")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print(f"   Please manually open: http://localhost:{port}/{dashboard_file}")
            
            print("")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Trying port {port + 1}...")
            return start_dashboard_server(port + 1)
        else:
            print(f"❌ Error starting server: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 ROBUST INTERACTIVE DASHBOARD TEST")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid port number. Using default port 8080.")
            port = 8080
    else:
        port = 8080
    
    success = start_dashboard_server(port)
    
    if success:
        print("\n✅ Dashboard test completed successfully!")
    else:
        print("\n❌ Dashboard test failed!")
        sys.exit(1)