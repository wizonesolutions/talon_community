from talon.engine import engine

ENABLED = False

def listener(topic, m):
    if topic == "cmd" and m["cmd"]["cmd"] == "g.load" and m["success"] == True:
        print("[grammar reloaded]")
    else:
        print(topic, m)


if ENABLED:
    engine.register("", listener)
