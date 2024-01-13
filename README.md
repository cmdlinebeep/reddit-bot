# Create Your Own Reddit Bot

## My Bot's Backstory

Reddit has amazing and forward-thinking ability to allow good bots on their platform (at least, they did mid-2022 when I ran this bot, not sure if 2023 API changes will affect this).  

I wrote a bot to help spread the word about my website, which was a legal way to look and see if there is a non-paywalled version of an article on the internet.

Originally the bot was supposed to listen for keywords like "remove paywall www.article_link.com/blah" and automatically post a reply with the link to the paywall site.  This script does support that feature, and I did test it working on a small subreddit used for testing bots before they are ready for primetime.  But I realized an issue and never advertised this functionality to users, so, needless to say, no one ever said the magic *open sesame* words during the time the bot was active.  The issue has everything to do with the paywall site and nothing to do with this bot, and that is, I cannot guarantee 100% of the time that the site will always find a paywall-free version of the article.  So I didn't want this bot to be like a genie you could summon only to find that some non-trivial percent of the time, it couldn't do as you commanded.  I figured that would lead to a bad user experience for the bot, and also negative feelings towards my site, hence why I never advertised the feature of the bot.

However, what the bot did spend its life doing, was just looking for the word "paywall" in every comment on any subreddit the bot was subscribed to.  If it found that word on these news-related subreddits, it would simply send me an email and I could manually investigate.  In other words, if people on Reddit were talking about paywalls, I wanted to know about it!  This worked well for a long period, and if my site could find the paywall-free version, I would manually post that in the original thread.  This got me a lot of word-of-mouth advertising and growth really exploded.  But I got tired of being slave to my inbox whenever an email would come in.  I also had to pay some small amount for hosting this bot on Digital Ocean, and my site made me next to nothing, so it wasn't worth continuing to run it.

## Bot Setup with Reddit

I'm not going to rewrite all of Reddit's documentation here.  I found [this tutorial](https://new.pythonforengineers.com/blog/build-a-reddit-bot-part-1/) very helpful for the initial administrative setup stuff.  You also might want ot read the documention on the PRAW Python library [here](https://praw.readthedocs.io/en/stable/) (the official client).

In a nutshell, you're going to need to create a new account for the bot (highly recommended), register your script as an 'app' with Reddit, and get your authentication tokens.

## Running the Bot (and on DigitalOcean or other cloud provider)

You can run the bot locally, or on a cloud provider like Digital Ocean (in which case you'll need the included Pipfile, Procfile, and runtime.txt files).

You'll need to set your secrets as local environment variables first.

```
set REDDIT_PASSWORD=<blah>
set REDDIT_CLIENT_SECRET=<blah>
set MAILJET_API_KEY=<blah>
set MAILJET_API_SECRET=<blah>
pip install -r requirements.txt
python bot.py
```

## Example Message that the Bot was intended to post

Hello! I've attempted to find you a paywall-free version of the article you requested:  
{link_would_go_here}  

___

Bot Usage:  
`Remove paywall` to default to the article in the original post.  
`Remove paywall https://news.com/breaking-story/` to manually specify the article.  (Useful if requesting a different article mentioned in a comment).  

> If I've been helpful, karma helps me not get rate-limited! &mdash;🤖  

