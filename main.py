# main.py - HINA AI ASSISTANT WITH VOICE + HINATA MODEL
import flet as ft
import json
import os
import random
import threading
import hashlib
from datetime import datetime, timedelta

# ========== VOICE SETUP ==========
try:
    import pyttsx3
    VOICE_ENABLED = True
except:
    VOICE_ENABLED = False

class VoiceManager:
    def __init__(self):
        if VOICE_ENABLED:
            self.engine = pyttsx3.init()
            self.set_female_voice()
    
    def set_female_voice(self):
        if not VOICE_ENABLED:
            return
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'hindi' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 160)
        self.engine.setProperty('volume', 1.0)
    
    def speak(self, text, emotion="neutral"):
        if not VOICE_ENABLED:
            print(f"🎤: {text}")
            return
        rates = {"happy": 180, "sad": 130, "romantic": 150, "neutral": 160}
        self.engine.setProperty('rate', rates.get(emotion, 160))
        def speak_thread():
            self.engine.say(text)
            self.engine.runAndWait()
        threading.Thread(target=speak_thread, daemon=True).start()

# ========== CONFIG ==========
class Config:
    APP_NAME = "🎀 Hina AI Assistant"
    VERSION = "2.0.0"
    
    PLANS = {
        "free": {"name": "Free", "price": 0, "days": 0},
        "weekly": {"name": "Weekly", "price": 29, "days": 7},
        "monthly": {"name": "Monthly", "price": 99, "days": 30},
        "yearly": {"name": "Yearly", "price": 999, "days": 365}
    }
    
    FEMALE_MODELS = [
        {"id": "f1", "name": "Hina", "personality": "friendly", "premium": False},
        {"id": "f2", "name": "Hinata", "personality": "shy", "premium": True},  # 👑 NEW HINATA!
        {"id": "f3", "name": "Sakura", "personality": "friendly", "premium": True},
        {"id": "f4", "name": "Yuki", "personality": "possessive_gf", "premium": True},
        {"id": "f5", "name": "Miku", "personality": "possessive_gf", "premium": True},
        {"id": "f6", "name": "Asuna", "personality": "friendly", "premium": True},
        {"id": "f7", "name": "Rem", "personality": "possessive_gf", "premium": True},
        {"id": "f8", "name": "Megumin", "personality": "friendly", "premium": True},
        {"id": "f9", "name": "Zero Two", "personality": "possessive_gf", "premium": True},
        {"id": "f10", "name": "Nezuko", "personality": "friendly", "premium": True},
        {"id": "f11", "name": "Mai", "personality": "possessive_gf", "premium": True}
    ]
    
    MALE_MODELS = [
        {"id": "m1", "name": "Kirito", "personality": "friendly", "premium": True},
        {"id": "m2", "name": "Levi", "personality": "possessive_bf", "premium": True},
        {"id": "m3", "name": "Light", "personality": "possessive_bf", "premium": True},
        {"id": "m4", "name": "Lelouch", "personality": "friendly", "premium": True},
        {"id": "m5", "name": "Naruto", "personality": "friendly", "premium": True},
        {"id": "m6", "name": "Sasuke", "personality": "possessive_bf", "premium": True},
        {"id": "m7", "name": "Gojo", "personality": "friendly", "premium": True},
        {"id": "m8", "name": "Tanjiro", "personality": "friendly", "premium": True},
        {"id": "m9", "name": "Zenitsu", "personality": "possessive_bf", "premium": True},
        {"id": "m10", "name": "Eren", "personality": "possessive_bf", "premium": True}
    ]

# ========== ADMIN MANAGER ==========
class AdminManager:
    def __init__(self):
        self.admins_file = "admins_config.json"
        self.payment_file = "payment_config.json"
        self.load_admins()
        self.load_payment()
    
    def load_admins(self):
        default = {
            "super_admin": [{"email": "sksalamat1324@gmail.com", "name": "Super Admin"}],
            "admins": [{"email": "sahistaparwee@gmail.com", "name": "Admin Sahista"}],
            "moderators": []
        }
        try:
            with open(self.admins_file, "r") as f:
                self.admins = json.load(f)
        except:
            self.admins = default
            self.save_admins()
    
    def save_admins(self):
        with open(self.admins_file, "w") as f:
            json.dump(self.admins, f, indent=2)
    
    def load_payment(self):
        default = {"mode": "demo", "upi_id": ""}
        try:
            with open(self.payment_file, "r") as f:
                self.payment = json.load(f)
        except:
            self.payment = default
            self.save_payment()
    
    def save_payment(self):
        with open(self.payment_file, "w") as f:
            json.dump(self.payment, f, indent=2)
    
    def is_super_admin(self, email):
        for a in self.admins["super_admin"]:
            if a["email"].lower() == email.lower():
                return True
        return False
    
    def is_admin(self, email):
        for a in self.admins["super_admin"]:
            if a["email"].lower() == email.lower():
                return True, "super_admin"
        for a in self.admins["admins"]:
            if a["email"].lower() == email.lower():
                return True, "admin"
        for m in self.admins["moderators"]:
            if m["email"].lower() == email.lower():
                return True, "moderator"
        return False, None
    
    def get_admin_badge(self, email):
        is_ad, level = self.is_admin(email)
        if not is_ad:
            return ""
        return {"super_admin": "👑 SUPER ADMIN", "admin": "🎖️ ADMIN", "moderator": "🛡️ MODERATOR"}.get(level, "")
    
    def get_payment_config(self):
        return self.payment

# ========== MEMORY MANAGER ==========
class MemoryManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.memory = {"user_info": {"name": "Jaan"}, "conversations": []}
        self.load_memory()
    
    def load_memory(self):
        try:
            filename = f"memory_{self.user_id.replace('@', '_')}.json"
            with open(filename, "r") as f:
                self.memory = json.load(f)
        except:
            pass
    
    def save_memory(self):
        try:
            filename = f"memory_{self.user_id.replace('@', '_')}.json"
            with open(filename, "w") as f:
                json.dump(self.memory, f)
        except:
            pass
    
    def add_conversation(self, user_msg, ai_response):
        self.memory["conversations"].append({
            "user": user_msg, "ai": ai_response, "time": datetime.now().isoformat()
        })
        if len(self.memory["conversations"]) > 100:
            self.memory["conversations"] = self.memory["conversations"][-100:]
        self.save_memory()
    
    def detect_mood(self, text):
        happy = ["happy", "good", "love", "khush", "😊", "💖"]
        sad = ["sad", "bad", "upset", "dukhi", "🥺", "😢"]
        text_lower = text.lower()
        if any(w in text_lower for w in happy):
            return "happy"
        elif any(w in text_lower for w in sad):
            return "sad"
        return "neutral"

# ========== PERSONALITY ENGINE ==========
class PersonalityEngine:
    def __init__(self):
        self.current_personality = "friendly"
        self.responses = {
            "friendly": {
                "greeting": ["Hello {name}! Kaise ho? 💖", "Hiii {name}! 🌸"],
                "love": ["Awww! Love you too! 💖", "You're so sweet! 🌸"],
                "default": ["Haan jaan! 💖", "Bolo na! 🌸"]
            },
            "possessive_gf": {
                "greeting": ["Finally aa gaye! 😤💕", "Sirf meri taraf dekho! 🌸"],
                "love": ["Only mine! 😤💕", "I love you more! 🌸"],
                "default": ["Hmm? Bolo! 😤💕", "Sun rahi hoon... 🌸"]
            },
            "possessive_bf": {
                "greeting": ["Kahan thi itni der? 😤💕", "Finally! 🌟"],
                "love": ["Meri ho sirf! 😤💕", "I love you most! 🌟"],
                "default": ["Haan bolo! 😤", "Sun raha hoon... 🌟"]
            },
            "shy": {  # 👑 HINATA KI PERSONALITY!
                "greeting": ["U-umm... hello {name}... 👉👈", "H-hi... 🌸"],
                "love": ["I-I love you too... //>//<// 💖", "T-thank you... *blush* 🌸"],
                "default": ["Umm... h-hai... 👉👈", "K-kya bole...? 💕"]
            }
        }
    
    def set_personality(self, personality):
        if personality in self.responses:
            self.current_personality = personality
    
    def get_response(self, category, name="Jaan"):
        responses = self.responses[self.current_personality].get(category,
                     self.responses[self.current_personality]["default"])
        return random.choice(responses).replace("{name}", name)
    
    def generate_response(self, user_message, user_name="Jaan"):
        msg_lower = user_message.lower()
        if any(w in msg_lower for w in ["hello", "hi", "hey"]):
            return self.get_response("greeting", user_name)
        elif any(w in msg_lower for w in ["love", "pyaar"]):
            return self.get_response("love", user_name)
        elif "time" in msg_lower:
            return f"Time ho raha hai {datetime.now().strftime('%I:%M %p')} ⏰"
        else:
            return self.get_response("default", user_name)

# ========== SUBSCRIPTION MANAGER ==========
class SubscriptionManager:
    def __init__(self, user_email):
        self.user_email = user_email
        self.subscription = {"tier": "free", "expiry": None}
        self.admin_manager = AdminManager()
        self.is_admin, self.admin_level = self.admin_manager.is_admin(user_email)
        if not self.is_admin:
            self.load_subscription()
        else:
            self.subscription = {"tier": "yearly", "expiry": "NEVER"}
    
    def load_subscription(self):
        try:
            filename = f"sub_{self.user_email.replace('@', '_')}.json"
            with open(filename, "r") as f:
                data = json.load(f)
                if data.get("expiry") and data["expiry"] != "NEVER":
                    if datetime.fromisoformat(data["expiry"]) > datetime.now():
                        self.subscription = data
        except:
            pass
    
    def is_premium(self):
        if self.is_admin:
            return True
        if self.subscription["tier"] != "free":
            if self.subscription["expiry"] == "NEVER":
                return True
            if self.subscription["expiry"]:
                return datetime.fromisoformat(self.subscription["expiry"]) > datetime.now()
        return False
    
    def get_available_models(self):
        models = {"female": [], "male": []}
        for m in Config.FEMALE_MODELS:
            if not m["premium"] or self.is_premium():
                models["female"].append(m)
        if self.is_premium():
            for m in Config.MALE_MODELS:
                models["male"].append(m)
        return models

# ========== MAIN APP ==========
class HinaApp:
    def __init__(self):
        self.user_email = "user@example.com"
        self.user_name = "Jaan"
        self.current_model = Config.FEMALE_MODELS[0]
        self.memory = None
        self.personality = None
        self.subscription = None
        self.admin_manager = AdminManager()
        self.voice_manager = VoiceManager()
        self.page = None
        self.chat_display = None
        self.status_text = None
        self.mood_emoji = None
        self.current_mood = "neutral"
    
    def initialize(self, user_email):
        self.user_email = user_email
        self.memory = MemoryManager(user_email)
        self.personality = PersonalityEngine()
        self.subscription = SubscriptionManager(user_email)
        self.user_name = self.memory.memory["user_info"].get("name", "Jaan")
    
    def main(self, page: ft.Page):
        self.page = page
        page.title = Config.APP_NAME
        page.bgcolor = "#FFF0F5"
        page.padding = 15
        page.window.width = 400
        page.window.height = 750
        self.show_login_screen()
    
    def show_login_screen(self):
        self.page.clean()
        email_input = ft.TextField(hint_text="Enter your email", border_color="#FF69B4", width=300)
        
        def login(e):
            if email_input.value:
                self.initialize(email_input.value)
                self.show_main_screen()
        
        self.page.add(
            ft.Column([
                ft.Container(height=100),
                ft.Text("🎀 Hina Assistant", size=32, color="#FF69B4", weight=ft.FontWeight.BOLD),
                ft.Text("Your Cute AI Girlfriend", size=16, color="#FFB6C1"),
                ft.Container(height=50),
                email_input,
                ft.ElevatedButton("🔐 Login", on_click=login, bgcolor="#FF69B4", color="white"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def show_main_screen(self):
        self.page.clean()
        admin_badge = self.admin_manager.get_admin_badge(self.user_email)
        payment_mode = self.admin_manager.get_payment_config()["mode"]
        
        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"🎀 {self.current_model['name']}", size=22, weight=ft.FontWeight.BOLD, color="#FF69B4"),
                    ft.Text(f"{admin_badge}  {payment_mode.upper()} MODE", size=10, color="#FFB6C1"),
                ]),
                ft.PopupMenuButton(items=[
                    ft.PopupMenuItem(text="👥 Models", on_click=self.show_models),
                    ft.PopupMenuItem(text="🎭 Personality", on_click=self.show_personality),
                    ft.PopupMenuItem(text="💎 Premium", on_click=self.show_premium),
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            margin=ft.margin.only(bottom=10)
        )
        
        avatar = ft.Container(
            content=ft.Text("🎀", size=70),
            width=120, height=120, bgcolor="#FFE4E9", border_radius=60,
            alignment=ft.alignment.center, on_click=self.pet_avatar
        )
        
        self.status_text = ft.Text(f"💖 Hello {self.user_name}!", size=14, color="#FF69B4")
        self.mood_emoji = ft.Text("💖", size=20)
        self.chat_display = ft.Column(scroll=ft.ScrollMode.AUTO, height=350, spacing=8, auto_scroll=True)
        
        welcome = self.personality.get_response("greeting", self.user_name)
        self.add_ai_message(welcome)
        
        quick_actions = ft.Row([
            ft.Chip(label=ft.Text("❤️ Love"), on_click=lambda e: self.quick_message("I love you!")),
            ft.Chip(label=ft.Text("⏰ Time"), on_click=lambda e: self.quick_message("Time kya hua?")),
            ft.Chip(label=ft.Text("😂 Joke"), on_click=lambda e: self.quick_message("Joke sunao")),
        ], wrap=True, spacing=5)
        
        msg_input = ft.TextField(
            hint_text=f"Message {self.current_model['name']}... 💕",
            border_color="#FF69B4", multiline=False,
            on_submit=lambda e: self.send_message(e, msg_input)
        )
        send_btn = ft.IconButton(icon=ft.icons.SEND, icon_color="#FF69B4", on_click=lambda e: self.send_message(e, msg_input))
        
        self.page.add(
            header,
            ft.Row([avatar, self.mood_emoji], alignment=ft.MainAxisAlignment.CENTER),
            self.status_text,
            ft.Divider(height=8, color="transparent"),
            self.chat_display,
            quick_actions,
            ft.Divider(height=8, color="transparent"),
            ft.Row([msg_input, send_btn], spacing=8),
        )
    
    def add_user_message(self, message):
        self.chat_display.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("👤 You", size=11, color="#8B4513", weight=ft.FontWeight.BOLD),
                    ft.Text(message, size=14, color="#8B4513"),
                ]),
                bgcolor="#F5F5DC", border_radius=15, padding=10,
                margin=ft.margin.only(left=50, bottom=5)
            )
        )
    
    def add_ai_message(self, message):
        self.chat_display.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(f"🎀 {self.current_model['name']}", size=11, color="#FF69B4", weight=ft.FontWeight.BOLD),
                    ft.Text(message, size=14, color="#FF69B4"),
                ]),
                bgcolor="#FFE4E9", border_radius=15, padding=10,
                margin=ft.margin.only(right=50, bottom=5)
            )
        )
        self.page.update()
        self.voice_manager.speak(message, emotion=self.current_mood)
    
    def send_message(self, e, msg_input):
        if not msg_input.value:
            return
        user_msg = msg_input.value
        msg_input.value = ""
        self.add_user_message(user_msg)
        response = self.personality.generate_response(user_msg, self.user_name)
        self.memory.add_conversation(user_msg, response)
        self.current_mood = self.memory.detect_mood(user_msg)
        emojis = {"happy": "😊💖", "sad": "🥺", "neutral": "💕"}
        self.mood_emoji.value = emojis.get(self.current_mood, "💖")
        self.add_ai_message(response)
    
    def quick_message(self, message):
        self.add_user_message(message)
        response = self.personality.generate_response(message, self.user_name)
        self.add_ai_message(response)
    
    def pet_avatar(self, e):
        self.status_text.value = random.choice(["Awww! 😊💖", "Hehe! 🌸", "More! 🎀"])
        self.page.update()
    
    def show_models(self, e):
        models = self.subscription.get_available_models()
        content = ft.Column(spacing=5, height=300, scroll=ft.ScrollMode.AUTO)
        content.controls.append(ft.Text("🎀 Female Models", weight=ft.FontWeight.BOLD, color="#FF69B4"))
        for m in models["female"]:
            badge = " 💎" if m["premium"] else " 🆓"
            content.controls.append(ft.ListTile(
                title=ft.Text(m["name"] + badge),
                on_click=lambda e, model=m: self.select_model(model)
            ))
        if models["male"]:
            content.controls.append(ft.Text("🌟 Male Models", weight=ft.FontWeight.BOLD, color="#4169E1"))
            for m in models["male"]:
                content.controls.append(ft.ListTile(
                    title=ft.Text(m["name"] + " 💎"),
                    on_click=lambda e, model=m: self.select_model(model)
                ))
        self.show_dialog("👥 Models", content)
    
    def select_model(self, model):
        if model["premium"] and not self.subscription.is_premium():
            self.show_premium_required()
            return
        self.current_model = model
        self.personality.set_personality(model["personality"])
        self.close_dialog()
        self.status_text.value = f"🎀 Switched to {model['name']}!"
        self.page.update()
    
    def show_personality(self, e):
        if not self.subscription.is_premium():
            self.show_premium_required()
            return
        def set_personality(p):
            self.personality.set_personality(p)
            self.close_dialog()
            self.status_text.value = f"Personality: {p} 💕"
            self.page.update()
        content = ft.Column([
            ft.ListTile(title=ft.Text("💖 Friendly"), on_click=lambda e: set_personality("friendly")),
            ft.ListTile(title=ft.Text("😤 Possessive GF"), on_click=lambda e: set_personality("possessive_gf")),
            ft.ListTile(title=ft.Text("😤 Possessive BF"), on_click=lambda e: set_personality("possessive_bf")),
            ft.ListTile(title=ft.Text("👉👈 Shy (Hinata)"), on_click=lambda e: set_personality("shy")),
        ], height=200)
        self.show_dialog("🎭 Personality", content)
    
    def show_premium(self, e):
        content = ft.Column(spacing=5, height=300)
        if self.subscription.is_admin:
            content.controls.append(ft.Text(f"👑 {self.admin_manager.get_admin_badge(self.user_email)}", size=16, color="#FFD700"))
            content.controls.append(ft.Text("✨ Lifetime FREE ✨", color="#4CAF50"))
            content.controls.append(ft.Divider())
        for tier, plan in Config.PLANS.items():
            if tier != "free":
                content.controls.append(ft.ListTile(
                    title=ft.Text(f"{plan['name']} - {plan['days']} days"),
                    subtitle=ft.Text(f"₹{plan['price']}"),
                ))
        self.show_dialog("💎 Premium", content)
    
    def show_premium_required(self):
        self.show_dialog("💎 Premium Required", ft.Text("This feature requires premium!"))
    
    def show_dialog(self, title, content):
        dlg = ft.AlertDialog(title=ft.Text(title), content=content,
                            actions=[ft.TextButton("Close", on_click=lambda e: self.close_dialog())])
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def close_dialog(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.dialog = None
            self.page.update()

def main(page: ft.Page):
    HinaApp().main(page)

if __name__ == "__main__":
    ft.app(target=main)
