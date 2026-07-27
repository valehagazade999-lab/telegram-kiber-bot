# -*- coding: utf-8 -*-
"""
Kibertəhlükəsizlik Sual-Cavab Telegram Botu
--------------------------------------------
Ümumi kibertəhlükəsizlik mövzularında (parollar, fişinq, VPN, 2FA,
zərərli proqramlar, təhlükəsiz internet istifadəsi və s.) istifadəçilərə
ciddi, faydalı və dəqiq məlumat verir.

Quraşdırma:
    pip install python-telegram-bot --upgrade

İşə salmaq:
    1. Telegram-da @BotFather ilə yeni bot yaradın, TOKEN alın.
    2. Aşağıda BOT_TOKEN yerinə öz tokeninizi yazın (və ya mühit
       dəyişəni kimi verin: export BOT_TOKEN="....").
    3. python bot.py
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "BURAYA_TOKEN_YAZIN")

# ---------------------------------------------------------------------
# Bilik bazası: mövzu -> (başlıq, cavab mətni)
# ---------------------------------------------------------------------
KNOWLEDGE_BASE = {
    "passwords": {
        "title": "Güclü parol yaratmaq",
        "text": (
            "Güclü parol üçün əsas qaydalar:\n\n"
            "• Minimum 12-14 simvol istifadə edin.\n"
            "• Böyük/kiçik hərf, rəqəm və simvolları qarışdırın.\n"
            "• Şəxsi məlumatlardan (ad, doğum tarixi) istifadə etməyin.\n"
            "• Hər hesab üçün fərqli parol seçin.\n"
            "• Parol meneceri (Bitwarden, 1Password və s.) istifadə edin.\n"
            "• Mümkün olduqda passphrase (məs. 'Yaşıl7Kitab#Uçur') üsulundan yararlanın."
        ),
    },
    "2fa": {
        "title": "İki mərhələli təsdiqləmə (2FA)",
        "text": (
            "2FA hesabınıza əlavə təhlükəsizlik qatı əlavə edir:\n\n"
            "• Parol oğurlansa belə, hesaba giriş üçün ikinci amil (kod, "
            "tətbiq təsdiqi) tələb olunur.\n"
            "• SMS əsaslı 2FA ən zəif variantdır (SIM-swap riski var).\n"
            "• Authenticator tətbiqləri (Google Authenticator, Authy) daha "
            "təhlükəsizdir.\n"
            "• Fiziki təhlükəsizlik açarları (YubiKey) ən güclü qorunmanı verir.\n"
            "• Bütün vacib hesablarda (email, bank, sosial media) 2FA aktiv edin."
        ),
    },
    "phishing": {
        "title": "Fişinq (phishing) hücumları",
        "text": (
            "Fişinq — istifadəçini aldadaraq şəxsi məlumat və ya giriş "
            "məlumatlarını əldə etmək cəhdidir.\n\n"
            "Tanınma əlamətləri:\n"
            "• Təcili hərəkət tələb edən mesajlar ('hesabınız bloklanacaq').\n"
            "• Şübhəli və ya oxşar (spoofed) domenlər.\n"
            "• Qrammatik səhvlər, qeyri-adi göndərən ünvanı.\n"
            "• Naməlum linklər və ya əlavələr.\n\n"
            "Qorunma:\n"
            "• Linkə klikləmədən əvvəl ünvanı diqqətlə yoxlayın.\n"
            "• Rəsmi saytlara birbaşa brauzerdən daxil olun.\n"
            "• Şübhəli mesajları bildirin və silin."
        ),
    },
    "malware": {
        "title": "Zərərli proqramlar (malware)",
        "text": (
            "Zərərli proqram növləri:\n\n"
            "• Virus — özünü digər fayllara kopyalayır.\n"
            "• Troyan — zərərsiz proqram kimi gizlənir.\n"
            "• Ransomware — fayllarınızı şifrələyib fidyə tələb edir.\n"
            "• Spyware — məlumatlarınızı gizli izləyir.\n\n"
            "Qorunma yolları:\n"
            "• Etibarlı antivirus istifadə edin və yeniləyin.\n"
            "• Naməlum mənbələrdən proqram yükləməyin.\n"
            "• Əməliyyat sistemini və proqramları müntəzəm yeniləyin.\n"
            "• Vacib fayllardan mütəmadi ehtiyat nüsxəsi (backup) çıxarın."
        ),
    },
    "vpn": {
        "title": "VPN nədir və nə vaxt lazımdır",
        "text": (
            "VPN (Virtual Private Network) internet trafikinizi şifrələyir "
            "və IP ünvanınızı gizlədir.\n\n"
            "Nə vaxt faydalıdır:\n"
            "• İctimai Wi-Fi şəbəkələrindən istifadə edərkən.\n"
            "• Məlumat gizliliyini artırmaq istədikdə.\n\n"
            "Nəzərə alınmalı məqamlar:\n"
            "• VPN sizi anonim etmir, yalnız trafiki şifrələyir.\n"
            "• Etibarlı, aydın 'no-log' siyasəti olan provayder seçin.\n"
            "• Pulsuz VPN xidmətləri bəzən məlumatlarınızı sata bilər — diqqətli olun."
        ),
    },
    "social_media": {
        "title": "Sosial media hesablarının təhlükəsizliyi",
        "text": (
            "• Profilinizdə şəxsi məlumatları (ünvan, telefon) paylaşmayın.\n"
            "• Məxfilik parametrlərini müntəzəm yoxlayın.\n"
            "• Naməlum şəxslərin dost/əlaqə tələblərinə ehtiyatlı yanaşın.\n"
            "• Hesabınıza giriş edən cihazları müntəzəm yoxlayın.\n"
            "• Hər platforma üçün fərqli, güclü parol və 2FA istifadə edin."
        ),
    },
    "safe_browsing": {
        "title": "Təhlükəsiz internet gəzintisi",
        "text": (
            "• Yalnız HTTPS (kilid işarəli) saytlardan istifadə edin.\n"
            "• Brauzerinizi və əlavələrini (extension) yeniləyin.\n"
            "• Etibarsız reklamlara və 'sürpriz mükafat' bannerlərinə klikləməyin.\n"
            "• Açıq Wi-Fi-da bank və şəxsi hesablara daxil olmaqdan çəkinin.\n"
            "• Brauzerdə lazımsız icazələri (kamera, mikrofon, lokasiya) məhdudlaşdırın."
        ),
    },
    "data_privacy": {
        "title": "Şəxsi məlumatların qorunması",
        "text": (
            "• Hansı tətbiqlərin hansı məlumatlara giriş etdiyini yoxlayın.\n"
            "• Lazımsız tətbiq icazələrini ləğv edin.\n"
            "• Mühüm sənədləri şifrələnmiş şəkildə saxlayın.\n"
            "• Məlumat sızması (data breach) hallarında xəbərdarlıq üçün "
            "haveibeenpwned.com kimi xidmətlərdən yararlana bilərsiniz.\n"
            "• Şəxsi məlumatlarınızı yalnız etibar etdiyiniz xidmətlərlə paylaşın."
        ),
    },
}

MENU_KEYBOARD = [
    [InlineKeyboardButton("🔑 Parollar", callback_data="passwords")],
    [InlineKeyboardButton("📲 2FA (İki mərhələli təsdiq)", callback_data="2fa")],
    [InlineKeyboardButton("🎣 Fişinq", callback_data="phishing")],
    [InlineKeyboardButton("🦠 Zərərli proqramlar", callback_data="malware")],
    [InlineKeyboardButton("🌐 VPN", callback_data="vpn")],
    [InlineKeyboardButton("👥 Sosial media təhlükəsizliyi", callback_data="social_media")],
    [InlineKeyboardButton("🧭 Təhlükəsiz gəzinti", callback_data="safe_browsing")],
    [InlineKeyboardButton("🔒 Şəxsi məlumatların qorunması", callback_data="data_privacy")],
]

# Sadə açar sözlərə görə sərbəst mətn axtarışı
KEYWORD_MAP = {
    "parol": "passwords",
    "password": "passwords",
    "2fa": "2fa",
    "iki merhele": "2fa",
    "iki mərhələ": "2fa",
    "fişinq": "phishing",
    "fishing": "phishing",
    "phishing": "phishing",
    "virus": "malware",
    "malware": "malware",
    "zərərli": "malware",
    "vpn": "vpn",
    "sosial media": "social_media",
    "instagram": "social_media",
    "facebook": "social_media",
    "brauzer": "safe_browsing",
    "internet": "safe_browsing",
    "məlumat": "data_privacy",
    "privacy": "data_privacy",
    "gizlilik": "data_privacy",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Salam! Bu bot kibertəhlükəsizlik mövzusunda ümumi məlumat üçün "
        "nəzərdə tutulub.\n\n"
        "Aşağıdakı mövzulardan birini seçin və ya sualınızı birbaşa yazın."
    )
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(MENU_KEYBOARD))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — mövzu menyusunu göstərir\n"
        "İstədiyiniz mövzu haqqında sadəcə sual yaza bilərsiniz "
        "(məsələn: 'VPN nədir?', 'parolumu necə güclü edim?')."
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = KNOWLEDGE_BASE.get(query.data)
    if topic:
        await query.edit_message_text(f"*{topic['title']}*\n\n{topic['text']}", parse_mode="Markdown")
    else:
        await query.edit_message_text("Bu mövzu tapılmadı.")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    matched_key = None
    for keyword, key in KEYWORD_MAP.items():
        if keyword in user_text:
            matched_key = key
            break

    if matched_key:
        topic = KNOWLEDGE_BASE[matched_key]
        await update.message.reply_text(f"*{topic['title']}*\n\n{topic['text']}", parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "Sualınızı tam anlaya bilmədim. Aşağıdakı mövzulardan birini "
            "seçə bilərsiniz:",
            reply_markup=InlineKeyboardMarkup(MENU_KEYBOARD),
        )


def main():
    if BOT_TOKEN == "BURAYA_TOKEN_YAZIN":
        print(
            "XƏBƏRDARLIQ: BOT_TOKEN təyin edilməyib. "
            "Mühit dəyişəni kimi verin: export BOT_TOKEN='sizin_tokeniniz'"
        )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Bot işə düşdü...")
    app.run_polling()


if __name__ == "__main__":
    main()
