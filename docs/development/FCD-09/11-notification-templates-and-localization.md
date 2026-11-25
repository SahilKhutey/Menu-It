# FCD-09 §11 — Notification Templates & Localization

## 1. Directory Structure

Templates are located on the filesystem in `apps/api/src/menu_it/platform/notifications/templates/`:

```
templates/
├── email/
│   ├── account-welcome/
│   │   ├── en/
│   │   │   ├── subject.txt
│   │   │   ├── body.html
│   │   │   └── body.txt
│   │   └── hi/
│   │       ├── subject.txt
│   │       ├── body.html
│   │       └── body.txt
│   └── order-status/
│       └── en/
│           ├── subject.txt
│           ├── body.html
│           └── body.txt
└── in_app/
    ├── account-welcome/
    │   ├── title.txt
    │   └── body.txt
    └── order-status/
        ├── title.txt
        └── body.txt
```

---

## 2. Autoescaping & Security

`TemplateRenderer` constructs two isolated Jinja2 environments:
- **HTML Environment:** `select_autoescape(enabled_extensions=("html", "htm", "xml"), default_for_string=True)`. Any user-supplied string variable containing `<script>` or HTML tags is converted to safe HTML entities (`&lt;script&gt;`).
- **Text Environment:** Unescaped for clean email subject lines and SMS/console messages.

---

## 3. Language & Locale Fallback

When a template is requested in an unsupported or unrendered locale (e.g. `fr`), the renderer falls back automatically to English (`en`).
