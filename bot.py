from praw.models import MoreComments

from bot_utils import get_reddit, post_comment, send_email

import os
import time
from datetime import datetime, timedelta
import re


# import logging
# from loguru import logger

# Any environment setting other than 'false' or 'true' will evaluate to False
# DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
# READONLY = os.getenv('READONLY', 'false').lower() == 'true'
# COMMENT_LIMIT = int(os.getenv('COMMENT_LIMIT', -1))
# MAX_POST_AGE_DELTA = timedelta(minutes=int(os.getenv('MAX_POST_AGE_MINS', 30)))

# Set up logging
# logger.add("formatbot.log", backtrace=True, level=(logging.DEBUG if DEBUG else logging.INFO))
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG if DEBUG else logging.INFO)
# logger = logging.getLogger('prawcore')
# logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
# logger.addHandler(handler)
# logger.info('Bot started')
# logger.debug(me)


def main():
    # NOTE: Create a new Reddit account for your bot, follow their official instructions.
    # Add subreddits here and will build a + separated list
    # NOTE: even polling on these subreddits uses some credits, so disable the 'tech' related ones for now while I build karma.
    list_of_subreddits = [
        "testingground4bots",   # Comment out all others but this one first while testing!
        "UkrainianConflict",
        "Economics",
        # "apple",
        # "CryptoTechnology",
        "europe",
        # "Futurology",
        # "gadgets",
        "geopolitics",
        "GlobalTalk",
        # "google",
        # "hardware",
        "neutralnews",
        "news",
        "nottheonion",
        # "pcgaming",
        "PoliticalDiscussion",
        # "technology",
        "UpliftingNews",
        # "virtualreality",
        "worldnews",
        "politics",
        # "science",
        # "space",
        "AskHistorians",
        # "YouShouldKnow",
        "conspiracy",
        "Libertarian",
        "Conservative",
        "Liberal",
        "independent",
        # "offbeat",
        # "TrueReddit",
        "nba",
        "soccer",
        "nfl",
        # "Android",
        # "Bitcoin",
        # "CryptoCurrency",
        "USNews",
        "military",
        "todayilearned",
        "Coronavirus",
        "ukpolitics",
        "uknews",
        "AustralianPolitics",
    ]
    active_subreddits = "+".join(list_of_subreddits)
    
    # compile a regular expression and find potential comment_matches on test string
    # Don't need to do this every time in the loop.
    # https://regex101.com/r/QEcGwI/1
    # comment_matches "remove paywall" and an optional link.  Needs case insensitive comment_match.
    # /\s*(remove)\s+(paywall)\s+((http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]))?/gmi
    # group 1 = remove paywall
    # group 2 = http://www.example.com
    remove_paywall_regex = re.compile(r'\s*(remove paywall)(?:\s*)((http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]))?', re.IGNORECASE)

    # Used later to extract article url
    # Same as above but removed 'remove paywall' stuff and the url search no longer optional (? at end)
    article_url_regex = re.compile(r'((http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]))', re.IGNORECASE)

    # For now, just email me the post when people are asking for paywall removal
    paywall_word_regex = re.compile(r'(paywall)', re.IGNORECASE)

    print("INFO: Starting bot...")

    # Create reddit instance
    print("INFO: Getting Reddit client instance.")
    try:
        reddit = get_reddit()
        print("INFO: Reddit client instance obtained.")
    except Exception as e:
        print("ERROR: Failed to get Reddit client instance.")
        print(e)
        send_email(subject="Error in paywall bot script!", msg="ERROR: Failed to get Reddit client instance.")
        quit()

    # IMO this is confusing because Reddit refers to the "me" object which is actually the bot, not your own human Reddit handle.
    # Most people using this will have both, unless you decide to let the bot use your personal human handle (not recommended!)
    me = reddit.user.me().name.lower()              # 'xxx_BOT_HANDLE_xxx'  
    # To verify that you are authenticated as the correct user run:
    print(f"INFO: Reddit username: {me}")

    # # Get all comments from these subreddits
    # subreddit = reddit.subreddit(active_subreddits)

    # NOTE:
    # Later can add subreddits with the + sign
    # Then iterate over them like so:
    # for submission in reddit.subreddit("redditdev+learnpython").top(time_filter="all"):
    #     print(submission)
    # But mine would be more like:
    # for subreddit in reddit.subreddit("redditdev+learnpython")
    #     for comment in subreddit.stream.comments(skip_existing=True):
    # See official Reddit documentation, but this works for now.

    print(f"INFO: Monitoring subreddits: {active_subreddits}")
    print("INFO: Waiting for comments...")

    #############################################################
    # Main loop, lives in here
    #############################################################

    # Reddit gets 2.8M comments a day, which is 32 comments per second, which means we have to handle a comment in 30ms.
    # That's across all of Reddit though, we'll probably add subreddits manually.
    
    # Iterate over the actively subsribed subreddits
    # skip_existing so we don't process comments posted before the stream started
    for comment in reddit.subreddit(active_subreddits).stream.comments(skip_existing=True):

        if isinstance(comment, MoreComments):
            continue    # Skip comments if they are the MoreComments Tree object # https://praw.readthedocs.io/en/stable/tutorials/comments.html#extracting-comments-with-praw

        # When the bot posts a reply, that comment shows up in the feed too!  So we need to skip it.
        if comment.author.name.lower() == me:
            # print("INFO: skipping comment xxx_BOT_HANDLE_xxx just made!") # Don't clutter up the logs
            continue

        # See if the comment matches the key phrase "remove paywall [url]"
        comment_match = remove_paywall_regex.match(comment.body.strip())

        # If group 2 not there, needs to use the link in the submission, e.g. comment.submission.
        # If the comment includes group 2 url, then use that with paywall site.

        # Otherwise, if the comment just says "Remove paywall" and no additional text, then try to get the url from the submission.
        #   Check if submission is a self-post (post is text only).  If so, then search for first link within the post (like if they added commentary)
        #   because the url for the post will be like the reddit.com/blah/ link. --> Or just ignore self-posts.
        #   But if not a self-post, then use "url" field of the submission.

        # If matched the phrase at all
        # NOTE: In Real Life, my code never took this branch, though it was tested working in the 'testingground4bots' subreddit.
        # I never advertised this feature to users because my paywall site can't *guarantee* it can find a paywall-free version of every
        # article, so I decided it was a bad user experience in the end to have this bot post anything on my behalf, and it never did.
        if comment_match:        
            # If matched the phrase
            # group1 = remove paywall
            if comment_match[1]:
                # and there is a url in the comment
                # group2 = https://www.news.com/breaking-story/etc
                if comment_match[2]:
                    # print("has everything")
                    url = comment_match[2]
                    # print(url)
                    print(f"INFO: User commented with all info, including url: {url}")
                    post_comment(comment, url)
                    
                else:
                    # print("has everything but url")
                    print("INFO: User commented with all info, except url.")
                    # Try to get the url from the submission
                    parent_submission = comment.submission
                    if parent_submission.is_self:       # self-post *supposed* to mean it doesn't link outside Reddit, but have seen inconsistent.
                        # try to get the url from the submission
                        # print("self-post..")
                        # print(parent_submission.selftext)   # this had http://www.example.com

                        # Extract a link from the selftext
                        article_url_match = article_url_regex.match(parent_submission.selftext)

                        # If matched a url
                        if article_url_match[1]:
                            url = article_url_match[1]
                            # print(f"found a url match: {url}")
                            print(f"INFO: Self-post detected and url found in selftext: {url}")
                            # On these, we DO want to match if the selftext is a link.
                            # print(parent_submission.url)    # this had https://www.reddit.com/r/testingground4bots/comments/7xq7z/here+is_a_great_title/
                            post_comment(comment, url)
                            
                        else:
                            # skip if couldn't get a url from the selftext
                            print(f"WARNING: no url found in selftext, skipping. User comment at https://www.reddit.com{comment.permalink}")   # permalink is relative
                            continue
                    else:
                        # print("not self-post")
                        url = parent_submission.url
                        # print(f"url is: {url}")
                        if url is None:
                            print(f"WARNING: no url found in parent_submission.url, skipping. User comment at https://www.reddit.com{comment.permalink}")
                            continue
                        else:
                            print(f"INFO: Non-self-post detected, using parent_submission.url: {url}")
                            post_comment(comment, url)
                
                # After post attempts that weren't skipped, print the rate limits info
                print(f"INFO: Rate limits: {reddit.auth.limits}")
                
        else:
            # NOTE: Because I never advertised to anyone how to use the bot, the script only lived 100% of the time in this branch!
            # In other words, for the brief time I used this bot, anytime someone said "paywall" in an email, I got an email about it.
            # You can imagine, this got old fast.

            # Otherwise move on to next comment.  This will happen a TON so we don't want to print anything
            # print("no match")

            # If none of those other events happened, see if it just has the word "paywall" in the comment
            # If so, email me so I can manually demonstrate bot usage
            paywall_word_match = paywall_word_regex.match(comment.body)

            if paywall_word_match:

                # But skip if the user is me, because I usually type "Paywall-free version here:" when I manually comment
                if comment.author.name.lower() == 'xxx_HUMAN_REDDIT_HANDLE_xxx':  # this is different than the 'me' variable, which is actually the bot (Reddit's nomenclature)
                    continue    # Move on to next comment

                # If we get to here, send me an email so I can manually investigate the article on Reddit!
                parent_submission = comment.submission
                msg = f"See comment at: https://www.reddit.com{comment.permalink}    Parent post url at: https://www.reddit.com{parent_submission.permalink}"
                subject = "Paywall bot detected paywall word in comment"
                send_email(subject=subject, msg=msg)

            # Move on to next comment
            continue



if __name__ == "__main__":
    try:
        main()
    except Exception as e:

        # Trying to access private or restricted subreddit will result in a 403 error.
        # Banned subreddit will return 404.
        if ("403" in str(e)) or ("404" in str(e)) or ("502" in str(e)) or ("503" in str(e)) or ("500" in str(e)):
            print(f"ERROR: {e}")
        else:
            send_email(subject="Error in paywall bot script!", msg=f"ERROR: {e}")

        # quit either way, DigitalOcean will restart it automatically
        quit()