#!/usr/bin/env python3
"""
Crownit Automation Bot - Web Service Version
Deploy on Render Web Service (FREE Tier)
"""

import os
import sys
import json
import time
import random
import logging
import requests
import base64
import urllib.parse
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8575561951:AAHC8G5vGG24_v_W9sslfU38pQdVt0G8GMA')

# Data pools
INDIAN_MALE = [
    "Rakesh", "Mukesh", "Amit", "Vijay", "Suresh", "Rajesh", "Deepak",
    "Sanjay", "Anil", "Sunil", "Manish", "Rahul", "Arun", "Nitin",
    "Pradeep", "Vikram", "Karan", "Rohan", "Aditya", "Ajay", "Vivek",
    "Sachin", "Gaurav", "Harsh", "Ravi", "Mohan", "Shyam", "Anand",
    "Prakash", "Narendra", "Dinesh", "Mahesh"
]

INDIAN_FEMALE = [
    "Anita", "Priya", "Neha", "Pooja", "Sunita", "Rekha", "Kavita",
    "Shweta", "Divya", "Nisha", "Ritu", "Sangeeta", "Manisha", "Rashmi",
    "Swati", "Preeti", "Geeta", "Seema", "Asha", "Deepika", "Laxmi",
    "Kiran", "Meena", "Radha", "Sita", "Anjali", "Nandini", "Priyanka",
    "Kajal", "Simran", "Sapna", "Jyoti", "Mamta", "Komal"
]

INDIAN_LAST = [
    "Kumar", "Singh", "Sharma", "Verma", "Gupta", "Patel", "Reddy",
    "Joshi", "Mishra", "Pandey", "Raj", "Choudhary", "Saha", "Das",
    "Bose", "Sen", "Ghosh", "Biswas", "Nair", "Menon", "Iyer", "Rao",
    "Naidu", "Pillai", "Jain", "Agarwal", "Khatri", "Thakur", "Yadav",
    "Kaur", "Mehta", "Desai", "Shah", "Kapoor", "Malhotra"
]

SURVEY_RESPONSES = [
    "I find this product useful for daily use.",
    "The quality meets my expectations.",
    "I am satisfied with the service provided.",
    "The experience was good overall.",
    "I would recommend this to others.",
    "The delivery was on time and packaging was good.",
    "Good value for money.",
    "The interface is user friendly and easy to navigate.",
    "I have been using this for a while and it works well.",
    "Customer support was helpful in resolving my query."
]

class CrownitAutomation:
    """Complete Crownit automation class"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base = "https://feedback.crownit.in"
        self.node = "https://nodeserver.crownit.in"
        
        self.user_id = None
        self.session_id = None
        self.phone = None
        self.otp = None
        self.first_name = None
        self.full_name = None
        self.gender = None
        self.dob_display = None
        self.dob_iso = None
        
        self.status = {
            "profile": "⏳ Pending",
            "device": "⏳ Pending",
            "otp": "⏳ Pending",
            "location": "⏳ Pending",
            "surveys": "⏳ Pending",
            "scratch": "⏳ Pending",
            "redemption": "⏳ Pending"
        }
        
        self.survey_count = 0
        self.reward_amount = 0
        self.redemption_link = None
        self.error_message = None
        self.scratch_reward = None
        
        self._setup_headers()
        self._set_auth("6667", "759b064f-381d-11e5-810b-0286c96d2641")
    
    def _setup_headers(self):
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-IN,en-GB;q=0.9",
            "Origin": self.base,
            "Content-Type": "application/json",
        })
    
    def _set_auth(self, uid, sid):
        self.user_id = uid
        self.session_id = sid
        raw = f"{uid}:{sid}"
        b64 = base64.b64encode(raw.encode()).decode()
        self.session.headers.update({"Authorization": f"Basic {b64}"})
    
    def _api(self, method, path, json_data=None, headers=None):
        url = f"{self.base}{path}"
        try:
            r = self.session.request(method, url, json=json_data, headers=headers or {}, timeout=30)
            return r.json()
        except Exception as e:
            logger.error(f"API Error: {e}")
            return {"error": str(e)}
    
    def generate_profile(self):
        """Generate random Indian profile"""
        gender_key = random.choice(["male", "female"])
        first = random.choice(INDIAN_MALE if gender_key == "male" else INDIAN_FEMALE)
        last = random.choice(INDIAN_LAST)
        
        self.first_name = first
        self.full_name = f"{first} {last}"
        self.gender = "Male" if gender_key == "male" else "Female"
        
        today = datetime.now()
        max_dob = today - timedelta(days=20*365)
        min_dob = today - timedelta(days=55*365)
        dob = min_dob + timedelta(seconds=random.randint(0, int((max_dob - min_dob).total_seconds())))
        
        self.dob_display = dob.strftime("%d-%m-%Y")
        self.dob_iso = dob.strftime("%Y-%m-%d")
        
        self.status["profile"] = "✅ Done"
        return {
            "name": self.full_name,
            "gender": self.gender,
            "dob": self.dob_display
        }
    
    def register_device(self):
        """Register device"""
        params = {
            "isDeviceRooted": "0",
            "macAddress": "",
            "campaignType": "na",
            "manufacturerName": "Unknown",
            "emailId": "na",
            "deviceVersion": self.session.headers.get("User-Agent", ""),
            "modelNo": "PWA",
            "deviceId": "00000",
            "allAccounts": "",
            "screenName": "phoneScreen",
        }
        body = urllib.parse.urlencode(params)
        auth_empty = base64.b64encode(b":").decode()
        url = f"{self.base}/api/devices"
        
        try:
            r = self.session.post(url, data=body, headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {auth_empty}",
                "Api-Version": "71",
                "platform": "android",
            }, timeout=30)
            data = r.json()
            device_id = str(data.get("id", "10375346"))
            self.status["device"] = "✅ Done"
            return device_id
        except Exception as e:
            logger.error(f"Device registration error: {e}")
            self.status["device"] = "❌ Failed"
            return "10375346"
    
    def send_otp(self, reg_id):
        """Send OTP to phone"""
        resp = self._api("POST", "/api/users", {
            "phoneNo": self.phone,
            "deviceId": "00000",
            "registrationStatusId": reg_id
        }, headers={"app-type": "pwa"})
        
        if resp.get("responseCode") == 1:
            ud = resp.get("userDetails", {})
            return ud.get("id"), reg_id
        return None, None
    
    def verify_otp(self, otp, uid, reg_id):
        """Verify OTP"""
        resp = self._api("PUT", f"/api/users/{self.phone}/otp", {
            "phoneNo": self.phone,
            "deviceId": "00000",
            "registrationStatusId": reg_id,
            "otp": otp,
            "userId": self.phone,
            "api_version": "71"
        })
        
        if resp.get("responseCode") == 1:
            ud = resp.get("userDetails", {})
            sid = ud.get("sessionId")
            self._set_auth(uid, sid)
            self.status["otp"] = "✅ Done"
            return sid
        self.status["otp"] = "❌ Failed"
        return None
    
    def update_profile(self):
        """Update profile with location"""
        # Update city
        self._api("PUT", "/api/user/profile", {
            "city": "Bihar Sharif",
            "cityId": 1134
        })
        # Update milestone
        self._api("POST", "/api/user/milestone", {})
        self.status["location"] = "✅ Done"
        return True
    
    def get_surveys(self):
        """Get eligible surveys"""
        resp = self._api("POST", "/rer/pwa/eligible", {})
        surveys = resp.get("result", [])
        if surveys:
            self.survey_count = len(surveys)
        return surveys
    
    def take_survey(self, survey):
        """Take a single survey"""
        link = survey.get("link", "")
        sid = survey.get("survey_id", "")
        container_id = survey.get("container_id", "")
        
        if not link:
            return None
        
        # Start survey session
        web_link = f"fb{str(int(time.time() * 1000))}"
        
        session_payload = {
            "uid": "",
            "targetLanguage": "",
            "extraParams": {
                "fingerprintnew": int(time.time()),
                "clientscreen": {"availHeight": 720, "availWidth": 1366}
            },
            "referer": self.base + "/lite/onboarding",
            "autoAnswer": {},
            "preview": "published",
            "surveyLink": link,
            "webLink": web_link,
            "cookies": {"browserInfo": self.session.headers.get("User-Agent", "")},
            "channel": container_id or "default",
            "unique": str(int(time.time() * 1000)),
            "survey_source": "pwa",
            "utm_source": "pwa",
            "utm_medium": "registration",
            "sid": web_link,
            "isShowBackClicked": "false",
            "questionId": 1068,
            "options": [{"id": "-1", "text": ""}],
            "unselect": [],
            "otpGet": True,
            "seqNo": -1
        }
        
        session_resp = self._api("POST", "/api/survey/session", session_payload)
        survey_uid = session_resp.get("uid")
        
        if not survey_uid:
            return None
        
        # Answer questions
        question_payload = dict(session_payload)
        question_payload["uid"] = survey_uid
        for key in ["questionId", "options", "unselect", "otpGet", "seqNo", "isShowBackClicked"]:
            question_payload.pop(key, None)
        
        answered = 0
        for q_num in range(30):
            q_resp = self._api("POST", "/api/survey/smart/question", question_payload)
            
            if not q_resp or q_resp.get("ended") or q_resp.get("terminated"):
                break
            
            question_data = q_resp.get("question", {})
            qid = question_data.get("questionId")
            qtype = str(question_data.get("type", ""))
            
            if not qid:
                break
            
            # Generate answer
            options = question_data.get("choice", [])
            valid_opts = [o for o in options if isinstance(o, dict) and o.get("id")]
            
            answer_options = []
            if qtype in ("5", "text", "input", "textarea", "number", "T"):
                text = random.choice(SURVEY_RESPONSES)
                title = str(question_data.get("text", "")).lower()
                
                if "name" in title:
                    text = self.full_name
                elif "email" in title:
                    text = f"{self.first_name.lower()}{random.randint(1,999)}@gmail.com"
                elif "age" in title:
                    text = str(datetime.now().year - int(self.dob_iso[:4]))
                elif "city" in title:
                    text = "Bihar Sharif"
                elif "phone" in title:
                    text = self.phone
                
                if valid_opts:
                    opt = valid_opts[0]
                    misc = opt.get("misc", {})
                    if isinstance(misc, dict):
                        misc["rank"] = text
                    answer_options.append({
                        "id": str(opt["id"]),
                        "text": opt.get("text", "Please enter"),
                        "misc": misc
                    })
                else:
                    answer_options.append({
                        "id": str(int(time.time())),
                        "text": "Please enter",
                        "misc": {"rank": text}
                    })
            elif valid_opts:
                opt = random.choice(valid_opts)
                answer_options.append({
                    "id": str(opt["id"]),
                    "text": opt.get("text", ""),
                    "misc": opt.get("misc", {})
                })
            else:
                answer_options.append({"id": "-1", "text": "Skipped", "misc": {}})
            
            answer = {
                "uid": survey_uid,
                "options": answer_options,
                "unselect": [],
                "questionId": int(qid),
                "seqNo": q_num + 1,
                "type": qtype,
                "extraParams": {"fingerprintnew": int(time.time() / 2)},
                "autoAnswer": {},
                "preview": "published",
                "surveyLink": "",
                "linkReceived": web_link,
                "webLink": web_link,
                "survey_source": "pwa",
                "utm_source": "pwa",
                "utm_medium": "registration",
                "channel": container_id or "default",
                "sid": web_link,
                "unique": str(int(time.time() * 1000)),
                "cookies": {
                    "browserInfo": self.session.headers.get("User-Agent", ""),
                    f"weblink_cookies{survey_uid}": web_link
                }
            }
            
            a_resp = self._api("POST", "/api/survey/smart/answer", answer)
            if a_resp.get("responseCode") == 1:
                answered += 1
                if a_resp.get("ended") or a_resp.get("terminated"):
                    break
                time.sleep(random.uniform(3, 6))
        
        return sid if answered > 0 else None
    
    def claim_rewards(self, survey_id=None):
        """Claim scratch cards and redeem"""
        # Check for scratch cards
        resp = self._api("GET", "/api/user/rewards?type=all&pageNo=1&source=pwa", None)
        pending = resp.get("pendingCards", {})
        token = pending.get("token")
        pending_count = pending.get("pendingCount", 0)
        
        if pending_count > 0 and token and survey_id:
            scratch_resp = self._api("POST", "/api/scratch", {
                "surveyId": str(survey_id),
                "token": token
            })
            
            if scratch_resp.get("responseCode") == 1:
                rewards = scratch_resp.get("result", {}).get("allRewards", {})
                reward_details = rewards.get("rewardDetails", [])
                
                if reward_details:
                    reward_id = reward_details[0].get("reward_id")
                    rid = rewards.get("rid")
                    amount = reward_details[0].get("amount", 0)
                    
                    claim_resp = self._api("POST", "/api/scratch/claim", {
                        "surveyId": str(survey_id),
                        "rewardId": reward_id,
                        "rid": rid,
                        "token": token
                    })
                    
                    if claim_resp.get("responseCode") == 1:
                        self.reward_amount = amount
                        self.scratch_reward = reward_details[0]
                        self.status["scratch"] = f"✅ ₹{amount}"
                        self.status["redemption"] = "🔄 Processing"
        
        # Try to redeem
        if self.reward_amount > 0:
            balance_resp = self._api("POST", "/api/wallet/balance", {})
            balance = balance_resp.get("balance", 0)
            
            if balance > 0:
                options_resp = self._api("POST", "/api/redeem/options", {})
                options = options_resp.get("result", [])
                
                if options:
                    target = None
                    for opt in options:
                        name = str(opt.get("name", "")).lower()
                        if "amazon" in name:
                            target = opt
                            break
                        if "10" in str(opt.get("value", "")):
                            target = opt
                    
                    if not target:
                        target = options[0]
                    
                    reward_id = target.get("id") or target.get("optionId") or target.get("reward_id")
                    if reward_id:
                        red_resp = self._api("POST", "/api/redeem/submit", {
                            "rewardId": reward_id,
                            "phone": self.phone
                        })
                        
                        if red_resp.get("responseCode") == 1:
                            self.redemption_link = red_resp.get("redemptionLink") or red_resp.get("link")
                            self.status["redemption"] = "✅ Redeemed"
                            return
        
        if self.status["redemption"] == "🔄 Processing":
            self.status["redemption"] = "❌ Failed"
    
    def run_workflow(self, phone, otp):
        """Run complete workflow"""
        self.phone = phone
        self.otp = otp
        self.error_message = None
        
        try:
            # Step 1: Generate profile
            self.generate_profile()
            
            # Step 2: Register device
            reg_id = self.register_device()
            
            # Step 3: Send OTP
            uid, reg_id = self.send_otp(reg_id)
            if not uid:
                self.error_message = "Failed to send OTP"
                self.status["otp"] = "❌ Failed"
                return self.get_dashboard()
            
            # Step 4: Verify OTP
            sid = self.verify_otp(otp, uid, reg_id)
            if not sid:
                self.error_message = "OTP verification failed"
                return self.get_dashboard()
            
            # Step 5: Update profile
            self.update_profile()
            
            # Step 6: Get and take surveys
            surveys = self.get_surveys()
            survey_id = None
            if surveys:
                survey_taken = False
                for survey in surveys[:3]:
                    survey_id = self.take_survey(survey)
                    if survey_id:
                        survey_taken = True
                        break
                
                if survey_taken:
                    self.status["surveys"] = "✅ Done"
                else:
                    self.status["surveys"] = "❌ Failed"
            else:
                self.status["surveys"] = "ℹ️ No surveys"
                self.error_message = "No surveys eligible for this number at the moment."
            
            # Step 7: Claim rewards
            if survey_id:
                self.claim_rewards(survey_id)
            else:
                self.status["scratch"] = "❌ Failed (No survey)"
                self.status["redemption"] = "❌ Failed (No survey)"
            
        except Exception as e:
            self.error_message = str(e)
            logger.error(f"Workflow error: {e}")
        
        return self.get_dashboard()
    
    def get_dashboard(self):
        """Generate dashboard display"""
        profile_info = f"👤 {self.full_name} ({self.gender}, {self.dob_display})" if self.full_name else "👤 Not generated"
        phone_info = f"📞 {self.phone}" if self.phone else "📞 Not provided"
        
        dashboard = f"""
👑 *CROWNIT AUTOMATION DASHBOARD*
━━━━━━━━━━━━━━━━━━━━
{profile_info}
{phone_info}
━━━━━━━━━━━━━━━━━━━━
👤 Profile Generation:  {self.status.get('profile', '⏳ Pending')}
📱 Device Registration: {self.status.get('device', '⏳ Pending')}
🔑 OTP Verification:   {self.status.get('otp', '⏳ Pending')}
📍 Setting Location:    {self.status.get('location', '⏳ Pending')}
📋 Survey Automation:   {self.status.get('surveys', '⏳ Pending')}
⏳ Scratch Card Claim:  {self.status.get('scratch', '⏳ Pending')}
🎁 Voucher Redemption:  {self.status.get('redemption', '⏳ Pending')}
━━━━━━━━━━━━━━━━━━━━
"""
        
        if self.reward_amount > 0:
            dashboard += f"💰 *Reward Amount:* ₹{self.reward_amount}\n"
        
        if self.scratch_reward:
            dashboard += f"🎁 *Scratch Reward:* {json.dumps(self.scratch_reward, indent=2)}\n"
        
        if self.redemption_link:
            dashboard += f"\n🔗 *Redemption Link:*\n`{self.redemption_link}`\n"
        
        if self.survey_count > 0:
            dashboard += f"📊 *Surveys Found:* {self.survey_count}\n"
        
        if self.error_message:
            dashboard += f"""
━━━━━━━━━━━━━━━━━━━━
❌ *Error Encountered:*
{self.error_message}
"""
        
        dashboard += """
━━━━━━━━━━━━━━━━━━━━
🔄 Use /start to try again.
"""
        
        return dashboard

# ==================== TELEGRAM BOT HANDLERS ====================

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    user_data[user_id] = {}
    
    keyboard = [
        [InlineKeyboardButton("🚀 Start Automation", callback_data='start_bot')],
        [InlineKeyboardButton("📊 Check Status", callback_data='status')],
        [InlineKeyboardButton("ℹ️ Help / Guide", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🤖 *Crownit Automation Bot*
━━━━━━━━━━━━━━━━━━━━

I will help you automate Crownit tasks automatically!

📌 *How it works:*
1️⃣ Send your 10-digit phone number
2️⃣ Receive OTP on your phone
3️⃣ Send OTP to me
4️⃣ I'll complete everything automatically

⚡ *Features:*
• Random Indian profile generation
• Auto device registration
• OTP verification
• Auto survey completion
• Scratch card claiming
• Reward redemption

Click the button below to start!
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == 'start_bot':
        await query.edit_message_text(
            "📱 Please send your 10-digit phone number.\n\n"
            "Example: 9876543210\n\n"
            "Type /cancel to cancel."
        )
        user_data[user_id]['state'] = 'waiting_phone'
    
    elif query.data == 'status':
        if user_id in user_data and 'dashboard' in user_data[user_id]:
            await query.edit_message_text(
                user_data[user_id]['dashboard'],
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "ℹ️ No active session. Send /start to begin.",
                parse_mode='Markdown'
            )
    
    elif query.data == 'help':
        await query.edit_message_text(
            "📌 *Help Center*\n\n"
            "🔹 *Commands:*\n"
            "/start - Start the bot\n"
            "/cancel - Cancel current operation\n"
            "/status - Check current status\n\n"
            "🔹 *How to use:*\n"
            "1. Send your phone number\n"
            "2. I'll send OTP to your phone\n"
            "3. Send the OTP back to me\n"
            "4. I'll handle everything else\n\n"
            "🔹 *Features:*\n"
            "• Automatic profile generation\n"
            "• OTP verification\n"
            "• Survey automation\n"
            "• Reward claiming\n"
            "• Voucher redemption\n\n"
            "Made with ❤️ for Crownit",
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in user_data:
        user_data[user_id] = {}
    
    state = user_data[user_id].get('state', '')
    
    if text == '/cancel':
        user_data[user_id] = {}
        await update.message.reply_text(
            "❌ Operation cancelled.\n"
            "Send /start to begin again."
        )
        return
    
    if text == '/status':
        if 'dashboard' in user_data[user_id]:
            await update.message.reply_text(
                user_data[user_id]['dashboard'],
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("ℹ️ No active session. Send /start to begin.")
        return
    
    if state == 'waiting_phone':
        # Validate phone number
        if not re.match(r'^[6-9]\d{9}$', text):
            await update.message.reply_text(
                "❌ Invalid phone number!\n\n"
                "Please send a valid 10-digit number.\n"
                "Example: 9876543210"
            )
            return
        
        user_data[user_id]['phone'] = text
        
        # Initialize Crownit bot
        await update.message.reply_text(
            "⏳ Initializing Crownit automation...\n"
            "Please wait..."
        )
        
        crownit = CrownitAutomation()
        crownit.phone = text
        reg_id = crownit.register_device()
        uid, reg_id = crownit.send_otp(reg_id)
        
        if uid:
            user_data[user_id]['uid'] = uid
            user_data[user_id]['reg_id'] = reg_id
            user_data[user_id]['crownit'] = crownit
            
            await update.message.reply_text(
                f"✅ OTP sent to {text}!\n\n"
                "📱 Please check your phone and send the OTP here.\n"
                "Example: 123456\n\n"
                "Type /cancel to cancel."
            )
            user_data[user_id]['state'] = 'waiting_otp'
        else:
            await update.message.reply_text(
                "❌ Failed to send OTP.\n\n"
                "Possible reasons:\n"
                "• Invalid phone number\n"
                "• Network issues\n"
                "• Server down\n\n"
                "Send /start to try again."
            )
            user_data[user_id] = {}
    
    elif state == 'waiting_otp':
        # Validate OTP
        if not re.match(r'^\d{4,6}$', text):
            await update.message.reply_text(
                "❌ Invalid OTP!\n\n"
                "Please send a 4-6 digit OTP.\n"
                "Example: 123456"
            )
            return
        
        otp = text
        phone = user_data[user_id]['phone']
        crownit = user_data[user_id]['crownit']
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            "⏳ Processing your request...\n"
            "This may take 2-3 minutes.\n\n"
            "⏳ Please wait while I complete all tasks..."
        )
        
        try:
            # Run workflow
            dashboard = crownit.run_workflow(phone, otp)
            
            # Save dashboard for status check
            user_data[user_id]['dashboard'] = dashboard
            
            # Send final dashboard
            await processing_msg.edit_text(
                dashboard,
                parse_mode='Markdown'
            )
            
            # Clean up
            user_data[user_id] = {'dashboard': dashboard}
            
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            await processing_msg.edit_text(
                f"❌ An error occurred:\n{str(e)}\n\n"
                "Send /start to try again."
            )
            user_data[user_id] = {}

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred.\n"
            "Send /start to try again."
        )

# ==================== MAIN ====================

def main():
    """Main entry point"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # For Render Web Service
    PORT = int(os.environ.get('PORT', 10000))
    
    print(f"🤖 Crownit Bot is starting on port {PORT}...")
    print(f"Bot token: {BOT_TOKEN[:20]}...")
    
    # Use webhook for web service
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost')}"
    )

if __name__ == "__main__":
    main()
