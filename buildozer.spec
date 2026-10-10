[app]

title = Dog Runner
package.name = dogrunner
package.domain = org.dogrunner
version = 1.0

source.dir = .
source.include_exts = py,wav

requirements = python3==3.12.9,hostpython3==3.12.9,pygame

orientation = landscape
fullscreen = 0

android.permissions = INTERNET

android.api = 33
android.minapi = 24
android.ndk = 28c

p4a.local_recipes = ./p4a-recipes

android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
