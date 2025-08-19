import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


API_KEY = os.getenv("API_KEY")

MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")
URL = os.getenv
to_emails = [ "angelmiracles90@gmail.com","exercisespython@gmail.com"]

params = {
    "function": "NEWS_SENTIMENT",
    "topics": "financial_markets",
    "apikey": API_KEY,
    "limit": 5,
    "sort": "RELEVANCE"
}

# # === FETCH NEWS ===
responds = requests.get(url=URL, params=params)
json_data = responds.json()

# # Check for errors
if "Information" in json_data:
    print("Error:", json_data["Information"])
    exit()

articles = json_data.get("feed", [])

if not articles:
    print("No news articles found.")
else:
    print(f"Found {len(articles)} news articles:\n")
    print("=" * 120)
#
# # === Prepare Email Body ===
email_body_lines = []

for article in articles:
    title = article["title"]
    authors = ", ".join(article["authors"]) if article["authors"] else "Unknown"
    summary = article["summary"]
    published = article.get("published_utc", "Unknown time")
    overall_sentiment = article["overall_sentiment_label"]
    overall_sentiment_score = article["overall_sentiment_score"]

#     # Print to console
    print(f"🗞️  TITLE: {title}")
    print(f"📅 TIME: {published}")
    print(f"✍️  AUTHORS: {authors}")
    print(f"📊 OVERALL SENTIMENT: {overall_sentiment} ({overall_sentiment_score:.3f})")
    print(f"📝 SUMMARY: {summary}")

#     # === Process Ticker Sentiments ===
    ticker_sentiments = article.get("ticker_sentiment", [])
    ticker_lines = []
    if ticker_sentiments:
        print("💼 RELEVANT TICKERS:")
        for item in ticker_sentiments:
            symbol = item["ticker"]
            relevance = item["relevance_score"]
            sentiment_score = item["ticker_sentiment_score"]
            sentiment_label = item["ticker_sentiment_label"]

            ticker_line = f"   {symbol} | Relevance: {relevance} | Sentiment: {sentiment_label} ({sentiment_score})"
            ticker_lines.append(ticker_line)

            print(ticker_line)
    else:
        print("💼 RELEVANT TICKERS: None specified")

    # === Add to Email Body ===
    article_text = f"""
🗞️ TITLE: {title}
📅 Published: {published}
✍️ Authors: {authors}
📊 Overall Sentiment: {overall_sentiment} ({overall_sentiment_score:.3f})
📝 Summary: {summary}
"""
    if ticker_lines:
        article_text += "💼 Relevant Assets:\n" + "\n".join(ticker_lines)
    else:
        article_text += "💼 Relevant Assets: None specified"

    email_body_lines.append(article_text)
    print("-" * 120)

# # === SEND EMAIL (once, after all articles are processed) ===
if email_body_lines:
    full_email_body = "\n\n" + "\n\n".join(email_body_lines)

#     # Create MIME message
    msg = MIMEMultipart("alternative")
    msg["From"] = MY_EMAIL
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = "📈 Daily Trading News Update"

#     # Attach body
    text_body = f"Here are today's top market news updates:\n\n{full_email_body}"
    mime_text = MIMEText(text_body, "plain")
    msg.attach(mime_text)

#     # Send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=MY_PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=to_emails,
                msg=msg.as_string()
            )
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", str(e))
else:
    print("📭 No news to email.")

