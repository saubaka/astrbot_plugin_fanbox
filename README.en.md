<p align="center">
  <img src="https://raw.githubusercontent.com/saubaka/astrbot_plugin_fanbox/main/logo.png" width="128" height="128" alt="FANBOX 新帖推送">
</p>

<h1 align="center">FANBOX 新帖推送</h1>

<p align="center">
  <a href="https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/README.md">简体中文</a> · <a href="https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/README.zh-TW.md">繁體中文</a> · <a href="https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/README.ja.md">日本語</a> · <b>English</b>
</p>

<p align="center">An AstrBot plugin that pushes new posts from the pixivFANBOX creators you follow to QQ groups or private chats</p>

<p align="center">
  <a href="https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/LICENSE"><img src="https://img.shields.io/github/license/saubaka/astrbot_plugin_fanbox?color=f0a0ba" alt="License"></a>
  <a href="https://github.com/saubaka/astrbot_plugin_fanbox/releases"><img src="https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fsaubaka%2Fastrbot_plugin_fanbox%2Fmain%2Fmetadata.yaml&query=%24.version&label=version&color=8cc2ee" alt="Version"></a>
  <a href="https://github.com/AstrBotDevs/AstrBot"><img src="https://img.shields.io/badge/AstrBot-%E2%89%A5%204.26.0-8cc2ee" alt="AstrBot"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-a29ba0" alt="Python">
  <img src="https://img.shields.io/badge/platform-aiocqhttp-a29ba0" alt="Platform">
</p>

## Overview

An [AstrBot](https://github.com/AstrBotDevs/AstrBot) plugin for following [pixivFANBOX](https://www.fanbox.cc) creators. Whenever a creator you follow publishes a new post, the plugin sends a message to the QQ group or private chat where you subscribed.

There are two push styles. The text style builds a message from a "push template", where you can combine variables freely and place images anywhere. The card style renders an image modeled on FANBOX's post cards, with the cover, avatar, name, date, plan, title, excerpt and like count. You can also add text above and below the card, for example a link to the post underneath the image.

The plugin also comes with a dashboard page where you can browse the push history, manage subscriptions, change every setting and preview pushes in real time.

By default, covers of R-18 posts are not sent. On card images the cover is replaced with "R-18 · 封面已隐藏" so that adult images don't show up in QQ groups.

## Installation

In the AstrBot dashboard, open "Plugins → Install plugin → Install from link" and enter `https://github.com/saubaka/astrbot_plugin_fanbox`. To install it manually, put this repository in AstrBot's `data/plugins/astrbot_plugin_fanbox` folder, then restart AstrBot or reload the plugin from the dashboard.

The plugin depends on `httpx` and `Pillow`, which AstrBot already ships with. Card images need a CJK font. By default the plugin uses the system's Noto Sans CJK (the package is `fonts-noto-cjk` on Debian and Ubuntu), and you can point it to other font files in the settings.

It requires AstrBot v4.26.0 or later and has been tested on aiocqhttp (OneBot v11).

## Commands

| Command | Alias | What it does |
|---|---|---|
| `/fanbox关注 <creator ID or page link>` | `fanbox_follow` | Follow this creator in the current chat |
| `/fanbox取关 <creator ID>` | `fanbox_unfollow` | Unfollow the creator in the current chat |
| `/fanbox列表` | `fanbox_list` | List the creators followed in the current chat and where each one's pushes start |
| `/fanbox最新 <creator ID>` | `fanbox_latest` | Send the creator's latest post in the current push style. Useful for previewing the style; it doesn't affect push progress |
| `/fanbox变量` | `fanbox_vars` | List every variable available in templates |
| `/fanbox检查` | `fanbox_check` | Check all subscriptions right away (admins only) |

The command names are in Chinese, so type them exactly as shown above or use the English aliases. A creator ID is the `<ID>` part of the creator's page address `https://<ID>.fanbox.cc`. You can also paste links such as `https://www.fanbox.cc/@<ID>` directly.

## Dashboard page: FANBOX 推送面板

In the AstrBot dashboard, open "Plugin pages → FANBOX 新帖推送". Use the tabs in the top left to switch sections. The "本页章节" (on this page) bar on the right jumps straight to each part of the current tab and turns into a row of buttons at the top on narrow screens. The data refreshes every 30 seconds.

The page itself is in Chinese. The table gives each tab's name followed by a translation.

| Tab | Contents |
|---|---|
| 概览 (Overview) | Pushes in the last 24 hours with an hourly trend, plus the number of followed creators, checks, a countdown to the next check, pushes in the last 7 days, errors and total pushes. Each creator gets a card showing posts pushed, check results, hourly check activity and the latest post. "预览样式" (preview style) takes you straight to the live preview. |
| 推送记录 (Push history) | Shown as FANBOX-style post cards by default. The lower-left corner of each cover tells you which chat it was sent to, which style was used and whether it was delivered. Entries are grouped by day and can be switched to a list. Recent errors are listed below. |
| 订阅 (Subscriptions) | Add a subscription by picking a group from your QQ group list, or enter a QQ number to subscribe in a private chat. Each chat has its own block where you can preview or unsubscribe. |
| 推送样式 (Push style) | Once you pick a push style, only the settings that style uses are shown: the push template for the text style, or the card caption and card image settings for the card style. Switching styles animates the groups in and out. Click a variable to insert it into a template. The live preview sits on the right, or below the settings on narrow screens. After you enter a post link (`https://<ID>.fanbox.cc/posts/<post number>`) or a creator ID, every change to the settings re-renders the preview in the new style, including unsaved changes. Each bubble in the preview is one QQ message. Below the preview you can send a test push of that message to a chosen chat or private chat; it takes two clicks to confirm. Test pushes don't advance subscription progress, aren't counted in the statistics, and are marked "测试" (test) in the push history. |
| 设置 (Settings) | Basic settings and push start point. |

Settings take effect as soon as you save them, with no restart needed. Changing the polling interval restarts the timer with the new interval right away.

To preview a specific post, the plugin pages back through the creator's post list to find it, up to 30 pages. Posts are cached for 5 minutes and images for 30 minutes, so the preview stays fast while you tweak the style.

Statistics are stored in the plugin data key `fanbox_stats_v1`. Hourly statistics are kept for 90 days, and the latest 60 pushes and 60 errors are kept, with errors dropped after 30 days at most.

AstrBot runs plugin pages inside a sandboxed iframe that can't open new windows, so links on the page are "copy link" buttons instead.

## Push start point

By default, the plugin only pushes posts published after it was deployed, and never digs up older posts.

| Start point (`start_from`) | Which posts get pushed |
|---|---|
| `deploy` (default) | Posts published after the plugin first started. Posts published after deployment but before you subscribed are pushed at the first check after subscribing, at most `max_new_posts_per_poll` at a time. |
| `subscribe` | Each subscription starts counting from the moment you subscribed. Posts published before that are never pushed. |
| `custom` | Posts published after the time in `start_time`. Write the time as `2026-11-15 08:00` to have it read in the "timezone" setting, or include the offset, as in `2026-11-15T08:00:00+09:00`. If the format is wrong, the plugin falls back to `deploy` and says so in the log. |

The time the plugin first started is stored in the plugin data key `fanbox_deployed_at` and doesn't change when you update or restart.

When `max_post_age_hours` is a positive number, posts older than that many hours aren't pushed. For example, if the bot was down for a long time, it won't flood the chat with old posts when it comes back. The default, 0, means no limit.

Whichever start point you choose, each post is pushed to the same chat only once.

## Settings

The settings come in 5 groups and can be changed on the plugin page or in AstrBot's built-in plugin settings. The built-in settings also show only the items the current push style uses, but they lack subscription management, the live preview and test pushes, so the plugin page is recommended.

**Basic settings**

| Setting | Default | Description |
|---|---|---|
| `poll_interval_minutes` | 10 | Polling interval, at least 5 minutes. Each check requests each creator's post list once. |
| `max_new_posts_per_poll` | 3 | The most posts pushed per creator in one check |
| `proxy` | empty | Proxy used to reach FANBOX |

**Push start point**

| Setting | Default | Description |
|---|---|---|
| `start_from` | deploy | See the previous section |
| `start_time` | empty | The start time when `custom` is selected |
| `max_post_age_hours` | 0 | Skip posts older than this many hours; 0 means no limit |

**Push style**

| Setting | Default | Description |
|---|---|---|
| `push_style` | card | `text` sends messages from the push template; `card` sends a card image using the card caption template, and falls back to the push template if the card can't be rendered |
| `card_text` | merge | How captions go with the card image (only for the `card` style). `merge` combines the text and the card into one message in template order, `separate` sends the text above the card, the card and the text below the card as separate messages, and `none` sends only the card |
| `message_template` | see below | Push template for the `text` style. Clear it to restore the default |
| `card_template` | see below | Card caption template for the `card` style. It must keep exactly one `{card_image}`. Clear it to restore the default |
| `send_cover` | off | For the text style, whether `{cover_image}` in templates is sent |
| `send_adult_cover` | off | Send covers for R-18 posts too, and show the real cover on card images |
| `creator_cover_fallback` | on | When a post has no cover, use the creator page's cover instead, the same image FANBOX uses when sharing such posts. Applies to both card images and `{cover_image}`; when turned off, the card shows a gray placeholder |

**Displayed content** (applies to both templates and card images)

| Setting | Default | Description |
|---|---|---|
| `show_fee` | on | Show the paid plan |
| `show_timezone` | off | Add a timezone name such as "（日本时间）" after times |
| `show_tags` | on | Show tags |
| `show_adult_mark` | on | Show the R-18 mark |
| `excerpt_max_chars` | 120 | Maximum length of `{excerpt}`; 0 hides it |
| `max_tags` | 6 | The most tags to show |
| `time_format` | `%Y-%m-%d %H:%M` | Time format for `{published}` and `{updated}` (strftime syntax) |
| `timezone_offset_hours` | 9 | Timezone offset: 9 is Japan time (as on the FANBOX website), 8 is Beijing time |

**Card image**

| Setting | Default | Description |
|---|---|---|
| `card_show_likes` | on | Show the like count in the lower right |
| `card_excerpt_lines` | 2 | Maximum lines of excerpt; 0 hides it |
| `card_title_lines` | 2 | Maximum lines of title |
| `card_font_path` / `card_bold_font_path` | empty | Custom font files; Noto Sans CJK is used when empty |

Card images are 1430 pixels wide (the size of the web page on a 2x display), saved as JPEG at roughly 150 to 400 KB. Color emoji have no matching font and are left out of card images; emoji in text messages are unaffected.

## Push template

The plugin's output text is in Simplified Chinese, so the templates and sample values below are left as they are. The default template is:

```
【FANBOX】{creator_name} {headline}
《{title}》
{labels}
{excerpt}
{tags}
?发布时间：{published}
{post_url}
{cover_image}
```

### Card caption template

This template is used when the push style is `card`. The `{card_image}` in it is the card image itself: it has to stay, and there can only be one. The editor on the plugin page won't let you delete it, and if a template is missing it, the plugin adds it at the end. Text written above `{card_image}` appears above the card, and text written below it appears below the card. Other variables and rules work the same as in the push template, but other image variables are ignored here, since the card already contains the cover and avatar. The default template puts the creator's name and a short line above the card:

```
{creator_name}
发布了新的FANBOX文章：
{card_image}
```

With `card_text` set to `merge`, all of this is one QQ message, with the text on top and the card below. To put the post link under the card, add a `{post_url}` line below `{card_image}`. With `separate` (called "分开发" on the plugin page), the message is split at the card, and the text above, the card and the text below are sent one by one. With `none`, only the card is sent and the template isn't used.

On the plugin page, the "把卡片图移到光标处" (move card to cursor) button moves the card to a different spot in the template.

### Template rules

1. `{variable}` is replaced with its value. Variable names are case-sensitive.
2. `{{` and `}}` stand for literal braces.
3. An unknown `{xxx}` is shown as is, and the plugin mentions it in the log when it loads.
4. A line whose variables are all empty and that has no other text is removed automatically.
5. A line starting with `?` is conditional: if any variable in it is empty, the whole line is removed. The `?` itself is never shown, for example `?发布时间：{published}`.
6. An image variable puts the image exactly where you write it in the message.
7. An empty template means the default template is used.

### Text variables (30)

The sample values come from a paid post on the 500 yen plan, with every setting at its default.

| Variable | Meaning | Sample value |
|---|---|---|
| `{headline}` | "发布了新帖" (posted something new) for pushes, "的最新帖子" (latest post) for /fanbox最新 | `发布了新帖` |
| `{creator_name}` | Creator's display name | `pixivFANBOX公式` |
| `{creator_id}` | Creator ID, the <ID> in the page address https://<ID>.fanbox.cc | `official` |
| `{creator_url}` | Link to the creator's page | `https://official.fanbox.cc` |
| `{creator_icon_url}` | Link to the creator's avatar image | `https://pixiv.pximg.net/c/160x160_90_a2_g5/fanbox/public/…` |
| `{title}` | Post title, or "（无标题）" (untitled) when there is none | `新作イラストのお知らせ` |
| `{post_id}` | Post ID | `1234567` |
| `{post_url}` | Link to the post | `https://official.fanbox.cc/posts/1234567` |
| `{excerpt}` | Excerpt, cut to the "maximum excerpt length" setting; paid posts usually have no excerpt | `いつも応援ありがとうございます。今月の新作です。` |
| `{excerpt_full}` | The full excerpt, with blank lines tidied but nothing cut | `いつも応援ありがとうございます。今月の新作です。` |
| `{fee}` | Plan amount, 0 for free posts; not affected by "show the paid plan" | `500` |
| `{fee_text}` | "付费 · 500 日元及以上档位" (paid, 500 yen plan and above) or "免费公开" (free); empty when "show the paid plan" is off | `付费 · 500 日元及以上档位` |
| `{fee_badge}` | "500日元" or "免费" (free); empty when "show the paid plan" is off | `500日元` |
| `{paid}` | "付费" (paid) or "免费" (free); not affected by "show the paid plan" | `付费` |
| `{adult}` | "R-18" for R-18 posts, otherwise empty; also empty when "show the R-18 mark" is off | (empty) |
| `{labels}` | Plan and R-18 mark joined with " · ", for example "付费 · 500 日元及以上档位 · R-18" | `付费 · 500 日元及以上档位` |
| `{restricted}` | "需赞助" (support required) when the post body needs a paid plan, otherwise empty | `需赞助` |
| `{tags}` | Tags written as "#tag1 #tag2"; empty when "show tags" is off | `#イラスト #メイキング` |
| `{tags_plain}` | Tags joined as "tag1、tag2"; empty when "show tags" is off | `イラスト、メイキング` |
| `{tag_count}` | Number of tags | `2` |
| `{published}` | Publication time in the "time format" and timezone, followed by "（北京时间）" when "show the timezone" is on | `2026-11-13 21:12` |
| `{published_date}` | Publication date, such as 2026-11-13 | `2026-11-13` |
| `{published_time}` | Publication time of day, such as 20:12 | `21:12` |
| `{published_iso}` | FANBOX's original publication time, in ISO format in Japan time | `2026-11-13T21:12:54+09:00` |
| `{updated}` | Last update time, in the same format as published | `2026-11-14 09:30` |
| `{timezone}` | Timezone name, such as "北京时间" (Beijing time); not affected by "show the timezone" | `日本时间` |
| `{like_count}` | Number of likes | `12` |
| `{comment_count}` | Number of comments | `3` |
| `{cover_url}` | Link to the cover image. When the post has no cover, the creator page's cover is used depending on the setting; empty for R-18 posts when their covers aren't allowed | `https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public…` |
| `{pinned}` | "置顶" (pinned) for pinned posts, otherwise empty | (empty) |

### Image variables (3)

| Variable | Meaning |
|---|---|
| `{cover_image}` | Cover image. When the post has no cover, the creator page's cover is used depending on the setting. Not sent when "attach cover" is off, or for R-18 posts when their covers aren't allowed |
| `{card_image}` | Card image styled after FANBOX's web page |
| `{avatar_image}` | Creator's avatar |

### Template examples

Only the card, with a link underneath:

```
{card_image}
{post_url}
```

A short one-liner:

```
{creator_name} 更新了《{title}》 {fee_badge} {post_url}
```

Avatar plus details:

```
{avatar_image}
{creator_name}（{creator_id}）{headline}
《{title}》 {labels}
?标签：{tags_plain}
?{published_date} {published_time} {timezone}
♥ {like_count}  评论 {comment_count}
{post_url}
{cover_image}
```

## Known limitations

Some posts have no cover, and FANBOX's web page shows only a gray placeholder for them. In that case the plugin uses the creator page's cover by default; you can turn this off in the settings.

Each check only looks at the 10 latest posts of each creator. If a creator publishes more than 10 posts between two checks, the older ones won't be pushed.

Subscriptions are stored in AstrBot's plugin data under the key `fanbox_subscriptions_v1`.

## Development

```bash
python -m pytest -q tests
python -m ruff check .
python -m ruff format --check .
python -m compileall -q .
python -m json.tool _conf_schema.json
```

`fanbox_core.py`, `fanbox_api.py`, `fanbox_card.py`, `fanbox_stats.py` and `fanbox_settings.py` don't depend on AstrBot. `fanbox_webui.py` is the plugin page's backend and `pages/dashboard/` is its frontend. The tests need `httpx`, `pytest` and `Pillow`; card tests are skipped when the Noto Sans CJK font isn't available.

## License

This plugin is released under the MIT License. See [LICENSE](https://github.com/saubaka/astrbot_plugin_fanbox/blob/main/LICENSE) for details.
