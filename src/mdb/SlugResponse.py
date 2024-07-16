class SlugResponse:
    def __init__(self, count):
        self.count = count

    def __str__(self):
        return f"Slug detected, there has been {self.count} slugs since the last activity."