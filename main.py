import praw
import smtplib
from email.message import EmailMessage
import os
import openai
from datetime import datetime

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_CLIENT_SECRET'],
    user_agent=os.environ['REDDIT_USER_AGENT'],
    username=os.environ['REDDIT_USERNAME'],
    password=os.environ['REDDIT_PASSWORD']
)

# OpenAI API Key
openai.api_key = os.environ['OPENAI_API_KEY']

# List of subreddits grouped by niche
subreddits = {
    "Science": ["askscience"],
    "Health": ["AskDocs"],
    "Fitness": ["bodyweightfitness"],
    "Life": ["LifeProTips"],
    "Cooking": ["Cooking"],
    "Tech": ["technology"]
}

# Generate GPT Answer
def generate_answer(question):
    prompt = f"Answer the following question in 1-2 lines: {question}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Error generating answer: {e})"

# Translate using OpenAI
def translate(text, language):
    prompt = f"Translate this into {language}: {text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a translator."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Error translating to {language}: {e})"

# Build the email content
digest = ["🔥 DailyAnswerDose 🔥\n"]
for niche, subs in subreddits.items():
    digest.append(f"🧠 Niche: {niche}\n{'-'*40}")
    for sub in subs:
        try:
            posts = [p for p in reddit.subreddit(sub).hot(limit=15) if p.title.endswith("?")]
            posts.sort(key=lambda p: p.score, reverse=True)
            for post in posts[:2]:
                q = post.title
                en = generate_answer(q)
                hi = translate(en, "Hindi")
                mr = translate(en, "Marathi")
                link = f"https://www.reddit.com{post.permalink}"
                digest.append(f"\n❓ {q}\n🇬🇧 {en}\n🇮🇳 {hi}\n🇲🇭 {mr}\n👍 {post.score} | 🔗 {link}\n")
        except Exception as e:
            digest.append(f"⚠️ Error fetching r/{sub}: {e}")

# Email setup
msg = EmailMessage()
msg["Subject"] = f"📰 DailyAnswerDose | {datetime.now().strftime('%d %b %Y')}"
msg["From"] = os.environ['EMAIL_FROM']
msg["To"] = os.environ['EMAIL_TO']
msg.set_content("\n\n".join(digest))

# Send email
with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
    smtp.starttls()
    smtp.login(os.environ['EMAIL_FROM'], os.environ['EMAIL_PASSWORD'])
    smtp.send_message(msg)

print("✅ Email sent with DailyAnswerDose!")
