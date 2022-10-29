def cmd_log(msg):
    print("[log] -- new message")
    print(f"user -- {msg.from_user.first_name}")
    print(f"message -- {msg.text}")
    print("______________________________")