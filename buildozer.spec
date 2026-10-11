[app]
# (str) Title of your application
title = Dog Runner

# (str) Package name
package.name = dogrunner

# (str) Package domain
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# اگر کتابخانه اضافه دارید اینجا اضافه کنید (مثلا: kivy,requests)
requirements = python3,kivy

# (str) Application versioning
version = 0.1

# (list) Permissions
android.permissions = INTERNET

# (int) Android API to use
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use (این نسخه ۲۵b بسیار پایدار است)
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir (False)
android.private_storage = True

# (str) The orientation
orientation = landscape

# (bool) Indicate if the application should be fullscreen
fullscreen = 1

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display build progress in console
display_overrides = 1
