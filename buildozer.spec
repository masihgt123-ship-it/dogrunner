[app]
title = Dog Runner
package.name = dogrunner
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
# اگر کتابخانه‌هایی مثل requests یا ... دارید، حتما اینجا اضافه کنید
requirements = python3,kivy
version = 0.1
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.private_storage = True
orientation = landscape
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
