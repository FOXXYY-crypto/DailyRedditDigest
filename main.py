import praw
import smtplib
import ssl
from email.message import EmailMessage
import os

# --- Reddit credentials from GitHub Actions environment variables ---
reddit = praw.Reddit(
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
    user_agent="script:QuestScraper:v1.0 (by u/{})".format(os.environ["USERNAME"]),
    username=os.environ["USERNAME"],
    password=os.environ["PASSWORD"]
)

# --- Subreddits by niche ---
subreddits = {
    "Science": ["askscience", "science", "EverythingScience"],
    "Health": ["Health", "AskDocs"],
    "Fitness": ["fitness"],
    "Cooking": ["Cooking", "EatCheapAndHealthy"],
    "Tech": ["technology", "Futurology", "singularity"],
    "Life Tips": ["LifeProTips", "NoStupidQuestions", "TooAfraidToAsk"]
}

# --- Collect top questions ---
email_content = "🔥 Daily Reddit Digest 🔥\n\n"
for niche, subs in subreddits.items():
    email_content += f"🧠 Niche: {niche}\n" + "-"*40 + "\n"
    questions = []
    for sub in subs:
        try:
            for post in reddit.subreddit(sub).hot(limit=30):
                if post.title.endswith("?"):
                    questions.append((post.title, post.score, sub, f"https://www.reddit.com{post.permalink}"))
        except Exception as e:
            email_content += f"❌ Error reading r/{sub}: {e}\n"

    # Sort and pick top 2
    questions = sorted(questions, key=lambda x: x[1], reverse=True)[:2]
    for q in questions:
        email_content += f"❓ {q[0]}\n👍 {q[1]} upvotes | r/{q[2]}\n🔗 {q[3]}\n\n"
    email_content += "\n"

# --- Email configuration ---
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_RECEIVER = os.environ["EMAIL_RECEIVER"]
EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = int(os.environ["EMAIL_PORT"])

# --- Send Email ---
msg = EmailMessage()
msg.set_content(email_content)
msg["Subject"] = "🔥 Your Daily Reddit Questions Digest"
msg["From"] = EMAIL_ADDRESS
msg["To"] = EMAIL_RECEIVER

context = ssl.create_default_context()
with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
    server.starttls(context=context)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)

print("✅ Email sent successfully!")
