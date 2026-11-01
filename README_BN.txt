CINEBOX 24 — Telegram Video Bot starter

ফিচার:
- মুভি, গান, নাটক, ভাইরাল ভিডিও, শর্ট ভিডিও ক্যাটাগরি
- Admin /addvideo দিয়ে কনটেন্ট যোগ
- Telegram file_id সংরক্ষণ করে পরে আবার পাঠায় (ভিডিও ফাইল আলাদা সার্ভারে রাখতে হয় না)
- /stats দিয়ে ইউজার ও ভিডিও সংখ্যা
- /setad দিয়ে বিজ্ঞাপন লিংক

গুরুত্বপূর্ণ সীমাবদ্ধতা:
1) বটটি এখনো Telegram-এ চালু করা হয়নি। চালাতে BotFather token ও Admin Telegram numeric ID লাগবে।
2) TOKEN কাউকে চ্যাটে পাঠাবেন না; হোস্টিংয়ের Secret/Environment Variables-এ রাখবেন।
3) বিজ্ঞাপন লিংক খোলা হয়েছে কি না Telegram Bot API দিয়ে নির্ভরযোগ্যভাবে যাচাই করা যায় না। এখানে Continue বোতামটি স্ব-ঘোষণাভিত্তিক, বিজ্ঞাপন দেখা নিশ্চিত করে না। বিজ্ঞাপন নেটওয়ার্কের নিয়ম মেনে tracking/verification ব্যবস্থা আলাদাভাবে যুক্ত করতে হবে।
4) ফ্রি হোস্টিং ২৪/৭ চালু থাকবে—এ নিশ্চয়তা নেই। Free tier ঘুমিয়ে যেতে পারে/সীমা থাকতে পারে।
5) কপিরাইট অনুমতি আছে এমন ভিডিও/গান/নাটকই আপলোড করুন।

চালানোর জন্য (যিনি সেটআপ করবেন):
- Python 3.10+
- pip install -r requirements.txt
- Environment variables:
  BOT_TOKEN = BotFather থেকে পাওয়া token
  ADMIN_ID = Admin-এর numeric Telegram user ID
  AD_URL = (ঐচ্ছিক) বিজ্ঞাপন লিংক
- python bot.py

Admin ব্যবহার:
- /admin
- /addvideo
- ক্যাটাগরি বাছুন
- ভিডিওর নাম লিখুন
- ভিডিও পাঠান
- /stats
- /setad https://your-ad-link.example

নোট: এটি প্রাথমিক ভিত্তি/স্টার্টার। Production চালুর আগে hosting, backup, rate limit, নিরাপত্তা এবং প্রকৃত বিজ্ঞাপন নেটওয়ার্কের tracking যুক্ত করা দরকার।
