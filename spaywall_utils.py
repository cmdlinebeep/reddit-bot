from urllib.parse import urlparse
import praw
from mailjet_rest import Client

import config       # my global stuff

# Template uses markdown format
# NOTE: Originally my bot was going to respond to user's posts requesting a link to a paywall-free version of the article,
# but this never actually got used in practice.
REPLY_TEMPLATE = '''
Hello! I've attempted to find you a paywall-free version of the article you requested:  
{}  

___

Bot Usage:  
`Remove paywall` to default to the article in the original post.  
`Remove paywall https://news.com/breaking-story/` to manually specify the article.  (Useful if requesting a different article, like one mentioned in a comment).  

> If I've been helpful, karma helps me not get rate-limited! &mdash;🤖  
'''


def get_reddit():
    '''Return the Reddit Client'''
    reddit = praw.Reddit(
        client_id="xxx_REDDIT_CLIENT_ID_FOR_BOX_xxx",   # For my bot
        client_secret=config.REDDIT_CLIENT_SECRET,    
        password=config.REDDIT_PASSWORD,                # For my bot
        user_agent="script:xxx_BOT_HANDLE_xxx:v0.0.1 (by u/xxx_BOT_HANDLE_xxx)",  # I think this UA string is only seen by Reddit themselves
        username="xxx_BOT_HANDLE_xxx",
        ratelimit_seconds=(7*60),                   # try ratelimits at 7 minutes.  It will try again at 7 minutes, 1 second. https://praw.readthedocs.io/en/stable/getting_started/ratelimits.html
    )
    return reddit


def post_comment(comment, url):
    # Build the formatted Spaywall link
    parse_url = urlparse(url.strip())
    url = parse_url.scheme + "://" + parse_url.netloc + parse_url.path  # URL normalized to strip anchors and params
    url = "https://www.YOURLINKHERE.com/" + url

    # Build the formatted reply
    reply_text = REPLY_TEMPLATE.format(url)
    # print(reply_text)

    try:
        comment.reply(reply_text)
        print(f"INFO: successfully posted reply comment at https://www.reddit.com{comment.permalink}")   # Permalink is relative link
    except praw.exceptions.RedditAPIException as e:
        print(e)
        print(f"ERROR: Failed to post comment on https://www.reddit.com{comment.permalink}, likely rate-limited.")
    
    return


def send_email(subject, msg):
    # Create Mailjet client
    mailjet = Client(auth=(config.MAILJET_API_KEY, config.MAILJET_API_SECRET))

    # Create email object
    data = {
        'FromEmail': config.FROM_EMAIL,
        'FromName': 'Your Bot Name Here',
        'Subject': subject,
        'Text-part': f'{msg}.  See cloud logs for more details.',
        'Recipients': [{ "Email": config.TO_EMAIL}],
    }

    # Send the email
    result = mailjet.send.create(data=data)
    if str(result.status_code) != '200':
        print(f"WARNING: Issue sending email, non-200 status code: {result.status_code}")
    # print(f"INFO: Sent error email with result: {result.json()}")