[app]
# نام برنامه
title = Dog Runner
package.name = dogrunner
package.domain = org.test
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# کتابخانه‌های مورد نیاز (فقط موارد پایه)
requirements = python3,kivy

# تنظیمات اصلی
orientation = portrait
fullscreen = 0
android.presplash_color = #FFFFFF

[buildozer]
# سطح لاگ برای دیباگ (2 یعنی جزئیات بیشتر)
log_level = 2
# غیرفعال کردن اخطار مربوط به اجرای روت در داکر
warn_on_root = 0
