[app]
title = Dog Runner
package.name = dogrunner
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,pygame
orientation = portrait
fullscreen = 1

# اندروید
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a
android.presplash_color = #FFFFFF
android.skip_update = False
android.accept_sdk_license = True

# تنظیمات حیاتی برای رفع خطای بیلد
p4a.branch = develop
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
