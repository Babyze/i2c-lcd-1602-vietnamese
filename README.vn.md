# Charset tiếng Việt cho I2C LCD 16xx Driver

> Vietnamese charset driver cho LCD 1602, 1604

---

[![en](https://img.shields.io/badge/lang-en-blue.svg)](/README.md)

---

# Ví dụ

1. Hiển thị string có chỉ định vị trí bắt đầu của string
```python
import lcddriver
from time import *

lcd = lcddriver.lcd()

self.lcd.lcd_display_string_pos("Máy phân loại", 1, 0)
self.lcd.lcd_display_string_pos("rác hoạt động", 2, 1)
```
Kết quả:
![Display within position](/images/display-string-position.jpg)

2. Hiển thị string không chỉ định vị trí bắt đầu
```python
import lcddriver
from time import *

lcd = lcddriver.lcd()

self.lcd.lcd_display_string("Máy Đang Bảo Trì!", 1)
self.lcd.lcd_display_string("Xin thử lại sau", 2)
```
Kết quả:
![Display without position](/images/display-string.jpg)

---

# API

### lcd_display_string(string, line)

Hiển thị string


| Parameter |   Type    | Min | Max | Description               |
|-----------|-----------|-----|-----|---------------------------|
| string    |  string   |  -  |  -  | String muốn hiển thị      |
| line      |  number   |  1  |  4  | Dòng muốn hiển thị string |

### lcd_display_string_pos(string, line, pos)

Hiển thị string có chỉ định vị trí bắt đầu của string

| Parameter |   Type    | Min | Max | Description                                |
|-----------|-----------|-----|-----|--------------------------------------------|
| string    |   string  |  -  |  -  | String muốn hiển thị                       |
| line      |   number  |  1  |  4  | Dòng muốn hiển thị string                  |
| pos       |   number  |  0  |  -  | Vị trí muốn hiển thị string                |

### lcd_clear()

Xóa string đang hiển thị trên LCD

### backlight(state)

Bật tắt đèn của LCD

| Parameter |   Type    | Min | Max | Description                                   |
|-----------|-----------|-----|-----|-----------------------------------------------|
| state     |   number  |  0  |  1  | bật (1) hoặc tắt (0) đèn LCD                  |

---

# License

MIT
