import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def invoke_notification(HOOK_URL, logger, title, body):
    
    text_body = ''

    if len(body) > 1:
        for text in body:
            text_body += str(text)
    else:
        text_body = str(body)

    message = {
      "@context": "https://schema.org/extensions",
      "@type": "MessageCard",
      "themeColor": "d63333",
      "title": title,
      "text": text_body
    }

    req = Request(HOOK_URL, json.dumps(message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Error message posted")
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)