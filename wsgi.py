import os
from app import app

if __name__ == "__main__":
    # Railway uses PORT environment variable (typically 8080)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
