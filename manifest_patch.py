import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

if "QUERY_ALL_PACKAGES" not in content:
    anchor = "<application"
    idx = content.find(anchor)
    if idx == -1:
        print("XATO: <application> topilmadi")
        sys.exit(1)
    permission_line = '<uses-permission android:name="android.permission.QUERY_ALL_PACKAGES" />\n    '
    content = content[:idx] + permission_line + content[idx:]

if "PACKAGE_USAGE_STATS" not in content:
    anchor = "<application"
    idx = content.find(anchor)
    if idx == -1:
        print("XATO: <application> topilmadi")
        sys.exit(1)
    permission_line = '<uses-permission android:name="android.permission.PACKAGE_USAGE_STATS" />\n    '
    content = content[:idx] + permission_line + content[idx:]

activity_block = """        <activity
            android:name="com.github.olga_yakovleva.rhvoice.android.AppLanguagePickerActivity"
            android:exported="false"
            android:label="Til tanlang" />
"""

anchor2 = "</application>"
if anchor2 not in content:
    print("XATO: </application> topilmadi")
    sys.exit(1)

if "AppLanguagePickerActivity" not in content:
    content = content.replace(anchor2, activity_block + anchor2, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("AndroidManifest.xml muvaffaqiyatli patch qilindi")
