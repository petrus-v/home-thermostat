import os
temperature_card_app_user = "pi"
temperature_card_app_user_home = "/home/pi"
temperature_card_app_dir = os.path.join(temperature_card_app_user_home, "temperature")
temperature_card_venv_path = os.path.join(temperature_card_app_user_home, "temperature-venv")
temperature_card_engine_on_calendar = "*-*-* *:*:04"