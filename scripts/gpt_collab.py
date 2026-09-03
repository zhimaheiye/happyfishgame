import json
import time
import urllib.request

WEBBRIDGE_URL = "http://127.0.0.1:10086/command"
SESSION = "maa-gpt-collab"


def call_bridge(action, args=None):
  payload = {"action": action, "session": SESSION}
  if args:
    payload["args"] = args
  req = urllib.request.Request(
      WEBBRIDGE_URL,
      data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
      headers={"Content-Type": "application/json; charset=utf-8"},
  )
  with urllib.request.urlopen(req) as resp:
    return json.loads(resp.read().decode("utf-8"))


def ensure_chatgpt_tab():
  # Check if current tab is already ChatGPT
  res = call_bridge("evaluate", {"code": "window.location.href"})
  url = res.get("data", {}).get("value", "")
  if "chatgpt.com" not in url:
    call_bridge("navigate", {"url": "https://chatgpt.com/c/6a994387-6dbc-83ec-ab43-eb2672ec1aa3"})
    time.sleep(4.0)


def send_to_gpt(text: str) -> bool:
  ensure_chatgpt_tab()
  # 1. fill text
  fill_resp = call_bridge(
      "fill", {"selector": "#prompt-textarea", "value": text}
  )
  if not fill_resp.get("ok"):
    print("Fill failed:", fill_resp)
    return False
  time.sleep(1.0)

  # 2. click send
  js = """(() => {
        const btn = document.querySelector('button[data-testid="send-button"]')
                 || document.querySelector('#composer-submit-button');
        if (btn && !btn.disabled) {
            btn.click();
            return {success: true};
        }
        return {success: false, disabled: btn ? btn.disabled : true};
    })()"""
  resp = call_bridge("evaluate", {"code": js})
  val = resp.get("data", {}).get("value", {})
  return val.get("success", False)


def wait_for_gpt_reply(timeout=90) -> str:
  ensure_chatgpt_tab()
  js_check = """(() => {
        const turns = document.querySelectorAll('[data-testid^="conversation-turn-"]');
        const last = turns[turns.length - 1];
        const streaming = !!document.querySelector('.result-streaming')
                       || !!document.querySelector('[data-testid="stop-button"]');
        return {
            isStreaming: streaming,
            fullText: last ? last.innerText : ''
        };
    })()"""
  time.sleep(5)
  deadline = time.time() + timeout
  while time.time() < deadline:
    resp = call_bridge("evaluate", {"code": js_check})
    data = resp.get("data", {}).get("value", {})
    if not data.get("isStreaming", True) and len(data.get("fullText", "")) > 10:
      return data.get("fullText", "")
    time.sleep(5)
  return "(timeout)"


def get_last_turn() -> str:
  ensure_chatgpt_tab()
  js = """(() => {
        const turns = document.querySelectorAll('[data-testid^="conversation-turn-"]');
        const last = turns[turns.length - 1];
        return last ? last.innerText : '';
    })()"""
  resp = call_bridge("evaluate", {"code": js})
  return resp.get("data", {}).get("value", "")


if __name__ == "__main__":
  last = get_last_turn()
  print("Current last turn snippet:", last[-300:])
