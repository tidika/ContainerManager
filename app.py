import http.server
import socketserver

def generate_static_website():
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Welcome to MountPointe</title>
    </head>
    <body>
        <h1>Hi and welcome to MountPointe</h1>
        <p>Your go-to place for everything machine learning operations.</p>
    </body>
    </html>
    '''
    
    with open("index.html", "w") as file:
        file.write(html_content)
    print("Static website content generated successfully.")

def serve_static_website():
    PORT = 8000

    # Start a simple HTTP server to serve the static content
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving static website at port {PORT}...")
        httpd.serve_forever()

# Generate the static website content
generate_static_website()

# Serve the static website content
serve_static_website()
