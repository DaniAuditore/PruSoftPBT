from hypothesis import settings

settings.register_profile("ci", max_examples=100, derandomize=True, print_blob=True)
settings.register_profile("explore", max_examples=100, print_blob=True)
settings.load_profile("ci")
