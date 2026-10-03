"""Language helpers: right-to-left display and translation style rules."""

RTL_LANGUAGES = {"Urdu", "Arabic"}

RTL_CSS = """
<style>
.st-key-brief, .st-key-brief * { direction: rtl; text-align: right; }
.st-key-brief { font-family: 'Noto Nastaliq Urdu', 'Noto Naskh Arabic', 'Jameel Noori Nastaleeq', Tahoma, serif;
                line-height: 2.1; font-size: 1.1rem; }
.st-key-brief a, .st-key-brief code { direction: ltr; unicode-bidi: embed; }
.st-key-brief ul, .st-key-brief ol { padding-right: 1.5rem; padding-left: 0; }
</style>
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&family=Noto+Naskh+Arabic&display=swap" rel="stylesheet">
"""
